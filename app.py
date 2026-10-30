import re
import sqlite3
from contextlib import closing
from urllib.parse import urlparse

from flask import Flask, render_template, request, session, redirect

from datenbank import (
    assets_tabelle_anlegen, mitarbeiter_tabelle_anlegen,
    historie_tabelle_anlegen, verbinden,
)
from funktionen_assets import (
    neues_asset_erstellen_sqlite, asset_freigeben_sqlite,
    assets_loeschen_sqlite, asset_zuweisen_sqlite, asset_suchen_sqlite,
    asset_speichern_popup_sqlite, asset_existiert_sqlite,
)
from funktionen_mitarbeiter import (
    mitarbeiter_anlegen_sqlite, mitarbeiter_loeschen_sqlite,
)

app = Flask(__name__)
app.secret_key = "fratelowsky_geheim"

@app.route("/")
def startseite():
    if not session.get("eingeloggt"):
        return redirect("/login")

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("SELECT COUNT(*) FROM assets")
    assets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM mitarbeiter")
    mitarbeiter = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE status = 'Ausgegeben'
    """)
    ausgegeben = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM assets
        WHERE status = 'Lager'
    """)
    lager = cursor.fetchone()[0]

    verbindung.close()

    return render_template(
        "startseite.html",
        assets=assets,
        mitarbeiter=mitarbeiter,
        ausgegeben=ausgegeben,
        lager=lager
    )

@app.route("/login")
def login():

    benutzer = request.args.get("benutzer")
    passwort = request.args.get("passwort")

    if benutzer == "admin" and passwort == "1234":

        session["eingeloggt"] = True

        return redirect("/")

    return """
    <h1>Login</h1>

    <form>

        Benutzer:<br>
        <input type="text" name="benutzer"><br><br>

        Passwort:<br>
        <input type="password" name="passwort"><br><br>

        <button>Anmelden</button>

    </form>
    """

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/assets")
def assets_dashboard():
    return render_template("asset_dashboard.html")


@app.route("/suche")
def suche():
    return render_template("suche.html")


@app.route("/infos")
def infos():
    return render_template("infos.html")


@app.route("/asset/anlegen")
def asset_anlegen():

    return render_template(
        "asset_anlegen.html"
    )

import re

def mac_normalisieren(mac):
    hex_only = re.sub(r"[^0-9A-Fa-f]", "", mac or "")
    if len(hex_only) != 12:
        return None  # ungültig
    hex_only = hex_only.upper()
    return ":".join(hex_only[i:i+2] for i in range(0, 12, 2))

def mitarbeiter_pruefen(benutzer):
    """Gibt die U-AccountID (so wie in der Datenbank geschrieben) zurück oder None."""
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT uaccountid FROM mitarbeiter WHERE LOWER(uaccountid) = LOWER(?)",
            (benutzer,)
        ).fetchone()
    return zeile[0] if zeile else None


@app.route("/asset/anlegen_popup", methods=["POST"])
def asset_anlegen_popup():

    inventarnummer = request.form.get("inventarnummer", "").strip()

    if not inventarnummer:
        return {"status": "fehler", "meldung": "Inventarnummer fehlt."}

    # MAC-Adresse: leer erlaubt, sonst muss sie gültig sein
    mac_roh = request.form.get("mac_adresse", "").strip()
    if request.form.get("druckertyp") == "Lokal":
        mac_roh = ""
    mac = ""
    if mac_roh:
        mac = mac_normalisieren(mac_roh)
        if mac is None:
            return {"status": "fehler", "meldung": "MAC-Adresse ist ungültig."}

    vorhanden = asset_existiert_sqlite(
        inventarnummer,
        request.form.get("rechnername", "").strip(),
        mac
    )

    if vorhanden:
        return {"status": "fehler", "meldung": f"{vorhanden} existiert bereits."}

    # request.form ist unveränderlich, daher Kopie mit normalisierter MAC
    daten = request.form.copy()
    daten["mac_adresse"] = mac

    benutzer = request.form.get("benutzer", "").strip()
    if benutzer:
        gefunden = mitarbeiter_pruefen(benutzer)
        if gefunden is None:
            return {"status": "fehler",
                    "meldung": f"Mitarbeiter '{benutzer}' existiert nicht. "
                               "Bitte zuerst unter Mitarbeiter anlegen."}
        daten["benutzer"] = gefunden
    try:
        neues_asset_erstellen_sqlite(daten)
    except sqlite3.Error as fehler:
        return {"status": "fehler", "meldung": f"Datenbankfehler: {fehler}"}

    return {"status": "ok"}


@app.route("/asset/bearbeiten/<id>")
def asset_bearbeiten(id):

    asset = asset_suchen_sqlite(id)

    return render_template(
        "asset_bearbeiten.html",
        asset=asset
    )

@app.route("/asset/speichern", methods=["POST"])
def asset_speichern():

    daten = request.form.copy()

    if "benutzer" in daten:
        benutzer = daten["benutzer"].strip()
        aktuell = asset_suchen_sqlite(daten["id"])
        alter_wert = (aktuell[26] or "") if aktuell else ""

        # unverändert gelassene Altwerte (z. B. "Vranesevic") nicht blockieren
        if benutzer and benutzer != alter_wert:
            gefunden = mitarbeiter_pruefen(benutzer)
            if gefunden is None:
                return {"status": "fehler",
                        "meldung": f"Mitarbeiter '{benutzer}' existiert nicht."}
            daten["benutzer"] = gefunden

    ergebnis = asset_speichern_popup_sqlite(daten["id"], daten)

    if ergebnis == "doppelt":
        return {"status": "fehler", "meldung": "Diese Inventarnummer existiert bereits."}
    if ergebnis == "leer":
        return {"status": "fehler", "meldung": "Inventarnummer darf nicht leer sein."}
    if not ergebnis:
        return {"status": "fehler", "meldung": "Asset nicht gefunden (ID ungültig)"}

    return {"status": "ok"}

from flask import redirect



from urllib.parse import urlparse

@app.route("/asset/loeschen")
def assets_loeschen():

    id = request.args.get("id")

    assets_loeschen_sqlite(id)

    ziel = urlparse(request.referrer or "/assets").path

    return redirect(ziel + "?geloescht=1")

@app.route("/asset/loeschen/bestaetigen")
def asset_loeschen_bestaetigen():

    id = request.args.get("id")

    assets_loeschen_sqlite(id)

    return f"""
    <h1>✅ Asset gelöscht</h1>

    Asset {id} wurde gelöscht.
    """


@app.route("/asset/zuweisen")
def assets_zuweisen():

    inventarnummer = request.args.get("inventarnummer")
    mitarbeiter = request.args.get("mitarbeiter")

    if inventarnummer and mitarbeiter:

        ergebnis = asset_zuweisen_sqlite(
            inventarnummer,
            mitarbeiter
        )

        return render_template(
            "asset_zuweisen.html",
            ergebnis=ergebnis,
            inventarnummer=inventarnummer,
            mitarbeiter=mitarbeiter
        )

    return render_template(
        "asset_zuweisen.html",
        ergebnis=""
    )


@app.route("/asset/freigeben")
def assets_freigeben():

    inventarnummer = request.args.get("inventarnummer")

    if inventarnummer:

        asset_freigeben_sqlite(inventarnummer)

        return f"""
        <h1>Asset freigegeben</h1>

        Asset {inventarnummer} wurde freigegeben.<br><br>

        <p><a href="/assets/freigeben">Neues Asset freigeben</a></p>
        <p><a href="/assets">Zurück zu Assets</a></p>
        """

    return """
    <h1>Asset freigeben</h1>

    <form>

        Inventarnummer:<br>
        <input type="text" name="inventarnummer"><br><br>

        <button>Freigeben</button>

    </form>

    <p><a href="/assets">Zurück zu Assets</a></p>
    """

@app.route("/asset/anzeigen")
def assets_anzeigen():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
        SELECT *
        FROM assets
    """)

    assets = cursor.fetchall()
    print(assets)

    verbindung.close()

    return render_template(
        "assets_anzeigen.html",
        assets=assets
    )

@app.route("/asset/details_json/<id>")
def asset_details_json(id):

    asset = asset_suchen_sqlite(id)

    if asset is None:
        return {"status": "fehler", "meldung": "Asset nicht gefunden"}, 404
    # Laptop, der auf diese Dockingstation verweist
    laptop = None
    if (asset[10] or "").lower() == "dockingstation":
        verbindung = sqlite3.connect("asset_management.db")
        try:
            cursor = verbindung.cursor()
            cursor.execute(
                """
                SELECT inventarnummer
                FROM assets
                WHERE dockingstation = ?
                  AND LOWER(assettyp) = 'laptop'
                """,
                (asset[1],)
            )
            laptop = ", ".join(z[0] for z in cursor.fetchall() if z[0])
        finally:
            verbindung.close()



    return {
        "id": asset[0],
        "inventarnummer": asset[1],
        "rechnername": asset[2],
        "seriennummer": asset[3],
        "kostenstelle": asset[4],
        "organisationseinheit": asset[5],
        "standort": asset[6],
        "zimmer": asset[7],
        "anschaffungsdatum": asset[8],
        "installationsdatum": asset[9],
        "assettyp": asset[10],
        "verwendungsart": asset[11],
        "status": asset[12],
        "hersteller": asset[13],
        "modell": asset[14],
        "mac_adresse": asset[15],
        "garantie": asset[16],
        "verwaltungsart": asset[17],
        "prozessor": asset[18],
        "kerne_threads": asset[19],
        "ram": asset[20],
        "festplatte": asset[21],
        "betriebssystem": asset[22],
        "displaygroesse": asset[23],
        "dockingstation": asset[24],
        "anlagenummer": asset[25],
        "benutzer": asset[26],
        "bemerkung": asset[27],
        "druckertyp": asset[28],
        "laptop": laptop
    }



@app.route("/asset/details/<inventarnummer>")
def asset_details(inventarnummer):

    asset = asset_suchen_sqlite(inventarnummer)

    return render_template(
        "asset_details.html",
        asset=asset
    )


#Mitarbeiter

import sqlite3
from contextlib import closing
from datenbank import verbinden
from funktionen_mitarbeiter import (
    mitarbeiter_anlegen_sqlite, mitarbeiter_loeschen_sqlite
)

MITARBEITER_SORT = {
    "vorname": "vorname", "nachname": "nachname", "uaccountid": "uaccountid",
    "organisationseinheit": "organisationseinheit", "standort": "standort",
    "zimmer": "zimmer", "arbeitsplatz": "arbeitsplatz",
    "kostenstelle": "kostenstelle", "status": "status", "bemerkung": "bemerkung",
}

MITARBEITER_FELDER = [
    "vorname", "nachname", "uaccountid", "organisationseinheit", "standort",
    "zimmer", "arbeitsplatz", "kostenstelle", "status", "bemerkung",
]

def einheit_schluessel(wert):
    ziffern = re.sub(r"\D", "", wert or "")
    return ziffern if ziffern else (wert or "").strip().upper()


ORGANISATIONSEINHEITEN = ["A600", "A601", "A602", "A603", "A736"]


@app.route("/mitarbeiter")
def mitarbeiter_start():
    with closing(verbinden()) as verbindung:
        eintraege = [z[0] for z in verbindung.execute(
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

@app.route("/mitarbeiter/anzeigen")
def mitarbeiter_liste():
    spalte = MITARBEITER_SORT.get(request.args.get("sort"), "nachname")
    richtung = request.args.get("richtung", "ASC")
    if richtung not in ("ASC", "DESC"):
        richtung = "ASC"

    einheit = request.args.get("einheit", "")

    sql = f"""
        SELECT id, vorname, nachname, uaccountid, organisationseinheit,
               standort, zimmer, arbeitsplatz, kostenstelle, status, bemerkung
        FROM mitarbeiter
        ORDER BY {spalte} COLLATE NOCASE {richtung}
    """

    with closing(verbinden()) as verbindung:
        zeilen = verbindung.execute(sql).fetchall()

    if einheit:
        gesucht = einheit_schluessel(einheit)
        zeilen = [z for z in zeilen if einheit_schluessel(z[4]) == gesucht]

    return render_template("mitarbeiter.html", mitarbeiter=zeilen)


@app.route("/mitarbeiter/details_json/<int:id>")
def mitarbeiter_details_json(id):
    with closing(verbinden()) as verbindung:
        verbindung.row_factory = sqlite3.Row
        zeile = verbindung.execute(
            "SELECT * FROM mitarbeiter WHERE id = ?", (id,)
        ).fetchone()
    if zeile is None:
        return {"status": "fehler", "meldung": "Mitarbeiter nicht gefunden"}, 404
    return dict(zeile)


@app.route("/mitarbeiter/anlegen", methods=["POST"])
def mitarbeiter_anlegen():
    werte = {f: request.form.get(f, "").strip() for f in MITARBEITER_FELDER}
    if not werte["uaccountid"]:
        return {"status": "fehler", "meldung": "U-AccountID fehlt."}
    if mitarbeiter_anlegen_sqlite(**werte) == "doppelt":
        return {"status": "fehler", "meldung": "Diese U-AccountID existiert bereits."}
    return {"status": "ok"}


@app.route("/mitarbeiter/speichern", methods=["POST"])
def mitarbeiter_speichern():
    mid = request.form.get("id")
    werte = {f: request.form.get(f, "").strip() for f in MITARBEITER_FELDER}
    if not werte["uaccountid"]:
        return {"status": "fehler", "meldung": "U-AccountID darf nicht leer sein."}

    setteil = ", ".join(f"{f} = ?" for f in MITARBEITER_FELDER)
    try:
        with closing(verbinden()) as verbindung:
            cur = verbindung.execute(
                f"UPDATE mitarbeiter SET {setteil} WHERE id = ?",
                [werte[f] for f in MITARBEITER_FELDER] + [mid],
            )
            verbindung.commit()
    except sqlite3.IntegrityError:
        return {"status": "fehler", "meldung": "Diese U-AccountID existiert bereits."}

    if cur.rowcount == 0:
        return {"status": "fehler", "meldung": "Mitarbeiter nicht gefunden."}
    return {"status": "ok"}


@app.route("/mitarbeiter/loeschen", methods=["POST"])
def mitarbeiter_loeschen():
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT uaccountid FROM mitarbeiter WHERE id = ?",
            (request.form.get("id"),)
        ).fetchone()
    if zeile is None:
        return {"status": "fehler", "meldung": "Mitarbeiter nicht gefunden."}
    if not mitarbeiter_loeschen_sqlite(zeile[0]):
        return {"status": "fehler",
                "meldung": "Mitarbeiter hat noch Assets und kann nicht gelöscht werden."}
    return {"status": "ok"}

@app.route("/mitarbeiter/auswahl_json")
def mitarbeiter_auswahl_json():
    with closing(verbinden()) as verbindung:
        zeilen = verbindung.execute(
            "SELECT uaccountid, vorname, nachname FROM mitarbeiter ORDER BY nachname"
        ).fetchall()
    return [{"uaccountid": u, "name": f"{v} {n}"} for u, v, n in zeilen]


#Infos
@app.route("/info/statistik")
def info_statistik():
    with closing(verbinden()) as verbindung:
        def zahl(sql):
            return verbindung.execute(sql).fetchone()[0]

        gesamt = zahl("SELECT COUNT(*) FROM assets")
        mitarbeiter = zahl("SELECT COUNT(*) FROM mitarbeiter")
        ausgegeben = zahl("SELECT COUNT(*) FROM assets WHERE status = 'Ausgegeben'")
        lager = zahl("SELECT COUNT(*) FROM assets WHERE LOWER(TRIM(status)) = 'lager'")
        sonstige = gesamt - ausgegeben - lager

        pro_typ = verbindung.execute("""
            SELECT COALESCE(NULLIF(assettyp, ''), 'Ohne Typ'), COUNT(*)
            FROM assets
            GROUP BY 1
            ORDER BY 2 DESC, 1
        """).fetchall()

    kennzahlen = [
        ("📦", "Assets gesamt", gesamt),
        ("👤", "Mitarbeiter", mitarbeiter),
        ("✅", "Ausgegeben", ausgegeben),
        ("🏢", "Im Lager", lager),
        ("🔧", "Sonstiger Status", sonstige),
    ]
    maximum = max((n for _, n in pro_typ), default=1)

    return render_template("statistik.html", kennzahlen=kennzahlen,
                           pro_typ=pro_typ, maximum=maximum)
def leere_spalten_entfernen(kopf, zeilen):
    if not zeilen:
        return kopf, zeilen
    behalten = [i for i in range(len(kopf))
                if any(z[i] not in (None, "") for z in zeilen)]
    return ([kopf[i] for i in behalten],
            [[z[i] for i in behalten] for z in zeilen])


@app.route("/info/lagerbestand")
def info_lagerbestand():
    typ = request.args.get("typ", "")

    typen = [z[0] for z in abfragen(
        "SELECT DISTINCT assettyp FROM assets "
        "WHERE status = 'Lager' AND assettyp IS NOT NULL AND assettyp != '' "
        "ORDER BY assettyp"
    )]

    kopf, zeilen, hinweis = [], [], None

    if typ:
        sql = ASSET_SQL + " WHERE status = 'Lager'"
        parameter = ()
        if typ != "ALLE":
            sql += " AND assettyp = ?"
            parameter = (typ,)
        sql += " ORDER BY assettyp, inventarnummer"

        zeilen = abfragen(sql, parameter)
        kopf, zeilen = leere_spalten_entfernen(ASSET_KOPF, zeilen)
        hinweis = f"Anzahl Assets im Lager: {len(zeilen)}"

    return render_template("info_seite.html",
                           titel="📦 Lagerbestand",
                           hinweis=hinweis, kopf=kopf, zeilen=zeilen,
                           typen=typen, typ=typ)

@app.route("/info/geraetetypen")
def info_geraetetypen():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
        SELECT geraetetyp, COUNT(*)
        FROM assets
        GROUP BY assettyp
    """)

    ergebnisse = cursor.fetchall()

    verbindung.close()

    ausgabe = """
    <h1>📊 Gerätetypen</h1>

    <table border="1">

        <tr>
            <th>Assettyp</th>
            <th>Anzahl</th>
        </tr>
    """

    for g in ergebnisse:

        ausgabe += f"""
        <tr>
            <td>{g[0]}</td>
            <td>{g[1]}</td>
        </tr>
        """

    ausgabe += """
    </table>

    <br>

    <p><a href="/infos">Zurück zu Infos</a></p>  """

    return ausgabe

#Startseite Dashboard


#Suche
STANDORTE_LISTE = ["ZLB", "AECC", "SSC", "SVP", "Büro des Zentrums"]

ASSET_SPALTEN = [
    ("inventarnummer", "Inventarnummer"), ("rechnername", "Rechnername"),
    ("seriennummer", "Seriennummer"), ("assettyp", "Typ"),
    ("verwendungsart", "Verwendungsart"), ("hersteller", "Hersteller"),
    ("modell", "Modell"), ("druckertyp", "Druckertyp"),
    ("status", "Status"), ("mitarbeiter", "Benutzer"),
    ("standort", "Standort"), ("zimmer", "Zimmer"),
    ("kostenstelle", "Kostenstelle"), ("organisationseinheit", "Organisationseinheit"),
    ("anschaffungsdatum", "Anschaffungsdatum"), ("installationsdatum", "Installationsdatum"),
    ("garantie", "Garantie"), ("verwaltungsart", "Verwaltungsart"),
    ("mac_adresse", "MAC-Adresse"), ("prozessor", "Prozessor"),
    ("kerne_threads", "Kerne/Threads"), ("ram", "RAM"),
    ("festplatte", "Festplatte"), ("betriebssystem", "Betriebssystem"),
    ("displaygroesse", "Displaygröße"), ("dockingstation", "Dockingstation"),
    ("anlagenummer", "Anlagenummer"), ("bemerkung", "Bemerkung"),
]

ASSET_KOPF = [label for _, label in ASSET_SPALTEN]
ASSET_SQL = "SELECT " + ", ".join(s for s, _ in ASSET_SPALTEN) + " FROM assets"
EINHEIT_INDEX = [s for s, _ in ASSET_SPALTEN].index("organisationseinheit")


def suche_seite(titel, platzhalter, kopf, zeilen, q, auswahl=None):
    # Spalten ausblenden, die bei allen Treffern leer sind
    if zeilen:
        behalten = [i for i in range(len(kopf))
                    if any(z[i] not in (None, "") for z in zeilen)]
        kopf = [kopf[i] for i in behalten]
        zeilen = [[z[i] for i in behalten] for z in zeilen]

    return render_template("suche_seite.html", titel=titel, platzhalter=platzhalter,
                           kopf=kopf, zeilen=zeilen, q=q, auswahl=auswahl)



def abfragen(sql, parameter=()):
    with closing(verbinden()) as verbindung:
        return verbindung.execute(sql, parameter).fetchall()

def suchbegriff():
    return (request.args.get("q") or "").strip()


@app.route("/suche/asset")
def suche_asset():
    q = suchbegriff()
    zeilen = []
    if q:
        m = f"%{q}%"
        zeilen = abfragen(
            ASSET_SQL + " WHERE inventarnummer LIKE ? OR seriennummer LIKE ? "
                        "OR rechnername LIKE ? ORDER BY inventarnummer LIMIT 200",
            (m, m, m))
    return suche_seite("🔍 Asset suchen",
                       "Inventarnummer, Seriennummer oder Rechnername",
                       ASSET_KOPF, zeilen, q)


@app.route("/suche/hersteller")
def suche_hersteller():
    q = suchbegriff()
    zeilen = []
    if q:
        zeilen = abfragen(
            ASSET_SQL + " WHERE hersteller LIKE ? ORDER BY assettyp, inventarnummer LIMIT 200",
            (f"%{q}%",))
    return suche_seite("🏭 Nach Hersteller suchen", "z. B. Dell, Lenovo",
                       ASSET_KOPF, zeilen, q)


@app.route("/suche/standort")
def suche_standort():
    q = suchbegriff()
    zeilen = []
    if q:
        zeilen = abfragen(
            ASSET_SQL + " WHERE standort = ? ORDER BY assettyp, inventarnummer LIMIT 200",
            (q,))
    return suche_seite("📍 Nach Standort suchen", "", ASSET_KOPF, zeilen, q,
                       auswahl=STANDORTE_LISTE)


@app.route("/suche/organisationseinheit")
def suche_organisationseinheit():
    q = suchbegriff()
    zeilen = []
    if q:
        alle = abfragen(
            ASSET_SQL + " WHERE organisationseinheit IS NOT NULL "
                        "AND organisationseinheit != '' ORDER BY assettyp, inventarnummer")
        gesucht = einheit_schluessel(q)
        zeilen = [z for z in alle if einheit_schluessel(z[EINHEIT_INDEX]) == gesucht]
    return suche_seite("🏢 Nach Organisationseinheit suchen", "", ASSET_KOPF, zeilen, q,
                       auswahl=ORGANISATIONSEINHEITEN)


@app.route("/suche/mitarbeiter")
def suche_mitarbeiter():
    q = suchbegriff()
    zeilen = []
    if q:
        m = f"%{q}%"
        zeilen = abfragen("""
            SELECT vorname || ' ' || nachname, uaccountid, organisationseinheit,
                   standort, zimmer
            FROM mitarbeiter
            WHERE vorname LIKE ? OR nachname LIKE ? OR uaccountid LIKE ?
            ORDER BY nachname LIMIT 200
        """, (m, m, m))
    return suche_seite("👤 Nach Mitarbeiter suchen", "Name oder U-AccountID",
                       ["Name", "U-AccountID", "Organisationseinheit", "Standort", "Zimmer"],
                       zeilen, q)


@app.route("/suche/assets-mitarbeiter")
def suche_assets_mitarbeiter():
    q = suchbegriff()
    zeilen = []
    if q:
        zeilen = abfragen(
            ASSET_SQL + " WHERE mitarbeiter LIKE ? ORDER BY assettyp, inventarnummer LIMIT 200",
            (f"%{q}%",))
    return suche_seite("🎒 Assets eines Mitarbeiters", "Name oder U-AccountID",
                       ASSET_KOPF, zeilen, q)



#Historie

@app.route("/historie")
def historie():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
        SELECT datum, typ, aktion
        FROM historie
        ORDER BY id DESC
    """)

    eintraege = cursor.fetchall()

    verbindung.close()

    return render_template(
        "historie.html",
        eintraege=eintraege
    )


#Asset_neu

@app.route("/assets/rechner")
def rechner():

    return render_template("rechner.html")

@app.route("/assets/mobile")
def mobile():

    return render_template("mobile.html")

@app.route("/assets/peripherie")
def peripherie():

    return render_template("peripherie.html")

@app.route("/assets/medientechnik")
def medientechnik():

    return render_template("medientechnik.html")





ZUBEHOER_SORT_SPALTEN = {
    "inventarnummer": "inventarnummer",
    "seriennummer": "seriennummer",
    "mitarbeiter": "mitarbeiter",
    "standort": "standort",
    "zimmer": "zimmer",
    "kostenstelle": "kostenstelle",
    "organisationseinheit": "organisationseinheit",
    "hersteller": "hersteller",
    "modell": "modell",
    "geraetetyp": "verwendungsart",
    "status": "status",
    "anschaffungsdatum": "anschaffungsdatum",
    "bemerkung": "bemerkung",
}

@app.route("/assets/zubehoer")
def zubehoer():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    spalte = ZUBEHOER_SORT_SPALTEN.get(sortierung, "inventarnummer")
    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, verwendungsart,
                   status, anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'zubehoer'
            ORDER BY {spalte} COLLATE NOCASE {richtung}
        """)
        zubehoerliste = cursor.fetchall()

    return render_template("zubehoer.html", zubehoerliste=zubehoerliste)



#Rechner
@app.route("/assets/laptop")
def laptops():
    sortierung = request.args.get("sort", "rechnername")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [

        "inventarnummer",
        "rechnername",
        "seriennummer",

        "kostenstelle",
        "organisationseinheit",

        "standort",
        "zimmer",

        "anschaffungsdatum",
        "installationsdatum",

        "assettyp",
        "verwendungsart",

        "status",

        "hersteller",
        "modell",

        "mac_adresse",
        "garantie",

        "verwaltungsart",

        "prozessor",
        "kerne_threads",

        "ram",
        "festplatte",

        "betriebssystem",

        "displaygroesse",
        "dockingstation",

        "anlagenummer",

        "mitarbeiter",

        "bemerkung"

    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "rechnername"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute(f"""
           SELECT *
           FROM assets
           WHERE LOWER(assettyp) = 'laptop'
           ORDER BY {sortierung} {richtung}
       """)

    laptops = cursor.fetchall()

    print(laptops)
    verbindung.close()
    return render_template(
        "laptops.html",
        laptops=laptops
    )

@app.route("/assets/standpc")
def standpcs():

    sortierung = request.args.get("sort", "rechnername")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [

        "inventarnummer",
        "rechnername",
        "seriennummer",

        "kostenstelle",
        "organisationseinheit",

        "standort",
        "zimmer",

        "anschaffungsdatum",
        "installationsdatum",

        "assettyp",
        "verwendungsart",

        "status",

        "hersteller",
        "modell",

        "mac_adresse",
        "garantie",

        "verwaltungsart",

        "prozessor",
        "kerne_threads",

        "ram",
        "festplatte",

        "betriebssystem",

        "displaygroesse",
        "dockingstation",

        "anlagenummer",

        "mitarbeiter",

        "bemerkung"

    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "rechnername"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute(f"""
        SELECT *
        FROM assets
        WHERE LOWER(assettyp) = 'stand-pc'
        ORDER BY {sortierung} {richtung}
    """)

    standpcs = cursor.fetchall()

    print(standpcs)
    verbindung.close()
    return render_template(
        "standpc.html",
        standpcs=standpcs
    )


TABLET_SORT_SPALTEN = {
    "inventarnummer": "t.inventarnummer",
    "seriennummer": "t.seriennummer",
    "mitarbeiter": "t.mitarbeiter",
    "standort": "t.standort",
    "zimmer": "t.zimmer",
    "kostenstelle": "t.kostenstelle",
    "organisationseinheit": "t.organisationseinheit",
    "hersteller": "t.hersteller",
    "modell": "t.modell",
    "displaygroesse": "t.displaygroesse",
    "ram": "t.ram",
    "festplatte": "t.festplatte",
    "mac_adresse": "t.mac_adresse",
    "status": "t.status",
    "garantie": "t.garantie",
    "anschaffungsdatum": "t.anschaffungsdatum",
    "bemerkung": "t.bemerkung",
}

@app.route("/assets/tablet")
def tablets():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    spalte = TABLET_SORT_SPALTEN.get(sortierung, "t.inventarnummer")
    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(f"""
            SELECT t.id, t.inventarnummer, t.seriennummer, t.mitarbeiter,
                   t.standort, t.zimmer, t.kostenstelle, t.organisationseinheit,
                   t.hersteller, t.modell,  t.displaygroesse, t.ram, t.festplatte,
                   t.mac_adresse,
                   t.status, t.garantie, t.anschaffungsdatum, t.bemerkung
            FROM assets t
            WHERE LOWER(t.assettyp) = 'tablet'
            ORDER BY {spalte} COLLATE NOCASE {richtung}
        """)
        tabletliste = cursor.fetchall()

    return render_template("tablets.html", tablets=tabletliste)







HANDY_SORT_SPALTEN = {
    "inventarnummer": "h.inventarnummer",
    "seriennummer": "h.seriennummer",
    "mitarbeiter": "h.mitarbeiter",
    "standort": "h.standort",
    "zimmer": "h.zimmer",
    "kostenstelle": "h.kostenstelle",
    "organisationseinheit": "h.organisationseinheit",
    "hersteller": "h.hersteller",
    "modell": "h.modell",
    "displaygroesse": "h.displaygroesse",
    "ram": "h.ram",
    "festplatte": "h.festplatte",
    "mac_adresse": "h.mac_adresse",
    "status": "h.status",
    "garantie": "h.garantie",
    "anschaffungsdatum": "h.anschaffungsdatum",
    "bemerkung": "h.bemerkung",
}

@app.route("/assets/diensthandy")
def diensthandys():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    spalte = HANDY_SORT_SPALTEN.get(sortierung, "h.inventarnummer")
    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(f"""
            SELECT h.id, h.inventarnummer, h.seriennummer, h.mitarbeiter,
                   h.standort, h.zimmer, h.kostenstelle, h.organisationseinheit,
                   h.hersteller, h.modell,  h.displaygroesse, h.ram, h.festplatte,
                   h.mac_adresse,
                   h.status, h.garantie, h.anschaffungsdatum, h.bemerkung
            FROM assets h
            WHERE LOWER(h.assettyp) = 'diensthandy'
            ORDER BY {spalte} COLLATE NOCASE {richtung}
        """)
        diensthandys = cursor.fetchall()

    return render_template("diensthandys.html", diensthandys=diensthandys)




@app.route("/assets/monitor")
def monitore():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "displaygroesse",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute(f"""
        SELECT *
        FROM assets
        WHERE LOWER(assettyp) = 'monitor'
        ORDER BY {sortierung} {richtung}
    """)

    monitore = cursor.fetchall()
    verbindung.close()

    return render_template(
        "monitore.html",
        monitore=monitore
    )

DRUCKER_SORT_SPALTEN = {
    "inventarnummer": "d.inventarnummer",
    "seriennummer": "d.seriennummer",
    "mitarbeiter": "d.mitarbeiter",
    "standort": "d.standort",
    "zimmer": "d.zimmer",
    "kostenstelle": "d.kostenstelle",
    "organisationseinheit": "d.organisationseinheit",
    "hersteller": "d.hersteller",
    "modell": "d.modell",
    "druckertyp": "d.druckertyp",
    "mac_adresse": "d.mac_adresse",
    "status": "d.status",
    "garantie": "d.garantie",
    "anschaffungsdatum": "d.anschaffungsdatum",
    "bemerkung": "d.bemerkung",
}

@app.route("/assets/drucker")
def drucker():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    spalte = DRUCKER_SORT_SPALTEN.get(sortierung, "d.inventarnummer")
    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(f"""
            SELECT d.id, d.inventarnummer, d.seriennummer, d.mitarbeiter,
                   d.standort, d.zimmer, d.kostenstelle, d.organisationseinheit,
                   d.hersteller, d.modell, d.druckertyp, d.mac_adresse,
                   d.status, d.garantie, d.anschaffungsdatum, d.bemerkung
            FROM assets d
            WHERE LOWER(d.assettyp) = 'drucker'
            ORDER BY {spalte} COLLATE NOCASE {richtung}
        """)
        druckerliste = cursor.fetchall()

    return render_template("drucker.html", druckerliste=druckerliste)



@app.route("/test")
def test():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("PRAGMA table_info(assets)")

    return str(cursor.fetchall())


DOCKING_SORT_SPALTEN = {
    "inventarnummer": "d.inventarnummer",
    "seriennummer": "d.seriennummer",
    "mitarbeiter": "d.mitarbeiter",
    "standort": "d.standort",
    "zimmer": "d.zimmer",
    "kostenstelle": "d.kostenstelle",
    "organisationseinheit": "d.organisationseinheit",
    "hersteller": "d.hersteller",
    "modell": "d.modell",
    "mac_adresse": "d.mac_adresse",      # NEU
    "laptop": "laptop",                  # Alias aus dem SELECT
    "status": "d.status",
    "garantie": "d.garantie",
    "anschaffungsdatum": "d.anschaffungsdatum",
    "bemerkung": "d.bemerkung",
}

@app.route("/assets/dockingstation")
def dockingstations():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    spalte = DOCKING_SORT_SPALTEN.get(sortierung, "d.inventarnummer")
    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()
        cursor.execute(f"""
            SELECT d.id, d.inventarnummer, d.seriennummer, d.mitarbeiter,
                   d.standort, d.zimmer, d.kostenstelle, d.organisationseinheit,
                   d.hersteller, d.modell, d.mac_adresse,
                   (SELECT GROUP_CONCAT(l.inventarnummer, ', ')
                      FROM assets l
                     WHERE l.dockingstation = d.inventarnummer
                       AND LOWER(l.assettyp) = 'laptop') AS laptop,
                   d.status, d.garantie, d.anschaffungsdatum, d.bemerkung
            FROM assets d
            WHERE LOWER(d.assettyp) = 'dockingstation'
            ORDER BY {spalte} COLLATE NOCASE {richtung}
        """)
        dockingstations = cursor.fetchall()

    return render_template("dockingstations.html",
                           dockingstations=dockingstations)


@app.route("/assets/scanner")
def scanner():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, status,
                   anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'scanner'
            ORDER BY {sortierung} COLLATE NOCASE {richtung}
        """)

        scanners = cursor.fetchall()

    return render_template(
        "scanner.html",
        scanners=scanners
    )




@app.route("/assets/maus")
def maeuse():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute(f"""
        SELECT id, inventarnummer, seriennummer, mitarbeiter,
               standort, zimmer, kostenstelle, organisationseinheit,
               hersteller, modell, status,
               anschaffungsdatum, bemerkung
        FROM assets
        WHERE LOWER(assettyp) = 'maus'
        ORDER BY {sortierung} COLLATE NOCASE {richtung}
    """)

    maeuse = cursor.fetchall()
    verbindung.close()

    return render_template(
        "maeuse.html",
        maeuse=maeuse
    )

@app.route("/assets/kopfhoerer")
def kopfhoerer():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute(f"""
        SELECT id, inventarnummer, seriennummer, mitarbeiter,
               standort, zimmer, kostenstelle, organisationseinheit,
               hersteller, modell, status,
               anschaffungsdatum, bemerkung
        FROM assets
        WHERE LOWER(assettyp) = 'kopfhoerer'
        ORDER BY {sortierung} COLLATE NOCASE {richtung}
    """)

    kopfhoerern = cursor.fetchall()
    verbindung.close()

    return render_template(
        "kopfhoerer.html",
        kopfhoerern=kopfhoerern
    )

@app.route("/assets/switch")
def switches():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute(f"""
        SELECT id, inventarnummer, seriennummer,
               standort, zimmer, kostenstelle, organisationseinheit,
               hersteller, modell, verwendungsart, status,
               anschaffungsdatum, bemerkung
        FROM assets
        WHERE LOWER(assettyp) = 'switch'
        ORDER BY {sortierung} COLLATE NOCASE {richtung}
    """)

    switches = cursor.fetchall()
    verbindung.close()

    return render_template(
        "switch.html",
        switches=switches
    )

@app.route("/assets/webcams")
def webcams():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, status,
                   anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'webcam'
            ORDER BY {sortierung} COLLATE NOCASE {richtung}
        """)

        webcams = cursor.fetchall()

    return render_template(
        "webcams.html",
        webcams=webcams
    )


@app.route("/assets/kameras")
def kameras():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, status,
                   anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'kamera'
            ORDER BY {sortierung} COLLATE NOCASE {richtung}
        """)

        kameras = cursor.fetchall()

    return render_template(
        "kameras.html",
        kameras=kameras
    )



@app.route("/assets/mikrofons")
def mikrofons():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, status,
                   anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'mikrofon'
            ORDER BY {sortierung} COLLATE NOCASE {richtung}
        """)

        mikrofons = cursor.fetchall()

    return render_template(
        "mikrofons.html",
        mikrofons=mikrofons
    )



@app.route("/assets/konferenzkameras")
def konferenzkameras():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, status,
                   anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'konferenzkamera'
            ORDER BY {sortierung} COLLATE NOCASE {richtung}
        """)

        konferenzkameras = cursor.fetchall()

    return render_template(
        "konferenzkameras.html",
        konferenzkameras=konferenzkameras
    )




@app.route("/assets/aufnahmegeraete")
def aufnahmegeraete():

    sortierung = request.args.get("sort", "inventarnummer")
    richtung = request.args.get("richtung", "ASC")

    erlaubte_spalten = [
        "inventarnummer",
        "seriennummer",
        "kostenstelle",
        "organisationseinheit",
        "standort",
        "zimmer",
        "anschaffungsdatum",
        "assettyp",
        "status",
        "hersteller",
        "modell",
        "garantie",
        "mitarbeiter",
        "bemerkung"
    ]

    if sortierung not in erlaubte_spalten:
        sortierung = "inventarnummer"

    if richtung not in ["ASC", "DESC"]:
        richtung = "ASC"

    with closing(sqlite3.connect("asset_management.db")) as verbindung:
        cursor = verbindung.cursor()

        cursor.execute(f"""
            SELECT id, inventarnummer, seriennummer, mitarbeiter,
                   standort, zimmer, kostenstelle, organisationseinheit,
                   hersteller, modell, status,
                   anschaffungsdatum, bemerkung
            FROM assets
            WHERE LOWER(assettyp) = 'aufnahmegeraet'
            ORDER BY {sortierung} COLLATE NOCASE {richtung}
        """)

        aufnahmegeraete = cursor.fetchall()

    return render_template(
        "aufnahmegeraete.html",
        aufnahmegeraete=aufnahmegeraete
    )


#Liste




@app.route("/update-db")
def update_db():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
        DELETE FROM historie
        WHERE typ = 'Test';
    """)

    verbindung.commit()
    verbindung.close()

    return "test wurde  entfernt"

@app.route("/asset-test")
def asset_test():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
        SELECT *
        FROM assets
    """)

    return str(cursor.fetchall())

from funktionen_assets import asset_zuweisen_sqlite
@app.route("/test-zuweisung")
def test_zuweisung():

    asset_zuweisen_sqlite("LT001", "Peter")

    return "Test erfolgreich"


@app.route("/mitarbeiter/asset_zuweisen")
def asset_zuweisen():

    return render_template(
        "asset_zuweisen.html"
    )





#Debugggging
#print(app.url_map)
if __name__ == "__main__":
    mitarbeiter_tabelle_anlegen()
    assets_tabelle_anlegen()
    historie_tabelle_anlegen()
    app.run(debug=True)