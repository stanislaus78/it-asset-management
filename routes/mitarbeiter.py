import sqlite3
from contextlib import closing
from funktionen_historie import historie_schreiben
from flask import Blueprint, render_template, request

from datenbank import verbinden
from funktionen_mitarbeiter import (
    mitarbeiter_anlegen_sqlite, mitarbeiter_loeschen_sqlite,
)
from hilfen import ORGANISATIONSEINHEITEN, abfragen, einheit_schluessel

bp = Blueprint("mitarbeiter", __name__)


MITARBEITER_SORT = {
    "vorname": "vorname", "nachname": "nachname", "uaccountid": "uaccountid",
    "organisationseinheit": "organisationseinheit", "standort": "standort",
    "zimmer": "zimmer", "arbeitsplatz": "arbeitsplatz",
    "kostenstelle": "kostenstelle", "status": "status", "bemerkung": "bemerkung",
    "anzahl_assets": "anzahl_assets",
}

MITARBEITER_FELDER = [
    "vorname", "nachname", "uaccountid", "organisationseinheit", "standort",
    "zimmer", "arbeitsplatz", "kostenstelle", "status", "bemerkung",
]


@bp.route("/mitarbeiter")
def mitarbeiter_start():
    eintraege = [z[0] for z in abfragen(
        "SELECT organisationseinheit FROM mitarbeiter "
        "WHERE organisationseinheit IS NOT NULL AND organisationseinheit != ''"
    )]

    zaehler = {}
    for e in eintraege:
        schluessel = einheit_schluessel(e)
        zaehler[schluessel] = zaehler.get(schluessel, 0) + 1

    einheiten = [(name, zaehler.get(einheit_schluessel(name), 0))
                 for name in ORGANISATIONSEINHEITEN]

    bekannt = {einheit_schluessel(n) for n in ORGANISATIONSEINHEITEN}
    for schluessel, anzahl in sorted(zaehler.items()):
        if schluessel not in bekannt:
            einheiten.append((schluessel, anzahl))

    return render_template("mitarbeiter_start.html", einheiten=einheiten)


@bp.route("/mitarbeiter/anzeigen")
def mitarbeiter_liste():
    spalte = MITARBEITER_SORT.get(request.args.get("sort"), "nachname")
    richtung = request.args.get("richtung", "ASC")
    if richtung not in ("ASC", "DESC"):
        richtung = "ASC"

    einheit = request.args.get("einheit", "")

    zeilen = abfragen(f"""
        SELECT m.id, m.vorname, m.nachname, m.uaccountid, m.organisationseinheit,
               m.standort, m.zimmer, m.arbeitsplatz, m.kostenstelle, m.status,
               m.bemerkung,
               (SELECT COUNT(*) FROM assets a
                 WHERE LOWER(TRIM(a.mitarbeiter)) = LOWER(m.uaccountid)) AS anzahl_assets
        FROM mitarbeiter m
        ORDER BY {spalte} COLLATE NOCASE {richtung}
    """)

    if einheit:
        gesucht = einheit_schluessel(einheit)
        zeilen = [z for z in zeilen if einheit_schluessel(z[4]) == gesucht]

    return render_template("mitarbeiter.html", mitarbeiter=zeilen)


@bp.route("/mitarbeiter/details_json/<int:id>")
def mitarbeiter_details_json(id):
    with closing(verbinden()) as verbindung:
        verbindung.row_factory = sqlite3.Row

        zeile = verbindung.execute(
            "SELECT * FROM mitarbeiter WHERE id = ?", (id,)
        ).fetchone()
        if zeile is None:
            return {"status": "fehler", "meldung": "Mitarbeiter nicht gefunden"}, 404

        daten = dict(zeile)
        assets = verbindung.execute("""
            SELECT inventarnummer, assettyp, hersteller, modell,
                   standort, zimmer, arbeitsplatz, status
            FROM assets
            WHERE LOWER(TRIM(mitarbeiter)) = LOWER(?)
            ORDER BY assettyp, inventarnummer
        """, (daten["uaccountid"],)).fetchall()

    daten["assets"] = [dict(a) for a in assets]
    return daten


@bp.route("/mitarbeiter/auswahl_json")
def mitarbeiter_auswahl_json():
    zeilen = abfragen(
        "SELECT uaccountid, vorname, nachname FROM mitarbeiter ORDER BY nachname"
    )
    return [{"uaccountid": u, "name": f"{v} {n}"} for u, v, n in zeilen]


@bp.route("/mitarbeiter/anlegen", methods=["POST"])
def mitarbeiter_anlegen():
    werte = {f: request.form.get(f, "").strip() for f in MITARBEITER_FELDER}
    if not werte["uaccountid"]:
        return {"status": "fehler", "meldung": "U-AccountID fehlt."}
    if mitarbeiter_anlegen_sqlite(**werte) == "doppelt":
        return {"status": "fehler", "meldung": "Diese U-AccountID existiert bereits."}
    return {"status": "ok"}


@bp.route("/mitarbeiter/speichern", methods=["POST"])
def mitarbeiter_speichern():
    mid = request.form.get("id")
    werte = {f: request.form.get(f, "").strip() for f in MITARBEITER_FELDER}
    if not werte["uaccountid"]:
        return {"status": "fehler", "meldung": "U-AccountID darf nicht leer sein."}

    setteil = ", ".join(f"{f} = ?" for f in MITARBEITER_FELDER)
    alt = None
    angepasst = 0

    try:
        with closing(verbinden()) as verbindung:
            zeile = verbindung.execute(
                "SELECT uaccountid FROM mitarbeiter WHERE id = ?", (mid,)
            ).fetchone()
            if zeile is None:
                return {"status": "fehler", "meldung": "Mitarbeiter nicht gefunden."}
            alt = zeile[0]

            verbindung.execute(
                f"UPDATE mitarbeiter SET {setteil} WHERE id = ?",
                [werte[f] for f in MITARBEITER_FELDER] + [mid],
            )

            if alt and alt != werte["uaccountid"]:
                angepasst = verbindung.execute(
                    "UPDATE assets SET mitarbeiter = ? "
                    "WHERE LOWER(TRIM(mitarbeiter)) = LOWER(?)",
                    (werte["uaccountid"], alt),
                ).rowcount
            verbindung.commit()
    except sqlite3.IntegrityError:
        return {"status": "fehler", "meldung": "Diese U-AccountID existiert bereits."}

    if alt and alt != werte["uaccountid"]:
        historie_schreiben(
            "Mitarbeiter",
            f"U-AccountID {alt} in {werte['uaccountid']} geändert "
            f"({angepasst} Assets angepasst)")
    return {"status": "ok"}

@bp.route("/mitarbeiter/loeschen", methods=["POST"])
def mitarbeiter_loeschen():
    zeile = abfragen(
        "SELECT uaccountid FROM mitarbeiter WHERE id = ?",
        (request.form.get("id"),)
    )
    if not zeile:
        return {"status": "fehler", "meldung": "Mitarbeiter nicht gefunden."}
    if not mitarbeiter_loeschen_sqlite(zeile[0][0]):
        return {"status": "fehler",
                "meldung": "Mitarbeiter hat noch Assets und kann nicht gelöscht werden."}
    return {"status": "ok"}