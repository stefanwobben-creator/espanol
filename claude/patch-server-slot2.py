#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
patch-server-slot2: /api/sync en /api/log gaan dicht, en de AI zegt waarom hij weigert.

Twee dingen van de lanceerlijst, allebei in server/index.js, en ze delen hun machinerie.

## 1. /api/sync en /api/log stonden open

Stefan op de lijst: "`/api/sync` en `/api/log` staan open. Kosten geen geld, wel rommel in de
database." Precies zo. `/api/sync` doet een upsert op een zelfverzonnen code van acht tekens; wie
dat eindpunt vindt kan er ongelimiteerd profielen in schrijven, en elke rij bevat een `state` van
maximaal 512 kB. `/api/log` schrijft in een tabel die nooit wordt opgeruimd.

Er stond al een slot op de AI-ingangen (11 aug): herkomstcontrole plus een teller per IP. Dat slot
wordt nu gedeeld in plaats van gekopieerd, want twee sloten die uit elkaar lopen zijn slechter dan
één. Nieuw: `tellerSlot(kaart, req, perUur, perDag)`, en `aiSlot()` gebruikt hem ook.

De grenzen voor de twee nieuwe ingangen zijn ruim gekozen op wat de app zelf doet. `scheduleSync()`
wacht vier seconden na de laatste wijziging, dus een fanatieke sessie van een uur levert hooguit een
paar tientallen aanroepen op. Een gezin achter één IP-adres moet er ook nog bij passen:

    /api/sync   120 per uur, 600 per dag per IP
    /api/log     60 per uur, 300 per dag per IP

En een noodrem in dezelfde vorm als `AI_UIT`, want die vorm heeft zich bewezen: **`POORT_UIT=1`**
zet beide sloten open zonder opnieuw uitrollen. Dat is er voor het geval dat de herkomstcontrole
iets blokkeert wat we niet hadden voorzien: dan is de app binnen een minuut weer heel, en pas
daarna zoeken we uit wat er aan de hand was.

Wat er bewust **niet** dicht gaat: `GET /api/state/:code`. Die is beveiligd met de sync-code zelf,
en een browser stuurt bij een GET niet altijd een Origin mee. Een herkomstcontrole zou daar dus
echte gebruikers kunnen buitensluiten om iets te beschermen dat al beschermd is.

## 2. Waarom de AI weigert, in een code in plaats van in proza

De app zei bij elke geweigerde aanroep "De AI is even niet bereikbaar", en dat is sinds het slot
bijna nooit waar. De vier redenen krijgen nu een korte code mee in het antwoord:

    uit          AI_UIT=1 staat aan
    herkomst     de aanroep kwam niet van de app
    dagplafond   het dagplafond over alle bezoekers heen is bereikt
    tempo        deze bezoeker gaat te snel
    stuk         de AI zelf gaf geen bruikbaar antwoord

De app vertaalt die code naar de taal van het profiel (v23.70). De Nederlandse zin blijft gewoon in
`error` staan, zodat een oudere app er nog iets zinnigs mee kan.

## Volgorde van uitrollen

Deze patch mag vóór of ná v23.70 live: de app valt terug op `error` als er geen `reden` in zit, en
de server stuurt `reden` mee ook als de app hem niet leest.

Idempotent. Draaien: `python3 claude/patch-server-slot2.py .`
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "server", "index.js")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function tellerSlot" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_KOP = '''/* ================= HET SLOT OP DE AI-KNOPPEN (11 aug, vóór de lancering) =================
   Zie de kop van claude/patch-server-slot.py voor het waarom. Drie sloten: herkomst, per bezoeker,
   en een dagplafond met een noodrem.

   De tellers staan in het geheugen van dit proces en zijn dus leeg na een herstart. Dat is met
   opzet: dit is een rem op een lus en geen boekhouding. Draait deze dienst ooit op meer dan één
   instantie tegelijk, dan telt elke instantie zijn eigen bezoekers en moet dit naar de database. */'''

A_TELLER = '''const aiTeller = new Map();          // ip -> {uur:[tijdstippen], dag:[tijdstippen]}
let aiDagTotaal = { dag: "", n: 0 };'''

A_SLOT = '''function aiSlot(req) {
  if (process.env.AI_UIT === "1") {
    return { code: 503, tekst: "de AI-hulp staat even uit" };
  }
  if (!herkomstOk(req)) {
    return { code: 403, tekst: "deze ingang is alleen voor de app zelf" };
  }
  const dag = vandaagUTC();
  if (aiDagTotaal.dag !== dag) aiDagTotaal = { dag, n: 0 };
  if (aiDagTotaal.n >= AI_DAGPLAFOND) {
    return { code: 429, tekst: "de AI-hulp is vandaag op; morgen kan het weer" };
  }
  const ip = String(req.headers["x-forwarded-for"] || req.ip || "").split(",")[0].trim() || "onbekend";
  const nu = Date.now();
  const t = aiTeller.get(ip) || { uur: [], dag: [] };
  t.uur = t.uur.filter((x) => nu - x < 3600000);
  t.dag = t.dag.filter((x) => nu - x < 86400000);
  if (t.uur.length >= AI_PER_UUR || t.dag.length >= AI_PER_DAG) {
    aiTeller.set(ip, t);
    return { code: 429, tekst: "even rustig aan met de AI-hulp; probeer het over een uur weer" };
  }
  t.uur.push(nu); t.dag.push(nu);
  aiTeller.set(ip, t);
  aiDagTotaal.n++;
  /* De kaart groeit anders door met IP's die één keer langskwamen. Opruimen op het moment dat je er
     toch al in zit is goedkoper dan een timer die altijd loopt. */
  if (aiTeller.size > 5000) {
    for (const [k, v] of aiTeller) { if (!v.dag.length) aiTeller.delete(k); }
  }
  return null;
}'''

A_STAND = '''function aiStand() {
  return { dag: aiDagTotaal.dag, gebruikt: aiDagTotaal.n, plafond: AI_DAGPLAFOND,
           bezoekers: aiTeller.size, uit: process.env.AI_UIT === "1" };
}'''

A_BAD = '''const ok = (res, data) => res.json({ ok: true, ...data });
const bad = (res, code, msg) => res.status(code).json({ ok: false, error: msg });'''

A_SYNC = '''app.post("/api/sync", async (req, res) => {
  const { code, name, track, state } = req.body || {};'''

A_LOG = '''app.post("/api/log", async (req, res) => {
  const { code, kind, payload } = req.body || {};'''

A_AICALL = '''  const slot = aiSlot(req);
  if (slot) return bad(res, slot.code, slot.tekst);'''

ontbreekt = [a for a in [A_KOP, A_TELLER, A_SLOT, A_STAND, A_BAD, A_SYNC, A_LOG] if a not in src]
if ontbreekt:
    print("server/index.js ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
          "\n  ".join(a[:90].replace("\n", " / ") for a in ontbreekt))
    sys.exit(1)
if src.count(A_AICALL) != 3:
    print("verwacht drie AI-ingangen met een slot, gevonden: %d" % src.count(A_AICALL))
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


rep(A_KOP, '''/* ================= DE SLOTEN OP DE INGANGEN =================
   11 aug: de AI-knoppen. 13 aug: /api/sync en /api/log erbij, met dezelfde machinerie in plaats van
   een tweede kopie ervan. Drie sloten: herkomst, een teller per bezoeker, en (alleen bij de AI) een
   dagplafond over alle bezoekers heen.

   De tellers staan in het geheugen van dit proces en zijn dus leeg na een herstart. Dat is met
   opzet: dit is een rem op een lus en geen boekhouding. Draait deze dienst ooit op meer dan één
   instantie tegelijk, dan telt elke instantie zijn eigen bezoekers en moet dit naar de database.

   Noodrem: AI_UIT=1 zet de AI-knoppen uit, POORT_UIT=1 zet de sloten op sync en log open. Allebei
   zonder opnieuw uitrollen, want een slot dat je niet binnen een minuut kunt openen is zelf een
   risico. */''')

rep(A_TELLER, '''const aiTeller = new Map();          // ip -> {uur:[tijdstippen], dag:[tijdstippen]}
let aiDagTotaal = { dag: "", n: 0 };

/* De ruimte voor de twee gewone ingangen is bepaald op wat de app zelf doet. scheduleSync() wacht
   vier seconden na de laatste wijziging, dus een fanatiek uur levert een paar tientallen aanroepen
   op; hier past een heel gezin achter één IP-adres nog ruim in. */
const SYNC_PER_UUR = Number(process.env.SYNC_PER_UUR || 120);
const SYNC_PER_DAG = Number(process.env.SYNC_PER_DAG || 600);
const LOG_PER_UUR = Number(process.env.LOG_PER_UUR || 60);
const LOG_PER_DAG = Number(process.env.LOG_PER_DAG || 300);
const syncTeller = new Map();
const logTeller = new Map();

function ipVan(req) {
  return String(req.headers["x-forwarded-for"] || req.ip || "").split(",")[0].trim() || "onbekend";
}

/* Eén teller voor alle ingangen die er een nodig hebben. Geeft true als het mag. */
function tellerSlot(kaart, req, perUur, perDag) {
  const ip = ipVan(req);
  const nu = Date.now();
  const t = kaart.get(ip) || { uur: [], dag: [] };
  t.uur = t.uur.filter((x) => nu - x < 3600000);
  t.dag = t.dag.filter((x) => nu - x < 86400000);
  if (t.uur.length >= perUur || t.dag.length >= perDag) {
    kaart.set(ip, t);
    return false;
  }
  t.uur.push(nu); t.dag.push(nu);
  kaart.set(ip, t);
  if (kaart.size > 5000) {
    for (const [k, v] of kaart) { if (!v.dag.length) kaart.delete(k); }
  }
  return true;
}

/* Het slot voor /api/sync en /api/log. Geeft null als het mag.
   GET /api/state/:code krijgt bewust géén herkomstcontrole: die is beveiligd met de sync-code zelf,
   en een browser stuurt bij een GET niet altijd een Origin mee. Dan zou je echte gebruikers
   buitensluiten om iets te beschermen dat al beschermd is. */
function gewoonSlot(req, kaart, perUur, perDag) {
  if (process.env.POORT_UIT === "1") return null;
  if (!herkomstOk(req)) {
    return { code: 403, tekst: "deze ingang is alleen voor de app zelf", reden: "herkomst" };
  }
  if (!tellerSlot(kaart, req, perUur, perDag)) {
    return { code: 429, tekst: "even rustig aan; probeer het over een uur weer", reden: "tempo" };
  }
  return null;
}''')

rep(A_SLOT, '''function aiSlot(req) {
  if (process.env.AI_UIT === "1") {
    return { code: 503, tekst: "de AI-hulp staat even uit", reden: "uit" };
  }
  if (!herkomstOk(req)) {
    return { code: 403, tekst: "deze ingang is alleen voor de app zelf", reden: "herkomst" };
  }
  const dag = vandaagUTC();
  if (aiDagTotaal.dag !== dag) aiDagTotaal = { dag, n: 0 };
  if (aiDagTotaal.n >= AI_DAGPLAFOND) {
    return { code: 429, tekst: "de AI-hulp is vandaag op; morgen kan het weer", reden: "dagplafond" };
  }
  if (!tellerSlot(aiTeller, req, AI_PER_UUR, AI_PER_DAG)) {
    return { code: 429, tekst: "even rustig aan met de AI-hulp; probeer het over een uur weer", reden: "tempo" };
  }
  aiDagTotaal.n++;
  return null;
}''')

rep(A_STAND, '''function aiStand() {
  return { dag: aiDagTotaal.dag, gebruikt: aiDagTotaal.n, plafond: AI_DAGPLAFOND,
           bezoekers: aiTeller.size, uit: process.env.AI_UIT === "1",
           /* zodat /health laat zien of de noodrem aanstaat; anders merk je pas over een maand dat
              hij ooit is aangezet en nooit meer uit. */
           poortUit: process.env.POORT_UIT === "1",
           sync: syncTeller.size, log: logTeller.size };
}''')

rep(A_BAD, '''const ok = (res, data) => res.json({ ok: true, ...data });
const bad = (res, code, msg) => res.status(code).json({ ok: false, error: msg });
/* Dezelfde vorm, met een korte code erbij. De app vertaalt die code naar de taal van het profiel
   (v23.70); `error` blijft staan zodat een oudere app er nog iets zinnigs mee kan. */
const badReden = (res, code, msg, reden) =>
  res.status(code).json({ ok: false, error: msg, reden: reden || "stuk" });''')

rep(A_SYNC, '''app.post("/api/sync", async (req, res) => {
  const slot = gewoonSlot(req, syncTeller, SYNC_PER_UUR, SYNC_PER_DAG);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { code, name, track, state } = req.body || {};''')

rep(A_LOG, '''app.post("/api/log", async (req, res) => {
  const slot = gewoonSlot(req, logTeller, LOG_PER_UUR, LOG_PER_DAG);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { code, kind, payload } = req.body || {};''')

rep(A_AICALL, '''  const slot = aiSlot(req);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);''', 3)

# de drie 502'jes van de AI zelf krijgen ook hun code mee
src = src.replace('bad(res, 502, "AI-fout");', 'badReden(res, 502, "AI-fout", "stuk");')
src = src.replace('return bad(res, 502, "onleesbaar AI-antwoord");', 'return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");')

# de omgevingsvariabelen bovenaan bijwerken
rep(''' *   AI_UIT            — zet op "1" om de AI-knoppen meteen uit te zetten, zonder opnieuw uitrollen''',
    ''' *   AI_UIT            — zet op "1" om de AI-knoppen meteen uit te zetten, zonder opnieuw uitrollen
 *   POORT_UIT         — zet op "1" om de sloten op /api/sync en /api/log open te zetten (noodrem)
 *   SYNC_PER_UUR      — sync-aanroepen per IP per uur (standaard 120), SYNC_PER_DAG (600)
 *   LOG_PER_UUR       — logregels per IP per uur (standaard 60), LOG_PER_DAG (300)''')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("server/index.js gepatcht: sync en log achter een slot, AI geeft een reden mee")
