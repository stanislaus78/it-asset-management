from asset import Asset
from funktionen_mitarbeiter import *
from funktionen_mitarbeiter import mitarbeiter_suchen
from mitarbeiter import Mitarbeiter
from datenbank import verbinden

def asset_suchen(assets,inventarnummer):

    for asset in assets:
        if asset.inventarnummer == inventarnummer:
            return asset

    return None


def alle_assets_anzeigen(assets):

    for asset in assets:
        asset.anzeigen()


def assets_nach_hersteller(assets, hersteller):

    gefunden = False

    for asset in assets:
        if asset.hersteller.lower() == hersteller.lower():
            asset.anzeigen()
            gefunden = True

    if not gefunden:
        print("Keine Assets gefunden")


def assets_von_mitarbeiter(assets, mitarbeiter):

    for asset in assets:
        if asset.mitarbeiter == mitarbeiter:
            asset.anzeigen()


def lager_assets(assets):

    for asset in assets:
        if asset.status == "Lager":
            asset.anzeigen()


def assets_statistik(assets):

    lager = 0
    ausgegeben = 0

    for asset in assets:

        if asset.status == "Lager":
            lager += 1

        elif asset.status == "Ausgegeben":
            ausgegeben += 1

    print()
    print("Assets gesamt:", len(assets))
    print("Im Lager:", lager)
    print("Ausgegeben:", ausgegeben)


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

def assets_nach_typ(assets, geraetetyp):
    for asset in assets:
        if asset.geraetetyp.lower() == geraetetyp.lower():
            asset.anzeigen()

def anzahl_assets_nach_typ(assets, geraetetyp):
    anzahl_typ = 0
    for asset in assets:
        if asset.geraetetyp.lower() == geraetetyp.lower():
            anzahl_typ += 1
    return anzahl_typ

def assets_nach_standort(assets, standort):
    for asset in assets:
        if asset.standort.lower() == standort.lower():
            asset.anzeigen()


def anzahl_assets_nach_standort(assets, standort):
    anzahl_standort = 0
    for asset in assets:
        if asset.standort.lower() == standort.lower():
            anzahl_standort += 1
    return anzahl_standort

def assets_nach_OA(assets, organisationseinheit):
    for asset in assets:
        if asset.organisationseinheit.lower() == organisationseinheit.lower():
            asset.anzeigen()

def anzahl_assets_nach_OA(assets, organisationseinheit):
    anzahl_OA = 0
    for asset in assets:
        if asset.organisationseinheit.lower() == organisationseinheit.lower():
            anzahl_OA += 1
    return anzahl_OA

def neues_asset_erstellen(assets, inventarnummer, hersteller, status, geraetetyp, standort, zimmer, organisationseinheit):

    asset = asset_suchen(assets, inventarnummer)
    if asset is None:


        neues_asset = Asset(
            inventarnummer,
            hersteller,
            status,
            geraetetyp,
            standort,
            zimmer,
            organisationseinheit
        )

        assets.append(neues_asset)
        verbindung = verbinden()

        cursor = verbindung.cursor()

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

        verbindung.close()
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

def assets_loeschen(assets, inventarnummer):

    for asset in assets:

        if asset.inventarnummer.lower() == inventarnummer.lower():

            assets.remove(asset)

            verbindung = verbinden()

            cursor = verbindung.cursor()

            cursor.execute(f"""
            DELETE FROM assets
            WHERE inventarnummer = '{inventarnummer}';
            """)

            verbindung.commit()

            verbindung.close()

            print("Asset gelöscht")

            return

    print("Asset nicht gefunden")


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


def assets_bearbeiten(assets, inventarnummer):
    for asset in assets:
        if asset.inventarnummer.lower() == inventarnummer.lower():
            # asset.inventarnummer = input("Neue Inventarnummer")
            print("1 - Inventarnummer")
            print("2 - Hersteller")
            print("3 - Status")
            print("4 - Gerätetyp")
            print("5 - Standort")
            print("6 - Zimmer")
            print("7 - Organisationseinheit")

            auswahl = input("Was möchten Sie ändern? ")
            if auswahl == "1":
                neuer_standort = input("Neuer Standort: ")

                asset.standort = neuer_standort

                asset_feld_aktualisieren(

                    inventarnummer,

                    "standort",

                    neuer_standort

                )

                print("Standort erfolgreich geändert")



            elif auswahl == "2":

                neuer_hersteller = input("Neuer Hersteller: ")

                asset.hersteller = neuer_hersteller

                asset_feld_aktualisieren(

                    inventarnummer,

                    "hersteller",

                    neuer_hersteller
                )
                print("Hersteller erfolgreich geändert")



            elif auswahl == "3":

                neuer_status = input("Neuer Status: ")

                asset.status = neuer_status

                asset_feld_aktualisieren(

                    inventarnummer,

                    "status",

                    neuer_status
                )
                print("Status erfolgreich geändert")

            elif auswahl == "4":
                neuer_standort = input("Neuer Standort: ")

                asset.standort = neuer_standort

                asset_feld_aktualisieren(

                    inventarnummer,

                    "standort",

                    neuer_standort

                )

                print("Standort erfolgreich geändert")



            elif auswahl == "5":

                neuer_standort = input("Neuer Standort: ")

                asset.standort = neuer_standort

                asset_feld_aktualisieren(

                    inventarnummer,

                    "standort",

                    neuer_standort

                )

                print("Standort erfolgreich geändert")

            elif auswahl == "6":
                neuer_standort = input("Neuer Standort: ")

                asset.standort = neuer_standort

                asset_feld_aktualisieren(

                    inventarnummer,

                    "standort",

                    neuer_standort

                )

                print("Standort erfolgreich geändert")


            elif auswahl == "7":
                neuer_standort = input("Neuer Standort: ")

                asset.standort = neuer_standort

                asset_feld_aktualisieren(

                    inventarnummer,

                    "standort",

                    neuer_standort

                )

                print("Standort erfolgreich geändert")

            else:
                print("Ungültige Auswahl")


            return
    print("Asset nicht gefunden")

    #print(
              #"1 - Inventarnummer"
              #"2 - Hersteller"
              #"3 - Status"
              #"4 - Gerätetyp"
             # "5 - Standort"
              #"6 - Zimmer"
              #"7 - Organisationseinheit")

        #auswahl = input("Welches Attribut soll verändert werden?")

def asset_zuweisen(assets, mitarbeiter_liste, inventarnummer, name):
    asset = asset_suchen(assets, inventarnummer)
    mitarbeiter = mitarbeiter_suchen(mitarbeiter_liste, name)
    if asset is not None and mitarbeiter is not None:
        asset.mitarbeiter = mitarbeiter
        asset.status = "Ausgegeben"
        print("Asset erfolgreich zugewiesen")



def assets_eines_mitarbeiters(assets, name):
    gefunden = False
    for asset in assets:
        if asset.mitarbeiter is not None:
            if asset.mitarbeiter.name.lower() == name.lower():
                asset.anzeigen()

    if not gefunden:
        print("Kein Assets gefunden")


def assets_freigeben(assets, inventarnummer):
    asset = asset_suchen(assets, inventarnummer)
    if asset is not None and asset.mitarbeiter is not None:
        if asset.status == "Ausgegeben":
            asset.mitarbeiter = None
            asset.status = "Lager"
            print("Asset erfolgreich freigegeben")
        else:
            print("Asset ist nicht ausgegeben")
    else:
        print("Asset nicht gefunden")


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




def menue():
    print()
    print("===== Asset Management =====")
    print("1 -  Neues Asset erstellen")
    print("2 -  Asset bearbeiten")
    print("3 -  Asset löschen")
    print("4 -  Alle Assets anzeigen")
    print("5 -  Asset suchen")
    print("6 -  Nach Hersteller suchen")
    print("7 -  Statistik")
    print("8 -  Gerätetyp")
    print("9 -  Nach Standort suchen")
    print("10 - Nach Organisationseinheit suchen")
    print("11 - Nach Mitarbeiter suchen")
    print("12 - Asset zuweisen")
    print("13 - Assets eines Mitarbeiters anzeigen")
    print("14 - Assets freigeben")
    print("15 - Alle Mitarbeiter anzeigen")
    print("16 - Änderungen speichern")
    print("17 - Assets laden")
    print("18 - Mitarbeiter speichern")
    print("19 - Mitarbeiter laden")
    print("0 - Beenden")


    return input("Ihre Auswahl: ")


