from contextlib import closing

from flask import Blueprint, render_template, request

from datenbank import verbinden
from hilfen import ASSET_KOPF, ASSET_SQL, abfragen, leere_spalten_entfernen

bp = Blueprint("infos", __name__)


@bp.route("/infos")
def infos():
    return render_template("infos.html")


@bp.route("/info/statistik")
def info_statistik():
    with closing(verbinden()) as verbindung:
        def zahl(sql):
            return verbindung.execute(sql).fetchone()[0]

        gesamt = zahl("SELECT COUNT(*) FROM assets")
        mitarbeiter = zahl("SELECT COUNT(*) FROM mitarbeiter")
        ausgegeben = zahl("SELECT COUNT(*) FROM assets WHERE status = 'Ausgegeben'")
        lager = zahl("SELECT COUNT(*) FROM assets WHERE LOWER(TRIM(status)) = 'lager'")
        sonstige = gesamt - ausgegeben - lager

        pro_typ = verbindung.execute("""
            SELECT COALESCE(NULLIF(assettyp, ''), 'Ohne Typ'), COUNT(*)
            FROM assets
            GROUP BY 1
            ORDER BY 2 DESC, 1
        """).fetchall()

    kennzahlen = [
        ("📦", "Assets gesamt", gesamt),
        ("👤", "Mitarbeiter", mitarbeiter),
        ("✅", "Ausgegeben", ausgegeben),
        ("🏢", "Im Lager", lager),
        ("🔧", "Sonstiger Status", sonstige),
    ]
    maximum = max((n for _, n in pro_typ), default=1)

    return render_template("statistik.html", kennzahlen=kennzahlen,
                           pro_typ=pro_typ, maximum=maximum)


@bp.route("/info/lagerbestand")
def info_lagerbestand():
    typ = request.args.get("typ", "")

    typen = [z[0] for z in abfragen(
        "SELECT DISTINCT assettyp FROM assets "
        "WHERE assettyp IS NOT NULL AND assettyp != '' ORDER BY assettyp"
    )]

    kopf, zeilen, hinweis = [], [], None

    if typ:
        sql = ASSET_SQL + " WHERE LOWER(TRIM(status)) = 'lager'"
        parameter = ()
        if typ != "ALLE":
            sql += " AND assettyp = ?"
            parameter = (typ,)
        sql += " ORDER BY assettyp, inventarnummer"

        zeilen = abfragen(sql, parameter)
        kopf, zeilen = leere_spalten_entfernen(ASSET_KOPF, zeilen)
        hinweis = f"Anzahl Assets im Lager: {len(zeilen)}"

    return render_template("info_seite.html",
                           titel="📦 Lagerbestand",
                           hinweis=hinweis, kopf=kopf, zeilen=zeilen,
                           typen=typen, typ=typ)


@bp.route("/info/geraetetypen")
def info_geraetetypen():
    zeilen = abfragen("""
        SELECT COALESCE(NULLIF(assettyp, ''), 'Ohne Typ'), COUNT(*)
        FROM assets
        GROUP BY 1
        ORDER BY 2 DESC, 1
    """)
    return render_template("info_seite.html",
                           titel="🖥️ Gerätetypen",
                           hinweis=f"{len(zeilen)} Typen",
                           kopf=["Gerätetyp", "Anzahl"], zeilen=zeilen)