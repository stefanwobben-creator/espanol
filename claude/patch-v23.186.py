#!/usr/bin/env python3
# v23.186 - de reeks vertelt zelf wie hem voorleest
#
# (Geschreven als v23.183. Hernummerd omdat de nachtrun ondertussen v23.183 t/m v23.185 heeft
#  uitgegeven; de inhoud is ongewijzigd. De v23.183-verwijzingen in de code hieronder verwijzen
#  naar deze wijziging.)
#
# Stefan, 23 aug: "als we nieuwe content toevoegen zoals boeken, direct de juiste ElevenLabs stem
# meenemen."
#
# WAAROM DAT NU NIET KAN, EN WAT ER TWEE KEER DOOR IS GEBEURD
#
# Bij El hilo de las palabras (v23.181) en bij Don Quijote (v23.182) staat in de patchkop dezelfde
# zin: "geen nieuwe stem, dus map:'boek'". Dat was geen keuze maar een omweg. De reden:
#
#   ALLE_GROEPEN = Object.keys(GROEP_ENV)
#
# GROEP_ENV is een handgeschreven lijst van vijf groepen met per groep de naam van een
# omgevingsvariabele. Een reeks met een nieuwe map staat daar niet in, dus leesConfig() vult voor die
# groep geen stem in, en stemVoor() valt terug op ELEVENLABS_VOICE_ID. In de avondrun staat die niet,
# dus een nieuwe map zou een reeks opleveren die er wel is en nooit klinkt.
#
# Het gevolg is dat elke nieuwe reeks de verteller van Chispa krijgt, of hij daar nou bij past of
# niet. Don Quijote wordt nu voorgelezen door dezelfde stem als het kinderboek over een wezentje dat
# zijn lied zoekt. Dat is niet stuk, maar het is ook niet gekozen.
#
# WAT ERAAN VERANDERT
#
# De reeks krijgt een veld `verteller` met de voice-id erin, en dat veld is de waarheid over wie hem
# voorleest. Vier gevolgen:
#
#   1. ALLE_GROEPEN telt voortaan ook de mappen van LEES_REEKSEN mee. Een reeks met een eigen map is
#      daarmee gewoon een groep.
#   2. stemVoor() valt terug op de verteller van de reeks. Volgorde: wat je nu in de omgeving zet
#      wint, dan wat er in het manifest vastligt, dan wat de reeks zegt. De eerste twee blijven zoals
#      ze waren; de derde is nieuw en vult alleen gaten.
#   3. Een groep die uit een reeks komt en geen eigen steminstelling heeft, krijgt die van `boek`.
#      Een reeks is een verteller, geen dicteeoefening.
#   4. Zegt het manifest iets anders dan de reeks, dan is dat een echte tegenspraak en die wordt
#      gemeld. Het manifest wint, want dat beschrijft de mp3's die er al liggen; de reeks zou dan
#      liegen over wie hem voorleest.
#
# Een voice-id is trouwens geen geheim. Ze staan al in audio/stemmen.json, dat gewoon in de repo
# staat. Het geheim is de API-sleutel, en die blijft waar hij staat: in de GitHub-secrets.
#
# WAT DIT NIET DOET
#
# Het geeft Don Quijote nog geen andere stem. Daar is een voice-id voor nodig die Stefan kiest, en
# die kan ik niet verzinnen: een id die niet bestaat laat de hele groep afketsen. Wat er nu ligt is
# de leiding. De reeksen krijgen de verteller die ze feitelijk al hebben, zodat het klopt, en zodra
# Stefan een id doorgeeft is het één regel.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
LIB = W / "tools" / "audio-lib.js"
WF = W / ".github" / "workflows" / "curriculum.yml"
VER = W / "versie.txt"
NIEUW = "v23.186"

src = APP.read_text(encoding="utf-8")
lib = LIB.read_text(encoding="utf-8")
wf = WF.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "verteller:" not in src
DOE_LIB = "reeksStemmen" not in lib
DOE_TEST = "--zelftest" not in lib
DOE_WF = "audio-lib.js --zelftest" not in wf
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

def lrep(anker, nieuw, n=1):
    global lib
    c = lib.count(anker)
    assert c == n, "lib-anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    lib = lib.replace(anker, nieuw, n)

# ---------------------------------------------------------------- 1. de reeks noemt zijn verteller
# De ids die er feitelijk al liggen in audio/stemmen.json. Niets gaat hier van stem veranderen; wat
# verandert is dat het ergens STAAT in plaats van dat het uit een omweg volgt.
BOEKSTEM = "imFXYz8XIletRKLZZQaA"
HISTSTEM = "YKrm0N1EAM9Bw27j8kuD"

if DOE_APP:
    rep(' {id:"chispa", pre:"boek-", nl:"Chispa", en:"Chispa", stem:true, map:"boek",',
        ' /* v23.183: `verteller` is de voice-id van wie deze reeks voorleest, en dat veld is vanaf nu\n'
        '    de waarheid daarover. Tot v23.182 volgde de stem uit de map, en de map werd gekozen omdat\n'
        '    een nieuwe map betekende dat er niets zou klinken. Dat is precies andersom: eerst kiezen\n'
        '    wie het voorleest, dan pas waar de bestanden staan.\n\n'
        '    `stem:true` blijft wat het was: heeft deze reeks audio, ja of nee. Een voice-id is geen\n'
        '    geheim (ze staan al in audio/stemmen.json); de API-sleutel wel, en die staat in de\n'
        '    GitHub-secrets. */\n'
        ' {id:"chispa", pre:"boek-", nl:"Chispa", en:"Chispa", stem:true, map:"boek", verteller:"' + BOEKSTEM + '",')
    rep(' {id:"quijote", pre:"quij-", nl:"Don Quijote", en:"Don Quijote", stem:true, map:"boek",',
        ' {id:"quijote", pre:"quij-", nl:"Don Quijote", en:"Don Quijote", stem:true, map:"boek", verteller:"' + BOEKSTEM + '",')
    rep(' {id:"letras", pre:"lit-", nl:"El hilo de las palabras", en:"El hilo de las palabras", stem:true, map:"boek",',
        ' {id:"letras", pre:"lit-", nl:"El hilo de las palabras", en:"El hilo de las palabras", stem:true, map:"boek", verteller:"' + BOEKSTEM + '",')
    rep(' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true, map:"hist",',
        ' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true, map:"hist", verteller:"' + HISTSTEM + '",')

# ---------------------------------------------------------------- 2. het gereedschap luistert ernaar
if DOE_LIB:
    lrep(
        '// Elke groep die dit bestand kent. Het is niet de lijst die een run verwerkt: welke groepen een run\n'
        '// aanraakt, geeft het aanroepende script mee aan leesConfig().\n'
        'const ALLE_GROEPEN = Object.keys(GROEP_ENV);',
        '/* v23.183: welke stem hoort bij welke map, volgens de reeksen zelf.\n'
        '\n'
        '   Tot nu toe stond dat nergens. GROEP_ENV is een handgeschreven lijst van vijf groepen, en een\n'
        '   reeks met een nieuwe map stond daar niet in. leesConfig() vulde voor die groep dus geen stem\n'
        '   en stemVoor() viel terug op ELEVENLABS_VOICE_ID, die in de avondrun niet staat. Gevolg: een\n'
        '   nieuwe map betekende een reeks die er wel is en nooit klinkt, en dus kreeg elke nieuwe reeks\n'
        '   maar de map (en de stem) van Chispa. Twee keer op rij, met dezelfde regel in de patchkop.\n'
        '\n'
        '   Nu vertelt de reeks het zelf. Eén feit, één plek. */\n'
        'function reeksStemmen(){\n'
        '  const uit = {};\n'
        '  try {\n'
        '    leesReeksen().forEach(function(r){\n'
        '      if(!r || !r.map || !r.verteller || r.stem === false) return;\n'
        '      if(!uit[r.map]) uit[r.map] = r.verteller;\n'
        '    });\n'
        '  } catch(e){}\n'
        '  return uit;\n'
        '}\n'
        '\n'
        '// Elke groep die dit bestand kent. Het is niet de lijst die een run verwerkt: welke groepen een run\n'
        '// aanraakt, geeft het aanroepende script mee aan leesConfig().\n'
        '// v23.183: de mappen van de reeksen tellen mee, anders bestaat een nieuwe reeks hier niet.\n'
        'const ALLE_GROEPEN = Object.keys(GROEP_ENV)\n'
        '  .concat(Object.keys(reeksStemmen()).filter(function(m){ return !GROEP_ENV[m]; }));')

    lrep(
        '  ALLE_GROEPEN.forEach(function(g){\n'
        '    const uitEnv = process.env[GROEP_ENV[g]] || basis || "";\n'
        '    const vast = vastgelegdeStem(g, man);\n'
        '    c.vast[g] = vast;\n'
        '    c.uitOmgeving[g] = !!uitEnv;\n'
        '    /* Volgorde: wat jij nu instelt wint, anders wat er al ligt. Zo kun je nog steeds bewust van\n'
        '       stem wisselen, maar hoef je voor "er zijn zinnen bijgekomen" niets te weten of te zetten. */\n'
        '    c.stemmen[g] = uitEnv || vast;\n'
        '  });',
        '  const uitReeks = reeksStemmen();\n'
        '  c.uitReeks = uitReeks;\n'
        '  ALLE_GROEPEN.forEach(function(g){\n'
        '    const uitEnv = (GROEP_ENV[g] ? process.env[GROEP_ENV[g]] : "") || basis || "";\n'
        '    const vast = vastgelegdeStem(g, man);\n'
        '    c.vast[g] = vast;\n'
        '    c.uitOmgeving[g] = !!uitEnv;\n'
        '    /* Volgorde: wat jij nu instelt wint, anders wat er al ligt. Zo kun je nog steeds bewust van\n'
        '       stem wisselen, maar hoef je voor "er zijn zinnen bijgekomen" niets te weten of te zetten.\n'
        '\n'
        '       v23.183: en als derde de verteller van de reeks. Die vult alleen gaten: een nieuwe reeks\n'
        '       klinkt vanaf de eerste nacht, zonder dat er iemand een omgevingsvariabele moet zetten. */\n'
        '    c.stemmen[g] = uitEnv || vast || uitReeks[g] || "";\n'
        '  });\n'
        '\n'
        '  /* Zegt het manifest iets anders dan de reeks, dan liegt een van de twee over wie er voorleest.\n'
        '     Het manifest wint, want dat beschrijft de mp3\'s die er al liggen. Maar stil laten staan is\n'
        '     erger dan de tegenspraak zelf: dan denkt iedereen dat de reeks klopt. */\n'
        '  Object.keys(uitReeks).forEach(function(g){\n'
        '    if(c.vast[g] && c.vast[g] !== uitReeks[g]){\n'
        '      console.error("De reeks zegt dat \'" + g + "\' wordt voorgelezen door " + uitReeks[g] + ",");\n'
        '      console.error("maar audio/stemmen.json heeft " + c.vast[g] + " vastgelegd. Het manifest wint,");\n'
        '      console.error("want dat hoort bij de opnames die er al staan. Pas de reeks aan, of draai met");\n'
        '      console.error("--nieuwe-stem als je de hele groep opnieuw wilt laten inspreken.");\n'
        '    }\n'
        '  });')

    lrep(
        '  const instelling = GROEP_STEMINSTELLING[groep];',
        '  /* v23.183: een groep die uit een reeks komt heeft geen eigen regel in GROEP_STEMINSTELLING.\n'
        '     Die krijgt die van `boek`: een reeks is een verteller, en de neutrale standaard van\n'
        '     spreekUit() klinkt vlakker dan een verhaal verdient. */\n'
        '  const instelling = GROEP_STEMINSTELLING[groep] || GROEP_STEMINSTELLING.boek;')

    lrep(
        'module.exports = { leesZinnen, leesHoofdstukken, leesReeksen, leesHoofdstukkenPerMap,',
        'module.exports = { leesZinnen, leesHoofdstukken, leesReeksen, leesHoofdstukkenPerMap, reeksStemmen,')

# ---------------------------------------------------------------- 3. de controle die het volhoudt
#
# Zonder dit is de rest van deze patch een belofte. Stefan vroeg niet om een veld maar om een
# gewoonte: bij nieuwe content gaat de stem mee. Een gewoonte die alleen in een patchkop staat gaat
# de derde keer weer mis, precies zoals hij dat bij v23.181 en v23.182 deed.
#
# De belangrijkste van de zes proeven is nummer 1, en die draait op de ECHTE app: elke reeks met
# geluid noemt een verteller. Wie het volgende boek toevoegt zonder stem krijgt geen stille reeks
# maar een rode stap in de nachtrun, mét de naam van de reeks erbij.
TEST = '''

/* ---------- zelftest ----------
   `node tools/audio-lib.js --zelftest`, en hij staat in de nachtrun naast de andere zelftests.

   Op een KOPIE in een tijdelijke map, om dezelfde reden als bij tools/stemmen-samenvoegen.js: een
   controle die de werkelijkheid aanraakt is geen controle maar een tweede bewerking. Proef 6 gaat
   daarover en is er niet voor de sier; de vorige keer leverde een test die zei dat alles goed was
   een diff van 2197 regels op.

   Proef 1 is de reden dat dit bestand bestaat. Proeven 3 en 4 zijn de controlegevallen: dit is
   triviaal groen te maken door de reeks altijd te laten winnen, en dan spreek je een groep opnieuw
   in die al mp3's heeft (geld), of je spreekt een reeks in die de app nergens laat horen (geld voor
   geluid dat niemand kan afspelen, de recepten van v23.166). */
if(require.main === module && process.argv.includes("--zelftest")){
  const os = require("os");
  let mis = 0;
  const proef = function(goed, wat){ console.log((goed ? "  ok   " : "  FOUT ") + wat); if(!goed) mis++; };

  // 1. op de echte app: elke reeks met geluid zegt wie hem voorleest
  const zonder = leesReeksen().filter(function(r){
    return r && r.stem !== false && r.map && !r.verteller;
  }).map(function(r){ return r.id; });
  proef(zonder.length === 0,
    "elke reeks met geluid noemt een verteller" +
    (zonder.length ? " (mist bij: " + zonder.join(", ") + ")" : ""));

  // vanaf hier op een kopie, met een verzonnen reeks in een map die nergens anders bestaat
  const voorApp = fs.readFileSync(HTML_PAD, "utf8");
  const voorMan = fs.existsSync(MANIFEST_PAD) ? fs.readFileSync(MANIFEST_PAD, "utf8") : null;
  const werk = fs.mkdtempSync(path.join(os.tmpdir(), "audiolib-"));
  fs.mkdirSync(path.join(werk, "tools"));
  fs.mkdirSync(path.join(werk, "audio"));
  fs.copyFileSync(path.join(__dirname, "audio-lib.js"), path.join(werk, "tools", "audio-lib.js"));
  if(voorMan !== null) fs.writeFileSync(path.join(werk, "audio", "stemmen.json"), voorMan);

  /* Drie verzonnen reeksen, en ze staan met opzet vóór de echte: reeksStemmen() houdt de eerste
     die hij tegenkomt aan, dus zo krijgt `boek` volgens de plank een andere stem dan volgens het
     manifest. Dat is de tegenspraak van proef 4, en zonder die tegenspraak vergelijkt die proef
     twee keer dezelfde waarde en is hij altijd groen. */
  const HAAK = "var LEES_REEKSEN = [";
  const verzonnen =
    '\\n {id:"zt-botst", pre:"ztb-", nl:"Zelftest botsing", en:"Zelftest botsing", stem:true, map:"boek", verteller:"ZT_ANDERS"},' +
    '\\n {id:"zt-nieuw", pre:"zt-", nl:"Zelftest", en:"Zelftest", stem:true, map:"zeltestmap", verteller:"ZT_STEM"},' +
    '\\n {id:"zt-stil", pre:"zts-", nl:"Zelftest stil", en:"Zelftest stil", stem:false, map:"zelftestStil", verteller:"ZT_STIL"},';
  proef(voorApp.indexOf(HAAK) !== -1, "de boekenplank is te vinden in index.html");
  fs.writeFileSync(path.join(werk, "index.html"),
    voorApp.replace(HAAK, HAAK + verzonnen));

  const kopie = require(path.join(werk, "tools", "audio-lib.js"));
  const stemmen = kopie.reeksStemmen();

  // 2. de nieuwe map bestaat, met de stem van de reeks zelf
  proef(stemmen.zeltestmap === "ZT_STEM",
    "een reeks met een nieuwe map levert een stem (" + (stemmen.zeltestmap || "niets") + ")");
  proef(kopie.ALLE_GROEPEN.indexOf("zeltestmap") !== -1,
    "en die map telt mee als groep (" + kopie.ALLE_GROEPEN.join(", ") + ")");

  // 3. leesConfig vult het gat
  const gemeld = [];
  const echteError = console.error;
  console.error = function(){ gemeld.push(Array.prototype.join.call(arguments, " ")); };
  let cfg;
  try { cfg = kopie.leesConfig({droog: true}, ["zeltestmap"]); }
  finally { console.error = echteError; }
  proef(cfg.stemmen.zeltestmap === "ZT_STEM",
    "leesConfig vult de gaten met de verteller van de reeks");

  /* 4. HET CONTROLEGEVAL. `boek` heeft mp3's die met imFX... zijn ingesproken en het manifest zegt
        dat ook. De verzonnen reeks hierboven beweert ZT_ANDERS. Zou de reeks winnen, dan geldt de
        hele groep als "andere stem" en spreekt de eerstvolgende nacht 33 hoofdstukken opnieuw in.
        Dit is de proef die groen bleef toen ik de volgorde omdraaide, want hij vergeleek twee keer
        dezelfde waarde; vandaar de verzonnen botsing. */
  const vast = cfg.vast.boek;
  proef(!!vast && vast !== "ZT_ANDERS",
    "de proef zelf deugt: het manifest en de plank zeggen iets anders (" + vast + " tegenover ZT_ANDERS)");
  proef(cfg.stemmen.boek === vast,
    "CONTROLE: bij tegenspraak wint audio/stemmen.json (boek: " + cfg.stemmen.boek + ")");
  proef(gemeld.some(function(r){ return r.indexOf("ZT_ANDERS") !== -1; }),
    "CONTROLE: en de tegenspraak wordt gemeld in plaats van stil weggewerkt");

  // 4. HET TWEEDE CONTROLEGEVAL: stem:false doet niet mee
  proef(!stemmen.zelftestStil && kopie.ALLE_GROEPEN.indexOf("zelftestStil") === -1,
    "CONTROLE: een reeks met stem:false krijgt geen groep en dus geen opnames");

  // 5. de steminstelling valt terug op die van een verhaal, niet op de vlakke standaard
  proef(JSON.stringify(kopie.steminstellingVoor("zeltestmap")) ===
        JSON.stringify(kopie.steminstellingVoor("boek")),
    "een nieuwe reeks krijgt de steminstelling van een verteller");

  // 6. CONTROLE: er is niets aangeraakt wat van git is
  const naApp = fs.readFileSync(HTML_PAD, "utf8");
  const naMan = fs.existsSync(MANIFEST_PAD) ? fs.readFileSync(MANIFEST_PAD, "utf8") : null;
  proef(naApp === voorApp && naMan === voorMan,
    "CONTROLE: index.html en audio/stemmen.json zijn geen byte veranderd door deze test");

  console.log(mis ? "\\naudio-lib: " + mis + " fout" : "\\naudio-lib: alles goed");
  process.exit(mis ? 1 : 0);
}
'''

if DOE_TEST:
    # steminstellingVoor() erbij: proef 5 moet de terugval kunnen zien zonder hem na te bouwen, en
    # een controle die de regel overschrijft die hij controleert, controleert niets.
    lrep(
        '  /* v23.183: een groep die uit een reeks komt heeft geen eigen regel in GROEP_STEMINSTELLING.\n'
        '     Die krijgt die van `boek`: een reeks is een verteller, en de neutrale standaard van\n'
        '     spreekUit() klinkt vlakker dan een verhaal verdient. */\n'
        '  const instelling = GROEP_STEMINSTELLING[groep] || GROEP_STEMINSTELLING.boek;',
        '  const instelling = steminstellingVoor(groep);')
    lrep(
        'function stemVoor(groep, cfg){',
        '/* v23.183: als functie, zodat de zelftest de terugval kan aanwijzen in plaats van hem na te\n'
        '   bouwen. Een controle die zijn eigen regel overschrijft controleert niets. */\n'
        'function steminstellingVoor(groep){\n'
        '  /* Een groep die uit een reeks komt heeft geen eigen regel in GROEP_STEMINSTELLING. Die\n'
        '     krijgt die van `boek`: een reeks is een verteller, en de neutrale standaard van\n'
        '     spreekUit() klinkt vlakker dan een verhaal verdient. */\n'
        '  return GROEP_STEMINSTELLING[groep] || GROEP_STEMINSTELLING.boek;\n'
        '}\n'
        '\n'
        'function stemVoor(groep, cfg){')
    lrep(' hashVan, ALLE_GROEPEN, MANIFEST_PAD };',
         ' hashVan, steminstellingVoor, ALLE_GROEPEN, MANIFEST_PAD };')

    # En de raadgeving als er tóch geen stem is. Die noemde de omgevingsvariabele van de groep, en
    # een groep die uit een reeks komt heeft die niet: dan stond er letterlijk "Zet undefined".
    lrep(
        '    console.error("Zet " + GROEP_ENV[g] + " (aparte stem per groep) of ELEVENLABS_VOICE_ID");\n'
        '    console.error("(dezelfde stem voor alles). Kies je stem in");',
        '    if(GROEP_ENV[g]){\n'
        '      console.error("Zet " + GROEP_ENV[g] + " (aparte stem per groep) of ELEVENLABS_VOICE_ID");\n'
        '      console.error("(dezelfde stem voor alles). Kies je stem in");\n'
        '    } else {\n'
        '      /* v23.183: deze groep komt van de boekenplank en heeft geen omgevingsvariabele. Daar\n'
        '         "Zet undefined" neerzetten helpt niemand; de plek waar het hoort is de reeks. */\n'
        '      console.error("Deze groep komt van een leesreeks in index.html. Zet daar het veld");\n'
        '      console.error("verteller:\\"<voice-id>\\" bij, dan klinkt hij de eerstvolgende nacht.");\n'
        '      console.error("Kies je stem in");\n'
        '    }')
    lib = lib.rstrip("\n") + "\n" + TEST

# ---------------------------------------------------------------- 4. en hij draait elke nacht
if DOE_WF:
    anker = ("      - name: Zelftest van de manifestsamenvoeging\n"
             "        run: node tools/stemmen-samenvoegen.js --zelftest\n")
    assert wf.count(anker) == 1, "workflow-anker %d keer" % wf.count(anker)
    wf = wf.replace(anker, anker +
        "\n"
        "      # v23.183: elke leesreeks met geluid noemt zijn eigen verteller. Deze stap wordt rood\n"
        "      # zodra er een boek bij komt zonder stem, mét de naam van de reeks erbij. Dat is de hele\n"
        "      # reden dat hij er is: bij v23.181 en v23.182 stond in de patchkop dat er geen stem was\n"
        "      # gekozen, en een afspraak die alleen in een patchkop staat gaat de derde keer weer mis.\n"
        "      - name: Zelftest van de stem per reeks\n"
        "        run: node tools/audio-lib.js --zelftest\n", 1)

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: elke reeks noemt zijn verteller, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_LIB or DOE_TEST:
    LIB.write_text(lib, encoding="utf-8")
    print("tools/audio-lib.js: de reeks bepaalt de stem" + (", met zelftest" if DOE_TEST else ""))
else:
    print("tools/audio-lib.js: stond er al")

if DOE_WF:
    WF.write_text(wf, encoding="utf-8")
    print(".github/workflows/curriculum.yml: de zelftest draait elke nacht mee")
else:
    print(".github/workflows/curriculum.yml: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
