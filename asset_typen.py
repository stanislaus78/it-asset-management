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
    "laptop": ("Laptop", "laptop"),
    "anlagenummer": ("Anlagenummer", "anlagenummer"),
    "bemerkung": ("Bemerkung", "bemerkung"),
}


@dataclass(frozen=True)
class Typ:
    slug: str
    assettyp: str
    titel: str
    einzahl: str
    icon: str
    gruppen: list
    auswahl: dict = field(default_factory=dict)          # Feld -> feste Werte (Dropdown)
    labels: dict = field(default_factory=dict)           # Feld -> abweichende Beschriftung
    ohne_leer: tuple = ()                                # Dropdowns ohne leeren Eintrag
    anzeige_standard: dict = field(default_factory=dict) # Anzeigewert bei leerem Feld
    berechnet: dict = field(default_factory=dict)        # Feld -> SQL, nur Anzeige
    verbergen: dict = field(default_factory=dict)        # Feld -> (Feld, Wert): ausblenden, wenn gleich

    def felder(self):
        return [name for _, namen in self.gruppen for name in namen]

    def label(self, name):
        return self.labels.get(name, FELDER[name][0])

    def fuer_js(self):
        return {
            "assettyp": self.assettyp,
            "einzahl": self.einzahl,
            "felder": {n: self.label(n) for n in self.felder()},
            "gruppen": [[titel, list(namen)] for titel, namen in self.gruppen],
            "auswahl": self.auswahl,
            "ohne_leer": list(self.ohne_leer),
            "anzeige_standard": self.anzeige_standard,
            "nur_lesen": list(self.berechnet),
            "verbergen": {k: list(v) for k, v in self.verbergen.items()},
        }
ALLGEMEIN = ("Allgemein", ["inventarnummer", "seriennummer", "benutzer"])
STANDORT = ("Standort", ["standort", "zimmer", "arbeitsplatz",
                         "kostenstelle", "organisationseinheit"])
BEMERKUNG = ("Bemerkung", ["bemerkung"])


def einfach(slug, assettyp, titel, einzahl, icon, auswahl=None):
    return Typ(
        slug=slug, assettyp=assettyp, titel=titel, einzahl=einzahl, icon=icon,
        gruppen=[
            ALLGEMEIN, STANDORT,
            ("Hardware", ["hersteller", "modell"]),
            ("Verwaltung", ["status", "anschaffungsdatum"]),
            BEMERKUNG,
        ],
        auswahl=auswahl or {},
    )


def mobil(slug, assettyp, titel, einzahl, icon):
    return Typ(
        slug=slug, assettyp=assettyp, titel=titel, einzahl=einzahl, icon=icon,
        gruppen=[
            ALLGEMEIN, STANDORT,
            ("Hardware", ["hersteller", "modell", "displaygroesse", "ram",
                          "festplatte", "mac_adresse"]),
            ("Verwaltung", ["status", "garantie", "anschaffungsdatum"]),
            BEMERKUNG,
        ],
    )


TYPEN = {t.slug: t for t in [
    einfach("maus", "Maus", "Mäuse", "Maus", "🖱️"),
    einfach("scanner", "Scanner", "Scanner", "Scanner", "📄"),
    einfach("webcam", "Webcam", "Webcams", "Webcam", "📷"),
    einfach("kamera", "Kamera", "Kameras", "Kamera", "📹"),
    einfach("mikrofon", "Mikrofon", "Mikrofone", "Mikrofon", "🎤"),
    einfach("kopfhoerer", "Kopfhoerer", "Kopfhörer", "Kopfhörer", "🎧"),
    einfach("aufnahmegeraet", "Aufnahmegeraet", "Aufnahmegeräte", "Aufnahmegerät", "🎙️"),
    einfach("konferenzkamera", "Konferenzkamera", "Konferenzkameras", "Konferenzkamera",
            "🦉", auswahl={"status": ["Leihgerät", "Festgerät"]}),
    mobil("tablet", "Tablet", "Tablets", "Tablet", "📱"),
    mobil("diensthandy", "Diensthandy", "Diensthandys", "Diensthandy", "📱"),
    Typ(
        slug="switch", assettyp="Switch", titel="Switch", einzahl="Switch", icon="🔀",
        gruppen=[
            ("Allgemein", ["inventarnummer", "seriennummer"]),
            STANDORT,
            ("Hardware", ["hersteller", "modell", "verwendungsart"]),
            ("Verwaltung", ["status", "anschaffungsdatum"]),
            BEMERKUNG,
        ],
        auswahl={"verwendungsart": ["Netzwerkswitch", "KVM-Switch", "Umschalteswitch"]},
        labels={"verwendungsart": "Switchtyp"},
    ),
    Typ(
        slug="drucker", assettyp="Drucker", titel="Drucker", einzahl="Drucker", icon="🖨️",
        gruppen=[
            ALLGEMEIN, STANDORT,
            ("Hardware", ["hersteller", "modell", "druckertyp", "mac_adresse"]),
            ("Verwaltung", ["status", "garantie", "anschaffungsdatum"]),
            BEMERKUNG,
        ],
        auswahl={"druckertyp": ["Netzwerk", "Lokal"]},
        ohne_leer=("druckertyp",),
        anzeige_standard={"druckertyp": "Netzwerk"},
        verbergen={"mac_adresse": ("druckertyp", "Lokal")},
    ),
    Typ(
        slug="dockingstation", assettyp="Dockingstation", titel="Dockingstation",
        einzahl="Dockingstation", icon="🖥️",
        gruppen=[
            ALLGEMEIN, STANDORT,
            ("Hardware", ["hersteller", "modell", "mac_adresse", "laptop"]),
            ("Verwaltung", ["status", "garantie", "anschaffungsdatum"]),
            BEMERKUNG,
        ],
        berechnet={"laptop": (
            "SELECT GROUP_CONCAT(l.inventarnummer, ', ') FROM assets l "
            "WHERE l.dockingstation = assets.inventarnummer "
            "AND LOWER(l.assettyp) = 'laptop'")},
    ),
    Typ(
        slug="zubehoer", assettyp="Zubehoer", titel="Zubehör", einzahl="Zubehör", icon="📦",
        gruppen=[
            ALLGEMEIN, STANDORT,
            ("Hardware", ["hersteller", "modell", "verwendungsart"]),
            ("Verwaltung", ["status", "anschaffungsdatum"]),
            BEMERKUNG,
        ],
        auswahl={"status": ["Leihgerät", "Festgerät"]},
        ohne_leer=("status",),
        labels={"verwendungsart": "Gerätetyp"},
    ),
    Typ(
        slug="laptop", assettyp="Laptop", titel="Laptops", einzahl="Laptop", icon="💻",
        gruppen=[
            ("Allgemein", ["rechnername", "inventarnummer", "seriennummer", "benutzer"]),
            STANDORT,
            ("Hardware", ["hersteller", "modell", "prozessor", "kerne_threads", "ram",
                          "festplatte", "betriebssystem", "displaygroesse", "dockingstation"]),
            ("Verwaltung", ["status", "verwaltungsart", "verwendungsart", "mac_adresse",
                            "garantie", "anschaffungsdatum", "installationsdatum",
                            "anlagenummer"]),
            BEMERKUNG,
        ],
        auswahl={"verwendungsart": ["Dienstlaptop", "Teamslaptop", "Laborlaptop"]},
        ohne_leer=("verwendungsart",),
    ),
    Typ(
        slug="standpc", assettyp="Stand-PC", titel="Stand-PCs", einzahl="Stand-PC", icon="🖥️",
        gruppen=[
            ("Allgemein", ["rechnername", "inventarnummer", "seriennummer", "benutzer"]),
            STANDORT,
            ("Hardware", ["hersteller", "modell", "prozessor", "kerne_threads", "ram",
                          "festplatte", "betriebssystem"]),
            ("Verwaltung", ["status", "verwaltungsart", "verwendungsart", "mac_adresse",
                            "garantie", "anschaffungsdatum", "installationsdatum",
                            "anlagenummer"]),
            BEMERKUNG,
        ],
        auswahl={"verwendungsart": ["Arbeits-PC", "Hörsaal-PC", "Labor-PC"]},
        ohne_leer=("verwendungsart",),
    ),
]}