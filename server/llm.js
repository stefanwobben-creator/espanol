/*
 * LLM-redenering via een getrapte ladder — goedkoop eerst, duur als vangnet.
 * Node-port van Stefans Python-ladder. Eén ingang: reason(prompt, opts).
 *
 * Env:
 *   GEMINI_API_KEY (of GOOGLE_API_KEY), MISTRAL_API_KEY, ANTHROPIC_API_KEY,
 *   optioneel OPENAI_API_KEY / OPENROUTER_API_KEY
 *   LLM_LADDER            — "vendor:model,vendor:model" (leeg = default)
 *   LLM_MAX_PER_MINUTE    — default 10 (0 = geen limiet)
 *   LLM_TIER_COOLDOWN_S   — default 1800
 *
 * Ontwerpregels (zoals het origineel):
 * - Fail-closed: geen werkende trede → null; caller valt terug op eigen heuristiek.
 * - Geen sleutel = trede overslaan.
 * - Rate-limit/quota → trede in cooldown, door naar de volgende.
 * - Throttle: glijdend-venster begrenzer over alle calls heen.
 */

const DEFAULT_LADDER = "gemini:gemini-2.5-flash-lite,mistral:mistral-small-latest,gemini:gemini-2.5-flash,anthropic:claude-haiku-4-5";
const RATE_MARKERS = ["429", "resource_exhausted", "rate limit", "quota", "exhausted"];
const HTTP_TIMEOUT_MS = 30000;

const OPENAI_COMPAT = {
  mistral:    { base: "https://api.mistral.ai/v1",    env: "MISTRAL_API_KEY" },
  openai:     { base: "https://api.openai.com/v1",    env: "OPENAI_API_KEY" },
  openrouter: { base: "https://openrouter.ai/api/v1", env: "OPENROUTER_API_KEY" },
};

class RateLimitErr extends Error {}

function isRateLimit(msg) {
  const s = String(msg || "").toLowerCase();
  return RATE_MARKERS.some((m) => s.includes(m));
}

// ── throttle: glijdend venster ────────────────────────────────────────────────
const calls = [];
function maxPerMinute() {
  const n = parseInt(process.env.LLM_MAX_PER_MINUTE || "10", 10);
  return Number.isFinite(n) ? n : 10;
}
async function acquire() {
  const max = maxPerMinute();
  if (max <= 0) return;
  for (;;) {
    const now = Date.now();
    while (calls.length && calls[0] <= now - 60000) calls.shift();
    if (calls.length < max) { calls.push(now); return; }
    const wait = calls[0] + 60000 - now;
    await new Promise((r) => setTimeout(r, Math.max(wait, 50)));
  }
}

// ── cooldown per trede ────────────────────────────────────────────────────────
const cooldown = new Map(); // tier -> until (ms epoch)
function cooldownMs() {
  const s = parseFloat(process.env.LLM_TIER_COOLDOWN_S || "1800");
  return (Number.isFinite(s) ? s : 1800) * 1000;
}
function inCooldown(tier) {
  const until = cooldown.get(tier);
  if (!until) return false;
  if (Date.now() >= until) { cooldown.delete(tier); return false; }
  return true;
}
function setCooldown(tier) { cooldown.set(tier, Date.now() + cooldownMs()); }

// ── fetch met timeout ─────────────────────────────────────────────────────────
async function jfetch(url, init) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), HTTP_TIMEOUT_MS);
  try {
    const r = await fetch(url, { ...init, signal: ctl.signal });
    const text = await r.text();
    if (!r.ok) {
      if (r.status === 429 || isRateLimit(text)) throw new RateLimitErr("HTTP " + r.status);
      throw new Error("HTTP " + r.status + ": " + text.slice(0, 200));
    }
    return JSON.parse(text);
  } finally { clearTimeout(t); }
}

// ── vendor-treden ─────────────────────────────────────────────────────────────
async function tryGemini(model, prompt, { maxTokens, jsonMode }) {
  const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!key) return null;
  const gen = { maxOutputTokens: maxTokens };
  if (jsonMode) {
    gen.responseMimeType = "application/json";
    gen.thinkingConfig = { thinkingBudget: 0 }; // denk-tokens niet van het output-plafond laten snoepen
  }
  const data = await jfetch(
    "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + key,
    { method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: gen }) }
  );
  const parts = data && data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts;
  const text = (parts || []).map((p) => p.text || "").join("").trim();
  return text || null;
}

async function tryOpenAICompat(vendor, model, prompt, { maxTokens, jsonMode }) {
  const reg = OPENAI_COMPAT[vendor];
  const key = process.env[reg.env];
  if (!key) return null;
  if (!model) return null; // pure config vendor zonder model → overslaan
  const payload = { model, messages: [{ role: "user", content: prompt }], max_tokens: maxTokens };
  if (jsonMode) payload.response_format = { type: "json_object" };
  const data = await jfetch(reg.base + "/chat/completions", {
    method: "POST",
    headers: { authorization: "Bearer " + key, "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
  const text = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content || "").trim();
  return text || null;
}

async function tryAnthropic(model, prompt, { maxTokens }) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return null;
  const data = await jfetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({ model, max_tokens: maxTokens, messages: [{ role: "user", content: prompt }] }),
  });
  const text = ((data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("")).trim();
  return text || null;
}

const DEFAULT_MODELS = { gemini: "gemini-2.5-flash-lite", mistral: "mistral-small-latest", anthropic: "claude-haiku-4-5" };

function parseLadder(raw) {
  return raw.split(",").map((s) => s.trim()).filter(Boolean).map((spec) => {
    const i = spec.indexOf(":");
    if (i === -1) return { vendor: spec.toLowerCase(), model: null };
    return { vendor: spec.slice(0, i).trim().toLowerCase(), model: spec.slice(i + 1).trim() || null };
  });
}

function hasKey(vendor) {
  if (vendor === "gemini") return !!(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY);
  if (vendor === "anthropic") return !!process.env.ANTHROPIC_API_KEY;
  const reg = OPENAI_COMPAT[vendor];
  return reg ? !!process.env[reg.env] : false;
}

async function callTier(vendor, model, prompt, opts) {
  const m = model || DEFAULT_MODELS[vendor] || null;
  if (vendor === "gemini") return tryGemini(m, prompt, opts);
  if (vendor === "anthropic") return tryAnthropic(m, prompt, opts);
  if (OPENAI_COMPAT[vendor]) return tryOpenAICompat(vendor, m, prompt, opts);
  console.warn("llm: onbekende vendor in ladder:", vendor);
  return null;
}

/**
 * reason(prompt, {maxTokens=400, jsonMode=false, ladder=null, callSite="onbekend"})
 * → {text, tier} of null (fail-closed).
 */
async function reason(prompt, opts) {
  const o = { maxTokens: 400, jsonMode: false, ladder: null, callSite: "onbekend", ...(opts || {}) };
  await acquire();
  const steps = parseLadder(o.ladder || process.env.LLM_LADDER || DEFAULT_LADDER);
  const outcomes = [];
  for (const { vendor, model } of steps) {
    const tier = vendor + ":" + (model || "default");
    if (inCooldown(tier)) { outcomes.push(tier + "=cooldown"); continue; }
    if (!hasKey(vendor)) { outcomes.push(tier + "=geen sleutel"); continue; }
    try {
      const text = await callTier(vendor, model, prompt, o);
      if (text) {
        console.log("llm [" + o.callSite + "] prompt=" + prompt.length + " tekens → " + tier);
        return { text, tier };
      }
      outcomes.push(tier + "=lege respons");
    } catch (e) {
      if (e instanceof RateLimitErr || isRateLimit(e.message)) {
        setCooldown(tier);
        outcomes.push(tier + "=429/cooldown");
      } else {
        console.warn("llm-trede " + tier + " faalde:", e.message);
        outcomes.push(tier + "=fout");
      }
    }
  }
  console.warn("llm [" + o.callSite + "]: alle tredes uitgeput — " + (outcomes.join("; ") || "geen tredes"));
  return null;
}

module.exports = { reason };
