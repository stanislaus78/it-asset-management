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

    fetch(url, { method: "POST", body: daten })
    .then(response => response.json().catch(() => ({
        status: "fehler",
        meldung: "Server antwortete mit Status " + response.status
    })))
    .then(data => {
        popupSchliessen();
        if (data.status === "fehler") {
            alert("⚠️ " + data.meldung);
            return;
        }
        window.location.href = location.pathname + "?geloescht=1";
    })
    .catch(fehler => {
        console.error(fehler);
        alert("⚠️ Löschen fehlgeschlagen: " + fehler.message);
    });
}
let STATUS_WERTE = [];

if (!location.pathname.startsWith("/mitarbeiter")) {

    fetch("/asset/status_json")
        .then(response => response.json())
        .then(liste => { STATUS_WERTE = liste; });

    function statusOptionen(aktuell) {
        const alle = (aktuell && !STATUS_WERTE.includes(aktuell))
            ? [aktuell, ...STATUS_WERTE] : STATUS_WERTE;
        return `<option value=""></option>` + alle.map(w =>
            `<option value="${esc(w)}" ${w === aktuell ? "selected" : ""}>${esc(w)}</option>`
        ).join("");
    }

    function statusAlsAuswahl(feld) {
        const neu = feld.id.startsWith("neu_");
        const auswahl = document.createElement("select");
        auswahl.id = feld.id;
        auswahl.innerHTML = statusOptionen(neu ? (feld.value || "Lager") : feld.value);
        feld.replaceWith(auswahl);
    }

    new MutationObserver(() => {
        ["neu_status", "edit_status"].forEach(id => {
            const feld = document.getElementById(id);
            if (feld && feld.tagName === "INPUT") statusAlsAuswahl(feld);
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


fetch("/rolle_json")
    .then(r => r.json())
    .then(d => {
        if (d.rolle === "leser") {
            ["bearbeitenBtn", "loeschenBtn"].forEach(id => {
                const knopf = document.getElementById(id);
                if (knopf) knopf.style.display = "none";
            });
            document.querySelectorAll(".toolbar button").forEach(b => {
                if (b.textContent.includes("anlegen")) b.style.display = "none";
            });
        }
    });