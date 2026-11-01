import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# Datei: (Index von Zimmer, Index von Arbeitsplatz im Ergebnis der Route)
DATEIEN = {
    "laptops.html": (7, 29), "standpc.html": (7, 29), "monitore.html": (7, 29),
    "scanner.html": (5, 13), "maeuse.html": (5, 13), "kopfhoerer.html": (5, 13),
    "webcams.html": (5, 13), "kameras.html": (5, 13), "mikrofons.html": (5, 13),
    "konferenzkameras.html": (5, 13), "aufnahmegeraete.html": (5, 13),
    "tablets.html": (5, 18), "diensthandys.html": (5, 18),
    "drucker.html": (5, 16), "dockingstations.html": (5, 16),
    "zubehoer.html": (5, 14), "switch.html": (4, 13),
}

KOPF = '''<th class="dropdown-column">
                    Arbeitsplatz
                    <span class="dropdown-button">▼</span>
                    <div class="dropdown-menu">
                        <a href="#" class="show-filters">🔎 Filtern nach Spalte</a>
                        <a href="?sort=arbeitsplatz&richtung=ASC">↑ Nach Spalte sortieren A-Z</a>
                        <a href="?sort=arbeitsplatz&richtung=DESC">↓ Nach Spalte sortieren Z-A</a>
                    </div>
                </th>'''

FILTER = '<td><input type="text" placeholder="Arbeitsplatz"></td>'

DETAILS = '''<div>Arbeitsplatz</div>
        <div>${esc(data.arbeitsplatz) || "-"}</div>'''

BEARBEITEN = '''<tr>
    <td>Arbeitsplatz</td>
    <td><input id="edit_arbeitsplatz" value="${esc(data.arbeitsplatz) || ""}"></td>
</tr>'''


def bearbeiten(text, zimmer, arb):
    fehlt = []

    def ersetzen(name, muster, funktion, minimum=1):
        nonlocal text
        text, anzahl = re.subn(muster, funktion, text)
        if anzahl < minimum:
            fehlt.append(name)
        return anzahl

    ersetzen("Kopfzeile",
             r'<th class="dropdown-column">\s*Zimmer\s*<span class="dropdown-button">▼</span>[\s\S]*?</th>',
             lambda m: m.group(0) + "\n\n                " + KOPF)

    ersetzen("Filterzeile",
             r'<td><input type="text" placeholder="Zimmer"></td>',
             lambda m: m.group(0) + "\n            " + FILTER)

    ersetzen("Datenzeile",
             r'<td>\{\{ (\w+)\[' + str(zimmer) + r'\](?: or "")? \}\}</td>[ \t]*(?:<!--.*?-->)?',
             lambda m: m.group(0) + "\n                <td>{{ " + m.group(1)
                       + "[" + str(arb) + "] or \"\" }}</td>")

    ersetzen("Details",
             r'<div>Zimmer</div>\s*<div>\$\{esc\(data\.zimmer\) \|\| "-"\}</div>',
             lambda m: m.group(0) + "\n\n        " + DETAILS)

    ersetzen("Bearbeiten",
             r'<tr>\s*<td>Zimmer</td>\s*<td><input id="edit_zimmer"[^>]*></td>\s*</tr>',
             lambda m: m.group(0) + "\n\n" + BEARBEITEN)

    ersetzen("Anlegen-Feldliste",
             r'\["zimmer", "Zimmer"\],',
             lambda m: m.group(0) + '\n        ["arbeitsplatz", "Arbeitsplatz"],')

    listen = ersetzen("", r'(?<![\[(])"zimmer",',
                      lambda m: '"zimmer", "arbeitsplatz",', minimum=0)
    appends = ersetzen("", r'daten\.append\("zimmer",\s*document\.getElementById\("neu_zimmer"\)\.value\);',
                       lambda m: m.group(0) + '\n\n    daten.append("arbeitsplatz",\n'
                                 '        document.getElementById("neu_arbeitsplatz").value);',
                       minimum=0)
    if listen + appends < 2:
        fehlt.append("Speichern-Listen")

    return text, fehlt


schreiben = "--schreiben" in sys.argv
ok = uebersprungen = 0

for name, (zimmer, arb) in DATEIEN.items():
    pfad = TEMPLATES / name
    if not pfad.exists():
        print(f"FEHLT        {name}")
        uebersprungen += 1
        continue

    text = pfad.read_text(encoding="utf-8")
    if "arbeitsplatz" in text.lower():
        print(f"SCHON DRIN   {name}")
        continue

    neu, fehlt = bearbeiten(text, zimmer, arb)
    if fehlt:
        print(f"ÜBERSPRUNGEN {name}: nicht gefunden: {', '.join(fehlt)}")
        uebersprungen += 1
        continue

    print(f"OK           {name}")
    ok += 1
    if schreiben:
        pfad.write_text(neu, encoding="utf-8")

print(f"\n{ok} Dateien {'geändert' if schreiben else 'würden geändert'}, "
      f"{uebersprungen} übersprungen.")
if not schreiben:
    print("Probelauf. Zum Schreiben: python tools/arbeitsplatz_einfuegen.py --schreiben")