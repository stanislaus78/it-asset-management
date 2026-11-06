from contextlib import closing

from datenbank import verbinden


def asset_daten(**aenderung):
    daten = {
        "assettyp": "Maus",
        "inventarnummer": "MAUS-1",
        "seriennummer": "SN1",
        "status": "Lager",
        "anschaffungsdatum": "2024-05-01",
    }
    daten.update(aenderung)
    return daten


def zeile(inventarnummer):
    with closing(verbinden()) as v:
        return v.execute(
            "SELECT id, status, anschaffungsdatum FROM assets WHERE inventarnummer = ?",
            (inventarnummer,),
        ).fetchone()


def test_anlegen_speichert_in_datenbank(admin):
    antwort = admin.post("/asset/anlegen_popup", data=asset_daten())
    daten = antwort.get_json()
    assert daten["status"] != "fehler", daten
    assert zeile("MAUS-1") is not None


def test_angelegtes_asset_erscheint_in_liste(admin):
    admin.post("/asset/anlegen_popup", data=asset_daten())
    assert b"MAUS-1" in admin.get("/liste/maus").data


def test_doppelte_inventarnummer_wird_abgelehnt(admin):
    admin.post("/asset/anlegen_popup", data=asset_daten())
    antwort = admin.post("/asset/anlegen_popup", data=asset_daten())
    assert antwort.get_json()["status"] == "fehler"


def test_anschaffungsdatum_ist_pflicht(admin):
    antwort = admin.post("/asset/anlegen_popup", data=asset_daten(anschaffungsdatum=""))
    assert antwort.get_json()["status"] == "fehler"
    assert zeile("MAUS-1") is None


def test_datum_wird_als_iso_gespeichert(admin):
    admin.post("/asset/anlegen_popup", data=asset_daten(anschaffungsdatum="04.11.2026"))
    assert zeile("MAUS-1")[2] == "2026-11-04"


def test_loeschen_entfernt_asset(admin):
    admin.post("/asset/anlegen_popup", data=asset_daten())
    asset_id = zeile("MAUS-1")[0]
    antwort = admin.post("/asset/loeschen", data={"id": str(asset_id)})
    assert antwort.get_json()["status"] != "fehler"
    assert zeile("MAUS-1") is None


def test_loeschen_per_get_ist_nicht_erlaubt(admin):
    assert admin.get("/asset/loeschen?id=1").status_code == 405


def test_asset_ist_nach_typ_getrennt(admin):
    admin.post("/asset/anlegen_popup", data=asset_daten())
    assert b"MAUS-1" not in admin.get("/liste/scanner").data