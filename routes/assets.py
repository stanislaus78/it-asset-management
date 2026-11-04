import re
from urllib.parse import urlparse
from hilfen import STATUS_WERTE, abfragen, mitarbeiter_pruefen
from flask import Blueprint, redirect, render_template, request
from hilfen import abfragen
from datenbank import verbinden
from funktionen_assets import (
    asset_existiert_sqlite, asset_freigeben_sqlite, asset_speichern_popup_sqlite,
    asset_suchen_sqlite, asset_zuweisen_sqlite, assets_loeschen_sqlite,
    neues_asset_erstellen_sqlite,
)

import sqlite3
from contextlib import closing

from hilfen import (
    DATUMSFELDER, ORGANISATIONSEINHEITEN, STANDORTE_LISTE, STATUS_WERTE, abfragen,
    datum_normalisieren, garantie_monate, garantie_text, mitarbeiter_pruefen,
)



bp = Blueprint("assets", __name__)
@bp.route("/asset/listen_json")
def asset_listen_json():
    return {
        "status": STATUS_WERTE,
        "standort": STANDORTE_LISTE,
        "organisationseinheit": ORGANISATIONSEINHEITEN,
    }

def mac_normalisieren(mac):
    hex_only = re.sub(r"[^0-9A-Fa-f]", "", mac or "")
    if len(hex_only) != 12:
        return None
    hex_only = hex_only.upper()
    return ":".join(hex_only[i:i + 2] for i in range(0, 12, 2))

def garantie_pruefen(daten, alter_wert=None):
    """Gibt eine Fehlermeldung zurück oder None. Vereinheitlicht daten['garantie']."""
    if "garantie" not in daten:
        return None

    text = daten["garantie"].strip()
    if not text:
        daten["garantie"] = ""
        return None

    # unveränderter Altwert (zum Beispiel "lebenslang") blockiert das Speichern nicht
    if alter_wert is not None and text == (alter_wert or "").strip():
        return None

    monate = garantie_monate(text)
    if monate is None:
        return "Garantie: bitte eine Dauer angeben, zum Beispiel 3 Jahre oder 36 Monate."

    daten["garantie"] = garantie_text(monate)
    return None

# ---------- Menüseiten ----------

KACHELN = [
    # (Titel, Link, Symbol, Assettypen in Kleinschreibung)
    ("Rechner", "/assets/rechner", "💻",
     ["laptop", "stand-pc", "dockingstation", "monitor"]),
    ("Peripherie", "/assets/peripherie", "🖱️",
     ["maus", "scanner", "drucker", "kopfhoerer", "switch"]),
    ("Mobile Geräte", "/assets/mobile", "📱",
     ["tablet", "diensthandy"]),
    ("Medientechnik", "/assets/medientechnik", "🎥",
     ["webcam", "kamera", "mikrofon", "aufnahmegeraet", "konferenzkamera"]),
    ("Zubehör", "/liste/zubehoer", "📦",
     ["zubehoer"]),
]


@bp.route("/assets")
def assets_dashboard():
    zaehler = dict(abfragen(
        "SELECT LOWER(assettyp), COUNT(*) FROM assets GROUP BY LOWER(assettyp)"
    ))
    kacheln = [
        (titel, link, symbol, sum(zaehler.get(t, 0) for t in typen))
        for titel, link, symbol, typen in KACHELN
    ]
    return render_template("asset_dashboard.html", kacheln=kacheln)
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

    for feld, bezeichnung in DATUMSFELDER.items():
        if feld in daten:
            normiert = datum_normalisieren(daten[feld])
            if normiert is None:
                return {"status": "fehler",
                        "meldung": f"{bezeichnung} ist ungültig (TT.MM.JJJJ erwartet)."}
            daten[feld] = normiert

    if not daten.get("anschaffungsdatum"):
        return {"status": "fehler", "meldung": "Anschaffungsdatum fehlt."}

    fehler = garantie_pruefen(daten)
    if fehler:
        return {"status": "fehler", "meldung": fehler}

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
    except sqlite3.Error as db_fehler:
        return {"status": "fehler", "meldung": f"Datenbankfehler: {db_fehler}"}

    return {"status": "ok"}


@bp.route("/asset/bearbeiten/<id>")
def asset_bearbeiten(id):
    asset = asset_suchen_sqlite(id)
    return render_template("asset_bearbeiten.html", asset=asset)


@bp.route("/asset/speichern", methods=["POST"])
def asset_speichern():

    daten = request.form.copy()
    aktuell = asset_suchen_sqlite(daten.get("id", ""))

    for feld, bezeichnung in DATUMSFELDER.items():
        if feld in daten:
            normiert = datum_normalisieren(daten[feld])
            if normiert is None:
                return {"status": "fehler",
                        "meldung": f"{bezeichnung} ist ungültig (TT.MM.JJJJ erwartet)."}
            daten[feld] = normiert

    fehler = garantie_pruefen(daten, aktuell[16] if aktuell else None)
    if fehler:
        return {"status": "fehler", "meldung": fehler}

    if "benutzer" in daten:
        benutzer = daten["benutzer"].strip()
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


@bp.route("/asset/loeschen", methods=["POST"])
def assets_loeschen():
    id = request.form.get("id", "")
    if not id.isdigit():
        return {"status": "fehler", "meldung": "Ungültige ID."}
    if asset_suchen_sqlite(id) is None:
        return {"status": "fehler", "meldung": "Asset nicht gefunden."}

    assets_loeschen_sqlite(id)
    return {"status": "ok"}


# ---------- Zuweisen und Freigeben ----------

def asset_existiert(inventarnummer):
    return bool(abfragen(
        "SELECT 1 FROM assets WHERE LOWER(inventarnummer) = LOWER(?)",
        (inventarnummer,)
    ))

@bp.route("/asset/zuweisen", methods=["GET", "POST"])
def assets_zuweisen():
    mitarbeiter_liste = abfragen(
        "SELECT uaccountid, vorname, nachname FROM mitarbeiter ORDER BY nachname"
    )
    ergebnis = ""
    inventarnummer = ""
    mitarbeiter = ""

    if request.method == "POST":
        inventarnummer = request.form.get("inventarnummer", "").strip()
        mitarbeiter = request.form.get("mitarbeiter", "").strip()

        if not inventarnummer or not mitarbeiter:
            ergebnis = "Bitte Inventarnummer und Mitarbeiter angeben."
        else:
            gefunden = mitarbeiter_pruefen(mitarbeiter)
            if gefunden is None:
                ergebnis = f"Mitarbeiter '{mitarbeiter}' existiert nicht."
            else:
                code = asset_zuweisen_sqlite(inventarnummer, gefunden)
                ergebnis = {
                    "nicht_gefunden": f"Asset '{inventarnummer}' existiert nicht.",
                    "besetzt": f"Asset '{inventarnummer}' ist bereits vergeben. "
                               "Bitte zuerst freigeben.",
                    "erfolg": f"Asset {inventarnummer} wurde {gefunden} zugewiesen.",
                }.get(code, code)
                if code == "erfolg":
                    inventarnummer = ""
                    mitarbeiter = ""

    return render_template("asset_zuweisen.html", ergebnis=ergebnis,
                           inventarnummer=inventarnummer, mitarbeiter=mitarbeiter,
                           mitarbeiter_liste=mitarbeiter_liste)


@bp.route("/mitarbeiter/asset_zuweisen")
def asset_zuweisen():
    return redirect("/asset/zuweisen")


@bp.route("/asset/freigeben", methods=["GET", "POST"])
def assets_freigeben():
    ergebnis = ""
    inventarnummer = ""

    if request.method == "POST":
        inventarnummer = request.form.get("inventarnummer", "").strip()

        if not inventarnummer:
            ergebnis = "Bitte Inventarnummer angeben."
        else:
            code = asset_freigeben_sqlite(inventarnummer)
            ergebnis = {
                "nicht_gefunden": f"Asset '{inventarnummer}' existiert nicht.",
                "nicht_vergeben": f"Asset '{inventarnummer}' ist nicht vergeben.",
                "erfolg": f"Asset {inventarnummer} wurde freigegeben.",
            }.get(code, code)
            if code == "erfolg":
                inventarnummer = ""

    return render_template("asset_freigeben.html", ergebnis=ergebnis,
                           inventarnummer=inventarnummer)





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
        "arbeitsplatz": asset[29],
        "laptop": laptop
    }


@bp.route("/asset/details/<inventarnummer>")
def asset_details(inventarnummer):
    asset = asset_suchen_sqlite(inventarnummer)
    return render_template("asset_details.html", asset=asset)

@bp.route("/asset/status_json")
def asset_status_json():
    return STATUS_WERTE