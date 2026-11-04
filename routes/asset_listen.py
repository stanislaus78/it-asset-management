from flask import Blueprint, render_template, request

from hilfen import ASSET_SPALTEN, abfragen

bp = Blueprint("asset_listen", __name__)

ERLAUBTE_SORT = {name for name, _ in ASSET_SPALTEN} | {"id"}

BASIS = ("id, inventarnummer, seriennummer, mitarbeiter, standort, zimmer, "
         "kostenstelle, organisationseinheit, hersteller, modell, status, "
         "anschaffungsdatum, bemerkung")

MOBIL = ("id, inventarnummer, seriennummer, mitarbeiter, standort, zimmer, "
         "kostenstelle, organisationseinheit, hersteller, modell, displaygroesse, "
         "ram, festplatte, mac_adresse, status, garantie, anschaffungsdatum, bemerkung")

# Jeder Eintrag: URL, Endpoint, Template, Variablenname im Template, Assettyp,
# Spalten im SELECT, Standard-Sortierung (optional: Alias für Sortier-Links)
LISTEN = [
    dict(url="/assets/laptop", endpoint="laptops", template="laptops.html",
         variable="laptops", typ="laptop", spalten="*", sort="rechnername"),
    dict(url="/assets/standpc", endpoint="standpcs", template="standpc.html",
         variable="standpcs", typ="stand-pc", spalten="*", sort="rechnername"),
    dict(url="/assets/monitor", endpoint="monitore", template="monitore.html",
         variable="monitore", typ="monitor", spalten="*"),

    dict(url="/assets/tablet", endpoint="tablets", template="tablets.html",
         variable="tablets", typ="tablet", spalten=MOBIL),
    dict(url="/assets/diensthandy", endpoint="diensthandys", template="diensthandys.html",
         variable="diensthandys", typ="diensthandy", spalten=MOBIL),

    dict(url="/assets/drucker", endpoint="drucker", template="drucker.html",
         variable="druckerliste", typ="drucker",
         spalten=("id, inventarnummer, seriennummer, mitarbeiter, standort, zimmer, "
                  "kostenstelle, organisationseinheit, hersteller, modell, druckertyp, "
                  "mac_adresse, status, garantie, anschaffungsdatum, bemerkung")),
    dict(url="/assets/zubehoer", endpoint="zubehoer", template="zubehoer.html",
         variable="zubehoerliste", typ="zubehoer",
         spalten=("id, inventarnummer, seriennummer, mitarbeiter, standort, zimmer, "
                  "kostenstelle, organisationseinheit, hersteller, modell, verwendungsart, "
                  "status, anschaffungsdatum, bemerkung"),
         alias={"geraetetyp": "verwendungsart"}),
    dict(url="/assets/switch", endpoint="switches", template="switch.html",
         variable="switches", typ="switch",
         spalten=("id, inventarnummer, seriennummer, standort, zimmer, kostenstelle, "
                  "organisationseinheit, hersteller, modell, verwendungsart, status, "
                  "anschaffungsdatum, bemerkung")),

    dict(url="/assets/scanner", endpoint="scanner", template="scanner.html",
         variable="scanners", typ="scanner", spalten=BASIS),
    dict(url="/assets/kopfhoerer", endpoint="kopfhoerer", template="kopfhoerer.html",
         variable="kopfhoerern", typ="kopfhoerer", spalten=BASIS),
    dict(url="/assets/webcams", endpoint="webcams", template="webcams.html",
         variable="webcams", typ="webcam", spalten=BASIS),
    dict(url="/assets/kameras", endpoint="kameras", template="kameras.html",
         variable="kameras", typ="kamera", spalten=BASIS),
    dict(url="/assets/mikrofons", endpoint="mikrofons", template="mikrofons.html",
         variable="mikrofons", typ="mikrofon", spalten=BASIS),
    dict(url="/assets/konferenzkameras", endpoint="konferenzkameras",
         template="konferenzkameras.html", variable="konferenzkameras",
         typ="konferenzkamera", spalten=BASIS),
    dict(url="/assets/aufnahmegeraete", endpoint="aufnahmegeraete",
         template="aufnahmegeraete.html", variable="aufnahmegeraete",
         typ="aufnahmegeraet", spalten=BASIS),
]


def sortierung_waehlen(cfg):
    wunsch = request.args.get("sort", "")
    spalte = cfg.get("alias", {}).get(wunsch)
    if spalte is None:
        spalte = wunsch if wunsch in ERLAUBTE_SORT else cfg.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")
    if richtung not in ("ASC", "DESC"):
        richtung = "ASC"
    return spalte, richtung


def liste_bauen(cfg):
    spalten = cfg["spalten"]
    if spalten != "*":
        spalten += ", arbeitsplatz"
    def ansicht():
        spalte, richtung = sortierung_waehlen(cfg)
        zeilen = abfragen(
            f"SELECT {cfg['spalten']} FROM assets WHERE LOWER(assettyp) = ? "
            f"ORDER BY {spalte} COLLATE NOCASE {richtung}",
            (cfg["typ"],)
        )
        return render_template(cfg["template"], **{cfg["variable"]: zeilen})
    return ansicht


for _cfg in LISTEN:
    bp.add_url_rule(_cfg["url"], endpoint=_cfg["endpoint"], view_func=liste_bauen(_cfg))


@bp.route("/assets/dockingstation")
def dockingstations():
    sort_alias = {"laptop": "laptop"}
    wunsch = request.args.get("sort", "")
    spalte = sort_alias.get(wunsch) or (
        f"d.{wunsch}" if wunsch in ERLAUBTE_SORT else "d.inventarnummer")
    richtung = request.args.get("richtung", "ASC")
    if richtung not in ("ASC", "DESC"):
        richtung = "ASC"

    zeilen = abfragen(f"""
        SELECT d.id, d.inventarnummer, d.seriennummer, d.mitarbeiter,
               d.standort, d.zimmer, d.kostenstelle, d.organisationseinheit,
               d.hersteller, d.modell, d.mac_adresse,
               (SELECT GROUP_CONCAT(l.inventarnummer, ', ')
                  FROM assets l
                 WHERE l.dockingstation = d.inventarnummer
                   AND LOWER(l.assettyp) = 'laptop') AS laptop,
               d.status, d.garantie, d.anschaffungsdatum, d.bemerkung, d.arbeitsplatz
        FROM assets d
        WHERE LOWER(d.assettyp) = 'dockingstation'
        ORDER BY {spalte} COLLATE NOCASE {richtung}
    """)
    return render_template("dockingstations.html", dockingstations=zeilen)