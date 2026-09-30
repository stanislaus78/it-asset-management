from asset import Asset
from funktionen_mitarbeiter import *
from funktionen_mitarbeiter import mitarbeiter_suchen
from mitarbeiter import Mitarbeiter
from datenbank import verbinden

def asset_suchen_sqlite(inventarnummer):

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE inventarnummer = ?
    """, (inventarnummer,))

    return cursor.fetchone()


# def alle_assets_anzeigen(assets):
#
#     for asset in assets:
#         print()
#         print(f"Inventarnummer: {asset.inventarnummer}")
#         print(f"Hersteller: {asset.hersteller}")
#         print(f"Status: {asset.status}")
#         print(f"Geraetetyp: {asset.geraetetyp}")
#         print(f"Standort: {asset.standort}")
#         print(f"Zimmer: {asset.zimmer}")
#         print(f"Organisationseinheit: {asset.organisationseinheit}")
#
#         if asset.mitarbeiter is not None:
#             print(f"Mitarbeiter: {asset.mitarbeiter.name}")
#         else:
#             print("Mitarbeiter: Nicht zugewiesen")
#
#         print("-" * 30)

def alle_assets_anzeigen_sqlite():

    cursor.execute("SELECT * FROM assets")

    assets = cursor.fetchall()

    if not assets:
        print("Keine Assets vorhanden")
        return

    for asset in assets:

        print()
        print(f"Inventarnummer: {asset[0]}")
        print(f"Hersteller: {asset[1]}")
        print(f"Status: {asset[2]}")
        print(f"Geraetetyp: {asset[3]}")
        print(f"Standort: {asset[4]}")
        print(f"Zimmer: {asset[5]}")
        print(f"Organisationseinheit: {asset[6]}")
        print(f"Mitarbeiter: {asset[7]}")
        print("-" * 30)



def assets_freigeben_sqlite(inventarnummer):

    cursor.execute("""
        UPDATE assets
        SET mitarbeiter = NULL,
            status = 'Lager'
        WHERE inventarnummer = ?
    """, (inventarnummer,))

    verbindung.commit()

    print("Asset erfolgreich freigegeben")

# def assets_nach_hersteller(assets, hersteller):
#
#     gefunden = False
#
#     for asset in assets:
#         if asset.hersteller.lower() == hersteller.lower():
#             asset.anzeigen()
#             gefunden = True
#
#     if not gefunden:
#         print("Keine Assets gefunden")

def assets_nach_hersteller_sqlite(hersteller):
    cursor.execute("""
        SELECT *
        FROM assets
        WHERE LOWER(hersteller) = LOWER(?)
    """, (hersteller,))

    assets = cursor.fetchall()

    if not assets:
        print("Keine Assets gefunden")
        return

    for asset in assets:
        print(asset)


# def assets_eines_mitarbeiter(assets, mitarbeiter, inventarnummer, hersteller, status ):
#
#     for asset in assets:
#         if asset.mitarbeiter == mitarbeiter:
#             print(f"\n===== Assets von {mitarbeiter} =====")
#             print()
#             print(f"Inventarnummer: {inventarnummer} ")
#             print(f"Hersteller: {hersteller}")
#             print(f"Status: {status}")
#             #asset.anzeigen()

def assets_eines_mitarbeiters_sqlite(name):

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE mitarbeiter = ?
    """, (name,))

    assets = cursor.fetchall()

    print(f"\n===== Assets von {name} =====")

    if not assets:
        print("Keine Assets gefunden")
        return

    for asset in assets:

        print()
        print(f"Inventarnummer: {asset[0]}")
        print(f"Hersteller: {asset[1]}")
        print(f"Status: {asset[2]}")
        print("-" * 30)

def lager_assets(assets):

    for asset in assets:
        if asset.status == "Lager":
            asset.anzeigen()


# def statistik_anzeigen(assets, mitarbeiter_liste):
#
#     print("\n===== Statistik =====")
#
#     print(f"Assets gesamt: {len(assets)}")
#     print(f"Mitarbeiter gesamt: {len(mitarbeiter_liste)}")
#
#     ausgegeben = 0
#     lager = 0

def statistik_anzeigen_sqlite():

    cursor.execute("SELECT COUNT(*) FROM assets")
    assets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM mitarbeiter")
    mitarbeiter = cursor.fetchone()[0]

    print("\n===== Statistik =====")
    print(f"Assets gesamt: {assets}")
    print(f"Mitarbeiter gesamt: {mitarbeiter}")



    for asset in assets:
        if asset.status.lower() == "ausgegeben":
            ausgegeben += 1
        elif asset.status.lower() == "lager":
            lager += 1

    print(f"Ausgegeben: {ausgegeben}")
    print(f"Im Lager: {lager}")


def anzahl_assets_von_mitarbeiter(assets, mitarbeiter):

    anzahl = 0

    for asset in assets:
        if asset.mitarbeiter == mitarbeiter:
            anzahl += 1

    return anzahl


def anzahl_ausgegebene_assets(assets):

    ausgegeben = 0

    for asset in assets:
        if asset.status == "Ausgegeben":
            ausgegeben += 1

    return ausgegeben


def anzahl_lager_assets(assets):

    lager = 0

    for asset in assets:
        if asset.status == "Lager":
            lager += 1

    return lager

# def assets_nach_typ(assets, geraetetyp):
#     for asset in assets:
#         if asset.geraetetyp.lower() == geraetetyp.lower():
#             asset.anzeigen()

def assets_nach_typ_sqlite(geraetetyp):

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE LOWER(geraetetyp) = LOWER(?)
    """, (geraetetyp,))

    assets = cursor.fetchall()

    print(f"Anzahl: {len(assets)}")

    for asset in assets:
        print(asset)


def anzahl_assets_nach_typ(assets, geraetetyp):
    anzahl_typ = 0
    for asset in assets:
        if asset.geraetetyp.lower() == geraetetyp.lower():
            anzahl_typ += 1
    return anzahl_typ

# def assets_nach_standort(assets, standort):
#     for asset in assets:
#         if asset.standort.lower() == standort.lower():
#             asset.anzeigen()


# def assets_nach_standort_sqlite(standort):
#
#     cursor.execute("""
#         SELECT *
#         FROM assets
#         WHERE LOWER(standort) = LOWER(?)
#     """, (standort,))
#
#     assets = cursor.fetchall()
#
#     print(f"Anzahl: {len(assets)}")
#
#     for asset in assets:
#         print(asset)


def assets_nach_standort_sqlite(standort):

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE LOWER(standort) = LOWER(?)
    """, (standort,))

    assets = cursor.fetchall()

    if not assets:
        print("Keine Assets gefunden")
        return

    print(f"Anzahl: {len(assets)}")

    for asset in assets:

        print()
        print(f"Inventarnummer: {asset[0]}")
        print(f"Hersteller: {asset[1]}")
        print(f"Status: {asset[2]}")
        print(f"Geraetetyp: {asset[3]}")
        print(f"Standort: {asset[4]}")
        print(f"Zimmer: {asset[5]}")
        print(f"Organisationseinheit: {asset[6]}")
        print(f"Mitarbeiter: {asset[7]}")
        print("-" * 30)



def anzahl_assets_nach_standort(assets, standort):
    anzahl_standort = 0
    for asset in assets:
        if asset.standort.lower() == standort.lower():
            anzahl_standort += 1
    return anzahl_standort

# def assets_nach_OA(assets, organisationseinheit):
#     for asset in assets:
#         if asset.organisationseinheit.lower() == organisationseinheit.lower():
#             asset.anzeigen()

def assets_nach_oa_sqlite(organisationseinheit):

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE organisationseinheit = ?
    """, (organisationseinheit,))

    assets = cursor.fetchall()

    print(f"Anzahl: {len(assets)}")

    for asset in assets:
        print(asset)


def anzahl_assets_nach_OA(assets, organisationseinheit):
    anzahl_OA = 0
    for asset in assets:
        if asset.organisationseinheit.lower() == organisationseinheit.lower():
            anzahl_OA += 1
    return anzahl_OA, assets

# def neues_asset_erstellen(assets, inventarnummer, hersteller, status, geraetetyp, standort, zimmer, organisationseinheit):
#
#     asset = asset_suchen(assets, inventarnummer)
#     if asset is None:
#
#
#         neues_asset = Asset(
#             inventarnummer,
#             hersteller,
#             status,
#             geraetetyp,
#             standort,
#             zimmer,
#             organisationseinheit
#         )
#
#         assets.append(neues_asset)
#         verbindung = verbinden()
#
#         cursor = verbindung.cursor()
#
#         cursor.execute(f"""
#         INSERT INTO assets (
#             inventarnummer,
#             hersteller,
#             status,
#             geraetetyp,
#             standort,
#             zimmer,
#             organisationseinheit
#         )
#         VALUES (
#             '{inventarnummer}',
#             '{hersteller}',
#             '{status}',
#             '{geraetetyp}',
#             '{standort}',
#             '{zimmer}',
#             '{organisationseinheit}'
#         )
#         """)
#
#         verbindung.commit()
#
#         verbindung.close()
#         print("Asset erfolgreich angelegt")
#

def neues_asset_erstellen_sqlite(
        inventarnummer,
        hersteller,
        status,
        geraetetyp,
        standort,
        zimmer,
        organisationseinheit):

    cursor.execute("""
        INSERT INTO assets (
            inventarnummer,
            hersteller,
            status,
            geraetetyp,
            standort,
            zimmer,
            organisationseinheit,
            mitarbeiter
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        inventarnummer,
        hersteller,
        status,
        geraetetyp,
        standort,
        zimmer,
        organisationseinheit,
        None
    ))

    verbindung.commit()

    print("Asset erfolgreich angelegt")

# def assets_loeschen(assets, inventarnummer):
#
#     for asset in assets:
#         if asset.inventarnummer.lower() == inventarnummer.lower():
#             assets.remove(asset)
#             print("Asset gelöscht")
#             return
#
#     print("Asset nicht gefunden")

def assets_loeschen_sqlite(inventarnummer):

    asset = asset_suchen_sqlite(inventarnummer)

    if asset is None:
        print("Asset nicht gefunden")
        return

    bestaetigung = input(
        f"Asset {inventarnummer} wirklich löschen? (j/n): "
    )

    if bestaetigung.lower() == "j":

        cursor.execute("""
            DELETE FROM assets
            WHERE inventarnummer = ?
        """, (inventarnummer,))

        verbindung.commit()

        print("Asset erfolgreich gelöscht")

    else:
        print("Löschen abgebrochen")


#def assets_bearbeiten(assets, inventarnummer):
    #for asset in assets:
        #if asset.inventarnummer.lower() == inventarnummer.lower():
            #asset.inventarnummer = input("Neue Inventarnummer")
            #print("Neue Inventarnummer wurde vergeben")
            #return
    #print("Asset nicht gefunden")

def asset_feld_aktualisieren(
        inventarnummer,
        feld,
        neuer_wert):

    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute(f"""
    UPDATE assets
    SET {feld} = '{neuer_wert}'
    WHERE inventarnummer = '{inventarnummer}';
    """)

    verbindung.commit()

    verbindung.close()


def assets_bearbeiten_sqlite(inventarnummer):

    asset = asset_suchen_sqlite(inventarnummer)

    if asset is None:
        print("Asset nicht gefunden")
        return

    print("1 - Hersteller")
    print("2 - Status")
    print("3 - Gerätetyp")
    print("4 - Standort")
    print("5 - Zimmer")
    print("6 - Organisationseinheit")

    auswahl = input("Was möchten Sie ändern? ")

    if auswahl == "1":

        neuer_hersteller = input("Neuer Hersteller: ")

        cursor.execute("""
            UPDATE assets
            SET hersteller = ?
            WHERE inventarnummer = ?
        """, (neuer_hersteller, inventarnummer))

        verbindung.commit()

        print("Hersteller erfolgreich geändert")

    elif auswahl == "2":

        neuer_status = input("Neuer Status: ")

        cursor.execute("""
            UPDATE assets
            SET status = ?
            WHERE inventarnummer = ?
        """, (neuer_status, inventarnummer))

        verbindung.commit()

        print("Status erfolgreich geändert")

    elif auswahl == "3":

        neuer_typ = input("Neuer Gerätetyp: ")

        cursor.execute("""
            UPDATE assets
            SET geraetetyp = ?
            WHERE inventarnummer = ?
        """, (neuer_typ, inventarnummer))

        verbindung.commit()

        print("Gerätetyp erfolgreich geändert")

    elif auswahl == "4":

        neuer_standort = input("Neuer Standort: ")

        cursor.execute("""
            UPDATE assets
            SET standort = ?
            WHERE inventarnummer = ?
        """, (neuer_standort, inventarnummer))

        verbindung.commit()

        print("Standort erfolgreich geändert")

    elif auswahl == "5":

        neues_zimmer = input("Neues Zimmer: ")

        cursor.execute("""
            UPDATE assets
            SET zimmer = ?
            WHERE inventarnummer = ?
        """, (neues_zimmer, inventarnummer))

        verbindung.commit()

        print("Zimmer erfolgreich geändert")

    elif auswahl == "6":

        neue_oe = input("Neue Organisationseinheit: ")

        cursor.execute("""
            UPDATE assets
            SET organisationseinheit = ?
            WHERE inventarnummer = ?
        """, (neue_oe, inventarnummer))

        verbindung.commit()

        print("Organisationseinheit erfolgreich geändert")

    else:
        print("Ungültige Eingabe")
    #print(
              #"1 - Inventarnummer"
              #"2 - Hersteller"
              #"3 - Status"
              #"4 - Gerätetyp"
             # "5 - Standort"
              #"6 - Zimmer"
              #"7 - Organisationseinheit")

        #auswahl = input("Welches Attribut soll verändert werden?")

# def asset_zuweisen(assets, mitarbeiter_liste, inventarnummer, name):
#     asset = asset_suchen(assets, inventarnummer)
#     mitarbeiter = mitarbeiter_suchen(mitarbeiter_liste, name)
#     if asset is not None and mitarbeiter is not None:
#         asset.mitarbeiter = mitarbeiter
#         asset.status = "Ausgegeben"
#         print("Asset erfolgreich zugewiesen")

def asset_zuweisen_sqlite(inventarnummer, name):

    cursor.execute("""
        UPDATE assets
        SET mitarbeiter = ?,
            status = 'Ausgegeben'
        WHERE inventarnummer = ?
    """, (name, inventarnummer))

    verbindung.commit()

    print("Asset erfolgreich zugewiesen")



# def assets_eines_mitarbeiters(assets, name):
#     gefunden = False
#
#     print(f"\n===== Assets von {name} =====")
#
#     for asset in assets:
#         if asset.mitarbeiter is not None:
#             if asset.mitarbeiter.name.lower() == name.lower():
#
#                 gefunden = True
#
#                 print()
#                 print(f"Inventarnummer: {asset.inventarnummer}")
#                 print(f"Hersteller: {asset.hersteller}")
#                 print(f"Status: {asset.status}")
#                 print("-" * 30)
#
#     if not gefunden:
#         print("Keine Assets gefunden")

def assets_eines_mitarbeiters_sqlite(name):

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE LOWER(mitarbeiter) = LOWER(?)
    """, (name,))

    assets = cursor.fetchall()

    print(f"\n===== Assets von {name} =====")

    if not assets:
        print("Keine Assets gefunden")
        return

    for asset in assets:

        print()
        print(f"Inventarnummer: {asset[0]}")
        print(f"Hersteller: {asset[1]}")
        print(f"Status: {asset[2]}")
        print(f"Geraetetyp: {asset[3]}")
        print(f"Standort: {asset[4]}")
        print(f"Zimmer: {asset[5]}")
        print(f"Organisationseinheit: {asset[6]}")
        print("-" * 30)


# def assets_freigeben(assets, inventarnummer):
#     asset = asset_suchen(assets, inventarnummer)
#     if asset is not None and asset.mitarbeiter is not None:
#         if asset.status == "Ausgegeben":
#             asset.mitarbeiter = None
#             asset.status = "Lager"
#             print("Asset erfolgreich freigegeben")
#         else:
#             print("Asset ist nicht ausgegeben")
#     else:
#         print("Asset nicht gefunden")


def assets_freigeben_sqlite(inventarnummer):

    asset = asset_suchen_sqlite(inventarnummer)

    if asset is None:
        print("Asset nicht gefunden")
        return

    if asset[2].lower() != "ausgegeben":
        print("Asset ist nicht ausgegeben")
        return

    bestaetigung = input(
        f"Asset {inventarnummer} wirklich freigeben? (j/n): "
    )

    if bestaetigung.lower() == "j":

        cursor.execute("""
            UPDATE assets
            SET mitarbeiter = NULL,
                status = 'Lager'
            WHERE inventarnummer = ?
        """, (inventarnummer,))

        verbindung.commit()

        print("Asset erfolgreich freigegeben")

    else:
        print("Freigabe abgebrochen")

# def assets_speichern_csv(assets):
#
#     with open("assets_backup.csv", "w") as datei:
#
#         datei.write(
#             "inventarnummer,hersteller,status,geraetetyp,standort,zimmer,organisationseinheit, mitarbeiter\n"
#         )
#         for asset in assets:
#             mitarbeiter_name = ""
#             if asset.mitarbeiter is not None:
#                 mitarbeiter_name = asset.mitarbeiter.name
#             zeile = (
#                 f"{asset.inventarnummer},"
#                 f"{asset.hersteller},"
#                 f"{asset.status},"
#                 f"{asset.geraetetyp},"
#                 f"{asset.standort},"
#                 f"{asset.zimmer},"
#                 f"{asset.organisationseinheit},"
#                 f"{mitarbeiter_name}"
#             )
#             datei.write(zeile + "\n")







from asset import Asset

# def assets_laden_csv(mitarbeiter_liste):
#     assets = []
#     with open("assets_backup.csv", "r") as datei:
#         kopfzeile = datei.readline()
#         for zeile in datei:
#             werte = zeile.strip().split(",")
#             asset = Asset(
#                 werte[0],
#                 werte[1],
#                 werte[2],
#                 werte[3],
#                 werte[4],
#                 werte[5],
#                 werte[6],
#                 #werte[7]
#             )
#             if len(werte) > 7 and werte[7] != "":
#                 mitarbeiter = mitarbeiter_suchen(
#                     mitarbeiter_liste,
#                     werte[7]
#                 )
#                 if mitarbeiter is not None:
#                     asset.mitarbeiter = mitarbeiter
#             assets.append(asset)
#     print(f"{len(assets)} CSV Assets wurden geladen.")
#     return assets

def assets_laden_sqlite(mitarbeiter_liste):

    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute("""
    SELECT
        inventarnummer,
        hersteller,
        status,
        geraetetyp,
        standort,
        zimmer,
        organisationseinheit
    FROM assets
    """)

    assets = []

    for werte in cursor.fetchall():

        asset = Asset(
            werte[0],
            werte[1],
            werte[2],
            werte[3],
            werte[4],
            werte[5],
            werte[6]
        )

        assets.append(asset)

    verbindung.close()

    return assets

# def lagerbestand_anzeigen(assets):
#
#     gefunden = False
#
#     print("\n===== Lagernde Assets =====")
#
#     for asset in assets:
#
#         if asset.status.lower() == "lager":
#
#             gefunden = True
#
#             print()
#             print(f"Inventarnummer: {asset.inventarnummer}")
#             print(f"Hersteller: {asset.hersteller}")
#             print(f"Geraetetyp: {asset.geraetetyp}")
#             print(f"Standort: {asset.standort}")
#             print("-" * 30)
#
#     if not gefunden:
#         print("Keine lagernden Assets vorhanden")


def lagerbestand_anzeigen_sqlite():

    cursor.execute("""
        SELECT *
        FROM assets
        WHERE status = 'Lager'
    """)

    assets = cursor.fetchall()

    if not assets:
        print("Keine lagernden Assets vorhanden")
        return

    print("\n===== Lagerbestand =====")

    for asset in assets:

        print()
        print(f"Inventarnummer: {asset[0]}")
        print(f"Hersteller: {asset[1]}")
        print(f"Geraetetyp: {asset[3]}")
        print(f"Standort: {asset[4]}")
        print("-" * 30)

def menue():
    print()
    print("===== Asset Management =====")
    print("1 -  Neues Asset erstellen")
    print("2 -  Asset bearbeiten")
    print("3 -  Asset löschen")
    print("4 -  Assets freigeben")
    print("5 -  Asset zuweisen")
    print("6 -  Asset suchen")
    print("7 -  Alle Assets anzeigen")
    print("8 -  Nach Hersteller suchen")
    print("9 -  Nach Standort suchen")
    print("10 - Nach Organisationseinheit suchen")
    print("11 - Statistik")
    print("12 - Gerätetyp")
    print("13 - Lagerbestand")
    print("14 - Mitarbeiter anlegen")
    print("15 - Mitarbeiter bearbeiten")
    print("16 - Mitarbeiter löschen")
    print("17 - Nach Mitarbeiter suchen")
    print("18 - Assets eines Mitarbeiters anzeigen")
    print("19 - Alle Mitarbeiter anzeigen")
    print("0 -  Beenden")


    return input("Ihre Auswahl: ")


