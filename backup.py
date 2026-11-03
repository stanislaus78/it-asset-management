import re
import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

from datenbank import DB_PFAD

BACKUP_ORDNER = Path(__file__).resolve().parent / "backups"
AUFBEWAHRUNG_TAGE = 14
PRUEF_INTERVALL_SEKUNDEN = 2 * 60 * 60

NAME_MUSTER = re.compile(r"^asset_management_(\d{4}-\d{2}-\d{2})(?:_\d{4})?\.db$")
_sperre = threading.Lock()
_gestartet = False


def backup_anlegen(zusatz=""):
    """Legt eine konsistente Kopie an und gibt den Pfad zurück."""
    BACKUP_ORDNER.mkdir(exist_ok=True)
    jetzt = datetime.now()
    name = f"asset_management_{jetzt:%Y-%m-%d}{zusatz}.db"
    ziel = BACKUP_ORDNER / name
    teil = BACKUP_ORDNER / (name + ".tmp")

    with _sperre:
        teil.unlink(missing_ok=True)
        with closing(sqlite3.connect(DB_PFAD)) as quelle, \
                closing(sqlite3.connect(teil)) as kopie:
            quelle.backup(kopie)
        teil.replace(ziel)
    return ziel


def backups_auflisten():
    if not BACKUP_ORDNER.exists():
        return []
    liste = []
    for datei in BACKUP_ORDNER.iterdir():
        treffer = NAME_MUSTER.match(datei.name)
        if treffer:
            liste.append({
                "name": datei.name,
                "datum": datetime.fromtimestamp(datei.stat().st_mtime),
                "groesse_kb": round(datei.stat().st_size / 1024),
                "tag": treffer.group(1),
            })
    return sorted(liste, key=lambda b: b["datum"], reverse=True)


def alte_loeschen():
    grenze = (datetime.now() - timedelta(days=AUFBEWAHRUNG_TAGE)).date().isoformat()
    for b in backups_auflisten():
        if b["tag"] < grenze:
            (BACKUP_ORDNER / b["name"]).unlink(missing_ok=True)


def heute_vorhanden():
    heute = datetime.now().date().isoformat()
    return any(b["tag"] == heute for b in backups_auflisten())


def pruefen_und_sichern():
    try:
        if not heute_vorhanden():
            backup_anlegen()
        alte_loeschen()
    except Exception as fehler:
        print("Backup fehlgeschlagen:", fehler)


def _schleife():
    pruefen_und_sichern()
    while True:
        ereignis.wait(PRUEF_INTERVALL_SEKUNDEN)
        pruefen_und_sichern()


ereignis = threading.Event()


def automatik_starten():
    global _gestartet
    if _gestartet:
        return
    _gestartet = True
    threading.Thread(target=_schleife, daemon=True, name="backup").start()