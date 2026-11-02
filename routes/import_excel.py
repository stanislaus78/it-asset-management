import io
import re
from contextlib import closing
from datetime import date, datetime

from flask import Blueprint, Response, abort, render_template, request
from openpyxl import Workbook, load_workbook
from werkzeug.utils import secure_filename

from datenbank import verbinden
from funktionen_historie import historie_schreiben
from hilfen import (
    ASSET_SPALTEN, ORGANISATIONSEINHEITEN, STANDORTE_LISTE, STATUS_WERTE,
    admin_noetig, datum_normalisieren, einheit_schluessel, garantie_monate,
    garantie_text,
)
from routes.assets import mac_normalisieren

bp = Blueprint("import_excel", __name__)

ASSET_TYPEN = [
    "Laptop", "Stand-PC", "Monitor", "Tablet", "Diensthandy", "Drucker",
    "Dockingstation", "Scanner", "Maus", "Kopfhoerer", "Switch", "Webcam",
    "Kamera", "Mikrofon", "Konferenzkamera", "Aufnahmegeraet", "Zubehoer",
]

MITARBEITER_SPALTEN = [
    ("vorname", "Vorname"), ("nachname", "Nachname"), ("uaccountid", "U-AccountID"),
    ("organisationseinheit", "Organisationseinheit"), ("standort", "Standort"),
    ("zimmer", "Zimmer"), ("arbeitsplatz", "Arbeitsplatz"),
    ("kostenstelle", "Kostenstelle"), ("status", "Status"), ("bemerkung", "Bemerkung"),
]


def schluessel(text):
    t = str(text or "").lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(alt, neu)
    return re.sub(r"[\s_.\-/]", "", t)


def aliasse_bauen(spalten, extra):
    a = {}
    for feld, label in spalten:
        a[schluessel(feld)] = feld
        a[schluessel(label)] = feld
    for alias, feld in extra.items():
        a[schluessel(alias)] = feld
    return a


ASSET_ALIASSE = aliasse_bauen(ASSET_SPALTEN, {
    "Gerätetyp": "assettyp", "Asset-Typ": "assettyp",
    "Inventarnr": "inventarnummer", "Seriennr": "seriennummer",
})
MITARBEITER_ALIASSE = aliasse_bauen(MITARBEITER_SPALTEN, {
    "UAccount": "uaccountid", "Account": "uaccountid", "OE": "organisationseinheit",
})

TYPEN = {schluessel(t): t for t in ASSET_TYPEN}
STATUS = {schluessel(s): s for s in STATUS_WERTE + ["Leihgerät", "Festgerät"]}
STANDORTE = {schluessel(s): s for s in STANDORTE_LISTE}
EINHEITEN = {einheit_schluessel(e): e for e in ORGANISATIONSEINHEITEN}


def zelle_text(wert):
    if wert is None:
        return ""
    if isinstance(wert, (datetime, date)):
        return wert.strftime("%Y-%m-%d")
    if isinstance(wert, float) and wert.is_integer():
        return str(int(wert))
    return str(wert).strip()


def tabelle_lesen(inhalt, aliasse, pflicht):
    try:
        mappe = load_workbook(io.BytesIO(inhalt), read_only=True, data_only=True)
    except Exception:
        raise ValueError("Die Datei konnte nicht gelesen werden. Bitte als .xlsx speichern.")

    try:
        zeilen = mappe.active.iter_rows(values_only=True)
        kopf = next(zeilen, None)
        if not kopf:
            raise ValueError("Die Tabelle ist leer.")

        spalten, unbekannt = {}, []
        for i, name in enumerate(kopf):
            if name in (None, ""):
                continue
            feld = aliasse.get(schluessel(name))
            if feld and feld not in spalten.values():
                spalten[i] = feld
            else:
                unbekannt.append(str(name))

        fehlend = [f for f in pflicht if f not in spalten.values()]
        if fehlend:
            raise ValueError("In der ersten Zeile fehlen die Spalten: " + ", ".join(fehlend))

        daten = []
        for nr, z in enumerate(zeilen, start=2):
            werte = {feld: zelle_text(z[i]) if i < len(z) else ""
                     for i, feld in spalten.items()}
            if any(werte.values()):
                daten.append((nr, werte))
        return unbekannt, daten
    finally:
        mappe.close()


def assets_auswerten(daten):
    with closing(verbinden()) as v:
        vorhanden = {(z[0] or "").lower() for z in v.execute("SELECT inventarnummer FROM assets")}
        namen = {z[0].lower() for z in v.execute(
            "SELECT rechnername FROM assets WHERE rechnername IS NOT NULL AND rechnername != ''")}
        macs = {z[0] for z in v.execute(
            "SELECT mac_adresse FROM assets WHERE mac_adresse IS NOT NULL AND mac_adresse != ''")}
        benutzer = {z[0].lower(): z[0] for z in v.execute(
            "SELECT uaccountid FROM mitarbeiter WHERE uaccountid IS NOT NULL")}

    neu, uebersprungen, fehler = [], [], []
    datei_inv, datei_namen, datei_macs = set(), set(), set()

    for nr, w in daten:
        inv = w.get("inventarnummer", "")
        if not inv:
            fehler.append((nr, "Inventarnummer fehlt."))
            continue
        if inv.lower() in vorhanden:
            uebersprungen.append((nr, f"{inv} ist schon in der Datenbank."))
            continue
        if inv.lower() in datei_inv:
            fehler.append((nr, f"{inv} kommt in der Datei doppelt vor."))
            continue
        datei_inv.add(inv.lower())

        satz = {feld: "" for feld, _ in ASSET_SPALTEN}
        satz.update(w)
        probleme = []

        typ = TYPEN.get(schluessel(satz["assettyp"]))
        if typ is None:
            probleme.append(f"Typ '{satz['assettyp']}' ist unbekannt")
        else:
            satz["assettyp"] = typ

        for feld, name in (("anschaffungsdatum", "Anschaffungsdatum"),
                           ("installationsdatum", "Installationsdatum")):
            norm = datum_normalisieren(satz[feld])
            if norm is None:
                probleme.append(f"{name} '{satz[feld]}' ist ungültig")
            else:
                satz[feld] = norm
        if not satz["anschaffungsdatum"]:
            probleme.append("Anschaffungsdatum fehlt")

        if satz["garantie"]:
            monate = garantie_monate(satz["garantie"])
            if monate is None:
                probleme.append(f"Garantie '{satz['garantie']}' nicht lesbar (z. B. 3 Jahre)")
            else:
                satz["garantie"] = garantie_text(monate)

        if satz["standort"]:
            s = STANDORTE.get(schluessel(satz["standort"]))
            if s is None:
                probleme.append(f"Standort '{satz['standort']}' ist unbekannt")
            else:
                satz["standort"] = s

        if satz["organisationseinheit"]:
            e = EINHEITEN.get(einheit_schluessel(satz["organisationseinheit"]))
            if e is None:
                probleme.append(f"Organisationseinheit '{satz['organisationseinheit']}' ist unbekannt")
            else:
                satz["organisationseinheit"] = e

        if satz["mitarbeiter"]:
            b = benutzer.get(satz["mitarbeiter"].lower())
            if b is None:
                probleme.append(f"Benutzer '{satz['mitarbeiter']}' ist kein Mitarbeiter "
                                "(zuerst die Mitarbeiter importieren, es zählt die U-AccountID)")
            else:
                satz["mitarbeiter"] = b

        if satz["status"]:
            s = STATUS.get(schluessel(satz["status"]))
            if s is None:
                probleme.append(f"Status '{satz['status']}' ist unbekannt")
            else:
                satz["status"] = s
        else:
            satz["status"] = "Ausgegeben" if satz["mitarbeiter"] else "Lager"

        if satz["druckertyp"]:
            d = {"netzwerk": "Netzwerk", "lokal": "Lokal"}.get(satz["druckertyp"].lower())
            if d is None:
                probleme.append("Druckertyp muss Netzwerk oder Lokal sein")
            else:
                satz["druckertyp"] = d
        if satz["druckertyp"] == "Lokal":
            satz["mac_adresse"] = ""

        if satz["mac_adresse"]:
            mac = mac_normalisieren(satz["mac_adresse"])
            if mac is None:
                probleme.append(f"MAC-Adresse '{satz['mac_adresse']}' ist ungültig")
            elif mac in macs or mac in datei_macs:
                probleme.append(f"MAC-Adresse {mac} gibt es schon")
            else:
                satz["mac_adresse"] = mac

        name = satz["rechnername"].lower()
        if name and (name in namen or name in datei_namen):
            probleme.append(f"Rechnername '{satz['rechnername']}' gibt es schon")

        if probleme:
            fehler.append((nr, f"{inv}: " + "; ".join(probleme)))
            continue

        if name:
            datei_namen.add(name)
        if satz["mac_adresse"]:
            datei_macs.add(satz["mac_adresse"])
        neu.append((nr, satz))

    return neu, uebersprungen, fehler


def assets_speichern(neu):
    spalten = [f for f, _ in ASSET_SPALTEN]
    sql = (f"INSERT INTO assets ({', '.join(spalten)}) "
           f"VALUES ({', '.join('?' for _ in spalten)})")
    with closing(verbinden()) as v:
        v.executemany(sql, [[satz[f] or None for f in spalten] for _, satz in neu])
        v.commit()


def mitarbeiter_auswerten(daten):
    with closing(verbinden()) as v:
        vorhanden = {z[0].lower() for z in v.execute(
            "SELECT uaccountid FROM mitarbeiter WHERE uaccountid IS NOT NULL")}

    neu, uebersprungen, fehler = [], [], []
    datei_ids = set()

    for nr, w in daten:
        kennung = w.get("uaccountid", "")
        if not kennung:
            fehler.append((nr, "U-AccountID fehlt."))
            continue
        if kennung.lower() in vorhanden:
            uebersprungen.append((nr, f"{kennung} ist schon in der Datenbank."))
            continue
        if kennung.lower() in datei_ids:
            fehler.append((nr, f"{kennung} kommt in der Datei doppelt vor."))
            continue
        datei_ids.add(kennung.lower())

        satz = {feld: "" for feld, _ in MITARBEITER_SPALTEN}
        satz.update(w)
        probleme = []

        if not satz["nachname"]:
            probleme.append("Nachname fehlt")

        if satz["organisationseinheit"]:
            e = EINHEITEN.get(einheit_schluessel(satz["organisationseinheit"]))
            if e is None:
                probleme.append(f"Organisationseinheit '{satz['organisationseinheit']}' ist unbekannt")
            else:
                satz["organisationseinheit"] = e

        if satz["standort"]:
            s = STANDORTE.get(schluessel(satz["standort"]))
            if s is None:
                probleme.append(f"Standort '{satz['standort']}' ist unbekannt")
            else:
                satz["standort"] = s

        if probleme:
            fehler.append((nr, f"{kennung}: " + "; ".join(probleme)))
        else:
            neu.append((nr, satz))

    return neu, uebersprungen, fehler


def mitarbeiter_speichern(neu):
    spalten = [f for f, _ in MITARBEITER_SPALTEN]
    sql = (f"INSERT INTO mitarbeiter ({', '.join(spalten)}) "
           f"VALUES ({', '.join('?' for _ in spalten)})")
    with closing(verbinden()) as v:
        v.executemany(sql, [[satz[f] or None for f in spalten] for _, satz in neu])
        v.commit()


def seite(ergebnis=None, fehlermeldung=None):
    return render_template("import.html", ergebnis=ergebnis, fehlermeldung=fehlermeldung)


def importieren(art):
    datei = request.files.get("datei")
    probelauf = request.form.get("probelauf") == "1"

    if datei is None or not datei.filename:
        return seite(fehlermeldung="Bitte eine Datei auswählen.")
    if not datei.filename.lower().endswith(".xlsx"):
        return seite(fehlermeldung="Nur .xlsx-Dateien werden gelesen. In Excel: "
                                   "Speichern unter, Excel-Arbeitsmappe (.xlsx).")

    if art == "assets":
        aliasse = ASSET_ALIASSE
        pflicht = ["inventarnummer", "assettyp", "anschaffungsdatum"]
        auswerten, speichern, titel = assets_auswerten, assets_speichern, "Assets"
    else:
        aliasse = MITARBEITER_ALIASSE
        pflicht = ["uaccountid", "nachname"]
        auswerten, speichern, titel = mitarbeiter_auswerten, mitarbeiter_speichern, "Mitarbeiter"

    try:
        unbekannt, daten = tabelle_lesen(datei.read(), aliasse, pflicht)
    except ValueError as meldung:
        return seite(fehlermeldung=str(meldung))

    neu, uebersprungen, fehler = auswerten(daten)

    gespeichert = False
    if not probelauf and not fehler and neu:
        speichern(neu)
        historie_schreiben(
            "Import", f"{len(neu)} {titel} aus {secure_filename(datei.filename)} importiert")
        gespeichert = True

    return seite(ergebnis={
        "titel": titel, "datei": secure_filename(datei.filename),
        "probelauf": probelauf, "gespeichert": gespeichert,
        "neu": len(neu), "uebersprungen": uebersprungen, "fehler": fehler,
        "unbekannt": unbekannt, "gelesen": len(daten),
    })


@bp.route("/administration/import")
@admin_noetig
def import_seite():
    return seite()


@bp.route("/administration/import/assets", methods=["POST"])
@admin_noetig
def import_assets():
    return importieren("assets")


@bp.route("/administration/import/mitarbeiter", methods=["POST"])
@admin_noetig
def import_mitarbeiter():
    return importieren("mitarbeiter")


@bp.route("/administration/import/vorlage/<art>")
@admin_noetig
def import_vorlage(art):
    if art == "assets":
        kopf = [label for _, label in ASSET_SPALTEN]
    elif art == "mitarbeiter":
        kopf = [label for _, label in MITARBEITER_SPALTEN]
    else:
        abort(404)

    mappe = Workbook()
    mappe.active.append(kopf)
    puffer = io.BytesIO()
    mappe.save(puffer)
    return Response(
        puffer.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=vorlage_{art}.xlsx"},
    )