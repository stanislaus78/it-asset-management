
import sqlite3
from datetime import datetime

from contextlib import closing
from datetime import datetime
from datenbank import verbinden


def historie_schreiben(typ, aktion):
    with closing(verbinden()) as verbindung:
        verbindung.execute(
            "INSERT INTO historie (datum, typ, aktion) VALUES (?, ?, ?)",
            (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), typ, aktion)
        )
        verbindung.commit()



def historie_anzeigen():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
    SELECT *
    FROM historie
    """)

    print(cursor.fetchall())

    verbindung.close()




#historie_anzeigen()