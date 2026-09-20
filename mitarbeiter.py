

class Mitarbeiter:

    def __init__(self, name, abteilung):
        self.name = name
        self.abteilung = abteilung

    def alle_mitarbeiter_anzeigen(self, mitarbeiter_liste):
        print("Name: ", self.name)
        print("Mitarbeiter: ", self.abteilung)
        print()
        for mitarbeiter in mitarbeiter_liste:
            mitarbeiter.anzeigen()
