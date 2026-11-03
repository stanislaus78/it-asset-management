import sqlite3
from contextlib import closing
from urllib.parse import urlparse
from urllib.parse import quote, urlparse
from flask import abort
from flask import Flask, render_template, request, session, redirect
from hilfen import abfragen
from datenbank import (
    assets_tabelle_anlegen, mitarbeiter_tabelle_anlegen,
    historie_tabelle_anlegen, benutzer_tabelle_anlegen,
)
import secrets
from pathlib import Path
from datenbank import (
    assets_tabelle_anlegen, mitarbeiter_tabelle_anlegen,
    historie_tabelle_anlegen, benutzer_tabelle_anlegen,
    login_versuche_tabelle_anlegen,
)
schluessel_datei = Path(__file__).resolve().parent / "secret.key"
if not schluessel_datei.exists():
    schluessel_datei.write_text(secrets.token_hex(32))

app = Flask(__name__)
app.secret_key = schluessel_datei.read_text().strip()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


from routes.suche import bp as suche_bp
app.register_blueprint(suche_bp)
from routes.infos import bp as infos_bp
app.register_blueprint(infos_bp)
from routes.administration import bp as administration_bp
app.register_blueprint(administration_bp)
from routes.mitarbeiter import bp as mitarbeiter_bp
app.register_blueprint(mitarbeiter_bp)
from routes.assets import bp as assets_bp
app.register_blueprint(assets_bp)
from routes.asset_listen import bp as asset_listen_bp
app.register_blueprint(asset_listen_bp)

from routes.login import bp as login_bp
app.register_blueprint(login_bp)
from routes.benutzer import bp as benutzer_bp
app.register_blueprint(benutzer_bp)

from routes.import_excel import bp as import_excel_bp
app.register_blueprint(import_excel_bp)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024



OFFENE_SEITEN = {"login.login", "static"}
NUR_LESEN_ERLAUBT = {"benutzer.passwort_aendern", "login.logout"}


@app.before_request
def anmeldung_pruefen():
    if request.endpoint is None or request.endpoint in OFFENE_SEITEN:
        return
    if not session.get("eingeloggt"):
        return redirect("/login?next=" + quote(request.path))
    if (session.get("rolle") == "leser"
            and request.method not in ("GET", "HEAD", "OPTIONS")
            and request.endpoint not in NUR_LESEN_ERLAUBT):
        abort(403, "Mit der Rolle „Nur lesen“ sind keine Änderungen erlaubt.")


@app.errorhandler(403)
def verboten(fehler):
    text = fehler.description
    if request.method != "GET":
        return {"status": "fehler", "meldung": text}, 403
    return (f"<h1>Kein Zugriff</h1><p>{text}</p>"
            '<p><a href="/">Zur Startseite</a></p>'), 403

@app.context_processor
def rolle_bereitstellen():
    return {"rolle": session.get("rolle")}


@app.before_request
def csrf_pruefen():
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return

    seite = request.headers.get("Sec-Fetch-Site")
    if seite is not None:
        if seite not in ("same-origin", "none"):
            abort(403, "Anfrage von einer anderen Adresse abgelehnt. "
                       "Bitte die Seite über dieselbe Adresse aufrufen.")
        return

    origin = request.headers.get("Origin")
    if origin is None or urlparse(origin).netloc != request.host:
        abort(403, "Anfrage von einer anderen Adresse abgelehnt. "
                   "Bitte die Seite über dieselbe Adresse aufrufen.")




@app.route("/")
def startseite():
    def zahl(sql):
        return abfragen(sql)[0][0]

    return render_template(
        "startseite.html",
        assets=zahl("SELECT COUNT(*) FROM assets"),
        mitarbeiter=zahl("SELECT COUNT(*) FROM mitarbeiter"),
        ausgegeben=zahl("SELECT COUNT(*) FROM assets WHERE status = 'Ausgegeben'"),
        lager=zahl("SELECT COUNT(*) FROM assets WHERE LOWER(TRIM(status)) = 'lager'"),
    )





@app.route("/rolle_json")
def rolle_json():
    return {"rolle": session.get("rolle"), "benutzer": session.get("benutzer")}



if __name__ == "__main__":
    mitarbeiter_tabelle_anlegen()
    assets_tabelle_anlegen()
    historie_tabelle_anlegen()
    benutzer_tabelle_anlegen()
    login_versuche_tabelle_anlegen()


    import os
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from backup import automatik_starten
        automatik_starten()

    app.run(debug=True)