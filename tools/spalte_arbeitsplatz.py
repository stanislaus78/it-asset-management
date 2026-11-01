import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datenbank import DB_PFAD

with sqlite3.connect(DB_PFAD) as con:
    spalten = [z[1] for z in con.execute("PRAGMA table_info(assets)")]
    if "arbeitsplatz" in spalten:
        print("Spalte existiert schon, Position", spalten.index("arbeitsplatz"))
    else:
        con.execute("ALTER TABLE assets ADD COLUMN arbeitsplatz TEXT")
        print("Spalte angelegt, Position", len(spalten))