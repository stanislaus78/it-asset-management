from contextlib import closing
from datenbank import verbinden
from funktionen_historie import historie_schreiben


def mitarbeiter_suchen_sqlite(uaccountid):
    with closing(verbinden()) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(
            "SELECT * FROM mitarbeiter WHERE LOWER(uaccountid) = LOWER(?)",
            (uaccountid,)
        )
        return cursor.fetchone()


def alle_mitarbeiter_sqlite():
    with closing(verbinden()) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute("""
            SELECT id, vorname, nachname, uaccountid, organisationseinheit,
                   standort, zimmer, arbeitsplatz, kostenstelle, status, bemerkung
            FROM mitarbeiter
            ORDER BY nachname COLLATE NOCASE
        """)
        return cursor.fetchall()


def mitarbeiter_anlegen_sqlite(vorname, nachname, uaccountid, organisationseinheit,
                               standort, zimmer, arbeitsplatz, kostenstelle,
                               status, bemerkung):

    if mitarbeiter_suchen_sqlite(uaccountid):
        return "doppelt"

    with closing(verbinden()) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute("""
            INSERT INTO mitarbeiter (
                vorname, nachname, uaccountid, organisationseinheit,
                standort, zimmer, arbeitsplatz, kostenstelle,
                status, bemerkung
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vorname, nachname, uaccountid, organisationseinheit,
              standort, zimmer, arbeitsplatz, kostenstelle,
              status, bemerkung))
        verbindung.commit()

    historie_schreiben("Mitarbeiter", f"Mitarbeiter {uaccountid} angelegt")
    return True


def mitarbeiter_loeschen_sqlite(uaccountid):
    with closing(verbinden()) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(
            "SELECT 1 FROM assets WHERE mitarbeiter = ? LIMIT 1", (uaccountid,)
        )
        if cursor.fetchone():
            return False

        cursor.execute("DELETE FROM mitarbeiter WHERE uaccountid = ?", (uaccountid,))
        verbindung.commit()

    historie_schreiben("Mitarbeiter", f"Mitarbeiter {uaccountid} gelöscht")
    return True


def mitarbeiter_bearbeiten_sqlite(uaccountid, organisationseinheit):
    with closing(verbinden()) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(
            "UPDATE mitarbeiter SET organisationseinheit = ? WHERE uaccountid = ?",
            (organisationseinheit, uaccountid)
        )
        verbindung.commit()

    historie_schreiben(
        "Mitarbeiter",
        f"Mitarbeiter {uaccountid} zu {organisationseinheit} geändert"
    )
    return True