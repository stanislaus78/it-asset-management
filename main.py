
from asset import Asset
from mitarbeiter import Mitarbeiter
from funktionen_assets import *
from funktionen_mitarbeiter import *




while True:

    auswahl = menue()

    if auswahl == "1":

        inventarnummer = input("Inventarnummer: ")

        asset = asset_suchen_sqlite(inventarnummer)

        if asset is not None:
            print("Inventarnummer bereits vergeben")

        else:
            hersteller = input("Hersteller: ")
            status = input("Status: ")
            geraetetyp = input("Gerätetyp: ")
            standort = input("Standort: ")
            zimmer = input("Zimmer: ")
            organisationseinheit = input("Organisationseinheit: ")

            neues_asset_erstellen_sqlite(
                inventarnummer,
                hersteller,
                status,
                geraetetyp,
                standort,
                zimmer,
                organisationseinheit
            )


    elif auswahl == "2":
        inventarnummer = input("Inventarnummer: ")
        assets_bearbeiten_sqlite(inventarnummer)

    elif auswahl == "3":
        inventarnummer = input("Inventarnummer: ")
        assets_loeschen_sqlite(inventarnummer)


    elif auswahl == "4":
        inventarnummer = input("Inventarnummer: ")
        assets_freigeben_sqlite(inventarnummer)


    elif auswahl == "5":
        inventarnummer = input("Inventarnummer: ")
        name = input("Mitarbeiter: ")
        asset_zuweisen_sqlite(inventarnummer, name)


    elif auswahl == "6":
        inventarnummer = input("Inventarnummer: ")
        asset = asset_suchen_sqlite(inventarnummer)
        if asset is not None:
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
        else:
            print("Asset nicht gefunden")

    elif auswahl == "7":
        alle_assets_anzeigen_sqlite()


    elif auswahl == "8":
        hersteller = input("Hersteller: ")
        assets_nach_hersteller_sqlite(hersteller)


    elif auswahl == "9":
        standort = input("Standort: ")
        assets_nach_standort_sqlite(standort)


    elif auswahl == "10":
        organisationseinheit = input("Organisationseinheit: ")
        assets_nach_oa_sqlite(organisationseinheit)


    elif auswahl == "11":
        statistik_anzeigen_sqlite()


    elif auswahl == "12":
        geraetetyp = input("Gerätetyp: ")
        assets_nach_typ_sqlite(geraetetyp)

    elif auswahl == "13":
        lagerbestand_anzeigen_sqlite()

    elif auswahl == "14":
        mitarbeiter_anlegen_sqlite()

    elif auswahl == "15":
        mitarbeiter_bearbeiten_sqlite()

    elif auswahl == "16":
        mitarbeiter_loeschen_sqlite()

    elif auswahl == "17":
        name = input("Name des Mitarbeiters: ")

        mitarbeiter = mitarbeiter_suchen_sqlite(name)

        if mitarbeiter is not None:

            print()
            print(f"ID: {mitarbeiter[0]}")
            print(f"Name: {mitarbeiter[1]}")
            print(f"Abteilung: {mitarbeiter[2]}")
            print("-" * 30)

        else:
            print("Mitarbeiter nicht gefunden")


    elif auswahl == "18":
        name = input("Name: ")
        assets_eines_mitarbeiters_sqlite(name)


    elif auswahl == "19":
        alle_mitarbeiter_anzeigen_sqlite()

    elif auswahl == "0":
        print("Programm beendet")
        break

    else:

        print("Ungültige Eingabe")

#a1.zuweisen(m1)
#asset.ausgeben()

#asset.anzeigen()


#a1.freigeben()
#a1.anzeigen()
#
#print(a1.mitarbeiter)
#print(a1.mitarbeiter.name)

#alle_assets_anzeigen(assets)

