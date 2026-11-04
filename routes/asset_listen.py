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






