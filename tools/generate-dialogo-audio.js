/*
 * Spreekt de luisterscenes in (v21.2).
 *
 * Elke regel van elke scene wordt een eigen mp3, want een dialoog heeft twee sprekers en ElevenLabs
 * doet een stem per aanroep. Spreker A gaat naar audio/dialogo-a/, spreker B naar audio/dialogo-b/,
 * met de bestandsnaam <scene>-<regelnummer>.mp3. Precies waar de app ze zoekt.
 *
 * GEBRUIK (vanaf de repo-root)
 *     export ELEVENLABS_API_KEY="PLAK-HIER-JE-SLEUTEL"
 *     node tools/generate-dialogo-audio.js --droog
 *     node tools/generate-dialogo-audio.js
 *
 * Welke stem elke spreker heeft, staat vast in audio/stemmen.json onder "standaard". Je hoeft dus
 * niets in te stellen; komt er over een half jaar een scene bij, dan krijgt die vanzelf dezelfde
 * twee stemmen als de rest. Van stem wisselen kan wel, maar moet je expliciet zeggen: zet
 * ELEVENLABS_VOICE_DIALOGO_A of ELEVENLABS_VOICE_DIALOGO_B en draai met --nieuwe-stem. Zonder die vlag
 * weigert het script, want een nieuwe stem betekent de hele groep opnieuw inspreken.
 *
 * Opties en overslaan-logica: zie de uitleg bovenin tools/generate-audio.js.
 *
 * Vereist: Node.js 18+.
 */

const lib = require("./audio-lib");

const GROEPEN = ["dialogo-a", "dialogo-b"];

async function main(){
  const opties = lib.leesOpties(process.argv);
  const cfg = lib.leesConfig(opties, GROEPEN);
  const perGroep = lib.leesDialogos();
  if(!opties.droog){
    await lib.controleerVooraf(cfg, GROEPEN);
    GROEPEN.forEach(function(g){ console.log("Stem " + g + ": " + lib.stemVoor(g, cfg)); });
    console.log("Model: " + cfg.model);
  }
  const delen = [];
  for(const g of GROEPEN){
    delen.push(await lib.verwerk(g, perGroep[g] || [], opties, cfg, 250));
  }
  lib.slotwoord(delen, cfg, opties);
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
