import sqlite3
import sys
from pathlib import Path

projekt = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(projekt))

from datenbank import DB_PFAD

backups = sorted((projekt / "backups").glob("asset_management_*.db"),
                 key=lambda p: p.stat().st_mtime)
if not backups:
    sys.exit("Keine Sicherung im Ordner backups gefunden.")

if len(sys.argv) > 1:
    sicherung = projekt / "backups" / sys.argv[1]
else:
    sicherung = backups[-1]

print("Sicherung :", sicherung.name)
print("Datenbank :", DB_PFAD.name)
print()


def zaehlen(pfad):
    # nur lesend öffnen, so kann nichts verändert werden
    con = sqlite3.connect(f"file:{pfad.as_posix()}?mode=ro", uri=True)
    try:
        integritaet = con.execute("PRAGMA integrity_check").fetchone()[0]
        tabellen = [z[0] for z in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        zahlen = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                  for t in tabellen}
        return integritaet, zahlen
    finally:
        con.close()


ok_backup, zahlen_backup = zaehlen(sicherung)
ok_db, zahlen_db = zaehlen(DB_PFAD)

print(f"{'Tabelle':<14}{'Sicherung':>10}{'Datenbank':>11}")
for tabelle in sorted(set(zahlen_backup) | set(zahlen_db)):
    b = zahlen_backup.get(tabelle, "fehlt")
    d = zahlen_db.get(tabelle, "fehlt")
    print(f"{tabelle:<14}{b:>10}{d:>11}")

print()
print("Integritätsprüfung der Sicherung:", ok_backup)
if ok_backup != "ok":
    print("⚠️ Die Sicherung ist beschädigt.")
elif set(zahlen_backup) != set(zahlen_db):
    print("⚠️ Die Tabellen der Sicherung und der Datenbank unterscheiden sich.")
else:
    print("✅ Die Sicherung ist lesbar und vollständig.")
    print("Abweichende Zeilenzahlen sind normal, wenn seit der Sicherung")
    print("etwas angelegt oder gelöscht wurde.")