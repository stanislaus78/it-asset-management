
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

    bemerkung TEXT

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


def historie_tabelle_anlegen():

    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historie (
            id INTEGER PRIMARY KEY,
            datum TEXT,
            typ TEXT,
            aktion TEXT

        )
    """)

    verbindung.commit()

    verbindung.close()

def historie_anzeigen():

    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute("""
    SELECT *
    FROM historie
    """)

    print(cursor.fetchall())

    verbindung.close()




