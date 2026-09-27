from datenbank import verbinden
from asset import Asset
import sqlite3



#from funktionen_assets import assets_laden_sqlite

# assets = assets_laden_sqlite()
#
# for asset in assets:
#
#     print(asset.inventarnummer)

verbindung = verbinden()

cursor = verbindung.cursor()
cursor.execute("""
DELETE FROM assets;
""")

verbindung.commit()

print("Alle Assets gelöscht.")

cursor.execute("SELECT * FROM assets")

print(cursor.fetchall())