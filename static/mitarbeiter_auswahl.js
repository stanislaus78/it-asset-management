fetch("/mitarbeiter/auswahl_json")
    .then(response => response.json())
    .then(liste => {
        const dl = document.createElement("datalist");
        dl.id = "mitarbeiterListe";
        liste.forEach(m => {
            const o = document.createElement("option");
            o.value = m.uaccountid;
            o.label = m.name;
            dl.appendChild(o);
        });
        document.body.appendChild(dl);
    });