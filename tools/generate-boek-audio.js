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

/* v23.166: welke reeks in welke map hoort, staat op de boekenplank in de app (LEES_REEKSEN) en
   nergens anders meer. Hier stond het als "hist- naar hist, de rest naar boek", en die regel wist
   niets van de recepten: die kwamen in audio/boek/ terecht terwijl de app ze in audio/receta/
   zocht, en er bestond geen receta-stem. Nu leest dit script hetzelfde als de app en de nachtrun.
   Reeksen zonder verteller (stem:false) doen niet mee; zie leesHoofdstukkenPerMap(). */

async function main(){
  const opties = lib.leesOpties(process.argv);
  const { perMap, wees } = lib.leesHoofdstukkenPerMap();
  if(wees.length){
    /* Een hoofdstuk dat bij geen enkele reeks hoort, staat ook op geen plank in de app: dan is
       ontbrekend geluid het kleinste van twee problemen. Melden, niet stilzwijgend inspreken. */
    console.error("Let op: " + wees.length + " hoofdstuk(ken) horen bij geen enkele reeks en worden " +
                  "overgeslagen: " + wees.join(", "));
  }
  const perGroep = perMap;
  const groepen = Object.keys(perGroep).filter(function(g){ return perGroep[g].length; });
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
