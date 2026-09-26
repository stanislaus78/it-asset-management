import sqlite3

verbindung = sqlite3.connect("asset_management.db")

cursor = verbindung.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS assets2 (
    id INTEGER PRIMARY KEY,
    inventarnummer TEXT,
    hersteller TEXT
)
""")

# cursor.execute("""
# INSERT INTO assets2
# (inventarnummer, hersteller)
# VALUES
# ('LT001', 'Dell')
# """)
#
# cursor.execute("""
# INSERT INTO assets2
# (inventarnummer, hersteller)
# VALUES
# ('LT002', 'Lenovo')
# """)
#
# cursor.execute("""
# INSERT INTO assets2
# (inventarnummer, hersteller)
# VALUES
# ('LT003', 'HP')
# """)
#



verbindung.commit()


cursor.execute("SELECT * FROM assets2")

daten = cursor.fetchall()

print("Anzahl Datensätze:", len(daten))

for asset in daten:
    print(asset)


cursor.execute("""
CREATE TABLE IF NOT EXISTS mitarbeiter (
    id INTEGER PRIMARY KEY,
    name TEXT,
    abteilung TEXT
)
""")


cursor.execute("""
INSERT INTO mitarbeiter
(name, abteilung)
VALUES
('Stanislav', 'IT')
""")

cursor.execute("""
SELECT * FROM mitarbeiter
""")

for mitarbeiter in cursor.fetchall():
    print(mitarbeiter)

verbindung.commit()


verbindung.close()