

import sqlite3

verbindung = sqlite3.connect("asset_management.db")

cursor = verbindung.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS assets (
#     inventarnummer TEXT,
#     hersteller TEXT,
#     status TEXT,
#     geraetetyp TEXT,
#     standort TEXT,
#     zimmer TEXT,
#     organisationseinheit TEXT
# )
# """)

# cursor.execute("""
# INSERT INTO assets
# VALUES (
#     'LT001',
#     'Dell',
#     'Ausgegeben',
#     'Laptop',
#     'Zlb',
#     '308',
#     '602'
# )
# """)
#cursor.execute("SELECT * FROM assets")
cursor.execute("SELECT * FROM assets WHERE inventarnummer = 'LT001';")

# cursor.execute("""
# UPDATE assets
# SET status = 'Lager'
# WHERE inventarnummer = 'LT001';
# """)

for asset in cursor.fetchall():
    print(asset)
verbindung.commit()

print("Datensatz hinzugefügt")

verbindung.close()
