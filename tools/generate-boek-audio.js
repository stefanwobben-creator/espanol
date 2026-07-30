/*
 * Spreekt alléén de hoofdstukken van het Chispa-boek in (audio/boek/<hoofdstuk-id>.mp3), één
 * bestand per hoofdstuk: het hele verhaal als mini-luisterboek, niet los per zin zoals bij dictado.
 *
 * Meestal wil je tools/generate-audio.js: dat doet de zinnen én het boek met dezelfde stem. Dit
 * script bestaat voor als je bewust alleen het boek wil bijwerken, bijvoorbeeld nadat er een
 * hoofdstuk is bijgekomen of om je quota te spreiden.
 *
 * GEBRUIK (vanaf de repo-root)
 *     export ELEVENLABS_API_KEY="PLAK-HIER-JE-SLEUTEL"
 *     export ELEVENLABS_VOICE_BOEK="PLAK-HIER-DE-VOICE-ID"      # of ELEVENLABS_VOICE_ID voor dezelfde stem overal
 *     node tools/generate-boek-audio.js --droog
 *     node tools/generate-boek-audio.js --max=4
 *
 * Het boek is met ~17.000 tekens veruit de grootste post; --max=N is hier je vriend als je op de
 * gratis laag zit. De app valt automatisch terug op browser-TTS zolang een hoofdstuk nog ontbreekt
 * (zie boekSpreek() in index.html), dus half af is geen probleem, alleen minder mooi.
 *
 * Opties en overslaan-logica: zie de uitleg bovenin tools/generate-audio.js.
 *
 * Vereist: Node.js 18+.
 */

const lib = require("./audio-lib");

async function main(){
  const opties = lib.leesOpties(process.argv);
  const cfg = lib.leesConfig(opties, ["boek"]);
  const hoofdstukken = lib.leesHoofdstukken();
  if(!opties.droog){
    await lib.controleerVooraf(cfg, ["boek"]);
    console.log("Stem: " + lib.stemVoor("boek", cfg) + " · model: " + cfg.model);
  }
  const r = await lib.verwerk("boek", hoofdstukken, opties, cfg, 400);
  lib.slotwoord([r], cfg, opties);
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
