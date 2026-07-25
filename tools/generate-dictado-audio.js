/*
 * Genereert echte, vloeiende Spaanse audio (via ElevenLabs) voor alle Dictado/Vertalen-zinnen
 * uit de app, en slaat ze op als statische mp3's onder audio/dictado/<id>.mp3.
 *
 * Waarom dit los script en niet in de app zelf: de app draait in de browser en heeft geen
 * geheime API-key om veilig te bewaren. Dit script draai je ÉÉN keer lokaal (of opnieuw als er
 * nieuwe zinnen bijkomen), en de resulterende mp3's committen we gewoon mee in de repo. GitHub
 * Pages serveert ze daarna gratis en statisch aan iedereen — geen doorlopende kosten of een
 * eigen audio-backend nodig.
 *
 * GEBRUIK
 *   1. Maak een (gratis) account op https://elevenlabs.io en haal je API-key op
 *      (Profile → API Keys).
 *   2. Kies een Spaanse stem: ga naar https://elevenlabs.io/app/voice-library, zoek op
 *      "Spanish" of "Spain" en voeg een stem toe die je bevalt (Castiliaans-Spaans klinkt het
 *      meest bij de rest van de app). Kopieer de voice-id (staat in de URL/voice-instellingen).
 *   3. Zet beide als omgevingsvariabele en draai het script vanaf de repo-root:
 *        export ELEVENLABS_API_KEY="sk_..."
 *        export ELEVENLABS_VOICE_ID="..."
 *        node tools/generate-dictado-audio.js
 *   4. Controleer een paar bestanden in audio/dictado/ door ze even af te spelen.
 *   5. Commit + push de nieuwe/gewijzigde mp3's mee met de rest van je wijzigingen.
 *
 * Het script is idempotent: bestaande mp3's worden overgeslagen. Na een nachttaak die nieuwe
 * zinnen toevoegt, hoef je dit dus gewoon opnieuw te draaien — alleen de nieuwe zinnen kosten
 * dan tekens uit je ElevenLabs-quota.
 *
 * Kosten: de hele huidige zinnenset is ~86 zinnen / ~2500 tekens — ruim binnen de gratis
 * ElevenLabs-laag (~10.000 tekens/maand). Ook na een paar nachttaken met nieuwe zinnen blijft
 * dit voorlopig ruim binnen de gratis laag.
 *
 * Vereist: Node.js 18+ (voor de ingebouwde fetch — dit project gebruikt al Node >=20, zie
 * server/package.json).
 */

const fs = require("fs");
const path = require("path");

const API_KEY = process.env.ELEVENLABS_API_KEY;
const VOICE_ID = process.env.ELEVENLABS_VOICE_ID;
const MODEL_ID = process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2";
const REPO_ROOT = path.join(__dirname, "..");
const HTML_PAD = path.join(REPO_ROOT, "index.html");
const OUT_DIR = path.join(REPO_ROOT, "audio", "dictado");

if(!API_KEY){
  console.error("Zet eerst ELEVENLABS_API_KEY (zie de uitleg bovenin dit bestand).");
  process.exit(1);
}
if(!VOICE_ID){
  console.error("Zet eerst ELEVENLABS_VOICE_ID: kies een stem in https://elevenlabs.io/app/voice-library en kopieer de voice-id.");
  process.exit(1);
}

// Leest een JS-array-literal (bv. "var SENTENCES = [...]") rechtstreeks uit index.html, zodat
// dit script nooit los kan raken van de daadwerkelijke appdata. We tellen vierkante haken om het
// einde van de array te vinden en evalueren dan alleen dat stukje.
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

function leesAlleZinnen(){
  const html = fs.readFileSync(HTML_PAD, "utf8");
  const m = html.match(/<script>([\s\S]*)<\/script>/);
  if(!m) throw new Error("Kon geen <script>-blok vinden in index.html");
  const src = m[1];
  const a2 = leesArrayLiteral(src, "SENTENCES");
  const a0 = leesArrayLiteral(src, "B_SENTENCES");
  const bij = {};
  a2.concat(a0).forEach(function(s){ bij[s.id] = s; }); // dedupliceren op id, mocht dat ooit overlappen
  return Object.keys(bij).map(function(id){ return bij[id]; });
}

async function genereerEen(zin){
  const outPath = path.join(OUT_DIR, zin.id + ".mp3");
  if(fs.existsSync(outPath)) return "skip";
  const res = await fetch("https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID, {
    method: "POST",
    headers: {
      "xi-api-key": API_KEY,
      "Content-Type": "application/json",
      "Accept": "audio/mpeg"
    },
    body: JSON.stringify({
      text: zin.es,
      model_id: MODEL_ID,
      voice_settings: { stability: 0.5, similarity_boost: 0.75 }
    })
  });
  if(!res.ok){
    const tekst = await res.text().catch(function(){ return ""; });
    throw new Error("HTTP " + res.status + " voor " + zin.id + ": " + tekst.slice(0, 200));
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(outPath, buf);
  return "ok";
}

async function main(){
  const zinnen = leesAlleZinnen();
  console.log("Gevonden zinnen (SENTENCES + B_SENTENCES, gedupliceerd op id): " + zinnen.length);
  if(!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  let nieuw = 0, overgeslagen = 0, mislukt = 0;
  for(const zin of zinnen){
    try{
      const r = await genereerEen(zin);
      if(r === "ok"){ nieuw++; console.log("✓ " + zin.id + " - " + zin.es.slice(0, 50)); }
      else { overgeslagen++; }
    }catch(e){
      mislukt++;
      console.error("✗ " + zin.id + " - " + e.message);
    }
    // kleine pauze tussen requests, aardig voor de API en voorkomt rate-limit-gedoe
    await new Promise(function(r){ setTimeout(r, 250); });
  }
  console.log("");
  console.log("Klaar: " + nieuw + " nieuw gegenereerd, " + overgeslagen + " al bestaand overgeslagen, " + mislukt + " mislukt.");
  if(mislukt > 0){
    console.log("Draai het script gerust nog eens: het is idempotent en probeert alleen ontbrekende bestanden opnieuw.");
    process.exitCode = 1;
  }
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
