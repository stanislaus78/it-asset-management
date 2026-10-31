let MITARBEITER_LISTE = [];

fetch("/mitarbeiter/auswahl_json")
    .then(response => response.json())
    .then(liste => { MITARBEITER_LISTE = liste; });

function htmlEsc(text) {
    return String(text ?? "")
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function mitarbeiterOptionen(aktuell) {
    const bekannt = MITARBEITER_LISTE.some(m => m.uaccountid === aktuell);
    let html = `<option value=""></option>`;

    // alter Freitext-Wert (z. B. "Vranesevic") bleibt als Option erhalten
    if (aktuell && !bekannt) {
        html += `<option value="${htmlEsc(aktuell)}" selected>${htmlEsc(aktuell)} (nicht in Mitarbeiterliste)</option>`;
    }

    html += MITARBEITER_LISTE.map(m =>
        `<option value="${htmlEsc(m.uaccountid)}" ${m.uaccountid === aktuell ? "selected" : ""}>` +
        `${htmlEsc(m.name)} (${htmlEsc(m.uaccountid)})</option>`
    ).join("");

    return html;
}

function benutzerAlsAuswahl(id) {
    const alt = document.getElementById(id);
    if (!alt) return;
    const auswahl = document.createElement("select");
    auswahl.id = id;
    auswahl.innerHTML = mitarbeiterOptionen(alt.value);
    alt.replaceWith(auswahl);
}