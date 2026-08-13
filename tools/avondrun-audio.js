#!/usr/bin/env node
/*
 * De avondrun spreekt zijn eigen zinnen in.
 *
 * WAAROM DIT BESTAAT
 *
 * Stefan, 13 aug: "hij moet ook eleven labs gebruiken om de zinnen in te spreken."
 *
 * Gemeten wat er aan de hand was. audio/dictado/ bevatte 201 bestanden: precies bs1-bs69 en
 * s1-s132, de stand van 30 juli. De laatste commit die de map raakte is ec32f10, ook 30 juli.
 * Sindsdien zijn er 50 zinnen bijgekomen (bs70-bs73 en s133-s179) en die hebben geen opname. Dat
 * is 20% van het corpus, en juist het nieuwste deel, dus alles wat de avondrun en de nachtrun
 * sinds die datum hebben geleverd.
 *
 * De oorzaak is niet dat er iets stuk was: er was gewoon nooit iets dat het deed. tools/
 * generate-audio.js is handwerk met een sleutel uit je eigen terminal, en geen enkele workflow
 * raakte het aan. Elke zin die de bot toevoegde kwam dus per definitie zonder stem binnen, en de
 * enige die dat kon zien was iemand die de map ging tellen.
 *
 * WAT DIT SCRIPT DOET
 *
 * Draait ná het genereren en vóór het publiceren, en spreekt in wat er in de repo staat maar nog
 * geen mp3 heeft. Drie groepen, want dat zijn de groepen die 's nachts kunnen groeien:
 *
 *   dictado    audio/dictado/<zin-id>.mp3        de "Hoor hem"-knop bij een oefenzin
 *   dialogo-a  audio/dialogo-a/<scene>-<n>.mp3   de luisterscenes van Escuchar, stem A
 *   dialogo-b  audio/dialogo-b/<scene>-<n>.mp3   dezelfde scenes, stem B
 *
 * Het boek staat er bewust niet bij. Dat groeit niet vanzelf; een nieuw hoofdstuk is een besluit
 * dat Stefan neemt, en dan draai je tools/generate-boek-audio.js met de hand.
 *
 * DRIE REGELS DIE HET VEILIG HOUDEN
 *
 * 1. Het publiceren gaat altijd door. Een mislukte opname is vervelend, een tegengehouden les is
 *    erger: de tekst is het leermateriaal, het geluid is de garnering. Dit script eindigt daarom
 *    op exitcode 0, ook als er niets gelukt is. Wat niet lukte staat morgen weer op de lijst, want
 *    het manifest is de waarheid en niet het bestaan van een bestand.
 *
 * 2. Een uitschieter wordt geweigerd, niet gecapt, en de alarmbel telt alleen opnieuw inspreken.
 *    Dit is de tweede versie van die regel, want de eerste was fout. Die telde alles wat er op de
 *    lijst stond, en toen er negen luisterscenes bijkwamen (v23.79) sloeg hij aan op 86 bestanden
 *    terwijl er niets aan de hand was: 86 nieuwe opnames van nieuwe content is precies waar deze
 *    stap voor bestaat.
 *
 *    Het verschil zit in de reden. Een bestand dat er niet is, hoort ingesproken te worden, hoeveel
 *    het er ook zijn: Stefan koos bewust géén bovengrens op nieuwe zinnen. Een bestand dat er wél
 *    is en tóch opnieuw moet, is iets anders: dan is de stem gewijzigd, het model gewijzigd of het
 *    manifest kwijt, en dan trekt een cronjob je tegoed leeg voor iets wat al bestond. Dáár staat
 *    de grens op, en bij overschrijding wordt er níéts ingesproken.
 *
 * 3. Geen sleutel is geen storing. Ontbreekt ELEVENLABS_API_KEY, dan zegt het script dat en stopt
 *    het rustig. De les gaat gewoon live, met browserstem in plaats van ElevenLabs.
 *
 * OMGEVING
 *   ELEVENLABS_API_KEY   verplicht om echt in te spreken (GitHub-secret)
 *   AUDIO_ALARM          bovengrens voor de alarmbel, standaard 80
 *   GITHUB_OUTPUT        krijgt audio=<aantal ingesproken> en audiotekens=<aantal>
 *
 * OPTIES
 *   --droog   alleen tellen en tonen, niets inspreken, werkt zonder sleutel
 */

const lib = require("./audio-lib");
const fs = require("fs");
const path = require("path");

const GROEPEN = ["dictado", "dialogo-a", "dialogo-b"];
const ALARM = Number(process.env.AUDIO_ALARM || 80);
const UIT = process.env.GITHUB_OUTPUT || "";
const SAMENVATTING = process.env.GITHUB_STEP_SUMMARY || "";

function schrijfUit(regel){ if(UIT) try{ fs.appendFileSync(UIT, regel + "\n"); }catch(e){} }
function schrijfSamenvatting(tekst){ if(SAMENVATTING) try{ fs.appendFileSync(SAMENVATTING, tekst + "\n"); }catch(e){} }

/* Wat zou er ingesproken worden? Dit is dezelfde vraag als --droog, en we stellen hem altijd
   eerst: pas als het antwoord redelijk is bellen we de API. leesOpties() geeft een vers
   optie-object, want verwerk() telt in opties.gedaan mee hoeveel het al deed. */
function telPlan(items, stil){
  const droog = lib.leesOpties(["node", "x", "--droog"]);
  const cfg = lib.leesConfig(droog, GROEPEN);
  let gepland = 0, tekens = 0;
  const perGroep = {};
  /* verwerk() vertelt wat het gaat doen terwijl het telt, en dat is precies wat je wil zien - één
     keer. Tellen we vooraf én doen we het daarna echt, dan staat hetzelfde blok twee keer in het
     log en lijkt het alsof er dubbel werk gebeurt. Bij een echte run houden we de telling dus
     stil en laat de echte ronde het zien. */
  const echt = console.log;
  if(stil) console.log = function(){};
  return (async function(){
    try{
      for(const g of GROEPEN){
        const r = await lib.verwerk(g, items[g], droog, cfg, 0);
        perGroep[g] = r.gepland;
        gepland += r.gepland;
        tekens += r.tekens;
      }
    } finally { console.log = echt; }
    return { gepland: gepland, tekens: tekens, perGroep: perGroep, opnieuw: telOpnieuw(items) };
  })();
}

/* Hoeveel van de geplande bestanden bestaan al? Dat zijn de opnieuw-gevallen, en alleen die tellen
   mee voor de alarmbel (zie regel 2 in de kop). verwerk() weet dit ook, in zijn interne `reden`,
   maar geeft het niet terug; het hier zelf tellen is één regel en scheelt een verbouwing in
   audio-lib, die door vier andere scripts wordt gebruikt. */
function telOpnieuw(items){
  let n = 0;
  const man = (function(){ try{ return JSON.parse(fs.readFileSync(lib.MANIFEST_PAD, "utf8")); }catch(e){ return {}; } })();
  GROEPEN.forEach(function(g){
    const dir = path.join(__dirname, "..", "audio", g);
    (items[g] || []).forEach(function(it){
      if(!fs.existsSync(path.join(dir, it.id + ".mp3"))) return;   // ontbreekt: altijd goed
      const eerder = (man[g] || {})[it.id];
      if(!eerder) { n++; return; }                                  // mp3 van vóór het manifest
      if(eerder.hash !== undefined && eerder.voice !== undefined && eerder.model !== undefined){
        // klopt alles nog, dan wordt hij overgeslagen en telt hij hier niet mee
        const stem = lib.stemVoor(g, lib.leesConfig(lib.leesOpties(["node","x","--droog"]), GROEPEN));
        if(eerder.voice !== stem) n++;
      }
    });
  });
  return n;
}

async function main(){
  const opties = lib.leesOpties(process.argv);
  const zinnen = lib.leesZinnen();
  const dial = lib.leesDialogos();
  const items = { dictado: zinnen, "dialogo-a": dial["dialogo-a"], "dialogo-b": dial["dialogo-b"] };

  console.log("Gevonden in de repo: " + zinnen.length + " oefenzinnen, " +
              (dial["dialogo-a"].length + dial["dialogo-b"].length) + " dialoogregels.");

  const plan = await telPlan(items, !opties.droog);
  console.log("");
  console.log("In te spreken: " + plan.gepland + " (" + plan.tekens.toLocaleString("nl-NL") + " tekens)" +
              ", waarvan opnieuw: " + plan.opnieuw);

  if(plan.gepland === 0){
    console.log("Alles heeft al een stem. Niets te doen.");
    schrijfUit("audio=0");
    schrijfUit("audiotekens=0");
    return;
  }

  if(plan.opnieuw > ALARM){
    /* Dit is het geval waarin doorgaan duurder is dan stilstaan. Zie regel 2 in de kop: de grens
       staat op opnieuw inspreken, niet op het totaal. Nieuwe content mag zo groot zijn als hij is. */
    const melding = "De audiostap wil " + plan.opnieuw + " bestanden opnieuw inspreken die er al " +
      "staan, en dat is meer dan de alarmgrens van " + ALARM + ". Dit betekent bijna altijd dat de " +
      "stem is gewijzigd of dat audio/stemmen.json niet meer klopt, en dan is dit geen inhaalslag " +
      "maar het opnieuw inspreken van de hele set. Er is niets ingesproken.";
    console.error(melding);
    console.error("Nakijken met: node tools/avondrun-audio.js --droog");
    console.error("Bewust doorzetten kan met AUDIO_ALARM hoger, of met de hand via tools/generate-audio.js.");
    schrijfSamenvatting("### Audio overgeslagen\n\n" + melding);
    schrijfUit("audio=0");
    schrijfUit("audiotekens=0");
    return;
  }

  if(opties.droog){
    console.log("Droogdraai, dus hier stopt het. Draai zonder --droog om het echt te doen.");
    return;
  }

  const cfg = lib.leesConfig(opties, GROEPEN);
  if(!cfg.key){
    // leesConfig() stopt hier normaal zelf al op; dit is voor de zekerheid, en zonder harde exit.
    console.log("Geen ELEVENLABS_API_KEY, dus er wordt niets ingesproken.");
    schrijfUit("audio=0");
    return;
  }

  await lib.controleerVooraf(cfg, GROEPEN);

  const delen = [];
  for(const g of GROEPEN){
    if(!items[g].length) continue;
    delen.push(await lib.verwerk(g, items[g], opties, cfg, 250));
  }
  lib.slotwoord(delen, cfg, opties);

  const nieuw = delen.reduce(function(n, d){ return n + d.nieuw; }, 0);
  const mislukt = delen.reduce(function(n, d){ return n + d.mislukt; }, 0);
  const tekens = delen.reduce(function(n, d){ return n + d.tekens; }, 0);

  schrijfUit("audio=" + nieuw);
  schrijfUit("audiotekens=" + tekens);
  schrijfSamenvatting("### Audio\n\n" + nieuw + " ingesproken" +
    (mislukt ? ", " + mislukt + " mislukt (die staan morgen weer op de lijst)" : "") +
    " · " + tekens.toLocaleString("nl-NL") + " tekens.");

  /* Zie regel 1 in de kop: mislukte opnames houden de les niet tegen. slotwoord() zet
     process.exitCode op 1 als er iets misging; dat draaien we hier bewust terug. */
  process.exitCode = 0;
}

main().catch(function(e){
  console.error("De audiostap klapte: " + e.message);
  console.error("De les gaat gewoon door; morgen wordt het opnieuw geprobeerd.");
  schrijfUit("audio=0");
  process.exitCode = 0;
});
