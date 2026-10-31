import sqlite3
import sys
from getpass import getpass
from pathlib import Path

projekt = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(projekt))

from werkzeug.security import generate_password_hash

from datenbank import benutzer_tabelle_anlegen

benutzer_tabelle_anlegen()

name = input("Benutzername: ").strip()
passwort = getpass("Passwort (mind. 10 Zeichen): ")
wiederholung = getpass("Passwort wiederholen: ")

if not name or len(passwort) < 10 or passwort != wiederholung:
    sys.exit("Abbruch: Name leer, Passwort zu kurz oder ungleich.")

with sqlite3.connect(projekt / "asset_management.db") as con:
    con.execute(
        "INSERT INTO benutzer (name, passwort_hash, rolle) VALUES (?, ?, 'admin')",
        (name, generate_password_hash(passwort)),
    )
print("Benutzer angelegt.")