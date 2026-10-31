import re
from urllib.parse import urlparse

from flask import Blueprint, redirect, render_template, request

from datenbank import verbinden
from funktionen_assets import (
    asset_existiert_sqlite, asset_freigeben_sqlite, asset_speichern_popup_sqlite,
    asset_suchen_sqlite, asset_zuweisen_sqlite, assets_loeschen_sqlite,
    neues_asset_erstellen_sqlite,
)
from hilfen import abfragen, mitarbeiter_pruefen

import sqlite3
from contextlib import closing

bp = Blueprint("assets", __name__)


def mac_normalisieren(mac):
    hex_only = re.sub(r"[^0-9A-Fa-f]", "", mac or "")
    if len(hex_only) != 12:
        return None
    hex_only = hex_only.upper()
    return ":".join(hex_only[i:i + 2] for i in range(0, 12, 2))


# ---------- Menüseiten ----------

@bp.route("/assets")
def assets_dashboard():
    return render_template("asset_dashboard.html")


@bp.route("/assets/rechner")
def rechner():
    return render_template("rechner.html")


@bp.route("/assets/mobile")
def mobile():
    return render_template("mobile.html")


@bp.route("/assets/peripherie")
def peripherie():
    return render_template("peripherie.html")


@bp.route("/assets/medientechnik")
def medientechnik():
    return render_template("medientechnik.html")


# ---------- Anlegen, Bearbeiten, Löschen ----------

@bp.route("/asset/anlegen")
def asset_anlegen():
    return render_template("asset_anlegen.html")


@bp.route("/asset/anlegen_popup", methods=["POST"])
def asset_anlegen_popup():

    inventarnummer = request.form.get("inventarnummer", "").strip()
    if not inventarnummer:
        return {"status": "fehler", "meldung": "Inventarnummer fehlt."}

    mac_roh = request.form.get("mac_adresse", "").strip()
    if request.form.get("druckertyp") == "Lokal":
        mac_roh = ""
    mac = ""
    if mac_roh:
        mac = mac_normalisieren(mac_roh)
        if mac is None:
            return {"status": "fehler", "meldung": "MAC-Adresse ist ungültig."}

    vorhanden = asset_existiert_sqlite(
        inventarnummer,
        request.form.get("rechnername", "").strip(),
        mac
    )
    if vorhanden:
        return {"status": "fehler", "meldung": f"{vorhanden} existiert bereits."}

    daten = request.form.copy()
    daten["mac_adresse"] = mac

    benutzer = request.form.get("benutzer", "").strip()
    if benutzer:
        gefunden = mitarbeiter_pruefen(benutzer)
        if gefunden is None:
            return {"status": "fehler",
                    "meldung": f"Mitarbeiter '{benutzer}' existiert nicht. "
                               "Bitte zuerst unter Mitarbeiter anlegen."}
        daten["benutzer"] = gefunden

    try:
        neues_asset_erstellen_sqlite(daten)
    except sqlite3.Error as fehler:
        return {"status": "fehler", "meldung": f"Datenbankfehler: {fehler}"}

    return {"status": "ok"}


@bp.route("/asset/bearbeiten/<id>")
def asset_bearbeiten(id):
    asset = asset_suchen_sqlite(id)
    return render_template("asset_bearbeiten.html", asset=asset)


@bp.route("/asset/speichern", methods=["POST"])
def asset_speichern():

    daten = request.form.copy()

    if "benutzer" in daten:
        benutzer = daten["benutzer"].strip()
        aktuell = asset_suchen_sqlite(daten["id"])
        alter_wert = (aktuell[26] or "") if aktuell else ""

        if benutzer and benutzer != alter_wert:
            gefunden = mitarbeiter_pruefen(benutzer)
            if gefunden is None:
                return {"status": "fehler",
                        "meldung": f"Mitarbeiter '{benutzer}' existiert nicht."}
            daten["benutzer"] = gefunden

    ergebnis = asset_speichern_popup_sqlite(daten["id"], daten)

    if ergebnis == "doppelt":
        return {"status": "fehler", "meldung": "Diese Inventarnummer existiert bereits."}
    if ergebnis == "leer":
        return {"status": "fehler", "meldung": "Inventarnummer darf nicht leer sein."}
    if not ergebnis:
        return {"status": "fehler", "meldung": "Asset nicht gefunden (ID ungültig)"}

    return {"status": "ok"}


@bp.route("/asset/loeschen")
def assets_loeschen():
    id = request.args.get("id")
    assets_loeschen_sqlite(id)
    ziel = urlparse(request.referrer or "/assets").path
    return redirect(ziel + "?geloescht=1")


@bp.route("/asset/loeschen/bestaetigen")
def asset_loeschen_bestaetigen():
    id = request.args.get("id")
    assets_loeschen_sqlite(id)
    return f"""
    <h1>✅ Asset gelöscht</h1>

    Asset {int(id) if str(id).isdigit() else ''} wurde gelöscht.
    """


# ---------- Zuweisen und Freigeben ----------

@bp.route("/asset/zuweisen")
def assets_zuweisen():
    inventarnummer = request.args.get("inventarnummer")
    mitarbeiter = request.args.get("mitarbeiter")

    if inventarnummer and mitarbeiter:
        gefunden = mitarbeiter_pruefen(mitarbeiter)
        if gefunden is None:
            ergebnis = f"Mitarbeiter '{mitarbeiter}' existiert nicht."
        else:
            ergebnis = asset_zuweisen_sqlite(inventarnummer, gefunden)

        return render_template("asset_zuweisen.html", ergebnis=ergebnis,
                               inventarnummer=inventarnummer,
                               mitarbeiter=mitarbeiter)

    return render_template("asset_zuweisen.html", ergebnis="")


@bp.route("/mitarbeiter/asset_zuweisen")
def asset_zuweisen():
    return render_template("asset_zuweisen.html")


@bp.route("/asset/freigeben")
def assets_freigeben():
    inventarnummer = request.args.get("inventarnummer")

    if inventarnummer:
        asset_freigeben_sqlite(inventarnummer)
        return render_template("info_seite.html",
                               titel="Asset freigegeben",
                               hinweis=f"Asset {inventarnummer} wurde freigegeben.",
                               kopf=[], zeilen=[], zurueck="/assets")

    return """
    <h1>Asset freigeben</h1>

    <form>
        Inventarnummer:<br>
        <input type="text" name="inventarnummer"><br><br>
        <button>Freigeben</button>
    </form>

    <p><a href="/assets">Zurück zu Assets</a></p>
    """


# ---------- Anzeigen und Details ----------

@bp.route("/asset/anzeigen")
def assets_anzeigen():
    assets = abfragen("SELECT * FROM assets")
    return render_template("assets_anzeigen.html", assets=assets)


@bp.route("/asset/details_json/<id>")
def asset_details_json(id):

    asset = asset_suchen_sqlite(id)

    if asset is None:
        return {"status": "fehler", "meldung": "Asset nicht gefunden"}, 404

    laptop = None
    if (asset[10] or "").lower() == "dockingstation":
        with closing(verbinden()) as verbindung:
            zeilen = verbindung.execute(
                "SELECT inventarnummer FROM assets "
                "WHERE dockingstation = ? AND LOWER(assettyp) = 'laptop'",
                (asset[1],)
            ).fetchall()
        laptop = ", ".join(z[0] for z in zeilen if z[0])

    return {
        "id": asset[0],
        "inventarnummer": asset[1],
        "rechnername": asset[2],
        "seriennummer": asset[3],
        "kostenstelle": asset[4],
        "organisationseinheit": asset[5],
        "standort": asset[6],
        "zimmer": asset[7],
        "anschaffungsdatum": asset[8],
        "installationsdatum": asset[9],
        "assettyp": asset[10],
        "verwendungsart": asset[11],
        "status": asset[12],
        "hersteller": asset[13],
        "modell": asset[14],
        "mac_adresse": asset[15],
        "garantie": asset[16],
        "verwaltungsart": asset[17],
        "prozessor": asset[18],
        "kerne_threads": asset[19],
        "ram": asset[20],
        "festplatte": asset[21],
        "betriebssystem": asset[22],
        "displaygroesse": asset[23],
        "dockingstation": asset[24],
        "anlagenummer": asset[25],
        "benutzer": asset[26],
        "bemerkung": asset[27],
        "druckertyp": asset[28],
        "laptop": laptop
    }


@bp.route("/asset/details/<inventarnummer>")
def asset_details(inventarnummer):
    asset = asset_suchen_sqlite(inventarnummer)
    return render_template("asset_details.html", asset=asset)