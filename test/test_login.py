from conftest import abfrage


def anmelden(client, name="anna", passwort="geheim123", **extra):
    return client.post("/login", data={"benutzer": name, "passwort": passwort, **extra})


def test_login_erfolgreich(anonym):
    antwort = anmelden(anonym)
    assert antwort.status_code == 302
    assert anonym.get("/assets").status_code == 200


def test_login_gross_klein_egal(anonym):
    assert anmelden(anonym, name="ANNA").status_code == 302


def test_falsches_passwort(anonym):
    antwort = anmelden(anonym, passwort="falsch")
    assert antwort.status_code == 200
    assert "falsch" in antwort.get_data(as_text=True)
    assert anonym.get("/assets").status_code == 302


def test_unbekannter_benutzer_gleiche_meldung(anonym):
    antwort = anmelden(anonym, name="gibtesnicht", passwort="x")
    assert "Benutzername oder Passwort ist falsch" in antwort.get_data(as_text=True)


def test_sperre_nach_fuenf_fehlversuchen(anonym):
    for _ in range(5):
        anmelden(anonym, passwort="falsch")
    antwort = anmelden(anonym)   # jetzt sogar mit richtigem Passwort
    assert "Zu viele" in antwort.get_data(as_text=True)
    assert anonym.get("/assets").status_code == 302


def test_erfolg_loescht_fehlversuche(anonym):
    for _ in range(3):
        anmelden(anonym, passwort="falsch")
    assert anmelden(anonym).status_code == 302
    assert abfrage("SELECT COUNT(*) FROM login_versuche")[0][0] == 0


def test_weiterleitung_nur_auf_eigene_seiten(anonym):
    antwort = anmelden(anonym, next="//boese.example")
    assert "boese" not in antwort.headers["Location"]


def test_logout(anonym):
    anmelden(anonym)
    anonym.get("/logout")
    assert anonym.get("/assets").status_code == 302