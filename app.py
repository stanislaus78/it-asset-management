from flask import Flask, render_template
import sqlite3

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
def asset_anlegen():
    return "Asset anlegen"

@app.route("/asset/bearbeiten")
def asset_bearbeiten():
    return "Asset bearbeiten"

@app.route("/asset/loeschen")
def asset_loeschen():
    return "Asset loeschen"

@app.route("/asset/zuweisen")
def asset_zuweisen():
    return "Asset zuweisen"

@app.route("/asset/freigeben")
def asset_freigeben():
    return "Asset freigeben"

@app.route("/mitarbeiter/anzeigen")
def mitarbeiter_anzeigen():
    return "Alle Mitarbeiter anzeigen"


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
    return "Nach Hersteller suchen"

@app.route("/suche/standort")
def suche_standort():
    return "Nach Standort suchen"

@app.route("/suche/organisationseinheit")
def suche_organisationseinheit():
    return "Nach Organisationseinheit suchen"

@app.route("/suche/asset")
def suche_asset():
    return "Nach Asset suchen"

@app.route("/suche/mitarbeiter")
def suche_Mitarbeiter():
    return "Nach Mitarbeiter suchen"

@app.route("/suche/assets-mitarbeiter")
def suche_assets_mitarbeiten():
    return "Assets eines Mitarbeiter anzeigen"

if __name__ == "__main__":
    app.run(debug=True)