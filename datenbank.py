import sqlite3
from contextlib import closing
from pathlib import Path

DB_PFAD = Path(__file__).resolve().parent / "asset_management.db"


def verbinden():
    return sqlite3.connect(DB_PFAD)


def assets_tabelle_anlegen():
    with closing(verbinden()) as verbindung:
        verbindung.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY,
                inventarnummer TEXT,
                rechnername TEXT,
                seriennummer TEXT,
                kostenstelle TEXT,
                organisationseinheit TEXT,
                standort TEXT,
                zimmer TEXT,
                anschaffungsdatum TEXT,
                installationsdatum TEXT,
                assettyp TEXT,
                verwendungsart TEXT,
                status TEXT,
                hersteller TEXT,
                modell TEXT,
                mac_adresse TEXT,
                garantie TEXT,
                verwaltungsart TEXT,
                prozessor TEXT,
                kerne_threads TEXT,
                ram TEXT,
                festplatte TEXT,
                betriebssystem TEXT,
                displaygroesse TEXT,
                dockingstation TEXT,
                anlagenummer TEXT,
                mitarbeiter TEXT,
                bemerkung TEXT,
                druckertyp TEXT
            )
        """)
        verbindung.commit()


def mitarbeiter_tabelle_anlegen():
    with closing(verbinden()) as verbindung:
        verbindung.execute("""
            CREATE TABLE IF NOT EXISTS mitarbeiter (
                id INTEGER PRIMARY KEY,
                vorname TEXT,
                nachname TEXT,
                uaccountid TEXT UNIQUE,
                organisationseinheit TEXT,
                standort TEXT,
                zimmer TEXT,
                arbeitsplatz TEXT,
                kostenstelle TEXT,
                status TEXT,
                bemerkung TEXT
            )
        """)
        verbindung.commit()


def historie_tabelle_anlegen():
    with closing(verbinden()) as verbindung:
        verbindung.execute("""
            CREATE TABLE IF NOT EXISTS historie (
                id INTEGER PRIMARY KEY,
                datum TEXT,
                typ TEXT,
                aktion TEXT
            )
        """)
        verbindung.commit()


def historie_anzeigen():
    with closing(verbinden()) as verbindung:
        print(verbindung.execute("SELECT * FROM historie").fetchall())