from contextlib import closing
from datetime import datetime

from flask import has_request_context, session

from datenbank import verbinden


def historie_schreiben(typ, aktion):
    if has_request_context() and session.get("benutzer"):
        aktion = f"{aktion} (von {session['benutzer']})"
    with closing(verbinden()) as verbindung:
        verbindung.execute(
            "INSERT INTO historie (datum, typ, aktion) VALUES (?, ?, ?)",
            (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), typ, aktion)
        )
        verbindung.commit()


def historie_anzeigen():
    with closing(verbinden()) as verbindung:
        print(verbindung.execute("SELECT * FROM historie").fetchall())