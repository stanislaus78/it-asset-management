const KONFIG = window.ASSET_KONFIG;

let ausgewaehlteId = "";
let idZumLoeschen = "";

function alleFelder() {
    return KONFIG.gruppen.flatMap(([titel, namen]) => namen);
}

function listenOptionen(liste, aktuell) {
    const alle = (aktuell && !liste.includes(aktuell)) ? [aktuell, ...liste] : liste;
    return `<option value=""></option>` + alle.map(w =>
        `<option value="${esc(w)}" ${w === aktuell ? "selected" : ""}>${esc(w)}</option>`
    ).join("");
}

function eingabeFeld(praefix, name, wert) {
    const id = `${praefix}_${name}`;
    const liste = KONFIG.auswahl[name];
    if (liste) {
        return `<select id="${id}">${listenOptionen(liste, wert || "")}</select>`;
    }
    return `<input id="${id}" value="${esc(wert)}">`;
}

function antwortLesen(response) {
    return response.json().catch(() => ({
        status: "fehler",
        meldung: "Server antwortete mit Status " + response.status
    }));
}

/* ---------- Popups ---------- */

function popupOeffnen(id) {
    idZumLoeschen = id;
    const zeile = document.querySelector(`.asset-checkbox[data-id="${id}"]`)?.closest("tr");
    const inventarnummer = zeile ? zeile.children[1].innerText.trim() : "";
    document.getElementById("popupText").innerText =
        `${KONFIG.einzahl} ${inventarnummer} wirklich löschen?`;
    document.getElementById("loeschPopup").style.display = "block";
}

function popupSchliessen() {
    document.getElementById("loeschPopup").style.display = "none";
}

function detailsSchliessen() {
    document.getElementById("detailsPopup").style.display = "none";
}

function bearbeitenSchliessen() {
    document.getElementById("bearbeitenPopup").style.display = "none";
}

function anlegenSchliessen() {
    document.getElementById("anlegenPopup").style.display = "none";
}

/* ---------- Details ---------- */

function detailsAnzeigen() {
    fetch("/asset/details_json/" + ausgewaehlteId)
    .then(response => response.json())
    .then(data => {
        const abschnitte = KONFIG.gruppen.map(([titel, namen]) => `
            <div class="details-section">
                <h3>${esc(titel)}</h3>
                <div class="details-grid">
                    ${namen.map(n => `
                        <div>${esc(KONFIG.felder[n])}</div>
                        <div>${esc(data[n]) || "-"}</div>
                    `).join("")}
                </div>
            </div>
        `).join("");

        document.getElementById("detailsText").innerHTML =
            `<div class="details-container">${abschnitte}</div>`;
        document.getElementById("detailsPopup").style.display = "block";
    });
}

/* ---------- Bearbeiten ---------- */

function assetBearbeiten() {
    fetch("/asset/details_json/" + ausgewaehlteId)
    .then(response => response.json())
    .then(data => {
        const zeilen = alleFelder().map(n => `
            <tr>
                <td>${esc(KONFIG.felder[n])}</td>
                <td>${eingabeFeld("edit", n, data[n])}</td>
            </tr>
        `).join("");

        document.getElementById("bearbeitenInhalt").innerHTML = `
            <input id="edit_id" type="hidden" value="${esc(data.id)}">
            <table class="bearbeiten-table">${zeilen}</table>
            <br>
            <button onclick="assetSpeichern()">💾 Speichern</button>
        `;

        benutzerAlsAuswahl("edit_benutzer");
        document.getElementById("bearbeitenPopup").style.display = "block";
    });
}

function assetSpeichern() {
    const daten = new FormData();
    daten.append("id", ausgewaehlteId);

    alleFelder().forEach(n => {
        const element = document.getElementById("edit_" + n);
        if (element) {
            daten.append(n, element.value);
        }
    });

    fetch("/asset/speichern", { method: "POST", body: daten })
    .then(antwortLesen)
    .then(data => {
        if (data.status === "fehler") {
            alert("⚠️ " + data.meldung);
            return;
        }
        bearbeitenSchliessen();
        location.reload();
    })
    .catch(fehler => {
        console.error(fehler);
        alert("⚠️ Speichern fehlgeschlagen: " + fehler.message);
    });
}

/* ---------- Anlegen ---------- */

function assetAnlegen() {
    const felder = alleFelder().map(n => `
        <div class="anlegen-feld">
            <label>${esc(KONFIG.felder[n])}</label>
            ${eingabeFeld("neu", n, "")}
        </div>
    `).join("");

    document.getElementById("anlegenInhalt").innerHTML = `
        <div class="anlegen-grid">${felder}</div>
        <br>
        <button onclick="assetNeuSpeichern()">💾 Anlegen</button>
        <button onclick="anlegenSchliessen()">✖ Schließen</button>
    `;

    benutzerAlsAuswahl("neu_benutzer");

    const popup = document.getElementById("anlegenPopup");
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.display = "block";
}

function assetNeuSpeichern() {
    const daten = new FormData();

    alleFelder().forEach(n => {
        daten.append(n, document.getElementById("neu_" + n).value);
    });
    daten.append("assettyp", KONFIG.assettyp);

    fetch("/asset/anlegen_popup", { method: "POST", body: daten })
    .then(antwortLesen)
    .then(data => {
        if (data.status === "fehler") {
            alert("⚠️ " + data.meldung);
            return;
        }
        alert("✅ " + KONFIG.einzahl + " angelegt");
        anlegenSchliessen();
        location.reload();
    })
    .catch(fehler => {
        console.error(fehler);
        alert("⚠️ Anlegen fehlgeschlagen: " + fehler.message);
    });
}

/* ---------- Auswahl, Filter, Suche ---------- */

function pruefeAuswahl() {
    const markiert = document.querySelectorAll(".asset-checkbox:checked");
    if (markiert.length) {
        ausgewaehlteId = markiert[0].dataset.id;
    }
    ["detailsBtn", "bearbeitenBtn", "loeschenBtn"].forEach(id => {
        document.getElementById(id).disabled = markiert.length !== 1;
    });
}

document.querySelectorAll(".asset-checkbox").forEach(cb => {
    cb.addEventListener("change", pruefeAuswahl);
});

function filterTabelle() {
    const filter = [...document.querySelectorAll(".filter-row input")]
        .map(input => input.value.toLowerCase());

    document.querySelectorAll("table tr").forEach((zeile, index) => {
        if (index < 2) return;
        const zellen = zeile.querySelectorAll("td");
        const anzeigen = filter.every((wert, i) =>
            !wert || (zellen[i + 1] && zellen[i + 1].innerText.toLowerCase().includes(wert)));
        zeile.style.display = anzeigen ? "" : "none";
    });
}

document.querySelectorAll(".filter-row input").forEach(input => {
    input.addEventListener("keyup", filterTabelle);
});

function globaleSuche() {
    const suchtext = document.getElementById("globalFilter").value.toLowerCase();
    const zeilen = document.querySelectorAll("table tr");
    for (let i = 2; i < zeilen.length; i++) {
        zeilen[i].style.display =
            zeilen[i].textContent.toLowerCase().includes(suchtext) ? "" : "none";
    }
}

document.getElementById("globalFilter").addEventListener("keyup", globaleSuche);

/* ---------- Spaltenmenüs ---------- */

document.querySelectorAll(".dropdown-column").forEach(spalte => {
    const knopf = spalte.querySelector(".dropdown-button");
    const menue = spalte.querySelector(".dropdown-menu");

    knopf.addEventListener("click", event => {
        event.stopPropagation();
        document.querySelectorAll(".dropdown-menu").forEach(m => {
            if (m !== menue) m.style.display = "none";
        });
        menue.style.display = menue.style.display === "block" ? "none" : "block";
    });
});

document.addEventListener("click", () => {
    document.querySelectorAll(".dropdown-menu").forEach(m => m.style.display = "none");
});

document.querySelectorAll(".show-filters").forEach(link => {
    link.addEventListener("click", event => {
        event.preventDefault();
        document.getElementById("filter-row").style.display = "table-row";
    });
});

/* ---------- Popup verschieben ---------- */

function dragElement(element, griff) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    griff.onmousedown = function (e) {
        e.preventDefault();
        const rect = element.getBoundingClientRect();
        element.style.top = rect.top + "px";
        element.style.left = rect.left + "px";
        element.style.transform = "none";
        pos3 = e.clientX;
        pos4 = e.clientY;

        document.onmouseup = () => { document.onmouseup = null; document.onmousemove = null; };
        document.onmousemove = function (e) {
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
        };
    };
}

dragElement(document.getElementById("anlegenPopup"), document.getElementById("anlegenTitel"));

/* ---------- Hinweis nach dem Löschen ---------- */

window.addEventListener("DOMContentLoaded", function () {
    if (new URLSearchParams(window.location.search).get("geloescht") === "1") {
        const meldung = document.getElementById("meldung");
        if (meldung) {
            meldung.classList.add("sichtbar");
            setTimeout(() => meldung.classList.remove("sichtbar"), 3000);
        }
        history.replaceState(null, "", window.location.pathname);
    }
});

