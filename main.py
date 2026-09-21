
from asset import Asset
from mitarbeiter import Mitarbeiter
from funktionen_assets import *
from funktionen_mitarbeiter import *



# Mitarbeiter

m1 = Mitarbeiter("Stanislav", "IT")
m2 = Mitarbeiter("Marina", "Forschung")
m3 = Mitarbeiter("Peter", "Buchhaltung")

mitarbeiter_liste = [m1, m2, m3]

# Assets

a1 = Asset("LT001", "Dell", "Ausgegeben", "Laptop", "Zlb", "308", "602")
a2 = Asset("LT002", "Lenovo", "Lager", "Stand-PC", "Zlb", "348", "600")
a3 = Asset("LT003", "HP", "Lager", "Monitor", "Uza", "Bio Labor", "603")
a4 = Asset("LT004", "Samsung", "Lager", "Diensthandy", "Zlb", "349", "601")

assets = [a1, a2, a3, a4]




while True:

    auswahl = menue()

    if auswahl == "1":

        inventarnummer = input("Inventarnummer: ")

        asset = asset_suchen(assets, inventarnummer)

        if asset is not None:
            print("Inventarnummer bereits vergeben")

        else:
            hersteller = input("Hersteller: ")
            ...
        hersteller = input("Hersteller: ")
        status = input("Status: ")
        geraetetyp = input("Gerätetyp: ")
        standort = input("Standort: ")
        zimmer = input("Zimmer: ")
        organisationseinheit = input("Organisationseinheit: ")

        neues_asset_erstellen(
            assets,
            inventarnummer,
            hersteller,
            status,
            geraetetyp,
            standort,
            zimmer,
            organisationseinheit
        )


    elif auswahl == "2":
        inventarnummer = input("Auswahl: ")
        assets_bearbeiten(assets, inventarnummer)



    elif auswahl == "3":
        inventarnummer = input("Auswahl: ")
        assets_loeschen(assets, inventarnummer)

    elif auswahl == "4":

        alle_assets_anzeigen(assets)

    elif auswahl == "5":

        inventarnummer = input("Inventarnummer: ")
        asset = asset_suchen(assets, inventarnummer)

        if asset is not None:
            asset.anzeigen()
        else:
            print("Asset nicht gefunden")

    elif auswahl == "6":

        hersteller = input("Hersteller: ")
        assets_nach_hersteller(assets, hersteller)

    elif auswahl == "7":

        assets_statistik(assets)

    elif auswahl == "0":

        print("Programm beendet")
        break
    elif auswahl == "8":
        geraetetyp = input("Gerätetyp: ")
        assets_nach_typ(assets, geraetetyp)
        print("Anzahl:", anzahl_assets_nach_typ(assets,geraetetyp))

    elif auswahl == "9":
        standort = input("Standort: ")
        assets_nach_standort(assets, standort)
        print("Anzahl: ", anzahl_assets_nach_standort(assets, standort))

    elif auswahl == "10":
        organisationseinheit = input("Organisationseinheit: ")
        assets_nach_OA(assets, organisationseinheit)
        print("Anzahl: ", anzahl_assets_nach_OA(assets, organisationseinheit))

    elif auswahl == "11":
        name = input("Name des Mitarbeiters eingeben:")
        mitarbeiter = mitarbeiter_suchen(mitarbeiter_liste, name)
        if mitarbeiter is not None:
            print(mitarbeiter.name)
            print(mitarbeiter.abteilung)
        else:
            print("Mitarbeiter nicht gefunden")

    elif auswahl == "12":
        inventarnummer = input("Inventarnummer: ")
        name = input("Mitarbeiter: ")
        asset_zuweisen(assets, mitarbeiter_liste, inventarnummer, name)

    elif auswahl == "13":
        name = input("Name:")
        assets_eines_mitarbeiters(assets, name)

    elif auswahl == "14":
        inventarnummer = input("Inventarnummer:")

    elif auswahl == "15":
        alle_mitarbeiter_anzeigen(mitarbeiter_liste)

    elif auswahl == "16":
        assets_speichern_csv(assets)

    elif auswahl == "17":
        assets_laden_csv()
        if len(assets) > 0:
            print(f"{len(assets)} Assets wurden geladen.")
        else:
            print("Keine Assets gefunden.")



    else:

        print("Ungültige Eingabe")

#asset = asset_suchen("LT001")

#a1.zuweisen(m1)
#asset.ausgeben()

#asset.anzeigen()


#a1.freigeben()
#a1.anzeigen()
#
#print(a1.mitarbeiter)
#print(a1.mitarbeiter.name)

#alle_assets_anzeigen(assets)

