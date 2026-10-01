from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def startseite():
    return render_template("index.html")

@app.route("/assets")
def assets():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()

    cursor.execute("SELECT * FROM assets")

    assets = cursor.fetchall()

    print(assets)  # zum Testen

    ausgabe = ""

    for a in assets:

        print(a)
        print(len(a))

        ausgabe += f"Inventarnummer: {a[0]}<br>"
        ausgabe += f"Hersteller: {a[1]}<br>"
        ausgabe += f"Status: {a[2]}<br>"
        ausgabe += f"Gerätetyp: {a[3]}<br>"
        ausgabe += f"Standort: {a[4]}<br>"
        ausgabe += f"Zimmer: {a[5]}<br>"
        ausgabe += f"Organisationseinheit: {a[6]}<br>"

        if len(a) > 7:
            ausgabe += f"Mitarbeiter: {a[7]}<br><br>"
        else:
            ausgabe += "Mitarbeiter: Nicht zugewiesen<br><br>"

    return ausgabe
@app.route("/mitarbeiter")
def mitarbeiter():

    verbindung = sqlite3.connect("asset_management.db")
    cursor = verbindung.cursor()
    cursor.execute("SELECT * FROM mitarbeiter")
    mitarbeiter_liste = cursor.fetchall()
    ausgabe = ""
    for m in mitarbeiter_liste:
        ausgabe += f"ID: {m[0]}<br>"
        ausgabe += f"Name: {m[1]}<br>"
        ausgabe += f"Abteilung: {m[2]}<br><br>"
    return ausgabe

if __name__ == "__main__":
    app.run(debug=True)