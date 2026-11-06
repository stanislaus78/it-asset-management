import io

from openpyxl import Workbook

from conftest import abfrage


def excel(kopf, *zeilen):
    mappe = Workbook()
    mappe.active.append(kopf)
    for z in zeilen:
        mappe.active.append(z)
    puffer = io.BytesIO()
    mappe.save(puffer)
    puffer.seek(0)
    return puffer


def hochladen(client, art, datei, probelauf=False, name="liste.xlsx"):
    daten = {"datei": (datei, name)}
    if probelauf:
        daten["probelauf"] = "1"
    return client.post(f"/administration/import/{art}", data=daten,
                       content_type="multipart/form-data")


MA_KOPF = ["uaccountid", "vorname", "nachname", "standort"]
AS_KOPF = ["inventarnummer", "assettyp", "anschaffungsdatum", "status"]


def anzahl(tabelle):
    return abfrage(f"SELECT COUNT(*) FROM {tabelle}")[0][0]


def test_mitarbeiter_import(admin):
    hochladen(admin, "mitarbeiter", excel(MA_KOPF,
              ("u111", "Max", "Muster", "ZLB"), ("u222", "Eva", "Test", "SSC")))
    assert anzahl("mitarbeiter") == 2


def test_probelauf_speichert_nichts(admin):
    hochladen(admin, "mitarbeiter", excel(MA_KOPF, ("u111", "Max", "Muster", "ZLB")),
              probelauf=True)
    assert anzahl("mitarbeiter") == 0


def test_ein_fehler_stoppt_alles(admin):
    hochladen(admin, "mitarbeiter", excel(MA_KOPF,
              ("u111", "Max", "Muster", "ZLB"),
              ("u222", "Eva", "Test", "GibtEsNicht")))
    assert anzahl("mitarbeiter") == 0


def test_vorhandene_werden_uebersprungen(admin, neuer_mitarbeiter):
    neuer_mitarbeiter("u111")
    hochladen(admin, "mitarbeiter", excel(MA_KOPF,
              ("u111", "Max", "Muster", "ZLB"), ("u222", "Eva", "Test", "SSC")))
    assert anzahl("mitarbeiter") == 2


def test_assets_import_mit_deutschem_datum(admin):
    hochladen(admin, "assets", excel(AS_KOPF, ("LPT-1", "Laptop", "04.11.2026", "")))
    zeile = abfrage("SELECT anschaffungsdatum, status FROM assets WHERE inventarnummer='LPT-1'")[0]
    assert zeile == ("2026-11-04", "Lager")


def test_assets_unbekannter_typ_stoppt_alles(admin):
    hochladen(admin, "assets", excel(AS_KOPF,
              ("LPT-1", "Laptop", "2024-05-01", ""), ("X-1", "Raumschiff", "2024-05-01", "")))
    assert anzahl("assets") == 0


def test_assets_doppelte_in_datei_stoppen_alles(admin):
    hochladen(admin, "assets", excel(AS_KOPF,
              ("LPT-1", "Laptop", "2024-05-01", ""), ("LPT-1", "Laptop", "2024-05-01", "")))
    assert anzahl("assets") == 0


def test_assets_benutzer_muss_existieren(admin):
    hochladen(admin, "assets", excel(AS_KOPF + ["mitarbeiter"],
              ("LPT-1", "Laptop", "2024-05-01", "", "gibtesnicht")))
    assert anzahl("assets") == 0


def test_falsches_dateiformat(admin):
    antwort = hochladen(admin, "assets", io.BytesIO(b"abc"), name="liste.csv")
    assert ".xlsx" in antwort.get_data(as_text=True)


def test_pflichtspalte_fehlt(admin):
    antwort = hochladen(admin, "assets", excel(["inventarnummer"], ("LPT-1",)))
    assert "fehlen" in antwort.get_data(as_text=True)
    assert anzahl("assets") == 0


def test_leser_darf_nicht_importieren(leser):
    antwort = hochladen(leser, "mitarbeiter", excel(MA_KOPF, ("u111", "Max", "Muster", "ZLB")))
    assert antwort.status_code == 403
    assert anzahl("mitarbeiter") == 0