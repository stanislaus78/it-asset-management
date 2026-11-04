from flask import Blueprint, abort, render_template, request

from asset_typen import FELDER, TYPEN
from hilfen import abfragen

bp = Blueprint("asset_generisch", __name__)


@bp.route("/liste/<slug>")
def asset_liste(slug):
    typ = TYPEN.get(slug)
    if typ is None:
        abort(404)

    felder = []      # (name, Beschriftung, Sortierschlüssel)
    ausdruecke = []  # SQL-Ausdrücke für das SELECT
    for n in typ.felder():
        spalte = FELDER[n][1]
        if n in typ.berechnet:
            ausdruecke.append(f"({typ.berechnet[n]}) AS {n}")
            felder.append((n, typ.label(n), n))
        elif n in typ.anzeige_standard:
            vorgabe = typ.anzeige_standard[n].replace("'", "''")
            ausdruecke.append(f"COALESCE(NULLIF({spalte}, ''), '{vorgabe}') AS {n}")
            felder.append((n, typ.label(n), n))
        else:
            ausdruecke.append(spalte)
            felder.append((n, typ.label(n), spalte))

    erlaubt = [s for _, _, s in felder]
    sort = request.args.get("sort", "")
    spalte = sort if sort in erlaubt else "inventarnummer"
    richtung = request.args.get("richtung", "ASC")
    if richtung not in ("ASC", "DESC"):
        richtung = "ASC"

    zeilen = abfragen(
        f"SELECT id, {', '.join(ausdruecke)} FROM assets "
        f"WHERE LOWER(assettyp) = ? ORDER BY {spalte} COLLATE NOCASE {richtung}",
        (typ.assettyp.lower(),),
    )
    return render_template("asset_liste.html", typ=typ, felder=felder,
                           zeilen=zeilen, konfig=typ.fuer_js())