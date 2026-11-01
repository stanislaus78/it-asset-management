from contextlib import closing

from flask import Blueprint, render_template, request
from hilfen import (
    ABSCHREIBUNG_TYPEN, ASSET_KOPF, ASSET_SQL, NUTZUNGSDAUER_JAHRE, WARN_TAGE,
    abfragen, jahre_addieren, leere_spalten_entfernen,
)
from datenbank import verbinden
from hilfen import ASSET_KOPF, ASSET_SQL, abfragen, leere_spalten_entfernen
from datetime import date, datetime, timedelta

from hilfen import (
    ASSET_KOPF, ASSET_SQL, NUTZUNGSDAUER_JAHRE, WARN_TAGE,
    abfragen, jahre_addieren, leere_spalten_entfernen,
)
from hilfen import (
    ABSCHREIBUNG_TYPEN, ASSET_KOPF, ASSET_SQL, NUTZUNGSDAUER_JAHRE, WARN_TAGE,
    abfragen, garantie_monate, jahre_addieren, leere_spalten_entfernen,
    monate_addieren,
)
from hilfen import (
    ABSCHREIBUNG_TYPEN, ASSET_KOPF, ASSET_SQL, GARANTIE_TYPEN, NUTZUNGSDAUER_JAHRE,
    WARN_TAGE, abfragen, garantie_monate, jahre_addieren, leere_spalten_entfernen,
    monate_addieren,
)

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


STATUS_TEXT = {
    "abgelaufen": "🔴 Abgelaufen",
    "bald": "🟠 Läuft bald ab",
    "gueltig": "🟢 Gültig",
}


@bp.route("/info/abschreibung")
def info_abschreibung():
    filter_status = request.args.get("status", "")
    typ = request.args.get("typ", "")

    heute = date.today()
    grenze = heute + timedelta(days=WARN_TAGE)

    platzhalter = ", ".join("?" for _ in ABSCHREIBUNG_TYPEN)

    rohdaten = abfragen(f"""
        SELECT inventarnummer, assettyp, hersteller, modell, mitarbeiter,
               anschaffungsdatum
        FROM assets
        WHERE LOWER(assettyp) IN ({platzhalter})
          AND anschaffungsdatum GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
          AND LOWER(COALESCE(status, '')) != 'ausgeschieden'
    """, ABSCHREIBUNG_TYPEN)

    ohne_datum = abfragen(f"""
        SELECT COUNT(*) FROM assets
        WHERE LOWER(assettyp) IN ({platzhalter})
          AND LOWER(COALESCE(status, '')) != 'ausgeschieden'
          AND (anschaffungsdatum IS NULL
               OR anschaffungsdatum NOT GLOB
                  '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
    """, ABSCHREIBUNG_TYPEN)[0][0]

    eintraege = []
    for inv, art, hersteller, modell, benutzer, anschaffung in rohdaten:
        try:
            start = datetime.strptime(anschaffung, "%Y-%m-%d").date()
        except ValueError:
            ohne_datum += 1
            continue

        ende = jahre_addieren(start, NUTZUNGSDAUER_JAHRE)
        if ende < heute:
            status = "abgelaufen"
        elif ende <= grenze:
            status = "bald"
        else:
            status = "gueltig"

        eintraege.append({
            "inventarnummer": inv,
            "typ": art or "",
            "geraet": " ".join(t for t in (hersteller, modell) if t),
            "benutzer": benutzer or "",
            "anschaffung": start.strftime("%d.%m.%Y"),
            "ende": ende,
            "ende_text": ende.strftime("%d.%m.%Y"),
            "status": status,
        })

    typen = sorted({e["typ"] for e in eintraege if e["typ"]})
    sichtbar = [e for e in eintraege if not typ or e["typ"] == typ]
    anzahl = {k: sum(1 for e in sichtbar if e["status"] == k) for k in STATUS_TEXT}

    if filter_status in STATUS_TEXT:
        sichtbar = [e for e in sichtbar if e["status"] == filter_status]
    sichtbar.sort(key=lambda e: e["ende"])

    return render_template("abschreibung.html",
                           eintraege=sichtbar, anzahl=anzahl, typen=typen,
                           typ=typ, filter_status=filter_status,
                           status_text=STATUS_TEXT, ohne_datum=ohne_datum,
                           jahre=NUTZUNGSDAUER_JAHRE, warn_tage=WARN_TAGE)

@bp.route("/info/garantie")
def info_garantie():
    filter_status = request.args.get("status", "")
    typ = request.args.get("typ", "")

    heute = date.today()
    grenze = heute + timedelta(days=WARN_TAGE)

    platzhalter = ", ".join("?" for _ in GARANTIE_TYPEN)

    rohdaten = abfragen(f"""
        SELECT inventarnummer, assettyp, hersteller, modell, mitarbeiter,
               anschaffungsdatum, garantie
        FROM assets
        WHERE LOWER(assettyp) IN ({platzhalter})
          AND LOWER(COALESCE(status, '')) != 'ausgeschieden'
    """, GARANTIE_TYPEN)

    eintraege = []
    nicht_auswertbar = 0
    for inv, art, hersteller, modell, benutzer, anschaffung, garantie in rohdaten:
        try:
            start = datetime.strptime(anschaffung or "", "%Y-%m-%d").date()
        except ValueError:
            nicht_auswertbar += 1
            continue

        monate = garantie_monate(garantie)
        if monate is None:
            nicht_auswertbar += 1
            continue

        ende = monate_addieren(start, monate)
        if ende < heute:
            status = "abgelaufen"
        elif ende <= grenze:
            status = "bald"
        else:
            status = "gueltig"

        eintraege.append({
            "inventarnummer": inv,
            "typ": art or "",
            "geraet": " ".join(t for t in (hersteller, modell) if t),
            "benutzer": benutzer or "",
            "dauer": garantie,
            "anschaffung": start.strftime("%d.%m.%Y"),
            "ende": ende,
            "ende_text": ende.strftime("%d.%m.%Y"),
            "status": status,
        })

    typen = sorted({e["typ"] for e in eintraege if e["typ"]})
    sichtbar = [e for e in eintraege if not typ or e["typ"] == typ]
    anzahl = {k: sum(1 for e in sichtbar if e["status"] == k) for k in STATUS_TEXT}

    if filter_status in STATUS_TEXT:
        sichtbar = [e for e in sichtbar if e["status"] == filter_status]
    sichtbar.sort(key=lambda e: e["ende"])

    return render_template("garantie.html",
                           eintraege=sichtbar, anzahl=anzahl, typen=typen,
                           typ=typ, filter_status=filter_status,
                           status_text=STATUS_TEXT,
                           nicht_auswertbar=nicht_auswertbar, warn_tage=WARN_TAGE)