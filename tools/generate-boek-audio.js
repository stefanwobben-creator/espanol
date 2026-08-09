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
 *     node tools/generate-boek-audio.js --droog
 *     node tools/generate-boek-audio.js --max=4
 *
 * Meer is niet nodig: welke verteller het boek heeft, staat vast in audio/stemmen.json. Komt er een
 * hoofdstuk bij, dan krijgt dat vanzelf dezelfde verteller als de rest.
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

/* v23.27: BOOK bevat sinds v23.23 twee reeksen. Chispa (boek-*) houdt zijn verteller, de
   geschiedenisreeks (hist-*) krijgt een eigen stem en een eigen map. De verdeling gebeurt op het
   id-voorvoegsel, want dat is hoe de app ze zelf ook uit elkaar houdt. */
function groepVan(id){ return String(id).indexOf("hist-") === 0 ? "hist" : "boek"; }

async function main(){
  const opties = lib.leesOpties(process.argv);
  const alle = lib.leesHoofdstukken();
  const perGroep = { boek: [], hist: [] };
  alle.forEach(function(h){ perGroep[groepVan(h.id)].push(h); });
  const groepen = ["boek", "hist"].filter(function(g){ return perGroep[g].length; });
  const cfg = lib.leesConfig(opties, groepen);
  if(!opties.droog){
    await lib.controleerVooraf(cfg, groepen);
    groepen.forEach(function(g){
      console.log("Stem (" + g + "): " + lib.stemVoor(g, cfg) + " · model: " + cfg.model);
    });
  }
  const uit = [];
  for(const g of groepen){
    console.log("\n== " + g + " (" + perGroep[g].length + " hoofdstukken) ==");
    uit.push(await lib.verwerk(g, perGroep[g], opties, cfg, 400));
  }
  lib.slotwoord(uit, cfg, opties);
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
