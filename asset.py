
from mitarbeiter import Mitarbeiter


class Asset:

    def __init__(self, inventarnummer, hersteller, status, geraetetyp, standort, zimmer, organisationseinheit):
        self.inventarnummer = inventarnummer
        self.hersteller = hersteller
        self.status = status
        self.geraetetyp = geraetetyp
        self.standort = standort
        self.zimmer = zimmer
        self.organisationseinheit = organisationseinheit
        self.mitarbeiter = None

    def zuweisen(self, mitarbeiter):

        if self.mitarbeiter is not None:
            print("Asset bereits vergeben")
        else:
            self.mitarbeiter = mitarbeiter

    def anzeigen(self):
        print()
        print("Inventarnummer:", self.inventarnummer)
        print("Hersteller:", self.hersteller)
        print("Status:", self.status)
        print("Geraetetyp:", self.geraetetyp)
        print("Standort:", self.standort)
        print("Zimmer:", self.zimmer)
        print("Organisationseinheit:", self.organisationseinheit)

        if self.mitarbeiter is not None:
            print("Mitarbeiter:", self.mitarbeiter.name)
        else:
            print("Mitarbeiter: Kein Mitarbeiter zugewiesen")

    def ausgeben(self):
        self.status = "Ausgegeben"

    def zurueckgeben(self):
        self.status = "Lager"

    def freigeben(self):
        self.status = "Lager"
        self.mitarbeiter = None

    def umzuweisen(self, neuer_mitarbeiter):
        self.mitarbeiter = neuer_mitarbeiter

