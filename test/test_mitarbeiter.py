from conftest import abfrage


def mitarbeiter_id(uaccountid):
    return abfrage("SELECT id FROM mitarbeiter WHERE uaccountid = ?", (uaccountid,))[0][0]


FELDER = {"vorname": "Max", "nachname": "Muster", "organisationseinheit": "A600",
          "standort": "ZLB", "zimmer": "1", "arbeitsplatz": "a",
          "kostenstelle": "k", "status": "", "bemerkung": ""}


def test_doppelte_uaccountid_wird_abgelehnt(admin, neuer_mitarbeiter):
    neuer_mitarbeiter("u111")
    antwort = admin.post("/mitarbeiter/anlegen", data={**FELDER, "uaccountid": "u111"})
    assert antwort.get_json()["status"] == "fehler"


def test_uaccountid_ist_pflicht(admin):
    antwort = admin.post("/mitarbeiter/anlegen", data={**FELDER, "uaccountid": ""})
    assert antwort.get_json()["status"] == "fehler"


def test_asset_braucht_existierenden_mitarbeiter(admin):
    antwort = admin.post("/asset/anlegen_popup", data={
        "assettyp": "Laptop", "inventarnummer": "LPT-1", "benutzer": "gibtesnicht",
        "anschaffungsdatum": "2024-05-01", "status": "Lager"})
    assert antwort.get_json()["status"] == "fehler"


def test_aenderung_der_uaccountid_wandert_zu_den_assets(admin, neuer_mitarbeiter, neues_asset):
    neuer_mitarbeiter("u111")
    neues_asset("LPT-1", benutzer="u111")
    antwort = admin.post("/mitarbeiter/speichern", data={
        **FELDER, "id": mitarbeiter_id("u111"), "uaccountid": "u222"})
    assert antwort.get_json()["status"] == "ok"
    assert abfrage("SELECT mitarbeiter FROM assets WHERE inventarnummer='LPT-1'")[0][0] == "u222"


def test_aenderung_auf_vorhandene_uaccountid_wird_abgelehnt(admin, neuer_mitarbeiter):
    neuer_mitarbeiter("u111")
    neuer_mitarbeiter("u222")
    antwort = admin.post("/mitarbeiter/speichern", data={
        **FELDER, "id": mitarbeiter_id("u111"), "uaccountid": "u222"})
    assert antwort.get_json()["status"] == "fehler"


def test_mitarbeiter_mit_assets_kann_nicht_geloescht_werden(admin, neuer_mitarbeiter, neues_asset):
    neuer_mitarbeiter("u111")
    neues_asset("LPT-1", benutzer="u111")
    antwort = admin.post("/mitarbeiter/loeschen", data={"id": mitarbeiter_id("u111")})
    assert antwort.get_json()["status"] == "fehler"
    assert abfrage("SELECT COUNT(*) FROM mitarbeiter")[0][0] == 1


def test_mitarbeiter_ohne_assets_wird_geloescht(admin, neuer_mitarbeiter):
    neuer_mitarbeiter("u111")
    antwort = admin.post("/mitarbeiter/loeschen", data={"id": mitarbeiter_id("u111")})
    assert antwort.get_json()["status"] == "ok"
    assert abfrage("SELECT COUNT(*) FROM mitarbeiter")[0][0] == 0