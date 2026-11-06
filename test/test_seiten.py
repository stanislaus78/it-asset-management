import pytest

from asset_typen import TYPEN


def test_alle_17_typen_vorhanden():
    erwartet = {
        "maus", "scanner", "webcam", "kamera", "mikrofon", "kopfhoerer",
        "aufnahmegeraet", "konferenzkamera", "tablet", "diensthandy", "monitor",
        "switch", "drucker", "dockingstation", "zubehoer", "laptop", "standpc",
    }
    assert erwartet == set(TYPEN)


@pytest.mark.parametrize("slug", sorted(TYPEN))
def test_liste_laedt(admin, slug):
    antwort = admin.get(f"/liste/{slug}")
    assert antwort.status_code == 200


def test_unbekannter_typ_gibt_404(admin):
    assert admin.get("/liste/gibtesnicht").status_code == 404


@pytest.mark.parametrize("pfad", ["/", "/assets", "/mitarbeiter", "/infos", "/suche"])
def test_hauptseiten_laden(admin, pfad):
    assert admin.get(pfad).status_code == 200