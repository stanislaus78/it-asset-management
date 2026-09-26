import sqlite3


verbindung = sqlite3.connect("asset_management.db")

cursor = verbindung.cursor()


def assets_tabelle_anlegen():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        inventarnummer TEXT,
        hersteller TEXT,
        status TEXT,
        geraetetyp TEXT,
        standort TEXT,
        zimmer TEXT,
        organisationseinheit TEXT
    )
    """)
    verbindung.commit()
def mitarbeiter_tabelle_anlegen():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mitarbeiter (
        id INTEGER PRIMARY KEY,
        name TEXT,
        abteilung TEXT
    )
    """)
    verbindung.commit()
def asset_anlegen():

    inventarnummer = input("Inventarnummer: ")
    hersteller = input("Hersteller: ")
    status = input("Status: ")
    geraetetyp = input("Gerätetyp: ")
    standort = input("Standort: ")
    zimmer = input("Zimmer: ")
    organisationseinheit = input("Organisationseinheit: ")

    cursor.execute(f"""
    INSERT INTO assets (
        inventarnummer,
        hersteller,
        status,
        geraetetyp,
        standort,
        zimmer,
        organisationseinheit
    )
    VALUES (
        '{inventarnummer}',
        '{hersteller}',
        '{status}',
        '{geraetetyp}',
        '{standort}',
        '{zimmer}',
        '{organisationseinheit}'
    )
    
""")
    verbindung.commit()

def mitarbeiter_anlegen():

    name = input("Name: ")
    abteilung = input("Abteilung: ")

    cursor.execute(f"""
    INSERT INTO mitarbeiter
    (name, abteilung)
    VALUES
    ('{name}', '{abteilung}')
    """)
    verbindung.commit()

    print("Mitarbeiter angelegt.")

def assets_anzeigen():

    cursor.execute("SELECT * FROM assets")

    daten = cursor.fetchall()
    if len(daten) == 0:
        print("Keine Assets vorhanden.")
    else:
        for asset in daten:
            print(asset)

def mitarbeiter_anzeigen():
    cursor.execute("SELECT * FROM mitarbeiter")
    for mitarbeiter in cursor.fetchall():
        print(mitarbeiter)

def mitarbeiter_loeschen():
    name = input("Name des Mitarbeiters: ")
    cursor.execute(f"""
    DELETE FROM mitarbeiter
    WHERE name = '{name}';
    """)
    print("Mitarbeiter gelöscht.")
    verbindung.commit()
def asset_loeschen():
    inventarnummer_loeschen = input("Inventarnummer eintippen: ")
    cursor.execute(f"""
    DELETE FROM assets
    WHERE inventarnummer = '{inventarnummer_loeschen}';
    """)
    print("Asset gelöscht.")
    verbindung.commit()


def asset_suchen():
    asset_suchen = input("Tippen Sie Inventarnummer ein: ")
    cursor.execute(f"SELECT * FROM assets WHERE inventarnummer = '{asset_suchen}';")
    for asset in cursor.fetchall():
        print(asset)

def asset_bearbeiten():
    bearbeiten = input("Inventarnummer eintippen: ")
    neuer_status = input("Neuer Status: ")
    cursor.execute(f"""
    UPDATE assets
    SET status = '{neuer_status}'
    WHERE inventarnummer = '{bearbeiten}';
    """)
    verbindung.commit()
    print("Asset bearbeitet")

while True:
    print("1 -  Assets Tabelle anlegen")
    print("2 -  Mitarbeiter Tabelle anlegen")
    print("3 -  Asset anlegen")
    print("4 -  Assets anzeigen")
    print("5 -  Asset löschen")
    print("6 -  Mitarbeiter anlegen")
    print("7 -  Mitarbeiter anzeigen")
    print("8 -  Mitarbeiter löschen")
    print("9 -  Asset suchen")
    print("10 - Asset bearbeiten")
    print("0 - Beenden")

    auswahl = input("Ihre Auswahl: ")

    if auswahl == "1":
        assets_tabelle_anlegen()

    elif auswahl == "2":
        mitarbeiter_tabelle_anlegen()

    elif auswahl == "3":
        asset_anlegen()

    elif auswahl == "4":
        assets_anzeigen()

    elif auswahl == "5":
        asset_loeschen()

    elif auswahl == "6":
        mitarbeiter_anlegen()

    elif auswahl == "7":
        mitarbeiter_anzeigen()

    elif auswahl == "8":
        mitarbeiter_loeschen()

    elif auswahl == "9":
        asset_suchen()

    elif auswahl == "10":
        asset_bearbeiten()


    elif auswahl == "0":
        break


cursor.execute("SELECT COUNT(*) FROM assets")
print(cursor.fetchone())
verbindung.close()


