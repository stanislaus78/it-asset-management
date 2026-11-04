function esc(text) {
    return String(text ?? "")
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Überschreibt die alte GET-Variante in allen Vorlagen (diese Datei lädt zuletzt)
function assetLoeschen() {
    const url = location.pathname.startsWith("/mitarbeiter")
        ? "/mitarbeiter/loeschen"
        : "/asset/loeschen";

    const daten = new FormData();
    daten.append("id", idZumLoeschen);

    popupSchliessen();

    fetch(url, { method: "POST", body: daten })
    .then(response => response.json().catch(() => ({
        status: "fehler",
        meldung: "Server antwortete mit Status " + response.status
    })))
    .then(data => {
        if (data.status === "fehler") {
            alert("⚠️ " + data.meldung);
            return;
        }
        const pfad = "/" + location.pathname.replace(/^\/+/, "");
        window.location.assign(pfad + "?geloescht=1");
    })
    .catch(fehler => {
        console.error(fehler);
        alert("⚠️ Löschen fehlgeschlagen: " + fehler.message);
    });
}
const AUSWAHL = { status: [], standort: [], organisationseinheit: [] };

function auswahlSchluessel(feldname, text) {
    const t = String(text || "").toLowerCase().replace(/[\s\-_.]/g, "");
    if (feldname === "organisationseinheit") {
        return t.replace(/\D/g, "") || t;
    }
    return t;
}

function auswahlOptionen(feldname, aktuell) {
    const liste = AUSWAHL[feldname];
    const treffer = liste.find(
        w => auswahlSchluessel(feldname, w) === auswahlSchluessel(feldname, aktuell));
    const gewaehlt = treffer || aktuell;
    const alle = (gewaehlt && !liste.includes(gewaehlt)) ? [gewaehlt, ...liste] : liste;
    return `<option value=""></option>` + alle.map(w =>
        `<option value="${esc(w)}" ${w === gewaehlt ? "selected" : ""}>${esc(w)}</option>`
    ).join("");
}

if (!location.pathname.startsWith("/mitarbeiter")) {

    fetch("/asset/listen_json")
        .then(response => response.ok ? response.json() : null)
        .then(daten => {
            if (!daten) return;
            Object.keys(AUSWAHL).forEach(k => {
                if (Array.isArray(daten[k])) AUSWAHL[k] = daten[k];
            });
        })
        .catch(() => {});

    function alsAuswahl(feld, feldname) {
        const neu = feld.id.startsWith("neu_");
        const vorgabe = (neu && feldname === "status") ? "Lager" : "";
        const auswahl = document.createElement("select");
        auswahl.id = feld.id;
        auswahl.innerHTML = auswahlOptionen(feldname, feld.value || vorgabe);
        feld.replaceWith(auswahl);
    }

    new MutationObserver(() => {
        Object.keys(AUSWAHL).forEach(feldname => {
            ["neu_", "edit_"].forEach(praefix => {
                const feld = document.getElementById(praefix + feldname);
                if (feld && feld.tagName === "INPUT") alsAuswahl(feld, feldname);
            });
        });
    }).observe(document.body, { childList: true, subtree: true });
}

const DATUM_IDS = [
    "neu_anschaffungsdatum", "edit_anschaffungsdatum",
    "neu_installationsdatum", "edit_installationsdatum",
];

function zuIso(text) {
    const t = (text || "").trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(t)) return t;
    const m = t.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
    return m ? `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}` : "";
}

function zuAnzeige(iso) {
    const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? `${m[3]}.${m[2]}.${m[1]}` : iso;
}

function datumsfelderUmstellen() {
    DATUM_IDS.forEach(id => {
        const feld = document.getElementById(id);
        if (feld && feld.tagName === "INPUT" && feld.type !== "date") {
            const iso = zuIso(feld.value);
            feld.type = "date";
            feld.value = iso;

            if (feld.id === "neu_anschaffungsdatum") {
                const label = feld.closest(".anlegen-feld")?.querySelector("label");
                if (label && !label.textContent.includes("*")) label.textContent += " *";

            }
        }
    });
}

function datenAnzeigen() {
    document.querySelectorAll("td, .details-grid div").forEach(el => {
        const text = el.textContent.trim();
        if (el.children.length === 0 && /^\d{4}-\d{2}-\d{2}$/.test(text)) {
            el.textContent = zuAnzeige(text);
        }
    });
}

function garantiePlatzhalter() {
    document.querySelectorAll("input").forEach(feld => {
        if (/garantie$/.test(feld.id) && !feld.placeholder) {
            feld.placeholder = "z. B. 3 Jahre";
        }
    });
}

function datumAktualisieren() {
    datumsfelderUmstellen();
    datenAnzeigen();
    garantiePlatzhalter();
}
document.addEventListener("DOMContentLoaded", datumAktualisieren);
new MutationObserver(datumAktualisieren).observe(document.body, { childList: true, subtree: true });


const ROLLEN_NAMEN = { admin: "Administrator", bearbeiter: "Bearbeiter", leser: "Nur lesen" };

function anmeldungAnzeigen(d) {
    const feld = document.createElement("div");
    feld.style.cssText =
        "position:fixed; top:8px; right:12px; z-index:1000; font-size:13px;" +
        "background:white; border:1px solid #ccc; border-radius:8px;" +
        "padding:5px 12px; box-shadow:0 1px 4px rgba(0,0,0,0.12);";
    feld.innerHTML =
        `👤 <b>${esc(d.benutzer)}</b> (${esc(ROLLEN_NAMEN[d.rolle] || d.rolle)})` +
        ` · <a href="/passwort">🔑 Passwort</a>` +
        ` · <a href="/logout">🚪 Logout</a>`;
    document.body.appendChild(feld);
}

fetch("/rolle_json")
    .then(r => r.ok ? r.json() : {})
    .then(d => {
        if (!d.benutzer) return;

        anmeldungAnzeigen(d);

        if (d.rolle === "leser") {
            ["bearbeitenBtn", "loeschenBtn"].forEach(id => {
                const knopf = document.getElementById(id);
                if (knopf) knopf.style.display = "none";
            });
            document.querySelectorAll(".toolbar button").forEach(b => {
                if (b.textContent.includes("anlegen")) b.style.display = "none";
            });
        }
    })
    .catch(() => {});
