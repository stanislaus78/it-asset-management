import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datenbank import DB_PFAD

FELDER = ["anschaffungsdatum", "installationsdatum"]
FORMATE = ["%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y", "%d/%m/%Y", "%d-%m-%Y"]


def umwandeln(text):
    for muster in FORMATE:
        try:
            return datetime.strptime(text.strip(), muster).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


geaendert = 0
with sqlite3.connect(DB_PFAD) as con:
    for feld in FELDER:
        zeilen = con.execute(
            f"SELECT id, inventarnummer, {feld} FROM assets "
            f"WHERE {feld} IS NOT NULL AND TRIM({feld}) != ''"
        ).fetchall()

        for id_, inventarnummer, wert in zeilen:
            neu = umwandeln(wert)
            if neu is None:
                print(f"NICHT UMGEWANDELT: {inventarnummer} {feld} = '{wert}'")
            elif neu != wert:
                con.execute(f"UPDATE assets SET {feld} = ? WHERE id = ?", (neu, id_))
                geaendert += 1

print(f"{geaendert} Werte umgewandelt.")