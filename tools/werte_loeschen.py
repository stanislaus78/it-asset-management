from datenbank import verbinden


# def mitarbeiter_tabelle_loeschen():
#
#     verbindung = verbinden()
#     cursor = verbindung.cursor()
#
#     cursor.execute("""
#         DROP TABLE IF EXISTS mitarbeiter
#     """)
#
#     verbindung.commit()
#     verbindung.close()
#
#     print("Tabelle Mitarbeiter gelöscht")
#

verbindung = verbinden()
cursor = verbindung.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    AND name='mitarbeiter'
""")

print(cursor.fetchone())

verbindung.close()


# def mitarbeiter_tabelle_anlegen():
#
#     verbindung = verbinden()
#     cursor = verbindung.cursor()
#
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS mitarbeiter (
#
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#
#             vorname TEXT,
#             nachname TEXT,
#
#             uaccountid TEXT,
#
#             organisationseinheit TEXT,
#
#             standort TEXT,
#             zimmer TEXT,
#             arbeitsplatz TEXT,
#
#             kostenstelle TEXT,
#
#             status TEXT,
#
#             bemerkung TEXT
#
#         )
#     """)
#
#     verbindung.commit()
#     verbindung.close()
#
#     print("Tabelle Mitarbeiter erstellt")
