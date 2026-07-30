/*
 * VASTE STEMMEN VOOR ALLES WAT WORDT VOORGELEZEN.
 *
 * Dit is het script dat je normaal draait. Het spreekt met vaste ElevenLabs-stemmen:
 *   - alle dictado-/vertaalzinnen  -> audio/dictado/<id>.mp3
 *   - alle hoofdstukken van het Chispa-boek -> audio/boek/<hoofdstuk-id>.mp3
 * En verder niets: de losse woordjes houden bewust hun browser-stem, dat is een oefening in
 * herkennen, geen luisterervaring.
 *
 * ÉÉN OF TWEE STEMMEN?
 * Dictado en het boek doen iets anders. Dictado is een oefening: je moet er woord voor woord in
 * kunnen meeschrijven, dus wil je een neutrale, rustige voorlezer. Het boek is een verhaal dat
 * je wil blijven horen, dus daar mag een warmere verteller staan. Je kunt het dus twee kanten op:
 *
 *   Dezelfde stem voor alles:      export ELEVENLABS_VOICE_ID="PLAK-HIER-DE-VOICE-ID"
 *   Een stem per groep:            export ELEVENLABS_VOICE_DICTADO="PLAK-HIER-DE-VOICE-ID"
 *                                  export ELEVENLABS_VOICE_BOEK="PLAK-HIER-DE-VOICE-ID"
 *
 * Het manifest onthoudt de stem PER GROEP, dus die twee bijten elkaar niet: dit script kan in
 * één run twee stemmen gebruiken en een volgende run ziet allebei als "al goed". Zet je alleen
 * ELEVENLABS_VOICE_ID, dan krijgen beide groepen die ene stem.
 *
 * GEBRUIK
 *   1. Haal je API-key op bij https://elevenlabs.io (Profile -> API Keys).
 *   2. Kies je stem(men) in https://elevenlabs.io/app/voice-library (Castiliaans past het best bij
 *      de rest van de app) en kopieer de voice-id's.
 *   3. Vanaf de repo-root:
 *
 *        export ELEVENLABS_API_KEY="PLAK-HIER-JE-SLEUTEL"
 *        export ELEVENLABS_VOICE_DICTADO="PLAK-HIER-DE-VOICE-ID"
 *        export ELEVENLABS_VOICE_BOEK="PLAK-HIER-DE-VOICE-ID"
 *        node tools/generate-audio.js --droog     # eerst kijken wat er gaat gebeuren
 *        node tools/generate-audio.js             # en dan echt
 *
 *   4. Luister een paar bestanden na, en commit audio/ samen met audio/stemmen.json.
 *
 * OPTIES
 *   --droog     laat alleen zien wat er zou gebeuren en wat het aan tekens kost. Werkt zonder key.
 *   --max=N     stop na N ingesproken bestanden, geteld over de hele run (dus niet N per groep).
 *               Handig om je quota over meerdere dagen te spreiden; de volgende run pakt gewoon op
 *               waar deze ophield. Samen met --droog zie je vooraf precies wat die N gaat kosten.
 *   --alles     spreek alles opnieuw in, ook wat volgens het manifest al klopt.
 *   --adopteer  neem bestaande mp3's zonder manifest-regel over als "deze zijn al met deze stem
 *               gemaakt", zonder ze opnieuw in te spreken. Kost nul tekens. Gebruik dit ALLEEN als
 *               je zeker weet dat die oude bestanden met precies deze ELEVENLABS_VOICE_ID zijn
 *               ingesproken én dat de bijbehorende tekst sindsdien niet is gewijzigd: het script
 *               kan geen van beide controleren en gelooft je op je woord. Luister eerst een paar
 *               oude bestanden terug naast een vers ingesproken bestand.
 *
 * WANNEER WORDT IETS OPNIEUW INGESPROKEN?
 * Het manifest audio/stemmen.json onthoudt per bestand welke stem, welk model en welke tekst erin
 * zit. Een bestand wordt overgeslagen als die drie nog kloppen, en anders opnieuw ingesproken.
 * Wissel je van stem, dan wordt dus alles vernieuwd - zo blijft de app consistent klinken.
 * De mp3's van vóór dit manifest staan er als "onbekende stem" in en worden één keer vernieuwd.
 *
 * KOSTEN
 * De hele set is ongeveer 24.000 tekens (~6.900 voor de zinnen, ~17.000 voor het boek). Dat past
 * niet in de gratis laag van ~10.000 tekens per maand. Twee routes: één maand een betaald
 * instapplan nemen en het in één keer doen, of met --max=N over meerdere maanden spreiden. De
 * zinnen eerst doen is het slimst: die hoor je dagelijks, het boek lees je één keer.
 *
 * Vereist: Node.js 18+ (voor de ingebouwde fetch).
 */

const lib = require("./audio-lib");

async function main(){
  const opties = lib.leesOpties(process.argv);
  const cfg = lib.leesConfig(opties, ["dictado", "boek"]);
  const zinnen = lib.leesZinnen();
  const hoofdstukken = lib.leesHoofdstukken();

  if(!opties.droog){
    await lib.controleerVooraf(cfg, ["dictado", "boek"]);
    const zelfde = lib.stemVoor("dictado", cfg) === lib.stemVoor("boek", cfg);
    console.log(zelfde ? "Eén stem voor dictado én het voorleesboek."
                      : "Twee stemmen: een voorlezer voor dictado, een verteller voor het boek.");
    console.log("  dictado: " + lib.stemVoor("dictado", cfg));
    console.log("  boek   : " + lib.stemVoor("boek", cfg));
    console.log("  model  : " + cfg.model);
  }

  const a = await lib.verwerk("dictado", zinnen, opties, cfg, 250);
  const b = await lib.verwerk("boek", hoofdstukken, opties, cfg, 400);
  lib.slotwoord([a, b], cfg, opties);
}

main().catch(function(e){ console.error("Onverwachte fout:", e); process.exit(1); });
