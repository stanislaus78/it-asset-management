from flask import Flask, render_template
import sqlite3
from flask import request
from funktionen_assets import neues_asset_erstellen_sqlite
from funktionen_assets import asset_freigeben_sqlite
from funktionen_assets import assets_bearbeiten_sqlite
from funktionen_assets import assets_loeschen_sqlite

app = Flask(__name__)

@app.route("/")
def startseite():
    return render_template("index.html")

@app.route("/assets")
def assets():
    return render_template("assets.html")

@app.route("/mitarbeiter")
def mitarbeiter():
    return render_template("mitarbeiter.html")

@app.route("/suche")
def suche():
    return render_template("suche.html")


@app.route("/infos")
def infos():
    return render_template("infos.html")



@app.route("/asset/anlegen")
def assets_anlegen():

    inventarnummer = request.args.get("inventarnummer")
    hersteller = request.args.get("hersteller")
    status = request.args.get("status")
    geraetetyp = request.args.get("geraetetyp")
    standort = request.args.get("standort")
    zimmer = request.args.get("zimmer")
    organisationseinheit = request.args.get("organisationseinheit")

    if inventarnummer:

        neues_asset_erstellen_sqlite(
            inventarnummer,
            hersteller,
            status,
            geraetetyp,
            standort,
            zimmer,
            organisationseinheit
        )

        return f"""
        <h1>Asset erfolgreich angelegt</h1>

        Inventarnummer: {inventarnummer}<br>
        Hersteller: {hersteller}<br><br>

        <p><a href="/assets/anlegen">Neues Asset anlegen</a></p>
        <p><a href="/assets">Zurück zu Assets</a></p>
        """

    return """
    <h1>Neues Asset anlegen</h1>

    <form>

        Inventarnummer:<br>
        <input type="text" name="inventarnummer"><br><br>

        Hersteller:<br>
        <input type="text" name="hersteller"><br><br>

        Status:<br>
        <input type="text" name="status"><br><br>

        Gerätetyp:<br>
        <input type="text" name="geraetetyp"><br><br>

        Standort:<br>
        <input type="text" name="standort"><br><br>

        Zimmer:<br>
        <input type="text" name="zimmer"><br><br>

        Organisationseinheit:<br>
        <input type="text" name="organisationseinheit"><br><br>

        <button>Anlegen</button>

    </form>

    <p><a href="/assets">Zurück zu Assets</a></p>
    """

@app.route("/asset/bearbeiten")
def assets_bearbeiten():

    inventarnummer = request.args.get("inventarnummer")
    hersteller = request.args.get("hersteller")

    if inventarnummer and hersteller:

        assets_bearbeiten_sqlite(
            inventarnummer,
            hersteller
        )

        return f"""
        <h1>Asset bearbeitet</h1>

        Asset {inventarnummer} wurde geändert.

        <p><a href"/assets/bearbeiten">Weiteres Asset bearbeiten</a></p>
        <p><a href="/assets">Zurück zu Assets</a></p>
        """

    return """
    <h1>Asset bearbeiten</h1>

    <form>

        Inventarnummer:<br>
        <input type="text" name="inventarnummer"><br><br>

        Neuer Hersteller:<br>
        <input type="text" name="hersteller"><br><br>

        <button>Speichern</button>

    </form>

    <p><a href="/assets">Zurück zu Assets</a></p>
    """

@app.route("/asset/loeschen")
def assets_loeschen():

    inventarnummer = request.args.get("inventarnummer")

    if inventarnummer:

        assets_loeschen_sqlite(inventarnummer)

        return f"""
        <h1>Asset gelöscht</h1>

        Asset {inventarnummer} wurde gelöscht.<br><br>

        <p><a href="/assets/loeschen">Weiteres Asset löschen</a></p>
        <p><a href="/assets">Zurück zu Assets</a></p>
        """

    return """
    <h1>Asset löschen</h1>

    <form>

        Inventarnummer:<br>
        <input type="text" name="inventarnummer"><br><br>

        <button>Löschen</button>

    </form>

    <p><a href="/assets">Zurück zu Assets</a></p>
    """

@app.route("/asset/zuweisen")
def assets_zuweisen():

    inventarnummer = request.args.get("inventarnummer")
    mitarbeiter = request.args.get("mitarbeiter")

    if inventarnummer and mitarbeiter:

        asset_zuweisen_sqlite(
            inventarnummer,
            mitarbeiter
        )

        return f"""
        <h1>Asset zugewiesen</h1>

        Asset {inventarnummer} wurde an
        {mitarbeiter} zugewiesen.

        <p><a href="/assets">Zurück zu Assets</a></p>
        """

    return """
    <h1>Asset zuweisen</h1>

    <form>

        Inventarnummer:<br>
        <input type="text" name="inventarnummer"><br><br>

        Mitarbeiter:<br>
        <input type="text" name="mitarbeiter"><br><br>

        <button>Zuweisen</button>

    </form>

    <p><a href="/assets">Zurück zu Assets</a></p>
    """

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

    verbindung.close()

    return render_template(
        "assets_anzeigen.html",
        assets=assets
    )


@app.route("/mitarbeiter/anlegen")
def mitarbeiter_anlegen():
    return "Mitarbeiter anlegen"


@app.route("/mitarbeiter/bearbeiten")
def mitarbeiter_bearbeiten():
    return "Mitarbeiter bearbeiten"


@app.route("/mitarbeiter/loeschen")
def mitarbeiter_loeschen():
    return "Mitarbeiter löschen"


@app.route("/info/statistik")
def statistik():
    return "Statistik"

@app.route("/info/lagerbestand")
def lagerbestand():
    return "Lagerbestand"

@app.route("/info/geraetetypen")
def geraetetypen():
    return "Gerätetypen"

@app.route("/suche/hersteller")
def suche_hersteller():

    hersteller = request.args.get("hersteller")

    if hersteller:

        verbindung = sqlite3.connect("asset_management.db")
        cursor = verbindung.cursor()

        cursor.execute("""
            SELECT *
            FROM assets
            WHERE LOWER(hersteller) = LOWER(?)
        """, (hersteller,))

        ergebnisse = cursor.fetchall()

        verbindung.close()

        if not ergebnisse:
            return f"""
            <h1>Keine Assets gefunden</h1>

            Hersteller '{hersteller}' wurde nicht gefunden.<br><br>

            <p><a href="/suche/hersteller">Neue Suche</a></p>
            <p><a href="/suche">Zurück zur Suche</a></p>
            """
        ausgabe = """
        <h1>Gefundene Assets</h1>

        <table border="1">
            <tr>
                <th>Inventarnummer</th>
                <th>Hersteller</th>
                <th>Status</th>
            </tr>
        """

        for a in ergebnisse:

            ausgabe += f"""
            <tr>
                <td>{a[0]}</td>
                <td>{a[1]}</td>
                <td>{a[2]}</td>
            </tr>
            """

        ausgabe += """
        </table>

        <p><a href="/suche/hersteller">Neue Suche</a></p>
        <p><a href="/">Zurück zur Suche</a></p>  
        """

        return ausgabe

    return """
    <h1>Nach Hersteller suchen</h1>

    <form>
        <input type="text" name="hersteller">
        <button>Suchen</button>
    </form>
     <p><a href="/suche">Zurück zur Suche</a></p>
    """

@app.route("/suche/standort")
def suche_standort():

    standort = request.args.get("standort")
    if standort:
        return f"Gesucht wurde: {standort}"

    return """
    <h1>Nach Standort suchen</h1>
    <form>
        <input type="text" name="standort">
        <button>Suchen</button>
    </form>
    <p>/sucheZurück zur Suche</a></p>
    """

@app.route("/suche/organisationseinheit")
def suche_organisationseinheit():

    organisationseinheit = request.args.get("organisationseinheit")
    if organisationseinheit:
        return f"Gesucht wurde: {organisationseinheit}"

    return """
    <h1>Nach Organisationseinheit suchen</h1>
    <form>
        <input type="text" name="organisationseinheit">
        <button>Suchen</button>
    </form>
    <p><a href="/suche">Zurück zur Suche</a></p>
    """

@app.route("/suche/asset")
def suche_asset():

    asset = request.args.get("asset")

    if asset:

        verbindung = sqlite3.connect("asset_management.db")
        cursor = verbindung.cursor()

        cursor.execute("""
            SELECT *
            FROM assets
            WHERE LOWER(inventarnummer) = LOWER(?)
        """, (asset,))

        ergebnis = cursor.fetchone()

        verbindung.close()

        if ergebnis:

            return f"""
            <h1>Asset gefunden</h1>

            <table border="1">

                <tr>
                    <th>Inventarnummer</th>
                    <th>Hersteller</th>
                    <th>Status</th>
                    <th>Gerätetyp</th>
                    <th>Standort</th>
                    <th>Zimmer</th>
                    <th>Organisationseinheit</th>
                    <th>Mitarbeiter</th>
                </tr>

                <tr>
                    <td>{ergebnis[0]}</td>
                    <td>{ergebnis[1]}</td>
                    <td>{ergebnis[2]}</td>
                    <td>{ergebnis[3]}</td>
                    <td>{ergebnis[4]}</td>
                    <td>{ergebnis[5]}</td>
                    <td>{ergebnis[6]}</td>
                    <td>{ergebnis[7]}</td>
                </tr>

            </table>

            <p><a href="/suche">Neue Suche</a></p>
            <p><a href="/suche">Zurück zur Suche</a></p>  
            """

        return f"""
        <h1>Asset nicht gefunden</h1>

        Asset '{asset}' wurde nicht gefunden.<br><br>

        <p><a href="/suche">Neue Suche</a></p>
        <p><a href="/suche">Zurück zur Suche</a></p>
        """

    return """
    <h1>Nach Asset suchen</h1>

    <form>

        <input type="text" name="asset">

        <button>Suchen</button>

    </form>

    <p><a href="/suche">Zurück zur Suche</a></p>
    """

@app.route("/suche/mitarbeiter")
def suche_mitarbeiter():

    mitarbeiter = request.args.get("mitarbeiter")

    if mitarbeiter:

        verbindung = sqlite3.connect("asset_management.db")
        cursor = verbindung.cursor()

        cursor.execute("""
            SELECT *
            FROM mitarbeiter
            WHERE LOWER(name) = LOWER(?)
        """, (mitarbeiter,))

        ergebnis = cursor.fetchone()

        verbindung.close()

        if ergebnis:
            return f"""
            <h1>Mitarbeiter gefunden</h1>

            <table border="1">

                <tr>
                    <th>Name</th>
                    <th>Abteilung</th>
                </tr>

                <tr>
                    <td>{ergebnis[1]}</td>
                    <td>{ergebnis[2]}</td>
                </tr>

            </table>
        
            <p><a href="/suche/mitarbeiter">Neue Suche</a></p>
            <p><a href="/suche">Zurück zur Suche</a></p>  
            """

        return f"""
        <h1>Mitarbeiter nicht gefunden</h1>

        Mitarbeiter '{mitarbeiter}' wurde nicht gefunden.<br><br>

        <p><a href="/suche/mitarbeiter">Neue Suche</a></p>
        <p><a href="/suche">Zurück zur Suche</a></p>    
        """
    return """
    
    <h1>Nach Mitarbeiter suchen</h1>
    
    <form>
        <input type="text" name="mitarbeiter">
        <button>Suchen</button>
    </form>
    <p><a href="/suche">Zurück zur Suche</a></p>
    """

@app.route("/suche/assets-mitarbeiter")
def suche_assets_mitarbeiter():

    mitarbeiter = request.args.get("mitarbeiter")
    if mitarbeiter:
        return f"Assets von {mitarbeiter} werden gesucht"

    return """
    <h1>Assets eines Mitarbeiters suchen</h1>
    <form>
        <input type="text" name="mitarbeiter">
        <button>Suchen</button>
    </form>
    <p>/sucheZurück zur Suche</a></p>
    """

@app.route("/test")
def test():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("PRAGMA table_info(assets)")

    return str(cursor.fetchall())

@app.route("/update-db")
def update_db():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("""
        ALTER TABLE assets
        ADD COLUMN mitarbeiter TEXT
    """)

    verbindung.commit()
    verbindung.close()

    return "Spalte mitarbeiter hinzugefügt"

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

if __name__ == "__main__":
    app.run(debug=True)