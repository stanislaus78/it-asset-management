
from asset import Asset
import sqlite3

def verbinden():

    verbindung = sqlite3.connect("asset_management.db")

    return verbindung

def assets_tabelle_anlegen():

    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY,
        inventarnummer TEXT,
        hersteller TEXT,
        status TEXT,
        geraetetyp TEXT,
        standort TEXT,
        zimmer TEXT,
        organisationseinheit TEXT
        mitarbeiter TEXT
    )
    """)

    verbindung.commit()

    verbindung.close()







def mitarbeiter_tabelle_anlegen():
    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mitarbeiter (
            id INTEGER PRIMARY KEY,
            name TEXT,
            abteilung TEXT   
        )
        """)

    verbindung.commit()

    verbindung.close()
