/*
 * Gedeelde motor achter de audio-generators (dictado + voorleesboek).
 *
 * Waarom dit bestand bestaat (v19.56, 30 juli 2026):
 * De twee oude scripts sloegen een zin over zodra er een mp3 met die naam bestond. Dat is prima
 * zolang je nooit van stem wisselt, maar het maakte het ONMOGELIJK om alles opnieuw met één stem
 * in te spreken: de bestanden bestonden immers al. Stefan: "in dictado moeten ze de elevenlabs
 * stem hebben en voorleesboek chispa ook. Verder niet."
 *
 * Daarom houden we nu een manifest bij (audio/stemmen.json) met per bestand: welke stem, welk
 * model en een hash van de ingesproken tekst. Overslaan gebeurt alleen als die drie allemaal
 * kloppen. Verander je van stem, of wijzigt de tekst van een zin, dan wordt hij vanzelf opnieuw
 * ingesproken. Dat is precies het gedrag dat je wil: consistentie is de regel, niet toeval.
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const REPO_ROOT = path.join(__dirname, "..");
const HTML_PAD = path.join(REPO_ROOT, "index.html");
const MANIFEST_PAD = path.join(REPO_ROOT, "audio", "stemmen.json");

// ---------------------------------------------------------------- bronbestand lezen

// Leest een JS-array-literal (bv. "var SENTENCES = [...]") rechtstreeks uit index.html, zodat de
// scripts nooit los kunnen raken van de daadwerkelijke appdata. We tellen vierkante haken om het
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

function leesAppBron(){
  const html = fs.readFileSync(HTML_PAD, "utf8");
  const m = html.match(/<script>([\s\S]*)<\/script>/);
  if(!m) throw new Error("Kon geen <script>-blok vinden in index.html");
  return m[1];
}

// Alle dictado-zinnen: SENTENCES (A2) + B_SENTENCES (B1), ontdubbeld op id.
function leesZinnen(){
  const src = leesAppBron();
  const bij = {};
  leesArrayLiteral(src, "SENTENCES").concat(leesArrayLiteral(src, "B_SENTENCES"))
    .forEach(function(s){ bij[s.id] = s; });
  return Object.keys(bij).map(function(id){
    return { id: id, tekst: bij[id].es, label: bij[id].es.slice(0, 50) };
  });
}

// Alle hoofdstukken van het Chispa-boek. \n\n scheidt alinea's in de brondata (voor de <p>-tags in
// de app); voor de voorleestekst maken we er gewone regelovergangen van, ElevenLabs pakt de pauzes
// vanzelf op via de leestekens.
function leesHoofdstukken(){
  return leesArrayLiteral(leesAppBron(), "BOOK").map(function(h){
    return { id: h.id, tekst: h.tekst.replace(/\n\n/g, "\n"), label: h.titel };
  });
}

// ---------------------------------------------------------------- manifest

function hashVan(tekst){
  return crypto.createHash("sha1").update(tekst, "utf8").digest("hex").slice(0, 16);
}

function leesManifest(){
  try{ return JSON.parse(fs.readFileSync(MANIFEST_PAD, "utf8")); }
  catch(e){ return {}; }
}

function schrijfManifest(man){
  fs.mkdirSync(path.dirname(MANIFEST_PAD), { recursive: true });
  fs.writeFileSync(MANIFEST_PAD, JSON.stringify(man, null, 2) + "\n");
}

// ---------------------------------------------------------------- opdrachtregel

function leesOpties(argv){
  const o = { alles: false, droog: false, adopteer: false, nieuweStem: false, max: Infinity };
  const args = argv.slice(2);
  for(let i = 0; i < args.length; i++){
    const a = args[i];
    /* Een losse # en alles erachter negeren we. Zsh, de standaard-shell op macOS, ziet # op de
       opdrachtregel NIET als commentaar. Wie een voorbeeldregel met uitleg erachter plakt, kreeg
       hier dus een foutmelding over een "onbekende optie #", terwijl het toelichting was en geen
       opdracht. Beter de uitleg wegslikken dan de hele run afbreken. */
    if(a.charAt(0) === "#") break;
    if(a === "--alles" || a === "--force") o.alles = true;
    else if(a === "--droog" || a === "--dry-run") o.droog = true;
    else if(a === "--adopteer") o.adopteer = true;
    else if(a === "--nieuwe-stem") o.nieuweStem = true;
    else if(a.indexOf("--max=") === 0) o.max = parseInt(a.slice(6), 10) || Infinity;
    else throw new Error("Onbekende optie: " + a + "  (geldig: --alles, --adopteer, --droog, --nieuwe-stem, --max=N)");
  }
  return o;
}

/* Twee stemmen, één per groep (30 juli 2026; tooling, dus geen APP_VERSIE-bump).
   Stefan: "leuk om twee verschillende dingen te doen." Dictado en het voorleesboek doen ook echt
   iets anders: dictado is een oefening waarin je woord voor woord moet kunnen volgen, het boek is
   een verhaal dat je wil blijven horen. Daarom onthoudt het manifest de stem per groep en kun je ze
   los zetten. Zet je alleen ELEVENLABS_VOICE_ID, dan krijgen beide groepen die ene stem: het oude
   gedrag blijft dus gewoon werken.

   Dit moest per groep, niet per run. Anders zou het gecombineerde generate-audio.js bij elke
   volgende run de ene groep als "andere stem" zien en 'm opnieuw inspreken, en dan betaal je elke
   keer voor het heen en weer wisselen. */
const GROEP_ENV = { dictado: "ELEVENLABS_VOICE_DICTADO", boek: "ELEVENLABS_VOICE_BOEK" };

// De oefening wil voorspelbaar en rustig zijn, het verhaal mag leven. Dit zijn geen kosten, alleen
// instellingen die met de tekst meegaan.
const GROEP_STEMINSTELLING = {
  dictado: { stability: 0.65, similarity_boost: 0.8 },
  boek:    { stability: 0.4,  similarity_boost: 0.75 }
};

function stemVoor(groep, cfg){
  return (cfg.stemmen && cfg.stemmen[groep]) || cfg.voice || "";
}

/*
 * De stem die deze groep al heeft, zoals vastgelegd in audio/stemmen.json.
 *
 * Dit is het antwoord op een vraag die pas over een half jaar opkomt: voeg je dan drie nieuwe
 * dictado-zinnen toe, hoe weet je script dan nog met welke stem de andere 201 zijn ingesproken?
 * Uit een omgevingsvariabele niet: die leeft één terminalvenster lang. Dus staat de gekozen stem
 * in het manifest, in de repo, naast de mp3's waar hij bij hoort. Een voice-id is geen geheim,
 * dus dat mag daar gewoon staan.
 */
function vastgelegdeStem(groep, man){
  const m = man || leesManifest();
  return (m.standaard && m.standaard[groep]) || "";
}

function leesConfig(opties, groepen){
  const basis = process.env.ELEVENLABS_VOICE_ID || "";
  const man = leesManifest();
  const lijst = groepen || ["dictado", "boek"];
  const c = {
    key: process.env.ELEVENLABS_API_KEY || "",
    voice: basis,
    stemmen: {},
    vast: {},
    uitOmgeving: {},
    model: process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2"
  };

  ["dictado", "boek"].forEach(function(g){
    const uitEnv = process.env[GROEP_ENV[g]] || basis || "";
    const vast = vastgelegdeStem(g, man);
    c.vast[g] = vast;
    c.uitOmgeving[g] = !!uitEnv;
    /* Volgorde: wat jij nu instelt wint, anders wat er al ligt. Zo kun je nog steeds bewust van
       stem wisselen, maar hoef je voor "er zijn zinnen bijgekomen" niets te weten of te zetten. */
    c.stemmen[g] = uitEnv || vast;
  });

  /* Zet je een andere stem dan wat er ligt, dan is dat geen kleine afwijking: dan wordt de hele
     groep opnieuw ingesproken, want anders klinkt de app door elkaar. Dat kost geld en dat wil je
     niet per ongeluk. Vandaar dat het expliciet moet. */
  const botsing = lijst.filter(function(g){
    return c.vast[g] && c.uitOmgeving[g] && c.stemmen[g] !== c.vast[g];
  });
  if(botsing.length && !opties.nieuweStem){
    botsing.forEach(function(g){
      console.error("De stem voor '" + g + "' ligt vast op " + c.vast[g] + " (audio/stemmen.json),");
      console.error("maar " + GROEP_ENV[g] + " staat nu op " + c.stemmen[g] + ".");
    });
    console.error("");
    console.error("Alles wat er al staat zou dan opnieuw worden ingesproken, want half-om-half");
    console.error("klinkt slordig. Twee wegen:");
    console.error("  wilde je alleen nieuwe zinnen erbij? Haal de instelling weg en draai opnieuw:");
    botsing.forEach(function(g){ console.error("    unset " + GROEP_ENV[g]); });
    console.error("  wil je echt van stem wisselen? Draai dan met --nieuwe-stem erachter.");
    console.error("    (kijk eerst met --droog wat dat aan tekens kost)");
    process.exit(1);
  }

  if(opties.droog) return c; // droogdraaien mag zonder sleutel: dan bel je de API niet
  if(!c.key){
    console.error("Zet eerst ELEVENLABS_API_KEY (zie de uitleg bovenin het script).");
    process.exit(1);
  }
  lijst.forEach(function(g){
    if(stemVoor(g, c)) return;
    console.error("Geen stem voor '" + g + "'. Er ligt er ook nog geen vast in audio/stemmen.json.");
    console.error("Zet " + GROEP_ENV[g] + " (aparte stem per groep) of ELEVENLABS_VOICE_ID");
    console.error("(dezelfde stem voor alles). Kies je stem in");
    console.error("https://elevenlabs.io/app/voice-library en kopieer de voice-id.");
    console.error("Daarna hoef je dat nooit meer te doen: de eerste run legt hem vast.");
    process.exit(1);
  });
  return c;
}

// ---------------------------------------------------------------- de eigenlijke run

async function spreekUit(cfg, tekst, stem, instelling){
  const res = await fetch("https://api.elevenlabs.io/v1/text-to-speech/" + stem, {
    method: "POST",
    headers: { "xi-api-key": cfg.key, "Content-Type": "application/json", "Accept": "audio/mpeg" },
    body: JSON.stringify({
      text: tekst,
      model_id: cfg.model,
      voice_settings: instelling || { stability: 0.5, similarity_boost: 0.75 }
    })
  });
  if(!res.ok){
    const body = await res.text().catch(function(){ return ""; });
    const e = new Error("HTTP " + res.status + ": " + body.slice(0, 200));
    /* 401/403 gaat over de sleutel, niet over deze zin. Doorploeteren levert dan alleen maar
       201 keer dezelfde foutmelding op, dus die markeren we als fataal. */
    if(res.status === 401 || res.status === 403) e.fataal = true;
    /* En hetzelfde geldt voor een voice-id die niet bestaat: dat is een instelling, geen zin.
       ElevenLabs antwoordt daarop met 400 en "invalid_uid". Zonder deze regel loopt de run
       vrolijk door alle 201 zinnen heen met exact dezelfde melding. */
    if(res.status === 400 && /invalid_uid|invalid ID has been received/i.test(body)){
      e.fataal = true;
      e.stemFout = true;
    }
    throw e;
  }
  return Buffer.from(await res.arrayBuffer());
}

/*
 * Even aankloppen voordat we tekens gaan uitgeven.
 *
 * Wat we hier controleren is niet "is de sleutel goed", maar "gaat de aanroep die deze run
 * honderden keren doet, überhaupt lukken". Dat is meer dan de sleutel alleen: een voice-id die
 * niet bestaat geeft precies dezelfde stroom fouten, en die kwam ook echt voor (een voorbeeldregel
 * met "..." erin blijft in zsh gewoon staan als waarde, zonder één waarschuwing).
 *
 * Daarom spreken we per groep die deze run gebruikt één woord in, met díé stem. Vier tekens per
 * stem, dus hooguit acht voor de hele controle. Een gescoopte sleutel die alleen Text to Speech
 * mag, komt hier gewoon doorheen: we vragen niets aan /v1/user, want dat is een ander recht.
 */
async function controleerVooraf(cfg, groepen){
  const paren = [];
  (groepen || ["dictado", "boek"]).forEach(function(g){
    const s = stemVoor(g, cfg);
    if(!s) return;
    // twee groepen met dezelfde stem hoeven maar één proef
    if(paren.some(function(p){ return p.stem === s; })) return;
    paren.push({ groep: g, stem: s });
  });

  for(const p of paren){
    try{
      await spreekUit(cfg, "Hola", p.stem, null);
    }catch(e){
      meldProefFout(p, e);
      process.exit(1);
    }
  }
  console.log("(Proefaanroep gelukt: sleutel en " + (paren.length === 1 ? "stem doen" : "stemmen doen") + " het.)");
}

function meldProefFout(p, e){
  console.error("");
  console.error("De proefaanroep werd geweigerd. Er is nog niets ingesproken en niets afgeschreven.");
  console.error("Antwoord: " + e.message);
  console.error("");

  if(e.stemFout){
    /* Dit is de duidelijkste fout van allemaal: de sleutel werkt, maar de voice-id bestaat niet.
       Bijna altijd is er een voorbeeldwaarde blijven staan of is er een stukje van de id
       weggevallen bij het plakken. */
    console.error("Je sleutel werkt, maar de stem voor '" + p.groep + "' bestaat niet bij ElevenLabs.");
    console.error("Kijk wat er nu echt in staat (dit is geen geheim, dus dit mag je gerust zien):");
    console.error("  echo \"[$" + GROEP_ENV[p.groep] + "]\"");
    console.error("Daar hoort een id van een stuk of twintig letters en cijfers te staan, zoals");
    console.error("imFXYz8XIletRKLZZQaA. Staat er iets als [...] of [] of een halve id, dan is dat het:");
    console.error("haal de id op via https://elevenlabs.io/app/voice-library (knop Copy voice ID),");
    console.error("zet hem opnieuw met export " + GROEP_ENV[p.groep] + "=... en probeer het nog eens.");
    return;
  }

  /* Let op de formulering: een 401/403 hoeft niet van ElevenLabs zelf te komen. Een proxy of
     bedrijfsfirewall ertussen geeft dezelfde codes terug, en dan is er niets mis met de sleutel.
     Daarom staat het antwoord hierboven, en presenteren we de sleutel-oorzaken als het meest
     waarschijnlijke geval in plaats van als vaststaand feit. */
  if(/unauthorized|api[ _-]?key|authentication/i.test(e.message)){
    console.error("Dat is een sleutelfout. Controleer eerst dit, het toont je sleutel niet:");
  }else{
    console.error("Staat daar niets over een key of unauthorized in, dan zit er iets tussen jouw");
    console.error("computer en api.elevenlabs.io (proxy, firewall, VPN) en is je sleutel prima.");
    console.error("Anders: controleer dit, het toont je sleutel niet:");
  }
  console.error("  echo \"lengte ${#ELEVENLABS_API_KEY} · begint met ${ELEVENLABS_API_KEY:0:3}\"");
  console.error("Een echte sleutel is ongeveer vijftig tekens lang en begint met sk_.");
  console.error("Drie dingen die dit meestal zijn:");
  console.error("  1. de sleutel staat nog als voorbeeld ingesteld (sk_... letterlijk overgenomen);");
  console.error("  2. er is een spatie, aanhalingsteken of # meegekopieerd;");
  console.error("  3. de sleutel heeft geen rechten voor Text to Speech (elevenlabs.io -> API Keys).");
}

/*
 * groep   : "dictado" of "boek" (bepaalt de map audio/<groep>/ en de sleutel in het manifest)
 * items   : [{ id, tekst, label }]
 * opties  : uit leesOpties()
 * cfg     : uit leesConfig()
 * pauzeMs : rustpauze tussen twee API-calls
 */
async function verwerk(groep, items, opties, cfg, pauzeMs){
  const outDir = path.join(REPO_ROOT, "audio", groep);
  fs.mkdirSync(outDir, { recursive: true });
  const man = leesManifest();
  if(!man[groep]) man[groep] = {};
  const stem = stemVoor(groep, cfg);
  const instelling = GROEP_STEMINSTELLING[groep];

  /* De stem vastleggen naast de bestanden waar hij bij hoort. Vanaf nu weet een volgende run,
     op een andere dag en in een andere terminal, vanzelf welke stem deze groep heeft. */
  if(!opties.droog && stem){
    if(!man.standaard) man.standaard = {};
    if(man.standaard[groep] !== stem){
      const oud = man.standaard[groep];
      man.standaard[groep] = stem;
      schrijfManifest(man);
      console.log(oud ? "  (stem voor " + groep + " gewijzigd: " + oud + " -> " + stem + ")"
                      : "  (stem voor " + groep + " vastgelegd in audio/stemmen.json: " + stem + ")");
    }
  }

  // eerst inventariseren, zodat we kunnen vertellen wat er gaat gebeuren vóór we quota opmaken
  const plan = items.map(function(it){
    const outPad = path.join(outDir, it.id + ".mp3");
    const h = hashVan(it.tekst);
    const eerder = man[groep][it.id];
    const bestaat = fs.existsSync(outPad);
    let reden = "";
    if(opties.alles) reden = "alles";
    else if(!bestaat) reden = "ontbreekt";
    else if(!eerder) reden = "onbekende stem";          // mp3 van vóór het manifest
    else if(eerder.voice !== stem) reden = "andere stem";
    else if(eerder.model !== cfg.model) reden = "ander model";
    else if(eerder.hash !== h) reden = "tekst gewijzigd";
    return { it: it, outPad: outPad, hash: h, reden: reden };
  });

  /* --adopteer: er stonden al 91 mp3's van vóór dit manifest. Die zijn ooit met ElevenLabs gemaakt,
     alleen weet het manifest niet met welke stem, dus staan ze als "onbekende stem" op de lijst.
     Weet jíj zeker dat ze met de stem uit ELEVENLABS_VOICE_ID zijn ingesproken, dan neem je ze
     hiermee over in het manifest zonder ze opnieuw in te spreken: nul tekens, nul kosten.
     Let op wat je hiermee bevestigt. Je zegt twee dingen tegelijk: (a) het is deze stem, en (b) de
     tekst in index.html is sindsdien niet gewijzigd. Dat tweede kan het script niet controleren,
     want er is geen oude hash om mee te vergelijken. Klopt het niet, dan hoor je bij die zin iets
     anders dan er staat, en het manifest zegt dat alles in orde is. Alleen gebruiken als je een
     paar bestanden hebt teruggeluisterd. Twijfel je: gewoon opnieuw inspreken, dan weet je het. */
  let geadopteerd = 0;
  if(opties.adopteer && !opties.alles){
    plan.forEach(function(p){
      if(p.reden !== "onbekende stem") return;
      man[groep][p.it.id] = { voice: stem, model: cfg.model, hash: p.hash, tekens: p.it.tekst.length, overgenomen: true };
      p.reden = "";
      geadopteerd++;
    });
    if(geadopteerd && !opties.droog) schrijfManifest(man);
  }

  /* --max is een budget voor de hele run, niet per groep. Anders doet één "--max=20" er stiekem
     veertig: twintig dictado plus twintig boek. Daarom houden we op opties bij hoeveel er al
     gepland/ingesproken is en heeft de tweede groep nog maar over wat de eerste liet liggen. */
  if(typeof opties.gedaan !== "number") opties.gedaan = 0;
  const ruimte = Math.max(0, opties.max - opties.gedaan);

  const alles = plan.filter(function(p){ return p.reden; });
  const todo = alles.slice(0, ruimte);
  const uitgesteld = alles.length - todo.length;
  const tekens = todo.reduce(function(n, p){ return n + p.it.tekst.length; }, 0);
  opties.gedaan += todo.length;
  const perReden = {};
  todo.forEach(function(p){ perReden[p.reden] = (perReden[p.reden] || 0) + 1; });

  console.log("");
  const herkomst = !stem ? "geen stem ingesteld"
                 : (cfg.uitOmgeving && cfg.uitOmgeving[groep]) ? "uit " + GROEP_ENV[groep]
                 : (cfg.vast && cfg.vast[groep] === stem) ? "vastgelegd in audio/stemmen.json"
                 : "";
  console.log("== " + groep + " ==  (stem " + (stem || "?") + (herkomst ? ", " + herkomst : "") + ")");
  console.log("  gevonden: " + items.length + " · al goed: " + (items.length - alles.length) + " · in te spreken: " + todo.length);
  if(geadopteerd) console.log("    (" + geadopteerd + " bestaande mp3's overgenomen op jouw woord, niet opnieuw ingesproken)");
  Object.keys(perReden).forEach(function(r){ console.log("    - " + r + ": " + perReden[r]); });
  if(uitgesteld) console.log("    - blijft staan door --max=" + opties.max + ": " + uitgesteld);
  console.log("  tekens die dit kost: " + tekens.toLocaleString("nl-NL"));

  if(opties.droog){
    todo.slice(0, 8).forEach(function(p){ console.log("    · zou doen: " + p.it.id + " (" + p.reden + ")"); });
    if(todo.length > 8) console.log("    · ... en nog " + (todo.length - 8));
    return { groep: groep, stem: stem, nieuw: 0, over: items.length - alles.length, mislukt: 0, tekens: tekens, gepland: todo.length, geadopteerd: geadopteerd };
  }

  let nieuw = 0, mislukt = 0, achterElkaar = 0;
  const OPGEVEN_NA = 5;
  for(const p of todo){
    try{
      const buf = await spreekUit(cfg, p.it.tekst, stem, instelling);
      fs.writeFileSync(p.outPad, buf);
      man[groep][p.it.id] = { voice: stem, model: cfg.model, hash: p.hash, tekens: p.it.tekst.length };
      schrijfManifest(man); // na elk bestand: een afgebroken run verliest hoogstens één zin
      nieuw++;
      achterElkaar = 0;
      console.log("  ✓ " + p.it.id + " (" + p.reden + ") " + String(p.it.label || "").slice(0, 46));
    }catch(e){
      mislukt++;
      achterElkaar++;
      console.error("  ✗ " + p.it.id + " - " + e.message);
      const rest = todo.length - nieuw - mislukt;
      if(e.fataal){
        console.error("  (dit gaat over je instellingen, niet over deze zin: gestopt zodat je niet");
        console.error("   dezelfde melding " + rest + " keer hoeft te lezen)");
        break;
      }
      /* Vangnet voor alles wat we níét van tevoren als fataal herkennen. Gaat het vijf keer op rij
         mis, dan is er iets structureels aan de hand en heeft doorgaan geen zin: dan kost het
         alleen tijd en levert het een scherm vol identieke regels op. */
      if(achterElkaar >= OPGEVEN_NA){
        console.error("  (" + OPGEVEN_NA + " keer op rij mis, dus gestopt. De " + rest + " die overblijven");
        console.error("   pak je gewoon op in een volgende run: wat wél lukte staat al in het manifest)");
        break;
      }
    }
    await new Promise(function(r){ setTimeout(r, pauzeMs); });
  }
  if(uitgesteld) console.log("  (--max bereikt, " + uitgesteld + " blijven staan voor een volgende ronde)");
  return { groep: groep, stem: stem, nieuw: nieuw, over: items.length - alles.length, mislukt: mislukt, tekens: tekens, gepland: todo.length, geadopteerd: geadopteerd };
}

function slotwoord(delen, cfg, opties){
  const nieuw = delen.reduce(function(n, d){ return n + d.nieuw; }, 0);
  const over = delen.reduce(function(n, d){ return n + d.over; }, 0);
  const mislukt = delen.reduce(function(n, d){ return n + d.mislukt; }, 0);
  const overgenomen = delen.reduce(function(n, d){ return n + (d.geadopteerd || 0); }, 0);
  console.log("");
  if(opties.droog){
    const gepland = delen.reduce(function(n, d){ return n + d.gepland; }, 0);
    const tekens = delen.reduce(function(n, d){ return n + d.tekens; }, 0);
    console.log("Droogdraai: " + gepland + (gepland === 1 ? " bestand zou" : " bestanden zouden") + " worden ingesproken, " + tekens.toLocaleString("nl-NL") + " tekens in totaal.");
    if(overgenomen) console.log("Daarnaast zouden " + overgenomen + " bestaande mp3's worden overgenomen zonder ze in te spreken (--adopteer).");
    console.log("Draai zonder --droog om het echt te doen.");
    return;
  }
  if(overgenomen) console.log(overgenomen + " bestaande mp3's overgenomen in het manifest (--adopteer), zonder tekens te verbruiken.");
  console.log("Klaar: " + nieuw + " ingesproken, " + over + " al goed, " + mislukt + " mislukt.");
  delen.forEach(function(d){ console.log("Stem voor " + d.groep + ": " + d.stem); });
  console.log("Model: " + cfg.model);
  console.log("Vergeet niet audio/ én audio/stemmen.json mee te committen.");
  if(mislukt > 0){
    console.log("Draai gerust nog eens (bijv. na een quota-reset): alleen wat nog niet klopt wordt opnieuw geprobeerd.");
    process.exitCode = 1;
  }
}

module.exports = { leesZinnen, leesHoofdstukken, leesOpties, leesConfig, controleerVooraf, verwerk, slotwoord, stemVoor, MANIFEST_PAD };
