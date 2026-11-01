from contextlib import closing

from datenbank import verbinden
from funktionen_historie import historie_schreiben

# Formularfeld -> Spalte in der Tabelle assets
FORMULAR_SPALTEN = {
    "inventarnummer": "inventarnummer",
    "rechnername": "rechnername",
    "seriennummer": "seriennummer",
    "benutzer": "mitarbeiter",
    "standort": "standort",
    "zimmer": "zimmer",
    "kostenstelle": "kostenstelle",
    "organisationseinheit": "organisationseinheit",
    "hersteller": "hersteller",
    "modell": "modell",
    "prozessor": "prozessor",
    "kerne_threads": "kerne_threads",
    "ram": "ram",
    "festplatte": "festplatte",
    "betriebssystem": "betriebssystem",
    "verwaltungsart": "verwaltungsart",
    "verwendungsart": "verwendungsart",
    "status": "status",
    "mac_adresse": "mac_adresse",
    "garantie": "garantie",
    "anschaffungsdatum": "anschaffungsdatum",
    "installationsdatum": "installationsdatum",
    "anlagenummer": "anlagenummer",
    "displaygroesse": "displaygroesse",
    "dockingstation": "dockingstation",
    "druckertyp": "druckertyp",
    "arbeitsplatz": "arbeitsplatz",
    "bemerkung": "bemerkung",
}


def asset_suchen_sqlite(id):
    with closing(verbinden()) as verbindung:
        return verbindung.execute(
            "SELECT * FROM assets WHERE id = ?", (id,)
        ).fetchone()


def asset_existiert_sqlite(inventarnummer, rechnername, mac_adresse):
    pruefungen = [
        ("Inventarnummer", "inventarnummer", inventarnummer),
        ("Rechnername", "rechnername", rechnername),
        ("MAC-Adresse", "mac_adresse", mac_adresse),
    ]

    with closing(verbinden()) as verbindung:
        for name, spalte, wert in pruefungen:
            if not wert:
                continue
            if verbindung.execute(
                f"SELECT 1 FROM assets WHERE {spalte} = ? LIMIT 1", (wert,)
            ).fetchone():
                return name
    return None


def neues_asset_erstellen_sqlite(werte):
    spalten = {**FORMULAR_SPALTEN, "assettyp": "assettyp"}
    gesendet = {f: s for f, s in spalten.items() if f in werte}

    spaltenliste = ", ".join(gesendet.values())
    platzhalter = ", ".join("?" for _ in gesendet)
    parameter = [werte[f] for f in gesendet]

    with closing(verbinden()) as verbindung:
        verbindung.execute(
            f"INSERT INTO assets ({spaltenliste}) VALUES ({platzhalter})",
            parameter
        )
        verbindung.commit()

    historie_schreiben("Asset", f"Asset {werte.get('inventarnummer', '')} angelegt")


def asset_speichern_popup_sqlite(asset_id, werte):
    gesendet = {f: s for f, s in FORMULAR_SPALTEN.items() if f in werte}
    if not gesendet:
        return False

    setteil = ", ".join(f"{spalte} = ?" for spalte in gesendet.values())
    parameter = [werte[feld] for feld in gesendet] + [asset_id]

    with closing(verbinden()) as verbindung:
        if "inventarnummer" in gesendet:
            neue_nr = werte["inventarnummer"].strip()
            if not neue_nr:
                return "leer"
            if verbindung.execute(
                "SELECT 1 FROM assets WHERE inventarnummer = ? AND id != ? LIMIT 1",
                (neue_nr, asset_id)
            ).fetchone():
                return "doppelt"

        cursor = verbindung.execute(
            f"UPDATE assets SET {setteil} WHERE id = ?", parameter
        )
        if cursor.rowcount == 0:
            return False
        verbindung.commit()

        zeile = verbindung.execute(
            "SELECT inventarnummer FROM assets WHERE id = ?", (asset_id,)
        ).fetchone()
        inventarnummer = zeile[0] if zeile else asset_id

    historie_schreiben("Asset", f"Asset {inventarnummer} bearbeitet")
    return True


def asset_zuweisen_sqlite(inventarnummer, uaccountid):
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT mitarbeiter FROM assets WHERE LOWER(inventarnummer) = LOWER(?)",
            (inventarnummer,)
        ).fetchone()

        if zeile is None:
            return "nicht_gefunden"
        if (zeile[0] or "").strip():
            return "besetzt"

        verbindung.execute(
            "UPDATE assets SET mitarbeiter = ?, status = 'Ausgegeben' "
            "WHERE LOWER(inventarnummer) = LOWER(?)",
            (uaccountid, inventarnummer)
        )
        verbindung.commit()

    historie_schreiben("Asset", f"Asset {inventarnummer} an {uaccountid} vergeben")
    return "erfolg"


def asset_freigeben_sqlite(inventarnummer):
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT mitarbeiter, status FROM assets "
            "WHERE LOWER(inventarnummer) = LOWER(?)",
            (inventarnummer,)
        ).fetchone()

        if zeile is None:
            return "nicht_gefunden"

        vergeben = (zeile[0] or "").strip() or (zeile[1] or "").lower() == "ausgegeben"
        if not vergeben:
            return "nicht_vergeben"

        verbindung.execute(
            "UPDATE assets SET mitarbeiter = NULL, status = 'Lager' "
            "WHERE LOWER(inventarnummer) = LOWER(?)",
            (inventarnummer,)
        )
        verbindung.commit()

    historie_schreiben("Asset", f"Asset {inventarnummer} freigegeben")
    return "erfolg"


def assets_loeschen_sqlite(id):
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT inventarnummer FROM assets WHERE id = ?", (id,)
        ).fetchone()
        if zeile is None:
            return False

        verbindung.execute("DELETE FROM assets WHERE id = ?", (id,))
        verbindung.commit()

    historie_schreiben("Asset", f"Asset {zeile[0]} gelöscht")
    return True