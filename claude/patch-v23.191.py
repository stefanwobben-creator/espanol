#!/usr/bin/env python3
# v23.191 - de schade opruimen, en de plek waar hij kon ontstaan dichttimmeren
#
# Stefan, 24 aug: "nee filter ze en ga echt grondig te werk nu. Denk vanuit architectuur niet vanuit
# een quick fix."
#
# Dus twee dingen, en de tweede is de belangrijkste.
#
# =============================================================================================
# EERST EEN CORRECTIE OP MIJZELF
#
# Ik schreef vorige ronde: "de nachtrun heeft daar drillzinnen op gebouwd." Dat is onjuist.
# curriculum.js gebruikt alleen fouten van het type zin, dictado, woord en quiz (analyseer(), regels
# 118, 128 en 138). Het type "gramwiz" wordt daar nergens gelezen. De schade blijft dus binnen de
# app en heeft geen content vervuild.
#
# =============================================================================================
# DEEL 1 - WAT ER PRECIES VERVUILD IS, EN WAT ERVAN TERUG TE HALEN IS
#
# gwKies() schrijft bij elk antwoord naar vier plekken. Bij een opfrisser was het oordeel
# (i === q.g) een kansspel, want q kwam uit een andere trekking dan de knoppen op het scherm.
#
#   plek                                vervuild   terug te halen
#   S.errors["gramwiz:opfris-*"]        helemaal   ja, op sleutel
#   S.gramLog[dag][cid].k.opfris        helemaal   ja, per kanaal (7 dagen bewaard)
#   S.gram[cid].goed / .fout            gedeeltelijk  exact voor de dagen die nog in gramLog staan
#   S.gram[cid].box / .due              gedeeltelijk  nee, maar wel eerlijk te verlagen
#   XP en tapas                         een beetje  nee, en dat blijft zo: niemand pakt punten af
#   S.brok                              niet        een opfrisstap draagt geen brok-veld
#   content uit de nachtrun             niet        zie de correctie hierboven
#
# EEN DETAIL DAT DE OPRUIMING MAKKELIJK MAAKT, EN DAT ZELF EEN WART IS
#
# De foutsleutel is `gramwiz:<id>-<stap>-<vraag>`, en een opfrisser heeft altijd stap 0 en vraag 0.
# Alle opfrisserfouten op één concept vallen dus samen in één regel met een oplopende teller. Dat is
# slecht voor de meting (je ziet niet wélke vraag), maar het maakt deze opruiming exact: één sleutel
# per concept, en niets anders raakt eraan.
#
# WAAROM DE DOOS OMLAAG EN NIET TERUG
#
# gramBij() zet de doos hoogstens één keer per dag ("if(st.bd !== today())"). En de opfrisser staat
# vóór de microles in lesFlowGramLijst(). Op elke dag dat je allebei deed, heeft dus het kansspel de
# doos van die dag gezet en kon het eerlijke antwoord van de microles die dag alleen nog de
# due-datum bijstellen. De doos is niet te reconstrueren.
#
# Wat wel eerlijk is: een doos is een bewering over hoe goed je iets kent. Is die bewering door een
# muntje gezet, dan is de eerlijke waarde "onbekend", en onbekend hoort snel terug te komen. Vandaar
# box omlaag naar hoogstens 1 en due op vandaag, alleen voor de concepten waar een opfrisser
# daadwerkelijk aan heeft gezeten. Nooit omhoog: de app hoort nooit meer kennis te claimen dan
# waarvoor bewijs is.
#
# Voor dagen die niet meer in gramLog staan is er geen record en dus niets eerlijks te doen. Dat is
# geen slordigheid maar de grens van wat er bewaard is, en die staat hier zodat niemand later denkt
# dat de opruiming compleet was.
#
# =============================================================================================
# DEEL 2 - DE ARCHITECTUUR, WANT DIT IS DE VIERDE KEER DEZE WEEK
#
# Vier fouten op één dag, en het is vier keer dezelfde vorm: twee plekken die hetzelfde werk doen en
# uit elkaar zijn gelopen.
#
#   v23.188  speelStart() maakt een spel vers, speelNaar() vergat letras en ws
#   v23.189  answerQuestion() markeert beide antwoorden, renderCheat() alleen het juiste
#   v23.190  gcOnderwerp() cachet zijn onderwerp, gcOpfrisOnderwerp() ging eromheen
#   v23.188  lesFlowVolgendeKern() had zes takken en geen bodem
#
# Elk van die vier is los gerepareerd. Dat is precies het soort reparatie waar Stefan vanaf wil,
# want de vijfde staat er al aan te komen: zodra iemand een derde onderwerpsoort of een derde
# keuzescherm toevoegt, begint het opnieuw. Deze patch haalt de tweede plek weg.
#
# 2a. ÉÉN FABRIEK VOOR EEN GEBOUWD ONDERWERP
#
#     Er waren twee bouwers (gcBouw voor de microles, gcOpfrisBouw voor de opfrisser) en twee
#     opvragers, en maar één daarvan zat in de cache. Nu is er één opvrager, gcGebouwd(), met een
#     register van bouwers erachter. Een derde soort is één regel in dat register, en krijgt de
#     cache en de vernieuwing automatisch mee. Overslaan kan niet meer: er is niets om over te slaan.
#
# 2b. ÉÉN PLEK DIE ZEGT WAT EEN BEANTWOORDE KEUZE DRAAGT
#
#     keuzeMerk(i, juist, gekozen) geeft "juist", "jouw" of "". Het toetsje en de wizard roepen
#     allebei die functie aan, en de twee oude klassenamen (.correct en .wrong op .opt) verdwijnen
#     ten gunste van één paar dat op elke knop werkt. Een derde scherm dat keuzeMerk() gebruikt is
#     vanzelf goed; een derde scherm dat het niet gebruikt, valt op in de poort (zie 2d).
#
# 2c. ÉÉN PLEK DIE EEN GRAMMATICA-ANTWOORD WEGSCHRIJFT, MET HERKOMST
#
#     gwKies() schreef naar vier stores door elkaar, midden tussen de sessieboekhouding. Daardoor was
#     de schade van v23.190 over vier plekken verspreid en nergens als één ding terug te vinden.
#     gramAntwoord() doet nu die vier schrijfacties, en zet er de herkomst bij: `bron` op de
#     foutregel, met "opfris" of "microles" erin.
#
#     Dat laatste is de eigenlijke les van vandaag. De opruiming in deel 1 kon alleen omdat de
#     sleutel toevallig "opfris-" bevat. Dat was geluk. Vanaf nu staat de herkomst er met opzet in,
#     zodat een volgende fout filterbaar is in plaats van te gissen.
#
# 2d. EN DE POORT BEWAAKT DE VORM, NIET HET GEVAL
#
#     Drie invarianten in pw-eenplek.js, en ze gaan niet over de bugs van vandaag maar over de vorm:
#     elk gebouwd onderwerp staat stil binnen een sessie en is vers bij een start; elk keuzescherm
#     gebruikt keuzeMerk(); elke weg naar een spel gebruikt dezelfde verse. Rood zodra er ergens een
#     tweede plek ontstaat.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.191"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "gcGebouwd" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 2a. één fabriek voor een gebouwd onderwerp
# =============================================================================================
if DOE_APP:
    # de opfrisser levert alleen nog zijn bouwer; het opvragen gaat via de fabriek
    rep('/* v23.190. Hier stond gcOpfrisOnderwerp() zelf, en die bouwde bij ELKE aanroep een nieuwe\n'
        '   vraag. gwKies() en renderCheat() halen het onderwerp allebei opnieuw op, dus één klik\n'
        '   raakte drie verschillende trekkingen: je klikte op de opties van A, werd afgerekend tegen\n'
        '   B, en zag de markering van C. Gemeten: acht van de acht opfrissers wisselden binnen vijf\n'
        '   aanroepen, acht van de acht microlessen niet.\n'
        '\n'
        '   Dat verschil zat \'m in de cache van gcOnderwerp(), met daarboven al sinds v20.5 precies de\n'
        '   waarschuwing waar dit in liep: "BINNEN een sessie moet het object stil blijven staan".\n'
        '   De opfrisser van v23.73 ging daar langsheen. Nu gaat hij er doorheen, met dezelfde sleutel\n'
        '   en dezelfde vernieuwing bij de start (zie gwStart). */\n'
        'function gcOpfrisOnderwerp(id){\n'
        '  var key = id + "|" + profLang();\n'
        '  if(!gcCache[key]) gcCache[key] = gcOpfrisBouw(id);\n'
        '  return gcCache[key];\n'
        '}\n'
        'function gcOpfrisBouw(id){',
        '/* v23.190/191. Hier stond gcOpfrisOnderwerp(), die bij ELKE aanroep een nieuwe vraag bouwde\n'
        '   en daarmee langs de cache van gcOnderwerp() heen ging. gwKies() en renderCheat() halen het\n'
        '   onderwerp allebei opnieuw op, dus één klik raakte drie trekkingen: je klikte op de opties\n'
        '   van A, werd afgerekend tegen B, en zag de markering van C.\n'
        '\n'
        '   v23.190 gaf deze functie zijn eigen cache. v23.191 haalt hem weg: er is nu één fabriek\n'
        '   (gcGebouwd) met een register van bouwers, en dit is nog alleen de bouwer. Een tweede\n'
        '   opvrager die de cache oversla­at kan niet meer bestaan, want er is niets om over te slaan. */\n'
        'function gcOpfrisBouw(id){')

    rep('/* De vragen worden bij elke start opnieuw gemaakt, maar BINNEN een sessie moet het object stil\n'
        '   blijven staan: gwKies() en gwVolgende() halen het onderwerp opnieuw op, en zonder cache zou de\n'
        '   vraag onder je handen veranderen. */\n'
        'var gcCache = {};\n'
        'function gcOnderwerp(id){\n'
        '  var key = id + "|" + profLang();\n'
        '  if(!gcCache[key]) gcCache[key] = gcBouw(id.replace(/^concept-/, ""));\n'
        '  return gcCache[key];\n'
        '}\n'
        'function gcVernieuw(id){\n'
        '  delete gcCache[id + "|" + profLang()];\n'
        '  /* v23.190: via gwOnderwerp() en niet via gcOnderwerp(), want die kent alleen concept-ids.\n'
        '     Met de oude regel bouwde een opfris-id na het legen nooit meer terug. */\n'
        '  return gwOnderwerp(id);\n'
        '}',
        '/* ================= DE FABRIEK VAN EEN GEBOUWD ONDERWERP (v23.191) =================\n'
        '\n'
        '   Twee eisen die alleen samen kloppen, en die tot v23.190 maar op één van de twee soorten\n'
        '   werden toegepast:\n'
        '\n'
        '     STIL BINNEN EEN SESSIE.  gwKies() en renderCheat() halen het onderwerp allebei opnieuw\n'
        '                              op. Bouwt het dan opnieuw, dan klik je op de opties van de ene\n'
        '                              trekking en word je afgerekend tegen een andere. Dat is precies\n'
        '                              wat er tussen v23.73 en v23.190 met de opfrisser gebeurde.\n'
        '     VERS BIJ ELKE START.     Anders krijg je maanden dezelfde vraag, en dan meet hij of je\n'
        '                              het antwoord onthoudt in plaats van of je de regel kent.\n'
        '\n'
        '   Tot nu toe stonden die twee eisen in gcOnderwerp() en in de regel in gwStart(), en een\n'
        '   tweede bouwer moest er zelf aan denken. Nu staan ze hier, één keer, en is een nieuwe soort\n'
        '   één regel in GC_BOUWERS. Vergeten kan niet meer: er is geen tweede weg naar binnen.\n'
        '\n'
        '   De sleutel draagt de taal, want de vragen worden in de taal van het profiel gebouwd. */\n'
        'var gcCache = {};\n'
        'var GC_BOUWERS = [\n'
        '  {pre: "concept-", bouw: function(id){ return gcBouw(id.replace(/^concept-/, "")); }},\n'
        '  {pre: "opfris-",  bouw: function(id){ return gcOpfrisBouw(id); }}\n'
        '];\n'
        'function gcBouwerVoor(id){\n'
        '  var s = String(id || "");\n'
        '  for(var i = 0; i < GC_BOUWERS.length; i++){\n'
        '    if(s.indexOf(GC_BOUWERS[i].pre) === 0) return GC_BOUWERS[i];\n'
        '  }\n'
        '  return null;\n'
        '}\n'
        'function gcGebouwd(id){\n'
        '  var b = gcBouwerVoor(id);\n'
        '  if(!b) return null;\n'
        '  var key = id + "|" + profLang();\n'
        '  if(!gcCache[key]) gcCache[key] = b.bouw(id);\n'
        '  return gcCache[key];\n'
        '}\n'
        '/* Blijft bestaan omdat een paar plekken hem bij naam kennen; hij is nu een doorgeefluik. */\n'
        'function gcOnderwerp(id){ return gcGebouwd(id); }\n'
        'function gcVernieuw(id){\n'
        '  delete gcCache[id + "|" + profLang()];\n'
        '  return gcGebouwd(id);\n'
        '}')

    # gwOnderwerp routeert allebei via de fabriek
    rep('  // v23.73: de opfrisser is een onderwerp van één stap met één vraag en geen uitleg.\n'
        '  if(/^opfris-/.test(id || "")) return gcOpfrisOnderwerp(id);\n'
        '  if(/^concept-/.test(id || "")) return gcOnderwerp(id);',
        '  /* v23.191: allebei via dezelfde fabriek. Hier stonden twee regels naar twee functies, en\n'
        '     die twee functies deden niet hetzelfde (zie de kop van gcGebouwd). */\n'
        '  if(gcBouwerVoor(id)) return gcGebouwd(id);')

    # en gwStart vernieuwt alles wat gebouwd wordt
    # de twee plekken die de oude naam bij naam kenden. Allebei staan ze in een try/catch, dus een
    # verdwenen functie zou hier geen fout geven maar stilletjes null opleveren: geen opfrisvraag in
    # je dagles, en niets dat het zegt. Precies de fout die deze patch de wereld uit wil.
    rep('      try { o = gcOpfrisOnderwerp(gcOpfrisId(top.c.id)); } catch(e){ o = null; }',
        '      try { o = gcGebouwd(gcOpfrisId(top.c.id)); } catch(e){ o = null; }')
    rep('  try { o = gcOpfrisOnderwerp(oid); } catch(e){ o = null; }',
        '  try { o = gcGebouwd(oid); } catch(e){ o = null; }')
    rep('   bestond al (gcOpfrisOnderwerp) en werd alleen gebruikt voor wat op de herhaallijst stond.',
        '   bestond al (de opfris-bouwer) en werd alleen gebruikt voor wat op de herhaallijst stond.')

    rep('  /* v23.190: en de opfrisser net zo goed. Hij zit sinds deze versie in dezelfde cache, en\n'
        '     zonder deze regel zou hij daardoor juist het omgekeerde krijgen: elke dag dezelfde vraag.\n'
        '     Vers bij de start, stil binnen de sessie. */\n'
        '  if(/^(concept|opfris)-/.test(id || "")) gcVernieuw(id);',
        '  /* v23.191: alles wat gebouwd wordt, wordt vers gebouwd bij een start. Hier stond een regel\n'
        '     met de soorten erin opgesomd, en dat is precies de plek waar de derde soort vergeten\n'
        '     wordt. gcBouwerVoor() is dezelfde vraag zonder lijstje. */\n'
        '  if(gcBouwerVoor(id)) gcVernieuw(id);')

# =============================================================================================
# 2b. één plek die zegt wat een beantwoorde keuze draagt
# =============================================================================================
if DOE_APP:
    rep('  .opt.correct{border-color:var(--green); background:var(--green-soft); color:var(--green); font-weight:700;}\n'
        '  .opt.wrong{border-color:var(--red); background:var(--red-soft); color:var(--red);}\n'
        '  /* v23.189: dezelfde twee kleuren voor de opfrisser. Die markeerde alleen het juiste\n'
        '     antwoord, en niet dat van jou, dus bij twee opties was niet te zien welke van de twee\n'
        '     je had aangetikt. Het toetsje doet dit al sinds jaar en dag met .correct en .wrong; dit\n'
        '     zijn dezelfde variabelen op een knop die geen .opt is. */\n'
        '  .gw-optie.juist{border-color:var(--green); background:var(--green-soft); color:var(--green); font-weight:700;}\n'
        '  .gw-optie.jouw{border-color:var(--red); background:var(--red-soft); color:var(--red);}',
        '  /* v23.191: één paar klassen voor élk beantwoord keuzeknopje, en niet meer per scherm.\n'
        '     Hier stonden .opt.correct/.opt.wrong (het toetsje) naast .gw-optie.juist/.gw-optie.jouw\n'
        '     (de opfrisser, v23.189), en die twee paren zijn ontstaan doordat twee schermen dezelfde\n'
        '     vraag stellen en het los oplosten. Wie welke klasse krijgt zegt keuzeMerk(). */\n'
        '  .juist{border-color:var(--green); background:var(--green-soft); color:var(--green); font-weight:700;}\n'
        '  .jouw{border-color:var(--red); background:var(--red-soft); color:var(--red);}')

    # de functie zelf, vlak boven logError zodat hij bij de andere gedeelde regels staat
    rep('function logError(id, type, tag, extra, paren){',
        '/* ================= WAT EEN BEANTWOORDE KEUZE DRAAGT (v23.191) =================\n'
        '\n'
        '   Twee schermen stellen dezelfde vraag: het toetsje (answerQuestion) en de grammatica-wizard\n'
        '   (renderCheat). Tot v23.189 markeerde het eerste allebei de antwoorden en het tweede alleen\n'
        '   het juiste, zodat je bij twee opties niet kon zien welke knop de jouwe was.\n'
        '\n'
        '   v23.189 repareerde dat door de tweede plek na te bouwen. Dit is de reparatie daarvan: één\n'
        '   functie die het zegt, en twee schermen die hem aanroepen. Een derde scherm krijgt het\n'
        '   gedrag mee zodra het deze functie gebruikt, en de poort merkt het als het dat niet doet.\n'
        '\n'
        '   Geeft "juist" voor het juiste antwoord, "jouw" voor jouw fout, en "" voor de rest. Het\n'
        '   juiste antwoord wint als je het goed had: dan hoort er één merkteken te staan en geen twee\n'
        '   op dezelfde knop. */\n'
        'function keuzeMerk(i, juist, gekozen){\n'
        '  if(i === juist) return "juist";\n'
        '  if(gekozen !== null && gekozen !== undefined && i === gekozen) return "jouw";\n'
        '  return "";\n'
        '}\n'
        '\n'
        'function logError(id, type, tag, extra, paren){')

    # het toetsje gebruikt hem
    rep('  var opts = el.querySelectorAll(".opt");\n'
        '  opts[v.c].classList.add("correct");\n'
        '  var goed = idx === v.c;\n'
        '  if(goed){ st.score++; addXP(2); trackPoging(false); } else { btn.classList.add("wrong"); logError(st.qz.id+"#"+item.oi, "quiz", st.qz.id, v.q); addXP(1); }',
        '  var opts = el.querySelectorAll(".opt");\n'
        '  /* v23.191: via keuzeMerk(), dezelfde functie die de wizard gebruikt. Hier stonden twee\n'
        '     losse classList.add()-regels met eigen klassenamen. */\n'
        '  opts.forEach(function(b, i){\n'
        '    var m = keuzeMerk(i, v.c, idx);\n'
        '    if(m) b.classList.add(m);\n'
        '  });\n'
        '  var goed = idx === v.c;\n'
        '  if(goed){ st.score++; addXP(2); trackPoging(false); } else { logError(st.qz.id+"#"+item.oi, "quiz", st.qz.id, v.q); addXP(1); }')

    # en de wizard ook
    rep('        /* v23.189: twee dingen tegelijk zichtbaar, precies zoals het toetsje het doet. Hier\n'
        '           stond alleen "het juiste antwoord wordt primary", dus jouw eigen keuze liet geen\n'
        '           spoor achter en met twee opties was de oranje knop niet thuis te brengen. */\n'
        '        var klasse = "ghost gw-optie";\n'
        '        if(beantwoord && i === q.g) klasse += " juist";\n'
        '        else if(beantwoord && i === gwSess.gekozen) klasse += " jouw";',
        '        /* v23.189/191: twee dingen tegelijk zichtbaar, en via dezelfde functie als het\n'
        '           toetsje. Hier stond alleen "het juiste antwoord wordt primary", dus jouw eigen\n'
        '           keuze liet geen spoor achter en met twee opties was die ene knop niet thuis te\n'
        '           brengen. */\n'
        '        var klasse = "ghost gw-optie";\n'
        '        if(beantwoord) klasse += " " + keuzeMerk(i, q.g, gwSess.gekozen);')

# =============================================================================================
# 2b-bis. en één plek die een spel vers zet
#
# v23.188 liet speelNaar() de verse van spelInfo() lezen, en dat repareerde het geval. De vorm bleef
# staan: speelStart() schrijft `g.verse()` en speelNaar() schrijft `spelInfoVan(v).verse()`. Twee
# uitdrukkingen van dezelfde regel, en dat is precies het patroon dat vandaag vier keer misging.
#
# Het viel op doordat de nieuwe poortsuite het niet kón toetsen: spelInfo() bouwt bij elke aanroep
# een nieuwe array met nieuwe closures, dus de twee wegen krijgen niet eens hetzelfde object in
# handen. Een invariant die je niet kunt meten, is geen invariant.
# =============================================================================================
if DOE_APP:
    rep('function speelStart(g){\n'
        '  if(!g) return;\n'
        '  if(g.open){ g.open(); return; }\n'
        '  if(g.gezien !== false) speelGezien(g.v);\n'
        '  if(g.verse) g.verse();',
        '/* v23.191: de enige plek die een spelstand leeggooit. Hij stond twee keer geschreven, één keer\n'
        '   in speelStart() (de tegel) en één keer in speelNaar() (de suggestie na je les), en die twee\n'
        '   liepen in v23.188 uit elkaar: letras en de woordenzoeker stonden maar in één van de twee.\n'
        '   Nu is het één functie, en kan de poort ook nakijken dat beide wegen hem aanroepen. */\n'
        'function speelVers(v){\n'
        '  var g = null;\n'
        '  try { g = spelInfoVan(v); } catch(e){ g = null; }\n'
        '  if(g && g.verse){ try { g.verse(); } catch(e){} }\n'
        '}\n'
        'function speelStart(g){\n'
        '  if(!g) return;\n'
        '  if(g.open){ g.open(); return; }\n'
        '  if(g.gezien !== false) speelGezien(g.v);\n'
        '  speelVers(g.v);')

    rep('  /* v23.188. Hier stond ook "kruis" en "adiv", en niet "letras" en niet "ws". Gevolg: klikte\n'
        '     je de suggestie na je les aan, dan stond de puzzel er nog zoals je hem had achtergelaten,\n'
        '     compleet met "Alles gevonden!". Via de tegel op de Speeltuin kreeg je wél een verse, want\n'
        '     speelStart() roept g.verse() aan.\n'
        '\n'
        '     Dat is exact de fout die v23.112 al eens heeft opgeruimd: een handgeschreven rij naast\n'
        '     spelInfo(), die ermee uit de pas loopt. Nu leest deze weg dezelfde verse als de tegel, en\n'
        '     is er nog één lijst. De drie regels hieronder blijven met de hand, want conj, hu en corr\n'
        '     staan niet in spelInfo(): zij hebben geen tegel. */\n'
        '  var info = null;\n'
        '  try { info = spelInfoVan(v); } catch(e){ info = null; }\n'
        '  if(info && info.verse){ try { info.verse(); } catch(e){} }\n'
        '  if(v === "conj"){ conjIdx = null; conjRonde = null; }',
        '  /* v23.188. Hier stond een handgeschreven rijtje spellen waar letras en de woordenzoeker\n'
        '     niet in stonden. Gevolg: klikte je de suggestie na je les aan, dan stond de puzzel er nog\n'
        '     zoals je hem had achtergelaten, compleet met "Alles gevonden!". Via de tegel op de\n'
        '     Speeltuin kreeg je wél een verse puzzel.\n'
        '\n'
        '     v23.191: en nu door dezelfde functie als de tegel. De drie regels hieronder blijven met\n'
        '     de hand, want conj, hu en corr staan niet in spelInfo(): zij hebben geen tegel. */\n'
        '  speelVers(v);\n'
        '  if(v === "conj"){ conjIdx = null; conjRonde = null; }')

# =============================================================================================
# 2c. één plek die een grammatica-antwoord wegschrijft, met herkomst
# =============================================================================================
if DOE_APP:
    rep('  if(stap.brok) brokBij(stap.brok, i === q.g);\n'
        '  else if(o.concept){ gramBij(o.concept, i === q.g);\n'
        '    /* opfrisser en microles zijn hetzelfde concept maar een ander blok, en dat verschil is precies\n'
        '       wat we willen kunnen zien. */\n'
        '    gramLog(o.concept, o.opfris ? "opfris" : "microles", i === q.g); }\n'
        '  persist();\n'
        '  renderCheat();\n'
        '}',
        '  gramAntwoord(o, stap, q, i);\n'
        '  persist();\n'
        '  renderCheat();\n'
        '}\n'
        '\n'
        '/* ================= WAT ER GEBEURT ALS EEN GRAMMATICAVRAAG BEANTWOORD IS (v23.191) ==========\n'
        '\n'
        '   Dit stond los in gwKies(), tussen de sessieboekhouding door, en schreef naar vier plekken:\n'
        '   S.errors, S.gram, S.gramLog en (via brokBij) S.brok. Toen bleek dat het oordeel van de\n'
        '   opfrisser een kansspel was (v23.190), moest de schade dus op vier plekken worden\n'
        '   teruggezocht, en op drie ervan was hij niet als opfrisser herkenbaar.\n'
        '\n'
        '   Eén plek, en met de herkomst erbij. Dat laatste is de eigenlijke les: de opruiming van\n'
        '   v23.191 kon alleen omdat de foutsleutel toevallig "opfris-" bevat. Dat was geluk. Vanaf nu\n'
        '   staat `bron` er met opzet in, zodat een volgende fout te filteren is in plaats van te\n'
        '   gissen. Dezelfde afspraak als S.errors[...].bron = "les" bij de vormdrill (v23.130).\n'
        '\n'
        '   De naam van het kanaal staat één keer, in gwKanaal(), want hij gaat naar twee stores. */\n'
        'function gwKanaal(o){ return o && o.opfris ? "opfris" : "microles"; }\n'
        'function gramAntwoord(o, stap, q, i){\n'
        '  var goed = i === q.g;\n'
        '  /* v23.107, en dit is de kern. Hier stond onvoorwaardelijk gramBij(o.concept), dus elke vraag\n'
        '     van elke stap van elk onderwerp ging naar één doos per onderwerp: 23 dozen voor 122\n'
        '     patronen. Draagt een stap een brok-id, dan gaat het antwoord daarheen. */\n'
        '  if(stap && stap.brok){ brokBij(stap.brok, goed); return; }\n'
        '  if(!o || !o.concept) return;\n'
        '  gramBij(o.concept, goed);\n'
        '  gramLog(o.concept, gwKanaal(o), goed);\n'
        '}')

    # de foutregel draagt de herkomst
    rep('    logError(gwSess.id + "-" + gwSess.stap + "-" + gwSess.vraag, "gramwiz", gwSess.id, gwOpties(q)[i]);',
        '    logError(gwSess.id + "-" + gwSess.stap + "-" + gwSess.vraag, "gramwiz", gwSess.id, gwOpties(q)[i]);\n'
        '    /* v23.191: waar deze fout vandaan komt. Zie de kop van gramAntwoord(). */\n'
        '    try { S.errors["gramwiz:" + gwSess.id + "-" + gwSess.stap + "-" + gwSess.vraag].bron = gwKanaal(o); } catch(e){}')

# =============================================================================================
# DEEL 1 - de opruiming, als migratie 4
# =============================================================================================
if DOE_APP:
    rep('    return weg;\n'
        '  }}\n'
        '];',
        '    return weg;\n'
        '  }},\n'
        '  {naar: 4, wat: "de uitslagen van de opfrisser opruimen, die tot v23.190 een kansspel waren", doe: function(s){\n'
        '    /* v23.190: gcOpfrisOnderwerp() bouwde bij elke aanroep een nieuwe vraag, dus gwKies()\n'
        '       rekende je klik op de ene trekking af tegen het juiste antwoord van een andere. Op een\n'
        '       vraag met twee opties is dat een muntje. Wat daaruit is voortgekomen staat op vier\n'
        '       plekken, en dit ruimt op wat eerlijk op te ruimen valt.\n'
        '\n'
        '       1. DE FOUTREGELS. Sleutel "gramwiz:opfris-<concept>-0-0", en die is eenduidig: alleen\n'
        '          de opfrisser schrijft hem. Alles eruit. Er zaten ook echte fouten tussen, maar die\n'
        '          zijn niet van de valse te onderscheiden en de verhouding was ongeveer één op één.\n'
        '          Een teller waarvan de helft ruis is, is geen teller.\n'
        '\n'
        '       2. HET LEDGER. S.gramLog houdt per dag per concept bij hoeveel beurten er per kanaal\n'
        '          waren. Het kanaal "opfris" gaat eruit, en de dagtotalen gaan met precies dat aantal\n'
        '          omlaag. Dit is exact, want het staat per kanaal geteld.\n'
        '\n'
        '       3. DE TELLERS. S.gram[cid].goed en .fout tellen alles bij elkaar op. Voor de dagen die\n'
        '          nog in het ledger staan (zeven) weten we precies hoeveel daarvan van de opfrisser\n'
        '          kwam; dat wordt afgetrokken, met nul als bodem. Voor oudere dagen bestaat het\n'
        '          record niet meer en valt er niets eerlijks te doen.\n'
        '\n'
        '       4. DE DOOS. Niet te reconstrueren: gramBij() zet de doos hoogstens één keer per dag, en\n'
        '          de opfrisser staat vóór de microles in de dagles, dus op elke gedeelde dag heeft het\n'
        '          muntje de doos gezet. Wat wél eerlijk is: een doos is een bewering over hoe goed je\n'
        '          iets kent, en een bewering die door een muntje is gezet hoort "onbekend" te zijn.\n'
        '          Dus omlaag naar hoogstens 1 en vandaag terug in beeld, en nooit omhoog: de app hoort\n'
        '          nooit meer kennis te claimen dan waarvoor bewijs is.\n'
        '\n'
        '       Wat hier NIET gebeurt: XP en tapas blijven staan (niemand pakt punten af), S.brok blijft\n'
        '       ongemoeid (een opfrisstap draagt geen brok-veld) en de content van de nachtrun is niet\n'
        '       geraakt, want curriculum.js leest alleen fouten van het type zin, dictado, woord en quiz.\n'
        '\n'
        '       Idempotent: draait dit twee keer, dan is er de tweede keer niets meer te vinden en\n'
        '       verandert er niets. Dat is eis 1 van het schemablok hierboven. */\n'
        '    var weg = 0;\n'
        '    /* 1. de foutregels */\n'
        '    if(s.errors){\n'
        '      Object.keys(s.errors).forEach(function(k){\n'
        '        if(k.indexOf("gramwiz:opfris-") === 0){ delete s.errors[k]; weg++; }\n'
        '      });\n'
        '    }\n'
        '    /* 2 en 3: het ledger uit, en wat eruit komt van de tellers af */\n'
        '    var perConcept = {};\n'
        '    if(s.gramLog){\n'
        '      Object.keys(s.gramLog).forEach(function(dag){\n'
        '        var d = s.gramLog[dag] || {};\n'
        '        Object.keys(d).forEach(function(cid){\n'
        '          var r = d[cid];\n'
        '          if(!r || !r.k || !r.k.opfris) return;\n'
        '          var n = r.k.opfris[0] || 0, g = r.k.opfris[1] || 0;\n'
        '          var b = perConcept[cid] || (perConcept[cid] = {n:0, goed:0});\n'
        '          b.n += n; b.goed += g;\n'
        '          r.n = Math.max(0, (r.n || 0) - n);\n'
        '          r.goed = Math.max(0, (r.goed || 0) - g);\n'
        '          delete r.k.opfris;\n'
        '          if(!Object.keys(r.k).length && !r.n) delete d[cid];\n'
        '          weg += n;\n'
        '        });\n'
        '      });\n'
        '    }\n'
        '    /* 4. en de doos van elk concept waar een opfrisser aan heeft gezeten */\n'
        '    if(s.gram){\n'
        '      Object.keys(perConcept).forEach(function(cid){\n'
        '        var st = s.gram[cid];\n'
        '        if(!st) return;\n'
        '        var b = perConcept[cid];\n'
        '        st.goed = Math.max(0, (st.goed || 0) - b.goed);\n'
        '        st.fout = Math.max(0, (st.fout || 0) - (b.n - b.goed));\n'
        '        if((st.box || 0) > 1) st.box = 1;\n'
        '        st.due = today();\n'
        '        /* bd op leeg, anders houdt gramBij() het antwoord van vandaag voor "al geveld" en\n'
        '           blijft de doos nog een dag op de waarde van het muntje staan. */\n'
        '        st.bd = "";\n'
        '      });\n'
        '    }\n'
        '    return weg;\n'
        '  }}\n'
        '];')

    rep('/* v23.182: 3, want er is een migratie bij gekomen. Blijft dit getal staan, dan denkt elke\n'
        '   bestaande state dat hij bij is en draait migratie 3 nooit. */\n'
        'var SCHEMA = 3;',
        '/* v23.191: 4. Zelfde reden als bij 3: blijft dit getal staan, dan denkt elke bestaande state\n'
        '   dat hij bij is en draait de opruiming van de opfrisser nooit. */\n'
        'var SCHEMA = 4;')

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: één fabriek, één merkteken, één schrijver, en migratie 4, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
