import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datenbank import DB_PFAD

with sqlite3.connect(DB_PFAD) as con:
    anzahl = con.execute("DELETE FROM login_versuche").rowcount
print(f"{anzahl} Einträge gelöscht, alle Sperren aufgehoben.")