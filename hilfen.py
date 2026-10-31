import re
from contextlib import closing
from functools import wraps

from flask import redirect, session

from datenbank import verbinden


ORGANISATIONSEINHEITEN = ["A600", "A601", "A602", "A603", "A736"]
STANDORTE_LISTE = ["ZLB", "AECC", "SSC", "SVP", "Büro des Zentrums"]
STATUS_WERTE = ["Lager", "Ausgegeben", "Defekt", "Ausgeschieden"]

ASSET_SPALTEN = [
    ("inventarnummer", "Inventarnummer"), ("rechnername", "Rechnername"),
    ("seriennummer", "Seriennummer"), ("assettyp", "Typ"),
    ("verwendungsart", "Verwendungsart"), ("hersteller", "Hersteller"),
    ("modell", "Modell"), ("druckertyp", "Druckertyp"),
    ("status", "Status"), ("mitarbeiter", "Benutzer"),
    ("standort", "Standort"), ("zimmer", "Zimmer"),
    ("kostenstelle", "Kostenstelle"), ("organisationseinheit", "Organisationseinheit"),
    ("anschaffungsdatum", "Anschaffungsdatum"), ("installationsdatum", "Installationsdatum"),
    ("garantie", "Garantie"), ("verwaltungsart", "Verwaltungsart"),
    ("mac_adresse", "MAC-Adresse"), ("prozessor", "Prozessor"),
    ("kerne_threads", "Kerne/Threads"), ("ram", "RAM"),
    ("festplatte", "Festplatte"), ("betriebssystem", "Betriebssystem"),
    ("displaygroesse", "Displaygröße"), ("dockingstation", "Dockingstation"),
    ("anlagenummer", "Anlagenummer"), ("bemerkung", "Bemerkung"),
]

ASSET_KOPF = [label for _, label in ASSET_SPALTEN]
ASSET_SQL = "SELECT " + ", ".join(s for s, _ in ASSET_SPALTEN) + " FROM assets"
EINHEIT_INDEX = [s for s, _ in ASSET_SPALTEN].index("organisationseinheit")


def abfragen(sql, parameter=()):
    with closing(verbinden()) as verbindung:
        return verbindung.execute(sql, parameter).fetchall()


def einheit_schluessel(wert):
    ziffern = re.sub(r"\D", "", wert or "")
    return ziffern if ziffern else (wert or "").strip().upper()


def leere_spalten_entfernen(kopf, zeilen):
    if not zeilen:
        return kopf, zeilen
    behalten = [i for i in range(len(kopf))
                if any(z[i] not in (None, "") for z in zeilen)]
    return ([kopf[i] for i in behalten],
            [[z[i] for i in behalten] for z in zeilen])


def mitarbeiter_pruefen(benutzer):
    """Gibt die U-AccountID (wie in der Datenbank geschrieben) zurück oder None."""
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT uaccountid FROM mitarbeiter WHERE LOWER(uaccountid) = LOWER(?)",
            (benutzer,)
        ).fetchone()
    return zeile[0] if zeile else None


def admin_noetig(f):
    @wraps(f)
    def innen(*args, **kwargs):
        if not session.get("eingeloggt"):
            return redirect("/login")
        return f(*args, **kwargs)
    return innen