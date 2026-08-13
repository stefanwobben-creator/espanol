#!/usr/bin/env node
/*
 * De hartslag afmaken: zeggen wat er écht van de run terecht is gekomen.
 *
 * Waarom dit bestaat. curriculum.js schrijft `gelukt: code === 0`, en dat betekent daar: "ik ben
 * klaar met genereren". Publiceren gebeurt daarna, in de workflow, en daar kan de poort de boel nog
 * afkeuren. Twee nachten op rij (12 en 13 aug) stond er dus `gelukt: true, geleverd: 5 zinnen` in de
 * hartslag terwijl er niets op main was aangekomen. Wie dat bestand leest om te weten of de
 * avondrun werkt, werd twee nachten voorgelogen door precies de meter die daarvoor bedoeld is.
 *
 * Dit script draait als laatste stap van de workflow, ook (juist) als er iets is misgegaan, en zet
 * de uitkomst van de hele run in het bestand:
 *
 *   gegenereerd    wat curriculum.js zelf vond: is er content gemaakt (de oude betekenis van gelukt)
 *   gepubliceerd   staat het op main (of als pull request) — dit is wat je wilde weten
 *   gelukt         gelijk aan gepubliceerd, want zo wordt het gelezen
 *   pogingen       hoe vaak er is gegenereerd voordat het lukte of opgaf
 *   reden          in gewone taal waarom er niets is gepubliceerd
 *
 * Gebruik:  node tools/hartslag-af.js <status> [pogingen]
 *   status: gepubliceerd | pull-request | niets-te-doen | poort-dicht | geen-sleutel | geklapt
 */
const fs = require("fs");
const path = require("path");

const PAD = path.join(__dirname, "avondrun-hart.json");
const status = process.argv[2] || "geklapt";
const pogingen = Number(process.argv[3] || 1);

const REDEN = {
  gepubliceerd: null,
  "pull-request": null,
  "niets-te-doen": "er viel niets te dichten en de voorraad was op orde",
  "poort-dicht": "de poort ging dicht op wat de bot schreef, in alle pogingen; niets gepusht",
  "geen-sleutel": "ADMIN_KEY ontbreekt, er valt niets te genereren",
  geklapt: "de run is niet afgemaakt",
};

let h = {};
try {
  h = JSON.parse(fs.readFileSync(PAD, "utf8"));
} catch (e) {
  // Geen hartslag betekent dat curriculum.js niet eens tot schrijven kwam. Dan is dít bestand de
  // enige plek waar dat nog te zien is, dus maken we hem alsnog.
  h = { wanneer: new Date().toISOString(), klachten: [] };
}

h.gegenereerd = !!h.gelukt;                       // de oude betekenis, bewaard
h.gepubliceerd = status === "gepubliceerd" || status === "pull-request";
h.gelukt = h.gepubliceerd;                        // en dit is voortaan wat het woord betekent
h.status = status;
h.pogingen = pogingen;
if (REDEN[status] !== null && REDEN[status] !== undefined) h.reden = REDEN[status];
else if (h.gepubliceerd) h.reden = null;
h.afgemaakt = new Date().toISOString();

fs.writeFileSync(PAD, JSON.stringify(h, null, 1) + "\n");
console.log("hartslag afgemaakt :: status=" + status + " pogingen=" + pogingen +
            " gegenereerd=" + h.gegenereerd + " gepubliceerd=" + h.gepubliceerd);
