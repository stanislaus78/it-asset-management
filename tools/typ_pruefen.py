import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datenbank import DB_PFAD

with sqlite3.connect(DB_PFAD) as con:
    for z in con.execute("SELECT id, inventarnummer, assettyp FROM assets ORDER BY id DESC LIMIT 10"):
        print(z[0], z[1], repr(z[2]))