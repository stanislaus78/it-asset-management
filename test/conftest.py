import pytest

import datenbank


@pytest.fixture()
def flask_app(tmp_path, monkeypatch):
    # temporäre Datenbank statt der echten
    monkeypatch.setattr(datenbank, "DB_PFAD", tmp_path / "test.db")
    datenbank.assets_tabelle_anlegen()
    datenbank.mitarbeiter_tabelle_anlegen()
    datenbank.historie_tabelle_anlegen()

    from app import app
    app.config["TESTING"] = True
    return app


def _client(flask_app, rolle):
    client = flask_app.test_client()
    client.environ_base["HTTP_SEC_FETCH_SITE"] = "same-origin"
    client.environ_base["HTTP_ORIGIN"] = "http://localhost"
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
    return flask_app.test_client()