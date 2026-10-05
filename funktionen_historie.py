
import sqlite3
from datetime import datetime

def historie_schreiben(typ, aktion):

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    datum = datetime.now().strftime("%d.%m.%Y %H:%M")

    cursor.execute("""
        INSERT INTO historie
        (datum, typ, aktion)
        VALUES (?, ?, ?)
    """, (datum, typ, aktion))

    verbindung.commit()
    verbindung.close()



def historie_anzeigen():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
    SELECT *
    FROM historie
    """)

    print(cursor.fetchall())

    verbindung.close()




historie_anzeigen()