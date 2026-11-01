import re
from contextlib import closing
from functools import wraps
from datetime import datetime
from flask import redirect, session
import calendar
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
    ("standort", "Standort"), ("zimmer", "Zimmer"), ("arbeitsplatz", "Arbeitsplatz"),
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

DATUMSFELDER = {
    "anschaffungsdatum": "Anschaffungsdatum",
    "installationsdatum": "Installationsdatum",
}


def datum_normalisieren(text):
    """Gibt 'JJJJ-MM-TT' zurück, '' bei leerer Eingabe, None bei ungültigem Datum."""
    text = (text or "").strip()
    if not text:
        return ""
    for muster in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, muster).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None



NUTZUNGSDAUER_JAHRE = 5
WARN_TAGE = 90

ABSCHREIBUNG_TYPEN = ["laptop", "stand-pc", "diensthandy"]
GARANTIE_TYPEN = ["laptop", "stand-pc", "drucker", "diensthandy", "monitor", "tablet"]


def jahre_addieren(d, jahre):
    try:
        return d.replace(year=d.year + jahre)
    except ValueError:  # 29.02. in einem Jahr ohne Schalttag
        return d.replace(year=d.year + jahre, day=28)


def monate_addieren(d, monate):
    gesamt = d.year * 12 + (d.month - 1) + monate
    jahr, monat = divmod(gesamt, 12)
    monat += 1
    tag = min(d.day, calendar.monthrange(jahr, monat)[1])
    return d.replace(year=jahr, month=monat, day=tag)


GARANTIE_MUSTER = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*([a-zäöüß]*)\.?\s*$", re.I)


def garantie_monate(text):
    """'3 Jahre', '3', '36 Monate' -> 36. None, wenn die Dauer nicht lesbar ist."""
    treffer = GARANTIE_MUSTER.match(text or "")
    if not treffer:
        return None
    zahl = float(treffer.group(1).replace(",", "."))
    einheit = treffer.group(2).lower()

    if einheit in ("", "j", "jahr", "jahre", "jahren"):
        monate = round(zahl * 12)
    elif einheit in ("m", "mon", "monat", "monate", "monaten"):
        monate = round(zahl)
    else:
        return None
    return monate if monate > 0 else None


def garantie_text(monate):
    if monate % 12 == 0:
        jahre = monate // 12
        return f"{jahre} Jahr" if jahre == 1 else f"{jahre} Jahre"
    return f"{monate} Monat" if monate == 1 else f"{monate} Monate"