from flask import Blueprint, render_template, request

from hilfen import (
    ASSET_KOPF, ASSET_SQL, EINHEIT_INDEX, ORGANISATIONSEINHEITEN,
    STANDORTE_LISTE, abfragen, einheit_schluessel, leere_spalten_entfernen,
)

bp = Blueprint("suche", __name__)


def suchbegriff():
    return (request.args.get("q") or "").strip()


def suche_seite(titel, platzhalter, kopf, zeilen, q, auswahl=None):
    kopf, zeilen = leere_spalten_entfernen(kopf, zeilen)
    return render_template("suche_seite.html", titel=titel, platzhalter=platzhalter,
                           kopf=kopf, zeilen=zeilen, q=q, auswahl=auswahl)


@bp.route("/suche")
def suche():
    return render_template("suche.html")



@bp.route("/suche/asset")
def suche_asset():
    q = suchbegriff()
    zeilen = []
    if q:
        m = f"%{q}%"
        zeilen = abfragen(
            ASSET_SQL + " WHERE inventarnummer LIKE ? OR seriennummer LIKE ? "
                        "OR rechnername LIKE ? ORDER BY inventarnummer LIMIT 200",
            (m, m, m))
    return suche_seite("🔍 Asset suchen",
                       "Inventarnummer, Seriennummer oder Rechnername",
                       ASSET_KOPF, zeilen, q)


@bp.route("/suche/hersteller")
def suche_hersteller():
    q = suchbegriff()
    zeilen = []
    if q:
        zeilen = abfragen(
            ASSET_SQL + " WHERE hersteller LIKE ? ORDER BY assettyp, inventarnummer LIMIT 200",
            (f"%{q}%",))
    return suche_seite("🏭 Nach Hersteller suchen", "z. B. Dell, Lenovo",
                       ASSET_KOPF, zeilen, q)


@bp.route("/suche/standort")
def suche_standort():
    q = suchbegriff()
    zeilen = []
    if q:
        zeilen = abfragen(
            ASSET_SQL + " WHERE standort = ? ORDER BY assettyp, inventarnummer LIMIT 200",
            (q,))
    return suche_seite("📍 Nach Standort suchen", "", ASSET_KOPF, zeilen, q,
                       auswahl=STANDORTE_LISTE)


@bp.route("/suche/organisationseinheit")
def suche_organisationseinheit():
    q = suchbegriff()
    zeilen = []
    if q:
        alle = abfragen(
            ASSET_SQL + " WHERE organisationseinheit IS NOT NULL "
                        "AND organisationseinheit != '' ORDER BY assettyp, inventarnummer")
        gesucht = einheit_schluessel(q)
        zeilen = [z for z in alle if einheit_schluessel(z[EINHEIT_INDEX]) == gesucht]
    return suche_seite("🏢 Nach Organisationseinheit suchen", "", ASSET_KOPF, zeilen, q,
                       auswahl=ORGANISATIONSEINHEITEN)


@bp.route("/suche/mitarbeiter")
def suche_mitarbeiter():
    q = suchbegriff()
    zeilen = []
    if q:
        m = f"%{q}%"
        zeilen = abfragen("""
            SELECT vorname || ' ' || nachname, uaccountid, organisationseinheit,
                   standort, zimmer
            FROM mitarbeiter
            WHERE vorname LIKE ? OR nachname LIKE ? OR uaccountid LIKE ?
            ORDER BY nachname LIMIT 200
        """, (m, m, m))
    return suche_seite("👤 Nach Mitarbeiter suchen", "Name oder U-AccountID",
                       ["Name", "U-AccountID", "Organisationseinheit", "Standort", "Zimmer"],
                       zeilen, q)


@bp.route("/suche/assets-mitarbeiter")
def suche_assets_mitarbeiter():
    q = suchbegriff()
    zeilen = []
    if q:
        zeilen = abfragen(
            ASSET_SQL + " WHERE mitarbeiter LIKE ? ORDER BY assettyp, inventarnummer LIMIT 200",
            (f"%{q}%",))
    return suche_seite("🎒 Assets eines Mitarbeiters", "Name oder U-AccountID",
                       ASSET_KOPF, zeilen, q)