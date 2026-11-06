def test_ohne_login_wird_umgeleitet(anonym):
    antwort = anonym.get("/liste/maus")
    assert antwort.status_code == 302
    assert "/login" in antwort.headers["Location"]


def test_leser_darf_lesen(leser):
    assert leser.get("/liste/maus").status_code == 200


def test_leser_darf_nicht_loeschen(leser):
    antwort = leser.post("/asset/loeschen", data={"id": "1"})
    assert antwort.status_code == 403


def test_leser_darf_nicht_anlegen(leser):
    antwort = leser.post("/asset/anlegen_popup", data={"inventarnummer": "X-1"})
    assert antwort.status_code == 403

def test_fremde_herkunft_wird_abgelehnt(admin):
    antwort = admin.post(
        "/asset/anlegen_popup",
        data={"assettyp": "Maus", "inventarnummer": "X-1", "anschaffungsdatum": "2024-05-01"},
        headers={"Sec-Fetch-Site": "cross-site", "Origin": "http://boese.example"},
    )
    assert antwort.get_json()["status"] == "fehler"