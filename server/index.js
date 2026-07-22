/*
 * ¡Vamos! API — profielsync, foutenlogs en AI-feedback
 *
 * Omgevingsvariabelen (in Render instellen):
 *   DATABASE_URL      — Neon connection string (postgresql://...)
 *   ANTHROPIC_API_KEY — sleutel van console.anthropic.com (voor /api/ai/*)
 *   ADMIN_KEY         — zelfverzonnen lang wachtwoord; nodig om alle logs uit te lezen
 *   ALLOWED_ORIGIN    — standaard https://espanol.stefanwobben.nl
 */
const express = require("express");
const { Pool } = require("pg");
const { reason } = require("./llm");

const app = express();
app.use(express.json({ limit: "512kb" }));

const ORIGIN = process.env.ALLOWED_ORIGIN || "https://espanol.stefanwobben.nl";
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
  `);
}

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
    ok(res, r.rows[0]);
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
