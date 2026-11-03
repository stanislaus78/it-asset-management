import csv
import io
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path
from hilfen import garantie_monate
from flask import Blueprint, Response, render_template
from hilfen import STATUS_WERTE
from datenbank import verbinden
from hilfen import (
    ASSET_KOPF, ASSET_SQL, ORGANISATIONSEINHEITEN, STANDORTE_LISTE,
    abfragen, admin_noetig,
)

bp = Blueprint("administration", __name__)


def csv_zelle(wert):
    if wert is None:
        return ""
    if isinstance(wert, str) and wert.startswith(("=", "+", "-", "@")):
        return "'" + wert
    return wert


def csv_antwort(dateiname, kopf, zeilen):
    puffer = io.StringIO()
    schreiber = csv.writer(puffer, delimiter=";")
    schreiber.writerow(kopf)
    for z in zeilen:
        schreiber.writerow([csv_zelle(c) for c in z])
    return Response(
        "\ufeff" + puffer.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={dateiname}"},
    )


@bp.route("/administration")
@admin_noetig
def administration():
    return render_template("administration.html")


@bp.route("/historie")
@admin_noetig
def historie():
    zeilen = abfragen(
        "SELECT datum, typ, aktion FROM historie ORDER BY id DESC LIMIT 500"
    )
    return render_template("info_seite.html",
                           titel="📜 Historie",
                           hinweis=f"Letzte {len(zeilen)} Einträge",
                           kopf=["Datum", "Typ", "Aktion"], zeilen=zeilen,
                           zurueck="/administration")


@bp.route("/administration/datenqualitaet")
@admin_noetig
def admin_datenqualitaet():
    pruefungen = []

    pruefungen.append(("Assets mit unbekanntem Benutzer",
        ["Inventarnummer", "Typ", "Benutzer"],
        abfragen("""
            SELECT inventarnummer, assettyp, mitarbeiter FROM assets
            WHERE mitarbeiter IS NOT NULL AND TRIM(mitarbeiter) != ''
              AND LOWER(TRIM(mitarbeiter)) NOT IN
                  (SELECT LOWER(uaccountid) FROM mitarbeiter WHERE uaccountid IS NOT NULL)
            ORDER BY inventarnummer
        """)))

    pruefungen.append(("Assets ohne Status",
        ["Inventarnummer", "Typ"],
        abfragen("""
            SELECT inventarnummer, assettyp FROM assets
            WHERE status IS NULL OR TRIM(status) = '' ORDER BY inventarnummer
        """)))

    pruefungen.append(("Assets ohne Standort",
        ["Inventarnummer", "Typ"],
        abfragen("""
            SELECT inventarnummer, assettyp FROM assets
            WHERE standort IS NULL OR TRIM(standort) = '' ORDER BY inventarnummer
        """)))

    pruefungen.append(("Doppelte MAC-Adressen",
        ["MAC-Adresse", "Anzahl", "Inventarnummern"],
        abfragen("""
            SELECT mac_adresse, COUNT(*), GROUP_CONCAT(inventarnummer, ', ')
            FROM assets
            WHERE mac_adresse IS NOT NULL AND mac_adresse != ''
            GROUP BY mac_adresse HAVING COUNT(*) > 1
        """)))
    pruefungen.append(("Assets ohne Anschaffungsdatum",
        ["Inventarnummer", "Typ"],
        abfragen("""
            SELECT inventarnummer, assettyp FROM assets
            WHERE anschaffungsdatum IS NULL OR TRIM(anschaffungsdatum) = ''
            ORDER BY inventarnummer
        """)))

    pruefungen.append(("Assets mit ungültigem Anschaffungsdatum",
        ["Inventarnummer", "Typ", "Anschaffungsdatum"],
        abfragen("""
            SELECT inventarnummer, assettyp, anschaffungsdatum FROM assets
            WHERE anschaffungsdatum IS NOT NULL AND TRIM(anschaffungsdatum) != ''
              AND anschaffungsdatum NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
            ORDER BY inventarnummer
        """)))
    garantien = abfragen("""
        SELECT inventarnummer, assettyp, garantie FROM assets
        WHERE garantie IS NOT NULL AND TRIM(garantie) != ''
          AND LOWER(assettyp) IN ('laptop', 'stand-pc', 'drucker',
                                  'diensthandy', 'monitor', 'tablet')
        ORDER BY inventarnummer
    """)
    pruefungen.append(("Assets mit nicht lesbarer Garantiedauer",
        ["Inventarnummer", "Typ", "Garantie"],
        [z for z in garantien if garantie_monate(z[2]) is None]))

    pruefungen.append(("Assets ohne Garantiedauer (Laptop, PC, Drucker, Handy, Monitor, Tablet)",
        ["Inventarnummer", "Typ"],
        abfragen("""
            SELECT inventarnummer, assettyp FROM assets
            WHERE (garantie IS NULL OR TRIM(garantie) = '')
              AND LOWER(assettyp) IN ('laptop', 'stand-pc', 'drucker',
                                      'diensthandy', 'monitor', 'tablet')
            ORDER BY inventarnummer
        """)))
    def nicht_in_liste(spalte, bezeichnung, liste):
        platz = ", ".join("?" for _ in liste)
        return (f"Assets mit {bezeichnung} außerhalb der Liste",
                ["Inventarnummer", "Typ", bezeichnung],
                abfragen(f"""
                    SELECT inventarnummer, assettyp, {spalte} FROM assets
                    WHERE {spalte} IS NOT NULL AND TRIM({spalte}) != ''
                      AND {spalte} NOT IN ({platz})
                    ORDER BY inventarnummer
                """, liste))

    pruefungen.append(nicht_in_liste(
        "status", "Status", STATUS_WERTE + ["Leihgerät", "Festgerät"]))
    pruefungen.append(nicht_in_liste("standort", "Standort", STANDORTE_LISTE))
    pruefungen.append(nicht_in_liste(
        "organisationseinheit", "Organisationseinheit", ORGANISATIONSEINHEITEN))

    pruefungen.append(("Assets ohne Arbeitsplatz",
        ["Inventarnummer", "Typ", "Standort", "Zimmer"],
        abfragen("""
            SELECT inventarnummer, assettyp, standort, zimmer FROM assets
            WHERE arbeitsplatz IS NULL OR TRIM(arbeitsplatz) = ''
            ORDER BY inventarnummer
        """)))
    personen = abfragen("""
        SELECT uaccountid, vorname || ' ' || nachname, organisationseinheit, standort
        FROM mitarbeiter ORDER BY nachname
    """)
    kopf_m = ["U-AccountID", "Name", "Organisationseinheit", "Standort"]

    pruefungen.append(("Mitarbeiter mit ungültiger Organisationseinheit", kopf_m,
        [z for z in personen if z[2] not in ORGANISATIONSEINHEITEN]))
    pruefungen.append(("Mitarbeiter mit ungültigem Standort", kopf_m,
        [z for z in personen if z[3] not in STANDORTE_LISTE]))

    return render_template("datenqualitaet.html", pruefungen=pruefungen)


@bp.route("/administration/export/assets")
@admin_noetig
def admin_export_assets():
    zeilen = abfragen(ASSET_SQL + " ORDER BY assettyp, inventarnummer")
    name = datetime.now().strftime("assets_%Y-%m-%d.csv")
    return csv_antwort(name, ASSET_KOPF, zeilen)


@bp.route("/administration/export/mitarbeiter")
@admin_noetig
def admin_export_mitarbeiter():
    zeilen = abfragen("""
        SELECT vorname, nachname, uaccountid, organisationseinheit, standort,
               zimmer, arbeitsplatz, kostenstelle, status, bemerkung
        FROM mitarbeiter ORDER BY nachname
    """)
    kopf = ["Vorname", "Nachname", "U-AccountID", "Organisationseinheit", "Standort",
            "Zimmer", "Arbeitsplatz", "Kostenstelle", "Status", "Bemerkung"]
    name = datetime.now().strftime("mitarbeiter_%Y-%m-%d.csv")
    return csv_antwort(name, kopf, zeilen)


@bp.route("/administration/export/backup")
@admin_noetig
def admin_backup():
    with tempfile.TemporaryDirectory() as ordner:
        ziel_pfad = Path(ordner) / "backup.db"
        with closing(verbinden()) as quelle, closing(sqlite3.connect(ziel_pfad)) as ziel:
            quelle.backup(ziel)
        daten = ziel_pfad.read_bytes()

    name = datetime.now().strftime("asset_management_%Y-%m-%d_%H%M.db")
    return Response(daten, mimetype="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={name}"})