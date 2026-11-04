from flask import Blueprint, abort, render_template, request

from asset_typen import FELDER, TYPEN
from hilfen import abfragen

bp = Blueprint("asset_generisch", __name__)


@bp.route("/liste/<slug>")
def asset_liste(slug):
    typ = TYPEN.get(slug)
    if typ is None:
        abort(404)

    felder = [(n, FELDER[n][0], FELDER[n][1]) for n in typ.felder()]
    spalten = [s for _, _, s in felder]

    sort = request.args.get("sort", "")
    spalte = sort if sort in spalten else "inventarnummer"
    richtung = request.args.get("richtung", "ASC")
    if richtung not in ("ASC", "DESC"):
        richtung = "ASC"

    zeilen = abfragen(
        f"SELECT id, {', '.join(spalten)} FROM assets "
        f"WHERE LOWER(assettyp) = ? ORDER BY {spalte} COLLATE NOCASE {richtung}",
        (typ.assettyp.lower(),),
    )
    return render_template("asset_liste.html", typ=typ, felder=felder,
                           zeilen=zeilen, konfig=typ.fuer_js())
