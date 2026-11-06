import pytest
from werkzeug.security import generate_password_hash

import datenbank
from datenbank import verbinden
from contextlib import closing


@pytest.fixture()
def flask_app(tmp_path, monkeypatch):
    monkeypatch.setattr(datenbank, "DB_PFAD", tmp_path / "test.db")
    datenbank.assets_tabelle_anlegen()
    datenbank.mitarbeiter_tabelle_anlegen()
    datenbank.historie_tabelle_anlegen()

    with closing(verbinden()) as v:
        v.execute("""CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL,
            passwort_hash TEXT NOT NULL, rolle TEXT NOT NULL DEFAULT 'admin')""")
        v.execute("""CREATE TABLE IF NOT EXISTS login_versuche (
            id INTEGER PRIMARY KEY, name TEXT, ip TEXT, zeit REAL)""")
        v.execute("INSERT INTO benutzer (name, passwort_hash, rolle) VALUES (?, ?, ?)",
                  ("anna", generate_password_hash("geheim123"), "admin"))
        v.commit()

    from app import app
    app.config["TESTING"] = True
    return app


def _client(flask_app, rolle=None):
    client = flask_app.test_client()
    client.environ_base["HTTP_SEC_FETCH_SITE"] = "same-origin"
    client.environ_base["HTTP_ORIGIN"] = "http://localhost"
    if rolle:
        with client.session_transaction() as sitzung:
            sitzung["eingeloggt"] = True
            sitzung["rolle"] = rolle
            sitzung["name"] = "testuser"
            sitzung["benutzer"] = "testuser"
    return client


@pytest.fixture()
def admin(flask_app):
    return _client(flask_app, "admin")


@pytest.fixture()
def leser(flask_app):
    return _client(flask_app, "leser")


@pytest.fixture()
def anonym(flask_app):
    return _client(flask_app)


def abfrage(sql, parameter=()):
    with closing(verbinden()) as v:
        return v.execute(sql, parameter).fetchall()


@pytest.fixture()
def neuer_mitarbeiter(admin):
    def erzeugen(uaccountid="u111", **extra):
        daten = {"vorname": "Max", "nachname": "Muster", "uaccountid": uaccountid,
                 "organisationseinheit": "A600", "standort": "ZLB", "zimmer": "1",
                 "arbeitsplatz": "a", "kostenstelle": "k", "status": "", "bemerkung": ""}
        daten.update(extra)
        antwort = admin.post("/mitarbeiter/anlegen", data=daten)
        assert antwort.get_json()["status"] == "ok", antwort.get_json()
    return erzeugen


@pytest.fixture()
def neues_asset(admin):
    def erzeugen(inventarnummer="LPT-1", **extra):
        daten = {"assettyp": "Laptop", "inventarnummer": inventarnummer,
                 "status": "Lager", "anschaffungsdatum": "2024-05-01"}
        daten.update(extra)
        antwort = admin.post("/asset/anlegen_popup", data=daten)
        assert antwort.get_json()["status"] == "ok", antwort.get_json()
    return erzeugen