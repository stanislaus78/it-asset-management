from asset import Asset
from mitarbeiter import Mitarbeiter

def mitarbeiter_suchen(mitarbeiter_liste, name):
    for mitarbeiter in mitarbeiter_liste:
        if mitarbeiter.name.lower() == name.lower():
            return mitarbeiter
    return None


def alle_mitarbeiter_anzeigen(mitarbeiter_liste):

    for mitarbeiter in mitarbeiter_liste:
        print(mitarbeiter.name)
        print(mitarbeiter.abteilung)
        print()

def mitarbeiter_csv(mitarbeiter_liste):
    with open("mitarbeiter.csv", "w") as datei:
        datei.write(
            "name, abteilung "
            "\n"
        )
        for user in mitarbeiter_liste:
            zeile = (
                f"{user.name},"
                f"{user.abteilung}"
            )
            datei.write(zeile + "\n")

def mitarbeiter_laden_csv():
    mitarbeiter_liste = []
    with open("mitarbeiter.csv", "r") as datei:
        kopfzeile = datei.readline()
        for zeile in datei:
            werte = zeile.strip().split(",")
            mitarbeiter = Mitarbeiter(
                werte[0],
                werte[1]
            )
            mitarbeiter_liste.append(mitarbeiter)
    return mitarbeiter_liste
