from contextlib import closing

from flask import Blueprint, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from datenbank import verbinden

bp = Blueprint("login", __name__)

# Hash für einen Fantasie-Benutzer: so dauert die Prüfung immer gleich lang
LEER_HASH = ("scrypt:32768:8:1$leer$"
             "0000000000000000000000000000000000000000000000000000000000000000"
             "0000000000000000000000000000000000000000000000000000000000000000")


def sicheres_ziel(ziel):
    if ziel and ziel.startswith("/") and not ziel.startswith("//"):
        return ziel
    return "/"


@bp.route("/login", methods=["GET", "POST"])
def login():
    fehler = None
    ziel = request.values.get("next", "")

    if request.method == "POST":
        name = request.form.get("benutzer", "").strip()
        passwort = request.form.get("passwort", "")

        with closing(verbinden()) as verbindung:
            zeile = verbindung.execute(
                "SELECT id, passwort_hash, rolle FROM benutzer WHERE LOWER(name) = LOWER(?)",
                (name,)
            ).fetchone()

        gueltig = check_password_hash(zeile[1] if zeile else LEER_HASH, passwort)

        if zeile and gueltig:
            session.clear()
            session["eingeloggt"] = True
            session["benutzer"] = name
            session["rolle"] = zeile[2]
            return redirect(sicheres_ziel(ziel))

        fehler = "Benutzername oder Passwort ist falsch."

    return render_template("login.html", fehler=fehler, ziel=ziel)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")