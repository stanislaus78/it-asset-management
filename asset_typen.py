from dataclasses import dataclass, field

# Feldname im Formular -> (Beschriftung, Spalte in der Tabelle assets)
FELDER = {
    "inventarnummer": ("Inventarnummer", "inventarnummer"),
    "rechnername": ("Rechnername", "rechnername"),
    "seriennummer": ("Seriennummer", "seriennummer"),
    "benutzer": ("Benutzer", "mitarbeiter"),
    "standort": ("Standort", "standort"),
    "zimmer": ("Zimmer", "zimmer"),
    "arbeitsplatz": ("Arbeitsplatz", "arbeitsplatz"),
    "kostenstelle": ("Kostenstelle", "kostenstelle"),
    "organisationseinheit": ("Organisationseinheit", "organisationseinheit"),
    "hersteller": ("Hersteller", "hersteller"),
    "modell": ("Modell", "modell"),
    "prozessor": ("Prozessor", "prozessor"),
    "kerne_threads": ("Kerne/Threads", "kerne_threads"),
    "ram": ("RAM", "ram"),
    "festplatte": ("Festplatte", "festplatte"),
    "betriebssystem": ("Betriebssystem", "betriebssystem"),
    "displaygroesse": ("Displaygröße", "displaygroesse"),
    "dockingstation": ("Dockingstation", "dockingstation"),
    "verwaltungsart": ("Verwaltungsart", "verwaltungsart"),
    "verwendungsart": ("Verwendungsart", "verwendungsart"),
    "druckertyp": ("Druckertyp", "druckertyp"),
    "status": ("Status", "status"),
    "mac_adresse": ("MAC-Adresse", "mac_adresse"),
    "garantie": ("Garantie", "garantie"),
    "anschaffungsdatum": ("Anschaffungsdatum", "anschaffungsdatum"),
    "installationsdatum": ("Installationsdatum", "installationsdatum"),
    "anlagenummer": ("Anlagenummer", "anlagenummer"),
    "bemerkung": ("Bemerkung", "bemerkung"),
}


@dataclass(frozen=True)
class Typ:
    slug: str
    assettyp: str          # so wie in der Datenbank gespeichert
    titel: str
    einzahl: str
    icon: str
    gruppen: list
    auswahl: dict = field(default_factory=dict)   # Feld -> feste Werte (Dropdown)

    def felder(self):
        return [name for _, namen in self.gruppen for name in namen]

    def fuer_js(self):
        return {
            "assettyp": self.assettyp,
            "einzahl": self.einzahl,
            "felder": {n: FELDER[n][0] for n in self.felder()},
            "gruppen": [[titel, list(namen)] for titel, namen in self.gruppen],
            "auswahl": self.auswahl,
        }


TYPEN = {
    "maus": Typ(
        slug="maus", assettyp="Maus", titel="Mäuse", einzahl="Maus", icon="🖱️",
        gruppen=[
            ("Allgemein", ["inventarnummer", "seriennummer", "benutzer"]),
            ("Standort", ["standort", "zimmer", "arbeitsplatz",
                          "kostenstelle", "organisationseinheit"]),
            ("Hardware", ["hersteller", "modell"]),
            ("Verwaltung", ["status", "anschaffungsdatum"]),
            ("Bemerkung", ["bemerkung"]),
        ],
    ),
}