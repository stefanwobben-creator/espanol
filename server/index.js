/*
 * ¡Vamos! API — profielsync, foutenlogs en AI-feedback
 *
 * Omgevingsvariabelen (in Render instellen):
 *   DATABASE_URL      — Neon connection string (postgresql://...)
 *   ANTHROPIC_API_KEY — sleutel van console.anthropic.com (voor /api/ai/*)
 *   ADMIN_KEY         — zelfverzonnen lang wachtwoord; nodig om alle logs uit te lezen
 *   ALLOWED_ORIGIN    — standaard https://vamos.stefanwobben.nl
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
    if (!m) return bad(res, 502, "onleesbaar AI-antwoord");
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

// ---- gezondheid ----
app.get("/health", (_req, res) => ok(res, { tijd: new Date().toISOString() }));

// ---- profielsync ----
// POST /api/sync  {code, name, track, state}
// Upsert op code. 'code' is de geheime profielcode die de app genereert.
app.post("/api/sync", async (req, res) => {
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

// GET /api/familia — scorebord van ALLEEN de familie (FAMILIA_NAMEN env, default stefan/elise/ilona).
// Vroeger toonde dit alle profielen; sinds de app openbaar deelbaar is, is dat expres dichtgezet.
app.get("/api/familia", async (_req, res) => {
  try {
    const namen = String(process.env.FAMILIA_NAMEN || "stefan,elise,ilona")
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
    ok(res, { spelers: lijst });
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
    const spelers = r.rows.map((row) => {
      const st = row.state || {};
      let lessen = 0;
      if (st.lessons) for (const k in st.lessons) { if (st.lessons[k] && st.lessons[k].done) lessen++; }
      const sd = st.streak || {};
      const streak = (sd.last === vandaag || sd.last === gisteren) ? (sd.count || 0) : 0;
      const doel = st.doel || 30;
      return { naam: row.name, niveau: row.track, txp: st.txp || 0, streak, lessen, doel,
        weekXp: sumXp(st, dezeWeek), weekDagen: dagenGehaald(st, dezeWeek),
        vorigeXp: sumXp(st, vorigeWeekDagen), vorigeDagen: dagenGehaald(st, vorigeWeekDagen) };
    }).sort((a, b) => (b.weekDagen - a.weekDagen) || (b.weekXp / (a.doel * 7) - a.weekXp / (b.doel * 7)) || (b.txp - a.txp));
    // winnaar vorige week: meeste dagen eigen doel gehaald; tiebreak: % van eigen weekdoel
    let vorigeWeek = null;
    const top = [...spelers].sort((a, b) =>
      (b.vorigeDagen - a.vorigeDagen) || (b.vorigeXp / (b.doel * 7) - a.vorigeXp / (a.doel * 7)))[0];
    if (top && top.vorigeXp > 0) vorigeWeek = { winnaar: top.naam, xp: top.vorigeXp, dagen: top.vorigeDagen, week: vorigeWeekDagen[0] };
    ok(res, { groep: g.rows[0], spelers, vorigeWeek, week: dezeWeek[0] });
  } catch (e) { console.error(e); bad(res, 500, "database-fout"); }
});

// GET /api/admin/schoon?key=ADMIN_KEY — verwijder lege profielen (0 XP); echte apparaten syncen zichzelf gewoon opnieuw aan
app.get("/api/admin/schoon", async (req, res) => {
  if (!process.env.ADMIN_KEY || req.query.key !== process.env.ADMIN_KEY) return bad(res, 403, "geen toegang");
  try {
    const r = await pool.query("DELETE FROM profiles WHERE COALESCE((state->>'txp')::int, 0) = 0 RETURNING name, code");
    ok(res, { verwijderd: r.rows.length, profielen: r.rows.map((x) => x.name) });
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
  const { nl, verwacht, gegeven } = req.body || {};
  if (!nl || !gegeven) return bad(res, 400, "nl en gegeven verplicht");
  try {
    const txt = await vraagLadder(
      "Je beoordeelt antwoorden in een Spaanse leerapp voor Nederlandstaligen (niveau A0-A2). " +
      "Antwoord UITSLUITEND met geldige JSON: {\"goed\": true/false, \"uitleg\": \"korte uitleg in het Nederlands (max 2 zinnen)\"}. " +
      "Wees streng op grammatica maar accepteer natuurlijke alternatieven (andere woordvolgorde, synoniemen, weglaten van onderwerp). " +
      "Kleine accentfouten: goed=true maar benoem ze in de uitleg.",
      "Nederlandse zin: \"" + nl + "\"\nModelantwoord: \"" + (verwacht || "-") + "\"\nAntwoord van de leerling: \"" + gegeven + "\"\nIs het antwoord van de leerling correct Spaans voor deze zin?",
      250, true, "ai-check"
    );
    const m = txt.match(/\{[\s\S]*\}/);
    if (!m) return bad(res, 502, "onleesbaar AI-antwoord");
    const parsed = JSON.parse(m[0]);
    ok(res, { goed: !!parsed.goed, uitleg: String(parsed.uitleg || "").slice(0, 500) });
  } catch (e) {
    console.error(e);
    bad(res, 502, "AI-fout");
  }
});

// POST /api/ai/zin {woord, zin}
// Schrijfoefening: beoordeel of de leerling het woord goed gebruikt in een eigen zin.
app.post("/api/ai/zin", async (req, res) => {
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
    if (!m) return bad(res, 502, "onleesbaar AI-antwoord");
    const parsed = JSON.parse(m[0]);
    ok(res, { goed: !!parsed.goed, uitleg: String(parsed.uitleg || "").slice(0, 500) });
  } catch (e) {
    console.error(e);
    bad(res, 502, "AI-fout");
  }
});

// POST /api/ai/uitleg {vraag, context}
// "Leg uit waarom"-knop: korte NL-uitleg over een grammaticapunt.
app.post("/api/ai/uitleg", async (req, res) => {
  const { vraag, context } = req.body || {};
  if (!vraag) return bad(res, 400, "vraag verplicht");
  try {
    const txt = await vraagLadder(
      "Je bent een geduldige Spaanse-taaldocent voor Nederlandstaligen (A0-A2). Antwoord in eenvoudig Nederlands, " +
      "maximaal 120 woorden, met één concreet voorbeeld. Geen opsommingstekens, gewoon lopende tekst.",
      (context ? "Context uit de oefening: " + context + "\n\n" : "") + "Vraag van de leerling: " + vraag,
      350, false, "ai-uitleg"
    );
    ok(res, { uitleg: txt.slice(0, 1200) });
  } catch (e) {
    console.error(e);
    bad(res, 502, "AI-fout");
  }
});

const port = process.env.PORT || 10000;
init()
  .then(() => app.listen(port, () => console.log("¡Vamos! API draait op poort " + port)))
  .catch((e) => { console.error("init faalde:", e); process.exit(1); });
