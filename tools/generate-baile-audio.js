#!/usr/bin/env node
/* De achtergrondmuziek bij Chispa's dansjes, gemaakt met Eleven Music (POST /v1/music).
 *
 * Waarom dit bestaat: wat er tot v23.34 speelde was geen muziek maar synthese in de browser, per
 * dans een patroon van kick, tik, palma, bas en melodie. Op papier klopt dat ritme, in je oren niet.
 * Dit maakt er acht echte instrumentale loops van, één per dans.
 *
 * De bpm in de prompt is dezelfde bpm die in index.html bij de dans staat. Dat is het hele punt: de
 * animatie duurt een heel aantal slagen op die bpm, dus als de muziek op dat tempo staat lopen ze
 * mee. Verander je hier een tempo, verander het daar ook.
 *
 *   ELEVENLABS_API_KEY=... node tools/generate-baile-audio.js
 *   node tools/generate-baile-audio.js --droog          # laat zien wat hij zou doen
 *   node tools/generate-baile-audio.js --alleen salsa   # één dans opnieuw
 *   node tools/generate-baile-audio.js --opnieuw        # ook wat er al staat
 *
 * Idempotent: een dans die er al staat met dezelfde prompt wordt overgeslagen. Het manifest
 * (audio/baile/muziek.json) onthoudt per dans welke prompt en welke bpm erin zaten, zodat je later
 * kunt zien waar een track vandaan komt en zodat een gewijzigde prompt vanzelf opnieuw gaat.
 */
const fs = require("fs");
const path = require("path");

const WORTEL = path.resolve(__dirname, "..");
const MAP = path.join(WORTEL, "audio", "baile");
const MANIFEST = path.join(MAP, "muziek.json");
const API = "https://api.elevenlabs.io/v1/music";
const LENGTE_MS = 20000;          // twintig seconden; de app speelt er twee tot vier van af

/* De prompts. Instrumentaal en zonder zang: er wordt Spaans geleerd op ditzelfde scherm, en een
 * stem die iets anders zingt is dan geen sfeer maar ruis. Kort, herkenbaar, en met de instrumenten
 * erbij die de stijl dragen; een prompt die alleen "salsa" zegt levert iets generieks op. */
const DANSEN = [
  { id: "salsa", bpm: 190, land: "Cuba",
    prompt: "Instrumental Cuban salsa, no vocals, {bpm} BPM, montuno piano, tumbao bass, congas, "
          + "timbales and a bright brass stab. Warm, danceable, loopable, consistent tempo." },
  { id: "flamenco", bpm: 180, land: "España",
    prompt: "Instrumental Spanish flamenco, no vocals, {bpm} BPM in a 12-beat compás, solo Spanish "
          + "guitar with rasgueado, palmas and cajón. Intimate, dry room, loopable." },
  { id: "cumbia", bpm: 95, land: "Colombia",
    prompt: "Instrumental Colombian cumbia, no vocals, {bpm} BPM, gaita flute, accordion, guacharaca "
          + "scraper and steady kick on the downbeat. Sunny, relaxed, loopable." },
  { id: "merengue", bpm: 132, land: "República Dominicana",
    prompt: "Instrumental Dominican merengue, no vocals, {bpm} BPM, fast tambora and güira, "
          + "accordion and punchy saxophone riffs. Joyful, driving, loopable." },
  { id: "bachata", bpm: 128, land: "República Dominicana",
    prompt: "Instrumental Dominican bachata, no vocals, {bpm} BPM, nylon lead guitar with tremolo, "
          + "bongo with the martillo pattern, güira and soft bass. Romantic, swaying, loopable." },
  { id: "tango", bpm: 116, land: "Argentina",
    prompt: "Instrumental Argentine tango, no vocals, {bpm} BPM, bandoneón lead, violin, upright "
          + "bass and piano marcato. Dramatic, moody, loopable." },
  { id: "reggaeton", bpm: 96, land: "Puerto Rico",
    prompt: "Instrumental reggaeton, no vocals, {bpm} BPM, classic dembow drum pattern, deep sub "
          + "bass and sparse synth plucks. Modern, clean, loopable." },
  { id: "jarabe", bpm: 132, land: "México",
    prompt: "Instrumental Mexican mariachi jarabe tapatío, no vocals, {bpm} BPM, trumpets, violins, "
          + "vihuela and guitarrón in fast 6/8. Festive, bright, loopable." }
];

const args = process.argv.slice(2);
const OPT = {
  droog: args.includes("--droog"),
  opnieuw: args.includes("--opnieuw"),
  alleen: (function () { const i = args.indexOf("--alleen"); return i >= 0 ? args[i + 1] : null; })()
};

function lees(p, val) { try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { return val; } }
function promptVan(d) { return d.prompt.replace("{bpm}", String(d.bpm)); }

async function main() {
  const sleutel = process.env.ELEVENLABS_API_KEY;
  if (!sleutel && !OPT.droog) {
    console.error("Geen ELEVENLABS_API_KEY in je omgeving. Zet hem erbij, of draai met --droog.");
    return 1;
  }
  fs.mkdirSync(MAP, { recursive: true });
  const manifest = lees(MANIFEST, {});
  const doen = DANSEN.filter(function (d) {
    if (OPT.alleen && d.id !== OPT.alleen) return false;
    if (OPT.opnieuw) return true;
    const bestand = path.join(MAP, d.id + ".mp3");
    const oud = manifest[d.id];
    // opnieuw als het bestand weg is, of als de prompt of de bpm veranderd is sinds de vorige keer
    return !fs.existsSync(bestand) || !oud || oud.prompt !== promptVan(d) || oud.bpm !== d.bpm;
  });

  console.log("— la música —");
  /* Welke sleutel er gebruikt wordt, gemaskeerd. Klinkt overbodig tot je drie sleutels hebt en de
     ene wel muziek mag maken en de andere niet: dan zie je hier meteen dat je shell nog de oude
     heeft, in plaats van te denken dat je aanpassing in de app niet is aangekomen. */
  if (sleutel) {
    console.log("  sleutel: …" + sleutel.slice(-6) + " (" + sleutel.length + " tekens)");
  }
  console.log("  " + DANSEN.length + " dansen, " + doen.length + " te doen"
    + (doen.length ? ": " + doen.map(function (d) { return d.id; }).join(", ") : ""));
  if (!doen.length) { console.log("  alles staat er al en niets is veranderd"); return 0; }
  if (OPT.droog) {
    doen.forEach(function (d) {
      console.log("\n  " + d.id + " (" + d.bpm + " bpm, " + d.land + ")");
      console.log("    " + promptVan(d));
    });
    console.log("\n  droog: er is niets gedownload en niets betaald");
    return 0;
  }

  let mis = 0;
  for (const d of doen) {
    const prompt = promptVan(d);
    process.stdout.write("  " + d.id + " … ");
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "xi-api-key": sleutel, "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt, music_length_ms: LENGTE_MS })
      });
      if (!res.ok) {
        const tekst = await res.text();
        /* Een foutmelding hoort te zeggen wat je eraan doet, niet alleen wat de server terugstuurde.
           Deze drie komen echt voor en kosten je anders een avond zoeken: een sleutel zonder het
           recht music_generation (dat is iets anders dan een sleutel die niet werkt), een abonnement
           dat Eleven Music niet heeft, en een lege sleutel. */
        if (res.status === 401 && /music_generation/.test(tekst)) {
          console.log("MISLUKT: je sleutel mag wel spreken maar geen muziek maken.");
          console.log("    Je API-sleutel mist het recht 'music_generation'. Dat staat los van de");
          console.log("    rechten voor tekst-naar-spraak, dus een sleutel die voor de hoofdstukken");
          console.log("    werkt hoeft hier niet te werken. Zet in de ElevenLabs-app bij API Keys het");
          console.log("    recht voor muziek aan, of maak een nieuwe sleutel met dat recht erbij en");
          console.log("    neem de rechten van de oude over. Daarna deze opdracht opnieuw.");
          return 1;                       // geen zin om er nog zeven te proberen met dezelfde sleutel
        }
        if (res.status === 401 || res.status === 403) {
          console.log("MISLUKT (" + res.status + "): de sleutel wordt niet geaccepteerd.");
          console.log("    " + tekst.slice(0, 300));
          return 1;
        }
        console.log("MISLUKT (" + res.status + "): " + tekst.slice(0, 300));
        mis++;
        continue;
      }
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length < 5000) { console.log("MISLUKT: te klein (" + buf.length + " bytes)"); mis++; continue; }
      fs.writeFileSync(path.join(MAP, d.id + ".mp3"), buf);
      manifest[d.id] = { prompt: prompt, bpm: d.bpm, ms: LENGTE_MS, bytes: buf.length,
                         wanneer: new Date().toISOString() };
      fs.writeFileSync(MANIFEST, JSON.stringify(manifest, null, 1) + "\n");
      console.log("klaar (" + Math.round(buf.length / 1024) + " kB)");
    } catch (e) {
      console.log("MISLUKT: " + (e && e.message ? e.message : e));
      mis++;
    }
  }

  console.log("\n— slot —");
  console.log("  " + (doen.length - mis) + " van de " + doen.length + " gelukt, in audio/baile/");
  if (mis) console.log("  " + mis + " mislukt; draai hem nog eens, hij slaat over wat al goed staat");
  /* audio/ gaat als geheel mee naar Pages (zie poort.yml), dus er hoeft niets aan de deploylijst
     te veranderen. Wel even luisteren voordat je pusht: een track die niet in de maat staat is
     erger dan de synthese die er nu is. */
  console.log("  luister ze even af voordat je pusht, en let vooral op het tempo");
  return mis ? 1 : 0;
}

main().then(function (code) { process.exit(code); })
  .catch(function (e) { console.error(e); process.exit(1); });
