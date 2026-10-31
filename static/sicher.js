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
    .then(response => {
        if (!response.ok) {
            throw new Error("Server antwortete mit Status " + response.status);
        }
        return response.json();
    })
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