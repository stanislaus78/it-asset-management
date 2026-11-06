import pytest

from hilfen import datum_normalisieren, garantie_monate


@pytest.mark.parametrize("text, monate", [
    ("3", 36), ("3 Jahre", 36), ("36 Monate", 36), ("1 Jahr", 12),
])
def test_garantie_monate(text, monate):
    assert garantie_monate(text) == monate


def test_datum_deutsch_nach_iso():
    assert datum_normalisieren("04.11.2026") == "2026-11-04"


def test_datum_iso_bleibt():
    assert datum_normalisieren("2026-11-04") == "2026-11-04"