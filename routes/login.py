import time
from contextlib import closing

from flask import Blueprint, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from datenbank import verbinden
from funktionen_historie import historie_schreiben

bp = Blueprint("login", __name__)

# Hash für einen Fantasie-Benutzer: so dauert die Prüfung immer gleich lang
LEER_HASH = ("scrypt:32768:8:1$leer$"
             "0000000000000000000000000000000000000000000000000000000000000000"
             "0000000000000000000000000000000000000000000000000000000000000000")

FENSTER_SEKUNDEN = 15 * 60
MAX_PRO_NAME_UND_IP = 5
MAX_PRO_IP = 20


def sicheres_ziel(ziel):
    if ziel and ziel.startswith("/") and not ziel.startswith("//"):
        return ziel
    return "/"


def sperre_rest(verbindung, name, ip):
    """Gibt die verbleibenden Sekunden der Sperre zurück, 0 wenn keine besteht."""
    jetzt = time.time()
    verbindung.execute("DELETE FROM login_versuche WHERE zeit < ?",
                       (jetzt - FENSTER_SEKUNDEN,))

    regeln = (
        ("SELECT zeit FROM login_versuche "
         "WHERE LOWER(name) = LOWER(?) AND ip = ? ORDER BY zeit",
         (name, ip), MAX_PRO_NAME_UND_IP),
        ("SELECT zeit FROM login_versuche WHERE ip = ? ORDER BY zeit",
         (ip,), MAX_PRO_IP),
    )

    rest = 0
    for sql, parameter, maximum in regeln:
        zeiten = [z[0] for z in verbindung.execute(sql, parameter)]
        if len(zeiten) >= maximum:
            # die Sperre endet, sobald genug alte Versuche aus dem Zeitfenster fallen
            freigabe = zeiten[len(zeiten) - maximum] + FENSTER_SEKUNDEN
            rest = max(rest, int(freigabe - jetzt) + 1)
    return rest


@bp.route("/login", methods=["GET", "POST"])
def login():
    fehler = None
    ziel = request.values.get("next", "")

    if request.method == "POST":
        name = request.form.get("benutzer", "").strip()[:50]
        passwort = request.form.get("passwort", "")
        ip = request.remote_addr or ""
        konto = None
        neu_gesperrt = False

        with closing(verbinden()) as verbindung:
            rest = sperre_rest(verbindung, name, ip)

            if not rest:
                zeile = verbindung.execute(
                    "SELECT passwort_hash, rolle, name FROM benutzer "
                    "WHERE LOWER(name) = LOWER(?)", (name,)
                ).fetchone()
                gueltig = check_password_hash(zeile[0] if zeile else LEER_HASH, passwort)

                if zeile and gueltig:
                    konto = (zeile[2], zeile[1])
                    verbindung.execute(
                        "DELETE FROM login_versuche WHERE LOWER(name) = LOWER(?) AND ip = ?",
                        (name, ip))
                else:
                    verbindung.execute(
                        "INSERT INTO login_versuche (name, ip, zeit) VALUES (?, ?, ?)",
                        (name, ip, time.time()))
                    rest = sperre_rest(verbindung, name, ip)
                    neu_gesperrt = rest > 0
                    fehler = "Benutzername oder Passwort ist falsch."

            verbindung.commit()

        if konto:
            session.clear()
            session["eingeloggt"] = True
            session["benutzer"], session["rolle"] = konto
            return redirect(sicheres_ziel(ziel))

        if rest:
            minuten = max(1, round(rest / 60))
            fehler = ("Zu viele fehlgeschlagene Anmeldungen. "
                      f"Bitte in etwa {minuten} Minuten erneut versuchen.")

        if neu_gesperrt:
            historie_schreiben(
                "Anmeldung",
                f"Anmeldung für '{name}' von {ip} nach zu vielen Fehlversuchen gesperrt")

    return render_template("login.html", fehler=fehler, ziel=ziel)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")