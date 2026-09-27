from asset import Asset
from mitarbeiter import Mitarbeiter
from datenbank import verbinden
import sqlite3
verbindung = sqlite3.connect("asset_management.db")

cursor = verbindung.cursor()
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

# def mitarbeiter_csv(mitarbeiter_liste):
#     with open("mitarbeiter.csv", "w") as datei:
#         datei.write(
#             "name, abteilung "
#             "\n"
#         )
#         for user in mitarbeiter_liste:
#             zeile = (
#                 f"{user.name},"
#                 f"{user.abteilung}"
#             )
#             datei.write(zeile + "\n")

# def mitarbeiter_laden_csv():
#     mitarbeiter_liste = []
#     with open("mitarbeiter.csv", "r") as datei:
#         kopfzeile = datei.readline()
#         for zeile in datei:
#             werte = zeile.strip().split(",")
#             mitarbeiter = Mitarbeiter(
#                 werte[0],
#                 werte[1]
#             )
#             mitarbeiter_liste.append(mitarbeiter)
#     return mitarbeiter_liste


from mitarbeiter import Mitarbeiter
from datenbank import verbinden

def mitarbeiter_anlegen_sqlite():
    name = input("Name: ")
    abteilung = input("Abteilung: ")
    verbindung = verbinden()
    cursor = verbindung.cursor()

    cursor.execute(f"""
        INSERT INTO mitarbeiter
        (name, abteilung)
        VALUES
        ('{name}', '{abteilung}')
        """)
    verbindung.commit()
    verbindung.close()

    print("Mitarbeiter angelegt.")


def mitarbeiter_laden_sqlite():

    verbindung = verbinden()

    cursor = verbindung.cursor()

    cursor.execute("""
    SELECT
        name,
        abteilung
    FROM mitarbeiter
    """)

    mitarbeiter_liste = []

    for zeile in cursor.fetchall():

        mitarbeiter = Mitarbeiter(
            zeile[0],
            zeile[1]
        )

        mitarbeiter_liste.append(mitarbeiter)

    verbindung.close()

    print(f"{len(mitarbeiter_liste)} Mitarbeiter wurden geladen.")

    return mitarbeiter_liste