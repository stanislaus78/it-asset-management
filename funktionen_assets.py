from asset import Asset
from funktionen_mitarbeiter import *


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
        print("Asset erfolgreich angelegt")



def assets_loeschen(assets, inventarnummer):

    for asset in assets:
        if asset.inventarnummer.lower() == inventarnummer.lower():
            assets.remove(asset)
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
                asset.inventarnummer = input("Neue Inventarnummer: ")
                print("Status erfolgreich geändert")

            elif auswahl == "2":
                asset.hersteller = input("Neuer Hersteller: ")
                print("Status erfolgreich geändert")

            elif auswahl == "3":
                asset.status = input("Neuer Status: ")
                print("Status erfolgreich geändert")

            elif auswahl == "4":
                asset.geraetetyp = input("Neuer Gerätetyp: ")
                print("Status erfolgreich geändert")

            elif auswahl == "5":
                asset.standort = input("Neuer Standort: ")
                print("Status erfolgreich geändert")

            elif auswahl == "6":
                asset.zimmer = input("Neues Zimmer: ")
                print("Status erfolgreich geändert")

            elif auswahl == "7":
                asset.organisationseinheit = input("Neue Organisationseinheit: ")
                print("Status erfolgreich geändert")
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


def assets_speichern_csv(assets):

    with open("assets.csv", "w") as datei:

        datei.write(
            "inventarnummer,hersteller,status,geraetetyp,standort,zimmer,organisationseinheit\n"
        )
        for asset in assets:
            zeile = zeile = (
                f"{asset.inventarnummer},"
                f"{asset.hersteller},"
                f"{asset.status},"
                f"{asset.geraetetyp},"
                f"{asset.standort},"
                f"{asset.zimmer},"
                f"{asset.organisationseinheit}"
            )
            datei.write(zeile + "\n")







from asset import Asset

def assets_laden_csv():
    assets = []
    with open("assets.csv", "r") as datei:
        kopfzeile = datei.readline()
        for zeile in datei:
            werte = zeile.strip().split(",")
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
    print("0 - Beenden")


    return input("Ihre Auswahl: ")


