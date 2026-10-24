import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent.parent / "asset_management.db"
print("Datenbank:", db)

con = sqlite3.connect(db)
for zeile in con.execute("PRAGMA table_info(assets)"):
    print(zeile[0], zeile[1])
con.close()