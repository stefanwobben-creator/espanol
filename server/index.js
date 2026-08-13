/*
 * ¡Vamos! API — profielsync, foutenlogs en AI-feedback
 *
 * Omgevingsvariabelen (in Render instellen):
 *   DATABASE_URL      — Neon connection string (postgresql://...)
 *   ANTHROPIC_API_KEY — sleutel van console.anthropic.com (voor /api/ai/*)
 *   ADMIN_KEY         — zelfverzonnen lang wachtwoord; nodig om alle logs uit te lezen
 *   ALLOWED_ORIGIN    — standaard https://vamos.stefanwobben.nl
 *   AI_PER_UUR        — AI-aanroepen per IP per uur (standaard 20)
 *   AI_PER_DAG        — AI-aanroepen per IP per dag (standaard 60)
 *   AI_DAGPLAFOND     — AI-aanroepen per dag over alle bezoekers heen (standaard 800)
 *   AI_UIT            — zet op "1" om de AI-knoppen meteen uit te zetten, zonder opnieuw uitrollen
 *   POORT_UIT         — zet op "1" om de sloten op /api/sync en /api/log open te zetten (noodrem)
 *   SYNC_PER_UUR      — sync-aanroepen per IP per uur (standaard 120), SYNC_PER_DAG (600)
 *   LOG_PER_UUR       — logregels per IP per uur (standaard 60), LOG_PER_DAG (300)
 */
const express = require("express");
const { Pool } = require("pg");
const { reason } = require("./llm");

const app = express();
app.use(express.json({ limit: "512kb" }));

const ORIGIN = process.env.ALLOWED_ORIGIN || "https://vamos.stefanwobben.nl";
app.use((req, res, next) => {
  const o = req.headers.origin || "";
  // sta het live-domein toe, plus lokaal testen vanaf file:// (origin "null")
  if (o === ORIGIN || o === "null" || o.endsWith(".stefanwobben.nl")) {
    res.setHeader("Access-Control-Allow-Origin", o === "null" ? "*" : o);
  }
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

/* ================= DE SLOTEN OP DE INGANGEN =================
   11 aug: de AI-knoppen. 13 aug: /api/sync en /api/log erbij, met dezelfde machinerie in plaats van
   een tweede kopie ervan. Drie sloten: herkomst, een teller per bezoeker, en (alleen bij de AI) een
   dagplafond over alle bezoekers heen.

   De tellers staan in het geheugen van dit proces en zijn dus leeg na een herstart. Dat is met
   opzet: dit is een rem op een lus en geen boekhouding. Draait deze dienst ooit op meer dan één
   instantie tegelijk, dan telt elke instantie zijn eigen bezoekers en moet dit naar de database.

   Noodrem: AI_UIT=1 zet de AI-knoppen uit, POORT_UIT=1 zet de sloten op sync en log open. Allebei
   zonder opnieuw uitrollen, want een slot dat je niet binnen een minuut kunt openen is zelf een
   risico. */
const AI_PER_UUR = Number(process.env.AI_PER_UUR || 20);
const AI_PER_DAG = Number(process.env.AI_PER_DAG || 60);
const AI_DAGPLAFOND = Number(process.env.AI_DAGPLAFOND || 800);
const aiTeller = new Map();          // ip -> {uur:[tijdstippen], dag:[tijdstippen]}
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
}

function vandaagUTC() { return new Date().toISOString().slice(0, 10); }

function herkomstOk(req) {
  const o = req.headers.origin || "";
  if (!o) return false;                                   // curl en losse scripts sturen niets mee
  if (o === ORIGIN || o === "null") return true;
  if (o.endsWith(".stefanwobben.nl")) return true;
  return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o);
}

/* Eén functie voor alle drie de AI-ingangen, zodat er geen ingang kan zijn die hem vergeet.
   Geeft null als het mag, en anders een {code, tekst} om terug te sturen. */
function aiSlot(req) {
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
}

// Zodat je kunt zien of het plafond in de buurt komt zonder in de logs te graven.
function aiStand() {
  return { dag: aiDagTotaal.dag, gebruikt: aiDagTotaal.n, plafond: AI_DAGPLAFOND,
           bezoekers: aiTeller.size, uit: process.env.AI_UIT === "1",
           /* zodat /health laat zien of de noodrem aanstaat; anders merk je pas over een maand dat
              hij ooit is aangezet en nooit meer uit. */
           poortUit: process.env.POORT_UIT === "1",
           sync: syncTeller.size, log: logTeller.size };
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 5,
});

async function init() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS profiles (
      code       text PRIMARY KEY,
      name       text NOT NULL,
      track      text NOT NULL,
      state      jsonb NOT NULL DEFAULT '{}'::jsonb,
      updated_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS logs (
      id         bigserial PRIMARY KEY,
      code       text NOT NULL,
      kind       text NOT NULL DEFAULT 'sessie',
      payload    jsonb NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS logs_created ON logs (created_at DESC);
    CREATE TABLE IF NOT EXISTS groups (
      gcode      text PRIMARY KEY,
      naam       text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS group_members (
      gcode      text NOT NULL,
      pcode      text NOT NULL,
      joined_at  timestamptz NOT NULL DEFAULT now(),
      PRIMARY KEY (gcode, pcode)
    );
    CREATE TABLE IF NOT EXISTS krabbels (
      van        text NOT NULL,
      naar       text NOT NULL,
      sleutel    text NOT NULL,
      dag        date NOT NULL DEFAULT current_date,
      created_at timestamptz NOT NULL DEFAULT now(),
      PRIMARY KEY (van, naar, dag)
    );
    /* v19.58 — een maatje is iemand die MEEKIJKT en zelf niet leert. Bewust een eigen token en
       geen hergebruik van de sync-code: met een sync-code geeft GET /api/state/:code de hele
       state weg (voortgang, e-mail, alles), en dat is precies wat je je moeder niet stuurt.
       Deze mcode opent alleen GET /api/maatje/:mcode, en dat geeft vijf getallen terug. */
    CREATE TABLE IF NOT EXISTS maatjes (
      mcode      text PRIMARY KEY,
      pcode      text NOT NULL,
      naam       text NOT NULL DEFAULT '',
      created_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS maatjes_pcode ON maatjes (pcode);
    CREATE TABLE IF NOT EXISTS duels (
      id         text PRIMARY KEY,
      rounds     int NOT NULL DEFAULT 5,
      letters    jsonb NOT NULL,
      players    jsonb NOT NULL DEFAULT '[]'::jsonb,
      moves      jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now(),
      updated_at timestamptz NOT NULL DEFAULT now()
    );
  `);
}

/* ---- Palabra Duel ---- */
const LETTER_SCORE = { a:1,e:1,o:1,i:1,s:1,n:1,r:1,u:1,l:1,t:1,d:2,g:2,c:3,b:3,m:3,p:3,f:4,h:4,v:4,y:4,q:5,j:8,x:8,z:10,"ñ":8 };
function duelLetters(rounds) {
  const vowels = "aaaeeeeooiiu";
  const cons = "nnrrssllttddccmmbbppgg" + "fhvyjqzñx";
  const out = [];
  for (let r = 0; r < rounds; r++) {
    const set = [];
    for (let i = 0; i < 3; i++) set.push(vowels[Math.floor(Math.random() * vowels.length)]);
    for (let i = 0; i < 4; i++) set.push(cons[Math.floor(Math.random() * cons.length)]);
    set.sort(() => Math.random() - 0.5);
    out.push(set);
  }
  return out;
}
function canMake(word, letters) {
  const pool = {};
  letters.forEach((l) => { pool[l] = (pool[l] || 0) + 1; });
  for (const ch of word) {
    if (!pool[ch]) return false;
    pool[ch]--;
  }
  return true;
}
function wordScore(word) {
  let s = 0;
  for (const ch of word) s += LETTER_SCORE[ch] || 1;
  return s + (word.length >= 6 ? 5 : 0); // bonus voor lange woorden
}

// POST /api/duel/nieuw {speler}
app.post("/api/duel/nieuw", async (req, res) => {
  const { speler } = req.body || {};
  if (!speler) return bad(res, 400, "speler verplicht");
  const id = Math.random().toString(36).slice(2, 8);
  const letters = duelLetters(5);
  try {
    await pool.query("INSERT INTO duels (id, rounds, letters, players) VALUES ($1,5,$2,$3)",
      [id, JSON.stringify(letters), JSON.stringify([String(speler).slice(0, 30)])]);
    const r = await pool.query("SELECT * FROM duels WHERE id=$1", [id]);
    ok(res, { duel: r.rows[0] });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// POST /api/duel/join {id, speler}
app.post("/api/duel/join", async (req, res) => {
  const { id, speler } = req.body || {};
  if (!id || !speler) return bad(res, 400, "id en speler verplicht");
  try {
    const r = await pool.query("SELECT * FROM duels WHERE id=$1", [id]);
    if (!r.rows.length) return bad(res, 404, "duel niet gevonden");
    const duel = r.rows[0];
    const players = duel.players;
    if (!players.includes(speler)) {
      if (players.length >= 2) return bad(res, 409, "duel zit al vol");
      players.push(String(speler).slice(0, 30));
      await pool.query("UPDATE duels SET players=$2, updated_at=now() WHERE id=$1", [id, JSON.stringify(players)]);
      duel.players = players;
    }
    ok(res, { duel });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// GET /api/duel/:id
app.get("/api/duel/:id", async (req, res) => {
  try {
    const r = await pool.query("SELECT * FROM duels WHERE id=$1", [req.params.id]);
    if (!r.rows.length) return bad(res, 404, "duel niet gevonden");
    ok(res, { duel: r.rows[0] });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// POST /api/duel/zet {id, speler, ronde, woord} of {id, speler, ronde, pas:true}
app.post("/api/duel/zet", async (req, res) => {
  const { id, speler, ronde, woord, pas } = req.body || {};
  if (!id || !speler || typeof ronde !== "number" || (!woord && !pas)) return bad(res, 400, "id/speler/ronde/woord verplicht");
  const w = pas ? "" : String(woord).toLowerCase().trim().normalize("NFC");
  if (!pas && (w.length < 2 || w.length > 7 || !/^[a-zñ]+$/.test(w))) return bad(res, 400, "ongeldig woord (2-7 letters)");
  try {
    const r = await pool.query("SELECT * FROM duels WHERE id=$1", [id]);
    if (!r.rows.length) return bad(res, 404, "duel niet gevonden");
    const duel = r.rows[0];
    if (!duel.players.includes(speler)) return bad(res, 403, "je doet niet mee aan dit duel");
    if (ronde < 0 || ronde >= duel.rounds) return bad(res, 400, "ongeldige ronde");
    const moves = duel.moves || {};
    if (moves[ronde] && moves[ronde][speler]) return bad(res, 409, "je hebt deze ronde al gespeeld");
    if (pas) {
      moves[ronde] = moves[ronde] || {};
      moves[ronde][speler] = { woord: "–", punten: 0, betekenis: "gepast" };
      await pool.query("UPDATE duels SET moves=$2, updated_at=now() WHERE id=$1", [id, JSON.stringify(moves)]);
      const rp = await pool.query("SELECT * FROM duels WHERE id=$1", [id]);
      return ok(res, { geldig: true, punten: 0, betekenis: "gepast", duel: rp.rows[0] });
    }
    if (!canMake(w, duel.letters[ronde])) return bad(res, 400, "dat woord past niet in de letters van deze ronde");
    // Spaanse geldigheid via de LLM-ladder (fail-closed)
    const ai = await reason(
      "Je bent scheidsrechter in een Spaans woordspel. Antwoord UITSLUITEND met geldige JSON {\"geldig\": true/false, \"betekenis\": \"NL-vertaling of korte reden\"}. " +
      "geldig=true alleen als dit een bestaand Spaans woord is (zelfstandig naamwoord, werkwoordsvorm, bijvoeglijk naamwoord, enz. — vervoegingen tellen mee). Eigennamen en afkortingen tellen niet.\n\nWoord: \"" + w + "\"",
      { maxTokens: 150, jsonMode: true, callSite: "duel-woord" }
    );
    if (!ai) return bad(res, 503, "de scheidsrechter (AI) is even niet bereikbaar, probeer zo opnieuw");
    const m = ai.text.match(/\{[\s\S]*\}/);
    if (!m) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
    const parsed = JSON.parse(m[0]);
    if (!parsed.geldig) {
      return ok(res, { geldig: false, betekenis: String(parsed.betekenis || "").slice(0, 200) });
    }
    const punten = wordScore(w);
    moves[ronde] = moves[ronde] || {};
    moves[ronde][speler] = { woord: w, punten, betekenis: String(parsed.betekenis || "").slice(0, 200) };
    await pool.query("UPDATE duels SET moves=$2, updated_at=now() WHERE id=$1", [id, JSON.stringify(moves)]);
    const r2 = await pool.query("SELECT * FROM duels WHERE id=$1", [id]);
    ok(res, { geldig: true, punten, betekenis: String(parsed.betekenis || "").slice(0, 200), duel: r2.rows[0] });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

const ok = (res, data) => res.json({ ok: true, ...data });
const bad = (res, code, msg) => res.status(code).json({ ok: false, error: msg });
/* Dezelfde vorm, met een korte code erbij. De app vertaalt die code naar de taal van het profiel
   (v23.70); `error` blijft staan zodat een oudere app er nog iets zinnigs mee kan. */
const badReden = (res, code, msg, reden) =>
  res.status(code).json({ ok: false, error: msg, reden: reden || "stuk" });

// ---- gezondheid ----
app.get("/health", (_req, res) => ok(res, { tijd: new Date().toISOString(), ai: aiStand() }));

// ---- profielsync ----
// POST /api/sync  {code, name, track, state}
// Upsert op code. 'code' is de geheime profielcode die de app genereert.
app.post("/api/sync", async (req, res) => {
  const slot = gewoonSlot(req, syncTeller, SYNC_PER_UUR, SYNC_PER_DAG);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { code, name, track, state } = req.body || {};
  if (!code || typeof code !== "string" || code.length < 8) return bad(res, 400, "ongeldige code");
  if (!name || !track || typeof state !== "object") return bad(res, 400, "name/track/state verplicht");
  try {
    const r = await pool.query(
      `INSERT INTO profiles (code, name, track, state, updated_at)
       VALUES ($1,$2,$3,$4, now())
       ON CONFLICT (code) DO UPDATE SET name=$2, track=$3, state=$4, updated_at=now()
       RETURNING updated_at`,
      [code, String(name).slice(0, 60), String(track).slice(0, 20), state]
    );
    ok(res, { updated_at: r.rows[0].updated_at });
  } catch (e) {
    console.error(e);
    bad(res, 500, "database-fout");
  }
});

// GET /api/state/:code -> {state, name, track, updated_at}
app.get("/api/state/:code", async (req, res) => {
  try {
    const r = await pool.query("SELECT name, track, state, updated_at FROM profiles WHERE code=$1", [req.params.code]);
    if (!r.rows.length) return bad(res, 404, "onbekende code");
    // groepslidmaatschappen meesturen, zodat elk apparaat je groepen kent
    const g = await pool.query(
      "SELECT gr.gcode, gr.naam FROM group_members m JOIN groups gr ON gr.gcode = m.gcode WHERE m.pcode=$1",
      [req.params.code]);
    ok(res, { ...r.rows[0], groepen: g.rows });
  } catch (e) {
    console.error(e);
    bad(res, 500, "database-fout");
  }
});

// ---- foutenlogs ----
// POST /api/log {code, kind, payload}
app.post("/api/log", async (req, res) => {
  const slot = gewoonSlot(req, logTeller, LOG_PER_UUR, LOG_PER_DAG);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { code, kind, payload } = req.body || {};
  if (!code || typeof payload !== "object") return bad(res, 400, "code/payload verplicht");
  try {
    await pool.query("INSERT INTO logs (code, kind, payload) VALUES ($1,$2,$3)", [
      code, String(kind || "sessie").slice(0, 30), payload,
    ]);
    ok(res, {});
  } catch (e) {
    console.error(e);
    bad(res, 500, "database-fout");
  }
});

// GET /api/logs?key=ADMIN_KEY&dagen=8 — voor de wekelijkse onderhoudstaak
app.get("/api/logs", async (req, res) => {
  if (!process.env.ADMIN_KEY || req.query.key !== process.env.ADMIN_KEY) return bad(res, 403, "geen toegang");
  const dagen = Math.min(60, parseInt(req.query.dagen, 10) || 8);
  try {
    const logs = await pool.query(
      "SELECT code, kind, payload, created_at FROM logs WHERE created_at > now() - ($1 || ' days')::interval ORDER BY created_at DESC LIMIT 500",
      [dagen]
    );
    const profs = await pool.query("SELECT code, name, track, updated_at FROM profiles ORDER BY updated_at DESC");
    ok(res, { logs: logs.rows, profielen: profs.rows });
  } catch (e) {
    console.error(e);
    bad(res, 500, "database-fout");
  }
});

/* ---- Krabbels: een schouderklopje bij een familielid, uitsluitend in het Spaans ----
 * v19.49 (Stefan: "bij de familie zou je een krabbel acher kunnen latne met een hyes banaan bij
 * een familie/teamlid, maar alleen in het spaans"). De client stuurt alleen een sleutel; de tekst
 * staat hier. Vrije tekst kan er dus niet in, en daarmee is "alleen in het Spaans" gegarandeerd
 * door de vorm van de API in plaats van door goed gedrag van de client.
 * Eén krabbel per paar per dag: opnieuw sturen overschrijft, dus je kunt niet spammen.
 */
const KRABBEL_TEKST = {
  hola: "¡Hola!",
  choca: "¡Choca esos cinco!",
  platano: "¡Un plátano para ti!",
  crack: "¡Eres un crack!",
  sigue: "¡Sigue así!",
  vamos: "¡Vamos, vamos!",
  ole: "¡Olé!",
  taco: "¡Te invito a un taco!",
  campeon: "¡Campeón!",
  abrazo: "¡Un abrazo!",
};
/* De muur (v22.6) tekent per lid zijn eigen Chispa in zijn eigen kleren, en leest zijn mijlpalen om
   te weten wat er te vieren valt. Dat zijn vier velden uit state, en meer heeft dat scherm niet nodig:
   de namen, de vertalingen, de plaatjes en de animaties staan al aan de clientkant.
   Bewust GEEN pcode in het antwoord: dat is de sync-sleutel van iemand anders. */
function oogstKort(o) {
  const vandaag = new Date().toISOString().slice(0, 10);
  const gisteren = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  const uit = {};
  if (o[vandaag]) uit[vandaag] = o[vandaag];
  if (o[gisteren]) uit[gisteren] = o[gisteren];
  return uit;
}

function muurVelden(st) {
  return {
    woorden: Object.keys((st && st.srs) || {}).length,
    mijlpalen: (st && st.mijlpalen) || {},
    wear: (st && st.wear) || {},
    baile: (st && st.baile) || null,
    petKleur: (st && st.petKleur) || null,   // v22.7: de muur tekent haar in haar eigen kleur
    bailes: (st && st.bailes) || [],
    // v22.6: de kleine dag naast de grote grenzen. Alleen vandaag en gisteren, want verder terug
    // kijkt de muur niet en de rest is dode last in een antwoord dat elk bezoek wordt opgehaald.
    oogst: oogstKort((st && st.oogst) || {}),
  };
}

function familiaNamen() {
  return String(process.env.FAMILIA_NAMEN || "stefan,elise,ilona,martina")
    .split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
}
/* v22.5. Drie dingen erbij, geen tabel gewijzigd.

   1. `gcode`: hoort de afzender bij dezelfde groep als de ontvanger, dan mag het. De vaste
      FAMILIA_NAMEN-lijst blijft werken voor het familiescherm, maar hij was nooit een goede
      toegangsregel: hij staat in een omgevingsvariabele en groeit niet mee met wie de app gebruikt.
   2. `dag`: vandaag of gisteren. De muur toont ook de regel van gisteren, en daar wil je nog op
      kunnen reageren. Verder terug niet: dan verander je geschiedenis.
   3. Sleutel "baile": het dansje. De tekst daarvan staat niet hier maar in BAILES aan de clientkant,
      samen met de vertaling en de animatie. Dit eindpunt weet alleen dát je danste, niet welk dansje;
      dat leest de ontvanger uit het `baile`-veld van de afzender. Zo staat de tekst op één plek. */
app.post("/api/krabbel", async (req, res) => {
  try {
    const van = String((req.body && req.body.van) || "").trim().toLowerCase();
    const naar = String((req.body && req.body.naar) || "").trim().toLowerCase();
    const sleutel = String((req.body && req.body.sleutel) || "").trim().toLowerCase();
    const gcode = String((req.body && req.body.gcode) || "").trim().toLowerCase();
    const dag = String((req.body && req.body.dag) || "").trim();
    if (sleutel !== "baile" && !KRABBEL_TEKST[sleutel]) return bad(res, 400, "onbekende krabbel");
    if (!van || !naar || van === naar) return bad(res, 400, "van/naar ongeldig");
    if (dag && !/^\d{4}-\d{2}-\d{2}$/.test(dag)) return bad(res, 400, "dag ongeldig");

    let mag = false;
    if (gcode) {
      const m = await pool.query(
        `SELECT lower(p.name) AS naam FROM group_members m JOIN profiles p ON p.code = m.pcode
          WHERE m.gcode = $1`, [gcode]);
      const leden = m.rows.map((x) => x.naam);
      mag = leden.indexOf(van) >= 0 && leden.indexOf(naar) >= 0;
      if (!mag) return bad(res, 403, "alleen binnen je eigen groep");
    } else {
      const namen = familiaNamen();
      if (namen.indexOf(van) === -1 || namen.indexOf(naar) === -1) return bad(res, 403, "alleen binnen de familie");
    }

    const r = await pool.query(
      `INSERT INTO krabbels (van, naar, sleutel, dag)
       VALUES ($1, $2, $3, GREATEST(LEAST(COALESCE($4::date, current_date), current_date), current_date - 1))
       ON CONFLICT (van, naar, dag) DO UPDATE SET sleutel = EXCLUDED.sleutel, created_at = now()
       RETURNING dag::text`,
      [van, naar, sleutel, dag || null]);
    ok(res, { tekst: KRABBEL_TEKST[sleutel] || "", dag: r.rows[0] && r.rows[0].dag });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// GET /api/familia — scorebord van ALLEEN de familie (FAMILIA_NAMEN env, default stefan/elise/ilona/martina).
// Vroeger toonde dit alle profielen; sinds de app openbaar deelbaar is, is dat expres dichtgezet.
app.get("/api/familia", async (_req, res) => {
  try {
    const namen = String(process.env.FAMILIA_NAMEN || "stefan,elise,ilona,martina")
      .split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
    const r = await pool.query(
      "SELECT name, track, state, updated_at FROM profiles WHERE lower(name) = ANY($1) ORDER BY updated_at DESC",
      [namen]);
    const spelers = r.rows.map((row) => {
      const st = row.state || {};
      let lessen = 0;
      if (st.lessons) for (const k in st.lessons) { if (st.lessons[k] && st.lessons[k].done) lessen++; }
      // streak alleen tellen als hij nog actueel is (vandaag of gisteren gehaald)
      const vandaag = new Date().toISOString().slice(0, 10);
      const gisteren = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      const sd = st.streak || {};
      const streak = (sd.last === vandaag || sd.last === gisteren) ? (sd.count || 0) : 0;
      return { naam: row.name, niveau: row.track, txp: st.txp || 0, streak, lessen, laatstActief: row.updated_at };
    });
    // ontdubbel op naam: hetzelfde gezinslid op twee apparaten telt één keer (hoogste score wint)
    const perNaam = {};
    spelers.forEach((s) => {
      const k = s.naam.toLowerCase();
      if (!perNaam[k] || s.txp > perNaam[k].txp) perNaam[k] = s;
    });
    const lijst = Object.values(perNaam).sort((a, b) => b.txp - a.txp);
    // krabbels van vandaag meesturen: het klassement en de schouderklopjes horen bij elkaar
    let krabbels = [];
    try {
      const kr = await pool.query(
        "SELECT van, naar, sleutel FROM krabbels WHERE dag = current_date ORDER BY created_at");
      krabbels = kr.rows;
    } catch (e2) { console.error(e2); }
    ok(res, { spelers: lijst, krabbels });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

/* ---- Herstel: voortgang terugvinden via e-mail (max 5 pogingen per IP per uur) ---- */
const herstelPogingen = new Map(); // ip -> [timestamps]
app.post("/api/herstel", async (req, res) => {
  const { mail } = req.body || {};
  const schoon = String(mail || "").trim().toLowerCase();
  if (!schoon || !schoon.includes("@")) return bad(res, 400, "vul een geldig e-mailadres in");
  const ip = req.headers["x-forwarded-for"] || req.socket.remoteAddress || "?";
  const nu = Date.now();
  const lijst = (herstelPogingen.get(ip) || []).filter((t) => t > nu - 3600000);
  if (lijst.length >= 5) return bad(res, 429, "te veel pogingen, probeer het over een uur nog eens");
  lijst.push(nu); herstelPogingen.set(ip, lijst);
  try {
    const r = await pool.query(
      "SELECT code, name, track FROM profiles WHERE lower(state->>'mail') = $1 ORDER BY updated_at DESC LIMIT 5", [schoon]);
    ok(res, { profielen: r.rows.map((x) => ({ naam: x.name, code: x.code, track: x.track })) });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

/* ---- Groepen: eigen klassementen naast de familie ---- */
// POST /api/groep/nieuw {naam, code} — code = sync-code van de maker
app.post("/api/groep/nieuw", async (req, res) => {
  const { naam, code } = req.body || {};
  const schoon = String(naam || "").trim().slice(0, 40);
  if (!schoon || !code) return bad(res, 400, "naam en code verplicht");
  try {
    const p = await pool.query("SELECT code FROM profiles WHERE code=$1", [String(code)]);
    if (!p.rows.length) return bad(res, 404, "profiel onbekend, oefen eerst even zodat je sync-code bestaat");
    const gcode = "g" + Math.random().toString(36).slice(2, 7);
    await pool.query("INSERT INTO groups (gcode, naam) VALUES ($1,$2)", [gcode, schoon]);
    await pool.query("INSERT INTO group_members (gcode, pcode) VALUES ($1,$2) ON CONFLICT DO NOTHING", [gcode, String(code)]);
    ok(res, { groep: { gcode, naam: schoon } });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// POST /api/groep/join {gcode, code}
app.post("/api/groep/join", async (req, res) => {
  const { gcode, code } = req.body || {};
  if (!gcode || !code) return bad(res, 400, "gcode en code verplicht");
  try {
    const g = await pool.query("SELECT gcode, naam FROM groups WHERE gcode=$1", [String(gcode).toLowerCase().trim()]);
    if (!g.rows.length) return bad(res, 404, "groep niet gevonden, check de code");
    const p = await pool.query("SELECT code FROM profiles WHERE code=$1", [String(code)]);
    if (!p.rows.length) return bad(res, 404, "profiel onbekend, oefen eerst even zodat je sync-code bestaat");
    await pool.query("INSERT INTO group_members (gcode, pcode) VALUES ($1,$2) ON CONFLICT DO NOTHING", [g.rows[0].gcode, String(code)]);
    ok(res, { groep: g.rows[0] });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// POST /api/groep/weg {gcode, code} — groep verlaten
app.post("/api/groep/weg", async (req, res) => {
  const { gcode, code } = req.body || {};
  if (!gcode || !code) return bad(res, 400, "gcode en code verplicht");
  try {
    await pool.query("DELETE FROM group_members WHERE gcode=$1 AND pcode=$2", [String(gcode), String(code)]);
    ok(res, {});
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// week-hulpjes: maandag t/m zondag, in UTC
function weekDates(offsetWeeks) {
  const now = new Date();
  const dag = (now.getUTCDay() + 6) % 7; // 0 = maandag
  const maandag = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() - dag + offsetWeeks * 7);
  const out = [];
  for (let i = 0; i < 7; i++) out.push(new Date(maandag + i * 86400000).toISOString().slice(0, 10));
  return out;
}
function sumXp(state, dates) {
  const xp = (state && state.xp) || {};
  return dates.reduce((s, d) => s + (xp[d] || 0), 0);
}

// GET /api/groep/:gcode — naam + klassement (met week-race en winnaar van vorige week)
app.get("/api/groep/:gcode", async (req, res) => {
  try {
    const g = await pool.query("SELECT gcode, naam FROM groups WHERE gcode=$1", [String(req.params.gcode).toLowerCase().trim()]);
    if (!g.rows.length) return bad(res, 404, "groep niet gevonden");
    const r = await pool.query(
      "SELECT p.name, p.track, p.state, p.updated_at FROM group_members m JOIN profiles p ON p.code = m.pcode WHERE m.gcode=$1",
      [g.rows[0].gcode]);
    const vandaag = new Date().toISOString().slice(0, 10);
    const gisteren = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    const dezeWeek = weekDates(0);
    const vorigeWeekDagen = weekDates(-1);
    // eerlijke race: winnaar is wie het vaakst zijn EIGEN dagdoel haalt (relaxed 10 telt even zwaar als fanatiek 60)
    function dagenGehaald(st, dates) {
      const doel = (st && st.doel) || 30;
      const xp = (st && st.xp) || {};
      return dates.reduce((s, d) => s + ((xp[d] || 0) >= doel ? 1 : 0), 0);
    }
    // "Start je les"-flow-voltooiingen deze week: st.lesFlow is een datum->true map (client-side
    // gededupliceerd, dus een dag met meerdere herhalingen telt hier gewoon 1x mee).
    function lesDagenTellen(st, dates) {
      const lf = (st && st.lesFlow) || {};
      return dates.reduce((s, d) => s + (lf[d] ? 1 : 0), 0);
    }
    const spelers = r.rows.map((row) => {
      const st = row.state || {};
      let lessen = 0;
      if (st.lessons) for (const k in st.lessons) { if (st.lessons[k] && st.lessons[k].done) lessen++; }
      const sd = st.streak || {};
      const streak = (sd.last === vandaag || sd.last === gisteren) ? (sd.count || 0) : 0;
      const doel = st.doel || 30;
      return Object.assign({ naam: row.name, niveau: row.track, txp: st.txp || 0, streak, lessen, doel,
        weekXp: sumXp(st, dezeWeek), weekDagen: dagenGehaald(st, dezeWeek), weekLessen: lesDagenTellen(st, dezeWeek),
        vorigeXp: sumXp(st, vorigeWeekDagen), vorigeDagen: dagenGehaald(st, vorigeWeekDagen) },
        muurVelden(st));
    }).sort((a, b) => (b.weekDagen - a.weekDagen) || (b.weekXp / (a.doel * 7) - a.weekXp / (b.doel * 7)) || (b.txp - a.txp));
    // winnaar vorige week: meeste dagen eigen doel gehaald; tiebreak: % van eigen weekdoel
    let vorigeWeek = null;
    const top = [...spelers].sort((a, b) =>
      (b.vorigeDagen - a.vorigeDagen) || (b.vorigeXp / (b.doel * 7) - a.vorigeXp / (a.doel * 7)))[0];
    if (top && top.vorigeXp > 0) vorigeWeek = { winnaar: top.naam, xp: top.vorigeXp, dagen: top.vorigeDagen, week: vorigeWeekDagen[0] };
    // De reacties van vandaag en gisteren, alleen tussen leden van deze groep. Twee dagen, want de
    // muur toont ook de regel van gisteren en daar moet je nog op kunnen reageren.
    let krabbels = [];
    try {
      const namen = spelers.map((x) => String(x.naam).toLowerCase());
      const kr = await pool.query(
        `SELECT van, naar, sleutel, dag::text FROM krabbels
          WHERE dag >= current_date - 1 AND van = ANY($1) AND naar = ANY($1) ORDER BY created_at`,
        [namen]);
      krabbels = kr.rows;
    } catch (e2) { console.error(e2); }
    ok(res, { groep: g.rows[0], spelers, vorigeWeek, week: dezeWeek[0], krabbels });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

/* ================= MAATJE (v19.58) =================
   Eén iemand die meekijkt en zelf niet meeleert. Rust op de STEP UP-trial (Patel e.a., JAMA
   Internal Medicine 2019, n=602): van de drie sociale vormen daar was juist de "support"-arm,
   één aangewezen persoon die wekelijks een rapportje kreeg en zelf nergens aan meedeed, de enige
   die ná afloop nog stand hield. En het is de enige sociale mechaniek die geen tweede gebruiker
   van deze app nodig heeft, wat met een handvol gebruikers nogal uitmaakt.

   Twee ontwerpregels zitten hier in de code, niet in de tekst:
   1. Een eigen token (mcode), niet de sync-code. Zie de opmerking bij de tabel.
   2. Dit eindpunt geeft alleen GEDANE DINGEN terug, geen voornemens. Harkin e.a. (Psychological
      Bulletin 2016, meta-analyse van 138 studies) vindt d=0,40 voor het bijhouden van voortgang,
      sterker bij publieke rapportage; het zwakkere maar consistente signaal uit Gollwitzer (2009)
      wijst dezelfde kant op voor het aankondigen van plannen: doe dat niet. Dus wel "4 van de 7
      dagen gehaald", nooit "wil 5 dagen per week". */

// POST /api/maatje/nieuw {code, naam} — koppel (of vervang) het maatje van dit profiel
app.post("/api/maatje/nieuw", async (req, res) => {
  const { code, naam } = req.body || {};
  if (!code) return bad(res, 400, "code verplicht");
  const schoon = String(naam || "").trim().slice(0, 40);
  try {
    const p = await pool.query("SELECT code FROM profiles WHERE code=$1", [String(code)]);
    if (!p.rows.length) return bad(res, 404, "profiel onbekend, oefen eerst even zodat je sync-code bestaat");
    // hoogstens één maatje per profiel: een nieuwe koppeling maakt de oude link meteen dood
    await pool.query("DELETE FROM maatjes WHERE pcode=$1", [String(code)]);
    const mcode = "m" + Math.random().toString(36).slice(2, 9);
    await pool.query("INSERT INTO maatjes (mcode, pcode, naam) VALUES ($1,$2,$3)", [mcode, String(code), schoon]);
    ok(res, { maatje: { mcode, naam: schoon } });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// POST /api/maatje/weg {code} — maatje loskoppelen; de link werkt daarna niet meer
app.post("/api/maatje/weg", async (req, res) => {
  const { code } = req.body || {};
  if (!code) return bad(res, 400, "code verplicht");
  try {
    await pool.query("DELETE FROM maatjes WHERE pcode=$1", [String(code)]);
    ok(res, {});
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// GET /api/maatje/:mcode — het weekbericht. Bewust smal: naam, en vijf getallen. Geen state.
app.get("/api/maatje/:mcode", async (req, res) => {
  try {
    const m = await pool.query("SELECT mcode, pcode, naam FROM maatjes WHERE mcode=$1",
      [String(req.params.mcode).toLowerCase().trim()]);
    if (!m.rows.length) return bad(res, 404, "deze link bestaat niet (meer)");
    const r = await pool.query("SELECT name, state FROM profiles WHERE code=$1", [m.rows[0].pcode]);
    if (!r.rows.length) return bad(res, 404, "profiel niet gevonden");
    const st = r.rows[0].state || {};
    const xp = st.xp || {};
    const lf = st.lesFlow || {};
    const doel = st.doel || 30;
    const vandaag = new Date().toISOString().slice(0, 10);
    const gisteren = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    const sd = st.streak || {};
    function week(offset) {
      const dates = weekDates(offset);
      return {
        start: dates[0],
        dagen: dates.reduce((s, d) => s + ((xp[d] || 0) >= doel ? 1 : 0), 0),
        lessen: dates.reduce((s, d) => s + (lf[d] ? 1 : 0), 0),
        // per dag: false = niets gedaan, true = dagdoel gehaald, "iets" = wel geoefend, doel niet gehaald
        dagelijks: dates.map((d) => ((xp[d] || 0) >= doel ? true : ((xp[d] || 0) > 0 ? "iets" : false)))
      };
    }
    ok(res, {
      leerling: r.rows[0].name,
      maatje: m.rows[0].naam,
      streak: (sd.last === vandaag || sd.last === gisteren) ? (sd.count || 0) : 0,
      woorden: Object.keys(st.srs || {}).length,
      week: week(0),
      vorige: week(-1)
    });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

/* POST /api/admin/llm?key=ADMIN_KEY  {prompt, maxTokens, jsonMode}
 * De avondrun (tools/curriculum.js) draait op GitHub Actions en heeft dus géén LLM-sleutels: die staan
 * hier op Render. De ladder in llm.js staat hier ook al. In plaats van dezelfde sleutels op een tweede
 * plek te zetten leent de nachtrun deze ingang, met de ADMIN_KEY die er voor het logboek al is.
 * Eén sleutel, één plek waar hij ligt, en één plek waar het LLM-verkeer langsgaat (inclusief de
 * bestaande rate-limiter en cooldowns van llm.js).
 * Bewust geen open ingang: zonder ADMIN_KEY geen antwoord, en de prompt wordt begrensd zodat dit geen
 * gratis LLM-doorgeefluik kan worden als de sleutel ooit uitlekt.
 */
app.post("/api/admin/llm", async (req, res) => {
  if (!process.env.ADMIN_KEY || req.query.key !== process.env.ADMIN_KEY) return bad(res, 403, "geen toegang");
  const { prompt, maxTokens, jsonMode } = req.body || {};
  if (!prompt || typeof prompt !== "string") return bad(res, 400, "prompt verplicht");
  if (prompt.length > 20000) return bad(res, 400, "prompt te lang");
  try {
    const txt = await vraagLadder("", prompt, Math.min(8000, maxTokens || 4000), !!jsonMode, "admin-llm");
    ok(res, { tekst: txt });
  } catch (e) {
    console.error("admin-llm:", e.message);
    badReden(res, 502, "AI-fout", "stuk");
  }
});

// GET /api/admin/schoon?key=ADMIN_KEY — verwijder lege profielen (0 XP); echte apparaten syncen zichzelf gewoon opnieuw aan
app.get("/api/admin/schoon", async (req, res) => {
  if (!process.env.ADMIN_KEY || req.query.key !== process.env.ADMIN_KEY) return bad(res, 403, "geen toegang");
  try {
    const r = await pool.query("DELETE FROM profiles WHERE COALESCE((state->>'txp')::int, 0) = 0 RETURNING name, code");
    ok(res, { verwijderd: r.rows.length, profielen: r.rows.map((x) => x.name) });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// GET /api/admin/terugkomst?key=... -> komen ze terug op dag 2?
//
// Stefan, 13 aug, op de vraag wat hij als eerste van een vreemde wil weten: "terugkomt op dag 2".
// Dat is te meten zonder iets te bouwen, want het staat er al. S.xp is een map van datum naar
// punten, dus de sleutels zijn precies de dagen waarop iemand iets heeft gedaan, en /api/sync zet
// die hele state hier neer.
//
// Twee getallen, want er zijn twee eerlijke definities en ze zeggen iets anders:
//
//   terug_dag2  actief op de kalenderdag ná de eerste. Streng, en dat is met opzet: dit is de
//               vraag "heeft de app een plek in zijn dag gekregen".
//   terug_week  ooit een tweede dag binnen zeven dagen. Milder, en dichter bij wat je wil weten
//               van iemand die vrijdagavond begint en zondag terugkomt.
//
// De eerste dag komt uit de data en niet uit created_at: dat is de dag waarop iemand écht iets
// deed, en niet de dag waarop er een rij is aangemaakt. Wie zich aanmeldt en meteen weggaat, telt
// hier dus niet mee als starter, en dat hoort ook niet.
app.get("/api/admin/terugkomst", async (req, res) => {
  if (!process.env.ADMIN_KEY || req.query.key !== process.env.ADMIN_KEY) return bad(res, 403, "geen toegang");
  try {
    const r = await pool.query(`
      WITH d AS (
        SELECT code,
               (SELECT min(k) FROM jsonb_object_keys(state->'xp') k)::date AS dag1,
               (SELECT count(*) FROM jsonb_object_keys(state->'xp'))       AS dagen,
               (SELECT array_agg(k::date) FROM jsonb_object_keys(state->'xp') k) AS lijst
          FROM profiles
         WHERE jsonb_typeof(state->'xp') = 'object'
           AND (SELECT count(*) FROM jsonb_object_keys(state->'xp')) > 0
      )
      SELECT dag1,
             count(*)                                                        AS starters,
             count(*) FILTER (WHERE dag1 + 1 = ANY(lijst))                   AS terug_dag2,
             count(*) FILTER (WHERE EXISTS (
               SELECT 1 FROM unnest(lijst) x WHERE x > dag1 AND x <= dag1 + 7
             ))                                                              AS terug_week,
             round(avg(dagen), 2)                                            AS dagen_gem
        FROM d
       GROUP BY dag1
       ORDER BY dag1 DESC
       LIMIT 30
    `);
    const rijen = r.rows.map((x) => ({
      dag1: x.dag1, starters: Number(x.starters),
      terugDag2: Number(x.terug_dag2), terugWeek: Number(x.terug_week),
      dagenGem: Number(x.dagen_gem),
      pctDag2: Number(x.starters) ? Math.round((Number(x.terug_dag2) / Number(x.starters)) * 100) : 0,
      pctWeek: Number(x.starters) ? Math.round((Number(x.terug_week) / Number(x.starters)) * 100) : 0
    }));
    const tot = rijen.reduce((a, x) => ({
      starters: a.starters + x.starters, dag2: a.dag2 + x.terugDag2, week: a.week + x.terugWeek
    }), { starters: 0, dag2: 0, week: 0 });
    ok(res, {
      perDag: rijen,
      totaal: Object.assign(tot, {
        pctDag2: tot.starters ? Math.round((tot.dag2 / tot.starters) * 100) : 0,
        pctWeek: tot.starters ? Math.round((tot.week / tot.starters) * 100) : 0
      })
    });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// ---- AI-feedback via de LLM-ladder (goedkoop eerst, duur als vangnet) ----
async function vraagLadder(system, user, maxTokens, jsonMode, callSite) {
  const res = await reason(system + "\n\n" + user, { maxTokens: maxTokens || 400, jsonMode: !!jsonMode, callSite });
  if (!res) throw new Error("alle LLM-tredes uitgeput");
  return res.text;
}

// POST /api/ai/check {nl, verwacht, gegeven}
// Beoordeelt of een afwijkende vertaling tóch goed Spaans is.
app.post("/api/ai/check", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { nl, verwacht, gegeven } = req.body || {};
  if (!nl || !gegeven) return bad(res, 400, "nl en gegeven verplicht");
  try {
    const txt = await vraagLadder(
      "Je beoordeelt antwoorden in een Spaanse leerapp voor Nederlandstaligen (niveau A0-A2). " +
      "Antwoord UITSLUITEND met geldige JSON: {\"goed\": true/false, \"uitleg\": \"korte uitleg in het Nederlands (max 2 zinnen)\"}. " +
      "Wees streng op grammatica maar accepteer natuurlijke alternatieven (andere woordvolgorde, synoniemen, weglaten van onderwerp). " +
      "Kleine accentfouten: goed=true maar benoem ze in de uitleg.",
      "Nederlandse zin: \"" + String(nl).slice(0, 300) + "\"\nModelantwoord: \"" +
        String(verwacht || "-").slice(0, 300) + "\"\nAntwoord van de leerling: \"" +
        String(gegeven).slice(0, 300) + "\"\nIs het antwoord van de leerling correct Spaans voor deze zin?",
      250, true, "ai-check"
    );
    const m = txt.match(/\{[\s\S]*\}/);
    if (!m) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
    const parsed = JSON.parse(m[0]);
    ok(res, { goed: !!parsed.goed, uitleg: String(parsed.uitleg || "").slice(0, 500) });
  } catch (e) {
    console.error(e);
    badReden(res, 502, "AI-fout", "stuk");
  }
});

// POST /api/ai/zin {woord, zin}
// Schrijfoefening: beoordeel of de leerling het woord goed gebruikt in een eigen zin.
app.post("/api/ai/zin", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { woord, zin } = req.body || {};
  if (!woord || !zin) return bad(res, 400, "woord en zin verplicht");
  try {
    const txt = await vraagLadder(
      "Je beoordeelt een schrijfoefening in een Spaanse leerapp voor Nederlandstaligen (A0-A2). De leerling moest een eigen " +
      "Spaanse zin maken met een doelwoord. Antwoord UITSLUITEND met geldige JSON: " +
      "{\"goed\": true/false, \"uitleg\": \"korte reactie in het Nederlands, max 2 zinnen, warm en concreet\"}. " +
      "goed=true als het doelwoord correct gebruikt is en de zin begrijpelijk Spaans is (kleine fouten mogen, benoem ze in de uitleg). " +
      "goed=false alleen als het doelwoord verkeerd gebruikt is of de zin geen begrijpelijk Spaans is.",
      "Doelwoord: \"" + woord + "\"\nZin van de leerling: \"" + zin + "\"",
      250, true, "ai-zin"
    );
    const m = txt.match(/\{[\s\S]*\}/);
    if (!m) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
    const parsed = JSON.parse(m[0]);
    ok(res, { goed: !!parsed.goed, uitleg: String(parsed.uitleg || "").slice(0, 500) });
  } catch (e) {
    console.error(e);
    badReden(res, 502, "AI-fout", "stuk");
  }
});

// POST /api/ai/uitleg {vraag, context}
// "Leg uit waarom"-knop: korte NL-uitleg over een grammaticapunt.
app.post("/api/ai/uitleg", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { vraag, context } = req.body || {};
  if (!vraag) return bad(res, 400, "vraag verplicht");
  try {
    const txt = await vraagLadder(
      "Je bent een geduldige Spaanse-taaldocent voor Nederlandstaligen (A0-A2). Antwoord in eenvoudig Nederlands, " +
      "maximaal 120 woorden, met één concreet voorbeeld. Geen opsommingstekens, gewoon lopende tekst.",
      (context ? "Context uit de oefening: " + String(context).slice(0, 600) + "\n\n" : "") +
        "Vraag van de leerling: " + String(vraag).slice(0, 400),
      350, false, "ai-uitleg"
    );
    ok(res, { uitleg: txt.slice(0, 1200) });
  } catch (e) {
    console.error(e);
    badReden(res, 502, "AI-fout", "stuk");
  }
});

const port = process.env.PORT || 10000;
init()
  .then(() => app.listen(port, () => console.log("¡Vamos! API draait op poort " + port)))
  .catch((e) => { console.error("init faalde:", e); process.exit(1); });
