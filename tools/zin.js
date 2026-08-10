#!/usr/bin/env node
/* Een zin opzoeken op id. De alt-poort en de nachtrun melden ids, en dan wil je die zin kunnen zien
   zonder in een bestand van twee megabyte te gaan zoeken.

     node tools/zin.js s154
     node tools/zin.js s154 s158 w12 q-imperfecto

   Werkt op zinnen, woorden en toetsjes: het id zegt zelf al genoeg over waar hij hoort. */
const lib = require("./content-lib.js");
const inv = lib.inventaris();
const ids = process.argv.slice(2);

if (!ids.length) {
  console.log("gebruik: node tools/zin.js <id> [id...]   bijvoorbeeld: node tools/zin.js s154");
  process.exit(1);
}

function lesVan(id) {
  const l = (inv.perLes || []).find(x => (x.sents || []).includes(id) || (x.words || []).includes(id)
                                      || (x.quizzes || []).includes(id));
  return l ? l.id + " \u00b7 " + l.titel : null;
}

let mis = 0;
ids.forEach(id => {
  const bak = ["sentences", "words", "quizzes"].find(k => (inv[k] || []).some(x => x.id === id));
  if (!bak) { console.log(id + ": niet gevonden"); mis++; return; }
  const item = inv[bak].find(x => x.id === id);
  console.log("== " + id + " (" + bak + (lesVan(id) ? ", " + lesVan(id) : "") + ") ==");
  console.log(JSON.stringify(item, null, 1));
  console.log("");
});
process.exit(mis ? 1 : 0);
