#!/usr/bin/env python3
# De AI-eindpunten op slot, vóór de lancering.
#
# Wat er nu staat: /api/ai/check, /api/ai/zin en /api/ai/uitleg zijn open. Er is wel een
# ALLOWED_ORIGIN, maar die zet alleen CORS-kopteksten en die gelden in een browser. Een script met
# curl stuurt geen Origin mee en komt er gewoon langs. Elke aanroep gaat naar jouw LLM-rekening.
#
# Voor een app met één gebruiker is dat geen probleem. Vanaf vrijdag staat de URL publiek, en een
# publieke URL wordt binnen dagen gescand. Dit is het enige dat ik "niet lanceren zonder" noem.
#
# Drie sloten, in oplopende volgorde van hoe erg het is als het misgaat:
#   1. Herkomst. Een verzoek aan /api/ai/* zonder toegestane Origin wordt geweigerd. Dat houdt de
#      losse scriptjes buiten, en het kost een echte gebruiker niets: zijn browser stuurt hem mee.
#   2. Per bezoeker. Twintig AI-aanroepen per uur en zestig per dag per IP. Dat is ruim voor iemand
#      die leert (de knoppen zijn hulpmiddelen, geen oefening) en krap voor een lus.
#   3. Een dagplafond over alles heen, met een noodrem die je zonder opnieuw uitrollen kunt
#      omzetten. Dat is de rem die je 's nachts laat slapen: wat er ook gebeurt, meer dan dit kost
#      een dag niet.
#
# Bewust geen npm-pakket erbij (express-rate-limit): dat is een extra afhankelijkheid in een dienst
# die het nu met twee doet, voor twintig regels werk. De teller staat in het geheugen van het proces
# en gaat dus leeg bij een herstart. Dat is precies goed genoeg: het plafond is er om een lus te
# stoppen, niet om boekhouding te doen. Draait er ooit meer dan één instantie, dan moet dit naar de
# database; dat staat als opmerking in de code.
import pathlib, sys

SRV = pathlib.Path.home() / "espanol" / "server" / "index.js"
src = SRV.read_text(encoding="utf-8")

if "aiSlot" in src:
    print("  server/index.js staat al bij")
    sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    aantal = src.count(anker)
    assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:80])
    src = src.replace(anker, nieuw, n)

# ---------------------------------------------------------------- 1. de omgevingsvariabelen erbij
rep(""" *   ALLOWED_ORIGIN    — standaard https://vamos.stefanwobben.nl
 */""",
    """ *   ALLOWED_ORIGIN    — standaard https://vamos.stefanwobben.nl
 *   AI_PER_UUR        — AI-aanroepen per IP per uur (standaard 20)
 *   AI_PER_DAG        — AI-aanroepen per IP per dag (standaard 60)
 *   AI_DAGPLAFOND     — AI-aanroepen per dag over alle bezoekers heen (standaard 800)
 *   AI_UIT            — zet op "1" om de AI-knoppen meteen uit te zetten, zonder opnieuw uitrollen
 */""")

# ---------------------------------------------------------------- 2. het slot zelf
rep("""const pool = new Pool({""",
    """/* ================= HET SLOT OP DE AI-KNOPPEN (11 aug, vóór de lancering) =================
   Zie de kop van claude/patch-server-slot.py voor het waarom. Drie sloten: herkomst, per bezoeker,
   en een dagplafond met een noodrem.

   De tellers staan in het geheugen van dit proces en zijn dus leeg na een herstart. Dat is met
   opzet: dit is een rem op een lus en geen boekhouding. Draait deze dienst ooit op meer dan één
   instantie tegelijk, dan telt elke instantie zijn eigen bezoekers en moet dit naar de database. */
const AI_PER_UUR = Number(process.env.AI_PER_UUR || 20);
const AI_PER_DAG = Number(process.env.AI_PER_DAG || 60);
const AI_DAGPLAFOND = Number(process.env.AI_DAGPLAFOND || 800);
const aiTeller = new Map();          // ip -> {uur:[tijdstippen], dag:[tijdstippen]}
let aiDagTotaal = { dag: "", n: 0 };

function vandaagUTC() { return new Date().toISOString().slice(0, 10); }

function herkomstOk(req) {
  const o = req.headers.origin || "";
  if (!o) return false;                                   // curl en losse scripts sturen niets mee
  if (o === ORIGIN || o === "null") return true;
  if (o.endsWith(".stefanwobben.nl")) return true;
  return /^https?:\\/\\/(localhost|127\\.0\\.0\\.1)(:\\d+)?$/.test(o);
}

/* Eén functie voor alle drie de AI-ingangen, zodat er geen ingang kan zijn die hem vergeet.
   Geeft null als het mag, en anders een {code, tekst} om terug te sturen. */
function aiSlot(req) {
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
}

// Zodat je kunt zien of het plafond in de buurt komt zonder in de logs te graven.
function aiStand() {
  return { dag: aiDagTotaal.dag, gebruikt: aiDagTotaal.n, plafond: AI_DAGPLAFOND,
           bezoekers: aiTeller.size, uit: process.env.AI_UIT === "1" };
}

const pool = new Pool({""")

# ---------------------------------------------------------------- 3. het slot op de drie ingangen
for naam, eis in [
  ("check", """  const { nl, verwacht, gegeven } = req.body || {};
  if (!nl || !gegeven) return bad(res, 400, "nl en gegeven verplicht");"""),
  ("zin", None),
  ("uitleg", """  const { vraag, context } = req.body || {};
  if (!vraag) return bad(res, 400, "vraag verplicht");"""),
]:
    pass  # de drie worden hieronder los gedaan, want hun eerste regels verschillen

rep("""app.post("/api/ai/check", async (req, res) => {
  const { nl, verwacht, gegeven } = req.body || {};""",
    """app.post("/api/ai/check", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return bad(res, slot.code, slot.tekst);
  const { nl, verwacht, gegeven } = req.body || {};""")

rep("""app.post("/api/ai/zin", async (req, res) => {""",
    """app.post("/api/ai/zin", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return bad(res, slot.code, slot.tekst);""")

rep("""app.post("/api/ai/uitleg", async (req, res) => {
  const { vraag, context } = req.body || {};""",
    """app.post("/api/ai/uitleg", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return bad(res, slot.code, slot.tekst);
  const { vraag, context } = req.body || {};""")

# ---------------------------------------------------------------- 4. invoer begrenzen
# Een lange invoer is een dure invoer: het model rekent per teken. De app stuurt nooit meer dan een
# zin, dus dit raakt alleen wie iets anders probeert.
rep("""      "Nederlandse zin: \\"" + nl + "\\"\\nModelantwoord: \\"" + (verwacht || "-") + "\\"\\nAntwoord van de leerling: \\"" + gegeven + "\\"\\nIs het antwoord van de leerling correct Spaans voor deze zin?",""",
    """      "Nederlandse zin: \\"" + String(nl).slice(0, 300) + "\\"\\nModelantwoord: \\"" +
        String(verwacht || "-").slice(0, 300) + "\\"\\nAntwoord van de leerling: \\"" +
        String(gegeven).slice(0, 300) + "\\"\\nIs het antwoord van de leerling correct Spaans voor deze zin?",""")

rep("""      (context ? "Context uit de oefening: " + context + "\\n\\n" : "") + "Vraag van de leerling: " + vraag,""",
    """      (context ? "Context uit de oefening: " + String(context).slice(0, 600) + "\\n\\n" : "") +
        "Vraag van de leerling: " + String(vraag).slice(0, 400),""")

# ---------------------------------------------------------------- 5. een ingang om het te zien
rep("""app.get("/health", (_req, res) => ok(res, { tijd: new Date().toISOString() }));""",
    """app.get("/health", (_req, res) => ok(res, { tijd: new Date().toISOString(), ai: aiStand() }));""")

SRV.write_text(src, encoding="utf-8")
print("  server/index.js: herkomstcontrole, limiet per bezoeker, dagplafond en een noodrem")
print("\nklaar. Controleer met:  node --check server/index.js")
