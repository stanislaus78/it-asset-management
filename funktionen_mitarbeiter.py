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
