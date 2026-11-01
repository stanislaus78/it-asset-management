import sqlite3
import sys
from pathlib import Path

projekt = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(projekt))

from datenbank import DB_PFAD


def zeige(name, ok, hinweis=""):
    print(("OK       " if ok else "FEHLT    ") + name + ("  -> " + hinweis if hinweis and not ok else ""))


with sqlite3.connect(DB_PFAD) as con:
    spalten = [z[1] for z in con.execute("PRAGMA table_info(assets)")]
zeige("Datenbank: Spalte arbeitsplatz", "arbeitsplatz" in spalten,
      "python tools/spalte_arbeitsplatz.py ausführen")
if "arbeitsplatz" in spalten:
    print("          Position:", spalten.index("arbeitsplatz"), "(erwartet 29)")


def enthaelt(datei, text):
    pfad = projekt / datei
    return pfad.exists() and text in pfad.read_text(encoding="utf-8")


zeige("funktionen_assets.py", enthaelt("funktionen_assets.py", '"arbeitsplatz": "arbeitsplatz"'),
      'Eintrag in FORMULAR_SPALTEN ergänzen')
zeige("hilfen.py", enthaelt("hilfen.py", '("arbeitsplatz", "Arbeitsplatz")'),
      'Eintrag in ASSET_SPALTEN ergänzen')
zeige("routes/assets.py", enthaelt("routes/assets.py", "asset[29]"),
      '"arbeitsplatz": asset[29] in asset_details_json ergänzen')
zeige("routes/asset_listen.py", enthaelt("routes/asset_listen.py", ", arbeitsplatz"),
      "neue liste_bauen einfügen")

print()
fehlen = []
for datei in sorted((projekt / "templates").glob("*.html")):
    text = datei.read_text(encoding="utf-8")
    hat_formular = "assetAnlegen" in text
    if hat_formular and "arbeitsplatz" not in text.lower():
        fehlen.append(datei.name)

if fehlen:
    print("Vorlagen ohne Arbeitsplatz:", ", ".join(fehlen))
    print("-> python tools/arbeitsplatz_einfuegen.py --schreiben")
else:
    print("Alle Asset-Vorlagen enthalten Arbeitsplatz.")