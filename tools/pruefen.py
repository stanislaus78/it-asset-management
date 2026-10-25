import sqlite3
import sys
from pathlib import Path

projekt = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(projekt))

from datenbank import mitarbeiter_tabelle_anlegen

mitarbeiter_tabelle_anlegen()

db = projekt / "asset_management.db"
print("Datenbank:", db)

con = sqlite3.connect(db)
print("Tabellen:", [z[0] for z in con.execute("SELECT name FROM sqlite_master WHERE type='table'")])

print("Spalten von mitarbeiter:")
for zeile in con.execute("PRAGMA table_info(mitarbeiter)"):
    print(" ", zeile[0], zeile[1])
con.close()



import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent.parent / "asset_management.db"

with sqlite3.connect(db) as con:
    con.row_factory = sqlite3.Row
    for z in con.execute("SELECT * FROM mitarbeiter"):
        print(dict(z))