/*
 * Spreekt alléén de dictado-/vertaalzinnen in (audio/dictado/<id>.mp3).
 *
 * Meestal wil je tools/generate-audio.js: dat doet de zinnen én het boek met dezelfde stem, en dat
 * is wat de app hoort te zijn. Dit script bestaat voor als je bewust alleen de zinnen wil
 * bijwerken, bijvoorbeeld om je quota over meerdere maanden te spreiden.
 *
 * GEBRUIK (vanaf de repo-root)
 *     export ELEVENLABS_API_KEY="sk_..."
 *     export ELEVENLABS_VOICE_DICTADO="..."   # of ELEVENLABS_VOICE_ID voor dezelfde stem overal
 *     node tools/generate-dictado-audio.js --droog
 *     node tools/generate-dictado-audio.js
 *
 * Opties en overslaan-logica: zie de uitleg bovenin tools/generate-audio.js. Kort: het manifest
 * audio/stemmen.json bepaalt wat er opnieuw moet, niet het enkele bestaan van een mp3.
 *
 * Vereist: Node.js 18+.
 */

const lib = require("./audio-lib");

async function main(){
  const opties = lib.leesOpties(process.argv);
  const cfg = lib.leesConfig(opties, ["dictado"]);
  const zinnen = lib.leesZinnen();
  if(!opties.droog) console.log("Stem: " + lib.stemVoor("dictado", cfg) + " · model: " + cfg.model);
  const r = await lib.verwerk("dictado", zinnen, opties, cfg, 250);
  lib.slotwoord([r], cfg, opties);
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
