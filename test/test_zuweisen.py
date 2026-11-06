from conftest import abfrage


def senden(client, pfad, **daten):
    """Akzeptiert POST und GET, je nach Stand der Route."""
    antwort = client.post(pfad, data=daten)
    if antwort.status_code == 405:
        antwort = client.get(pfad, query_string=daten)
    return antwort


def besitzer(inventarnummer):
    return abfrage("SELECT mitarbeiter FROM assets WHERE inventarnummer = ?",
                   (inventarnummer,))[0][0]


def test_zuweisen(admin, neuer_mitarbeiter, neues_asset):
    neuer_mitarbeiter("u111")
    neues_asset("LPT-1")
    senden(admin, "/asset/zuweisen", inventarnummer="LPT-1", mitarbeiter="u111")
    assert besitzer("LPT-1") == "u111"


def test_zuweisen_an_unbekannten_mitarbeiter(admin, neues_asset):
    neues_asset("LPT-1")
    senden(admin, "/asset/zuweisen", inventarnummer="LPT-1", mitarbeiter="gibtesnicht")
    assert not besitzer("LPT-1")


def test_besetztes_asset_wird_nicht_ueberschrieben(admin, neuer_mitarbeiter, neues_asset):
    neuer_mitarbeiter("u111")
    neuer_mitarbeiter("u222")
    neues_asset("LPT-1")
    senden(admin, "/asset/zuweisen", inventarnummer="LPT-1", mitarbeiter="u111")
    senden(admin, "/asset/zuweisen", inventarnummer="LPT-1", mitarbeiter="u222")
    assert besitzer("LPT-1") == "u111"


def test_freigeben(admin, neuer_mitarbeiter, neues_asset):
    neuer_mitarbeiter("u111")
    neues_asset("LPT-1")
    senden(admin, "/asset/zuweisen", inventarnummer="LPT-1", mitarbeiter="u111")
    senden(admin, "/asset/freigeben", inventarnummer="LPT-1")
    assert not besitzer("LPT-1")


def test_leser_darf_nicht_zuweisen(admin, leser, neuer_mitarbeiter, neues_asset):
    neuer_mitarbeiter("u111")
    neues_asset("LPT-1")
    senden(leser, "/asset/zuweisen", inventarnummer="LPT-1", mitarbeiter="u111")
    assert not besitzer("LPT-1")