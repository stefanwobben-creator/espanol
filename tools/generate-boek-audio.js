/*
 * Genereert echte, vloeiende Spaanse audio (via ElevenLabs) voor alle 13 hoofdstukken van het
 * Chispa-boek ("Las Crónicas de Chispa"), en slaat ze op als statische mp3's onder
 * audio/boek/<hoofdstuk-id>.mp3 — één bestand per hoofdstuk (het hele verhaal voorgelezen als
 * mini-luisterboek, in plaats van los per zin zoals bij Dictado).
 *
 * Zelfde aanpak als tools/generate-dictado-audio.js: dit script draai je ÉÉN keer lokaal (of
 * opnieuw als er nieuwe hoofdstukken bijkomen), de resulterende mp3's committen we mee in de
 * repo, en GitHub Pages serveert ze daarna gratis en statisch. De app zelf valt automatisch
 * terug op browser-TTS zolang een bestand nog ontbreekt (zie boekSpreek() in index.html) — dit
 * script is dus optioneel, de Lezen-tab werkt ook zonder.
 *
 * GEBRUIK
 *   1. Zelfde ElevenLabs-account/voice-id als voor Dictado (of een andere stem als je liever een
 *      verteller-achtige stem wil voor het boek dan voor de dictee-oefeningen — zie
 *      https://elevenlabs.io/app/voice-library).
 *   2. Zet de omgevingsvariabelen en draai vanaf de repo-root:
 *        export ELEVENLABS_API_KEY="sk_..."
 *        export ELEVENLABS_VOICE_ID="..."
 *        node tools/generate-boek-audio.js
 *   3. Controleer een paar hoofdstukken in audio/boek/ door ze af te spelen (bijv. audio/boek/boek-1.mp3).
 *   4. Commit + push de nieuwe/gewijzigde mp3's mee.
 *
 * Idempotent: bestaande mp3's worden overgeslagen, dus opnieuw draaien na een nieuw hoofdstuk
 * kost alleen tekens voor dat ene hoofdstuk.
 *
 * Kosten: 13 hoofdstukken van ~800-1700 tekens elk, in totaal ~16.500 tekens — dit is MEER dan
 * de gratis ElevenLabs-laag (~10.000 tekens/maand) in één keer, dus dit loopt waarschijnlijk in
 * 2 maandelijkse porties, of in één keer met een betaald plan. Het script is idempotent, dus je
 * kan het gewoon een tweede keer draaien zodra je quota ververst is — al gegenereerde
 * hoofdstukken worden overgeslagen.
 *
 * Vereist: Node.js 18+ (voor de ingebouwde fetch).
 */

const fs = require("fs");
const path = require("path");

const API_KEY = process.env.ELEVENLABS_API_KEY;
const VOICE_ID = process.env.ELEVENLABS_VOICE_ID;
const MODEL_ID = process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2";
const REPO_ROOT = path.join(__dirname, "..");
const HTML_PAD = path.join(REPO_ROOT, "index.html");
const OUT_DIR = path.join(REPO_ROOT, "audio", "boek");

if(!API_KEY){
  console.error("Zet eerst ELEVENLABS_API_KEY (zie de uitleg bovenin dit bestand).");
  process.exit(1);
}
if(!VOICE_ID){
  console.error("Zet eerst ELEVENLABS_VOICE_ID: kies een stem in https://elevenlabs.io/app/voice-library en kopieer de voice-id.");
  process.exit(1);
}

// Leest "var BOOK = [...]" rechtstreeks uit index.html (zelfde aanpak als generate-dictado-audio.js
// voor SENTENCES), zodat dit script nooit los kan raken van de daadwerkelijke boekinhoud. We tellen
// vierkante haken om het einde van de array te vinden en evalueren dan alleen dat stukje.
function leesArrayLiteral(src, varNaam){
  const startIdx = src.indexOf("var " + varNaam + " = [");
  if(startIdx === -1) throw new Error("Kon 'var " + varNaam + " = [' niet vinden in index.html");
  const afterEq = src.indexOf("=", startIdx) + 1;
  let depth = 0, started = false, endIdx = -1;
  for(let i = afterEq; i < src.length; i++){
    if(src[i] === "["){ depth++; started = true; }
    else if(src[i] === "]"){ depth--; if(started && depth === 0){ endIdx = i + 1; break; } }
  }
  if(endIdx === -1) throw new Error("Kon het einde van " + varNaam + " niet vinden (haakjes niet gebalanceerd?)");
  // eslint-disable-next-line no-eval
  return eval(src.slice(afterEq, endIdx));
}

function leesHoofdstukken(){
  const html = fs.readFileSync(HTML_PAD, "utf8");
  const m = html.match(/<script>([\s\S]*)<\/script>/);
  if(!m) throw new Error("Kon geen <script>-blok vinden in index.html");
  return leesArrayLiteral(m[1], "BOOK");
}

async function genereerEen(hoofdstuk){
  const outPath = path.join(OUT_DIR, hoofdstuk.id + ".mp3");
  if(fs.existsSync(outPath)) return "skip";
  // \n\n scheidt alinea's in de brondata (voor het opsplitsen in <p>-tags in de app) — voor
  // de voorleestekst maken we er gewone regelovergangen van, ElevenLabs pakt de pauzes vanzelf
  // op via de leestekens (punten, gedachtestreepjes bij dialoog).
  const tekst = hoofdstuk.tekst.replace(/\n\n/g, "\n");
  const res = await fetch("https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID, {
    method: "POST",
    headers: {
      "xi-api-key": API_KEY,
      "Content-Type": "application/json",
      "Accept": "audio/mpeg"
    },
    body: JSON.stringify({
      text: tekst,
      model_id: MODEL_ID,
      voice_settings: { stability: 0.5, similarity_boost: 0.75 }
    })
  });
  if(!res.ok){
    const responstekst = await res.text().catch(function(){ return ""; });
    throw new Error("HTTP " + res.status + " voor " + hoofdstuk.id + ": " + responstekst.slice(0, 200));
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(outPath, buf);
  return "ok";
}

async function main(){
  const hoofdstukken = leesHoofdstukken();
  console.log("Gevonden hoofdstukken (BOOK): " + hoofdstukken.length);
  if(!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  let nieuw = 0, overgeslagen = 0, mislukt = 0;
  for(const h of hoofdstukken){
    try{
      const r = await genereerEen(h);
      if(r === "ok"){ nieuw++; console.log("✓ " + h.id + " - " + h.titel + " (" + h.tekst.length + " tekens)"); }
      else { overgeslagen++; console.log("· " + h.id + " - al aanwezig, overgeslagen"); }
    }catch(e){
      mislukt++;
      console.error("✗ " + h.id + " - " + e.message);
    }
    // kleine pauze tussen requests, aardig voor de API en voorkomt rate-limit-gedoe
    await new Promise(function(r){ setTimeout(r, 400); });
  }
  console.log("");
  console.log("Klaar: " + nieuw + " nieuw gegenereerd, " + overgeslagen + " al bestaand overgeslagen, " + mislukt + " mislukt.");
  if(mislukt > 0){
    console.log("Draai het script gerust nog eens (bijv. na een quota-reset): het is idempotent en probeert alleen ontbrekende bestanden opnieuw.");
    process.exitCode = 1;
  }
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
