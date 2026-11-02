from contextlib import closing

from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from datenbank import verbinden
from funktionen_historie import historie_schreiben
from hilfen import ROLLEN, ROLLEN_TEXT, admin_noetig, passwort_fehler

bp = Blueprint("benutzer", __name__)


def admin_anzahl(verbindung):
    return verbindung.execute(
        "SELECT COUNT(*) FROM benutzer WHERE rolle = 'admin'"
    ).fetchone()[0]


def ist_selbst(name):
    return name.lower() == (session.get("benutzer") or "").lower()


@bp.route("/benutzer")
@admin_noetig
def benutzer_liste():
    with closing(verbinden()) as verbindung:
        zeilen = verbindung.execute(
            "SELECT id, name, rolle FROM benutzer ORDER BY LOWER(name)"
        ).fetchall()
    return render_template("benutzer.html", benutzer=zeilen, rollen=ROLLEN,
                           rollen_text=ROLLEN_TEXT)


@bp.route("/benutzer/anlegen", methods=["POST"])
@admin_noetig
def benutzer_anlegen():
    name = request.form.get("name", "").strip()
    rolle = request.form.get("rolle", "")
    fehler = passwort_fehler(request.form.get("passwort", ""),
                             request.form.get("wiederholung", ""))

    if not name or len(name) > 50:
        flash("Bitte einen Benutzernamen mit höchstens 50 Zeichen angeben.", "fehler")
    elif rolle not in ROLLEN:
        flash("Ungültige Rolle.", "fehler")
    elif fehler:
        flash(fehler, "fehler")
    else:
        with closing(verbinden()) as verbindung:
            if verbindung.execute(
                "SELECT 1 FROM benutzer WHERE LOWER(name) = LOWER(?)", (name,)
            ).fetchone():
                flash(f"Den Benutzer '{name}' gibt es schon.", "fehler")
            else:
                verbindung.execute(
                    "INSERT INTO benutzer (name, passwort_hash, rolle) VALUES (?, ?, ?)",
                    (name, generate_password_hash(request.form["passwort"]), rolle),
                )
                verbindung.commit()
                flash(f"Benutzer '{name}' angelegt.", "ok")
                historie_schreiben("Benutzer", f"Benutzer {name} angelegt ({rolle})")
    return redirect("/benutzer")


@bp.route("/benutzer/rolle", methods=["POST"])
@admin_noetig
def benutzer_rolle():
    rolle = request.form.get("rolle", "")
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT name, rolle FROM benutzer WHERE id = ?", (request.form.get("id", ""),)
        ).fetchone()

        if zeile is None or rolle not in ROLLEN:
            flash("Benutzer oder Rolle ungültig.", "fehler")
        elif zeile[1] == "admin" and rolle != "admin" and admin_anzahl(verbindung) <= 1:
            flash("Der letzte Administrator kann nicht herabgestuft werden.", "fehler")
        else:
            verbindung.execute("UPDATE benutzer SET rolle = ? WHERE id = ?",
                               (rolle, request.form["id"]))
            verbindung.commit()
            if ist_selbst(zeile[0]):
                session["rolle"] = rolle
            flash(f"Rolle von '{zeile[0]}' geändert.", "ok")
            historie_schreiben("Benutzer", f"Rolle von {zeile[0]} auf {rolle} geändert")
    return redirect("/benutzer")


@bp.route("/benutzer/passwort", methods=["POST"])
@admin_noetig
def benutzer_passwort():
    fehler = passwort_fehler(request.form.get("passwort", ""),
                             request.form.get("wiederholung", ""))
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT name FROM benutzer WHERE id = ?", (request.form.get("id", ""),)
        ).fetchone()

        if zeile is None:
            flash("Benutzer nicht gefunden.", "fehler")
        elif fehler:
            flash(fehler, "fehler")
        else:
            verbindung.execute(
                "UPDATE benutzer SET passwort_hash = ? WHERE id = ?",
                (generate_password_hash(request.form["passwort"]), request.form["id"]),
            )
            verbindung.commit()
            flash(f"Neues Passwort für '{zeile[0]}' gesetzt.", "ok")
            historie_schreiben("Benutzer", f"Passwort von {zeile[0]} zurückgesetzt")
    return redirect("/benutzer")


@bp.route("/benutzer/loeschen", methods=["POST"])
@admin_noetig
def benutzer_loeschen():
    with closing(verbinden()) as verbindung:
        zeile = verbindung.execute(
            "SELECT name, rolle FROM benutzer WHERE id = ?", (request.form.get("id", ""),)
        ).fetchone()

        if zeile is None:
            flash("Benutzer nicht gefunden.", "fehler")
        elif ist_selbst(zeile[0]):
            flash("Du kannst dich nicht selbst löschen.", "fehler")
        elif zeile[1] == "admin" and admin_anzahl(verbindung) <= 1:
            flash("Der letzte Administrator kann nicht gelöscht werden.", "fehler")
        else:
            verbindung.execute("DELETE FROM benutzer WHERE id = ?", (request.form["id"],))
            verbindung.commit()
            flash(f"Benutzer '{zeile[0]}' gelöscht.", "ok")
            historie_schreiben("Benutzer", f"Benutzer {zeile[0]} gelöscht")
    return redirect("/benutzer")


@bp.route("/passwort", methods=["GET", "POST"])
def passwort_aendern():
    if request.method == "POST":
        neu = request.form.get("neu", "")
        fehler = passwort_fehler(neu, request.form.get("wiederholung", ""))

        with closing(verbinden()) as verbindung:
            zeile = verbindung.execute(
                "SELECT id, passwort_hash FROM benutzer WHERE LOWER(name) = LOWER(?)",
                (session.get("benutzer", ""),),
            ).fetchone()

            if zeile is None or not check_password_hash(zeile[1],
                                                        request.form.get("aktuell", "")):
                flash("Das aktuelle Passwort ist falsch.", "fehler")
            elif fehler:
                flash(fehler, "fehler")
            elif check_password_hash(zeile[1], neu):
                flash("Das neue Passwort muss sich vom alten unterscheiden.", "fehler")
            else:
                verbindung.execute("UPDATE benutzer SET passwort_hash = ? WHERE id = ?",
                                   (generate_password_hash(neu), zeile[0]))
                verbindung.commit()
                flash("Passwort geändert.", "ok")
                historie_schreiben("Benutzer", "Eigenes Passwort geändert")
        return redirect("/passwort")

    return render_template("passwort.html")
