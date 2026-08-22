#!/usr/bin/env python3
# v23.172 - een afgerond onderwerp komt terug als opfrisser, en de ledger begint te kijken
#
# Stefan, 22 aug: "maak je een generiek leerconcept voor grammatica, want die hele grammatica flow,
# ook van andere oefeningen, loopt niet lekker, helemaal niet het herhaal. Ik krijg een vraag en
# spring van stap 1 naar 4 bijvoorbeeld, of oefenen twee keer en aan het einde nog een keer."
#
# De kaart hiervoor staat in het project en is voor de derde keer aangevallen en voor de derde keer
# gesneuveld op mijn eigen bronnen. Wat hier gebouwd wordt is wat overeind bleef.
#
# WAT ER NIET GEBOUWD WORDT, EN DAT IS HET BELANGRIJKSTE
#
# Mijn hoofdvoorstel was: één concept, één blok per dagles. Grond: "drie ontmoetingen binnen één
# sessie tellen samen als ongeveer één gespreide ontmoeting."
#
# Dat is precies omgekeerd. Karpicke & Bauernschmidt 2011 hebben dit experiment gedaan. Drie keer
# ophalen, direct achter elkaar: 26 procent retentie na een week. Drie keer ophalen mét andere items
# ertussen, nog steeds binnen dezelfde sessie: 49 tot 75 procent. Eén keer ophalen: 25 procent.
#
# Mijn claim geldt alleen voor herhalingen die aan elkaar geplakt zitten. Vamos' vier blokken liggen
# juist verspreid over een sessie van 168 antwoorden, dus dat is de gunstige conditie. Ik wilde het
# effect slopen waarvan ik dacht dat het niet bestond.
#
# Verder: elk volwassen SRS scheidt presentatie van planning. Anki en FSRS hebben learning steps die
# expliciet op dezelfde dag vallen, terwijl FSRS voor zijn geheugenmodel alleen de eerste review van
# die dag meetelt. Vamos heeft die planningshelft sinds v23.170. Er hoort geen presentatiebeperking
# bovenop die geen enkel serieus systeem oplegt.
#
# WAT ER WEL IN GAAT
#
# 1. EEN AFGEROND ONDERWERP KOMT TERUG ALS OPFRISSER, NIET OP ZIJN LAATSTE STAP.
#
#    Dit is Stefans "spring van stap 1 naar 4", en het is een echt defect. v.stap is een
#    hoogwatermerk: hij gaat alleen omhoog, nooit terug. gwStart() hervat op
#    Math.min(v.stap, aantalStappen - 1), dus zodra een concept één keer is afgerond land je er
#    voortaan altijd op de laatste stap, de begripsvraag, en zie je de voorbeelden nooit meer.
#
#    Een afgerond onderwerp hoort geen microles meer te zijn maar een opfrisser: één vraag. Die
#    bestaat al (gcOpfrisOnderwerp) en werd alleen gebruikt voor wat op de herhaallijst stond.
#
# 2. "JE WAS HIER GEBLEVEN" WORDT ALTIJD ZICHTBAAR.
#
#    gramWaaromHtml() zegt het wel, maar alleen binnen de dagles, en alleen als je niet eerder in de
#    fout-tak of de klaar-tak valt. Buiten de dagles staat er niets. Nu staat de stapregel er altijd
#    als je middenin een onderwerp zit.
#
# 3. DE LEDGER, EN DIE OBSERVEERT ALLEEN.
#
#    Per dag per concept: hoeveel vragen, hoeveel goed, en uit welk kanaal. Hij verandert niets en
#    beslist niets. Een week lang alleen kijken, want er is nooit een baseline geweest: van geen
#    enkel concept is bekend hoe vaak het werkelijk langskomt of via welke oefening.
#
#    Zeven oefeningen schrijven naar hetzelfde doosje met onvergelijkbare eenheden (een toets van 10
#    vragen telt als 1 met een drempel van 80 procent, een wizardvraag per vraag, een zin met 4
#    afleiders 4 keer en alleen fout, en Clasificador telt een verlopen timer als conceptfout). Wat
#    daaraan moet gebeuren is wegen, niet weggooien, en wegen kan pas als je weet wat er langskomt.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.172"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # 1. een afgerond onderwerp wordt een opfrisser
    # -----------------------------------------------------------------------
    rep('''function gwStart(id, stap){''',
        '''/* v23.172: een afgerond onderwerp komt terug als opfrisser, niet op zijn laatste stap.

   Stefan: "ik krijg een vraag en spring van stap 1 naar 4 bijvoorbeeld." Dat is geen verdwaalde
   klik maar het ontwerp: v.stap is een hoogwatermerk dat alleen omhoog gaat, en gwStart() hervat op
   Math.min(v.stap, aantalStappen - 1). Zodra je een conceptles één keer hebt afgerond wijst dat
   altijd naar de laatste stap, de begripsvraag, en zie je de voorbeelden nooit meer terug.

   Een onderwerp dat je hebt afgerond is geen microles meer maar een herhaling, en daar hoort een
   andere vorm bij: één vraag in plaats van de laatste stap van een les die je al kent. Die vorm
   bestond al (gcOpfrisOnderwerp) en werd alleen gebruikt voor wat op de herhaallijst stond.

   Geldt alleen voor conceptlessen, en alleen als je geen expliciete stap meegeeft: klikken op stap
   3 in de stapbalk hoort gewoon stap 3 te openen, en de handgeschreven wizards hebben een verhaal
   dat je wél in zijn geheel wil kunnen herlezen. */
function gwOpfrisInPlaats(id, stap){
  if(typeof stap === "number") return null;                 // je koos zelf een stap
  if(!/^concept-/.test(id || "")) return null;              // geen conceptles
  var v = null;
  try { v = gwVoortgangLees(id); } catch(e){ return null; }
  if(!v || !v.klaar) return null;                           // nog niet afgerond
  var oid = null;
  try { oid = gcOpfrisId(id); } catch(e){ return null; }
  var o = null;
  try { o = gcOpfrisOnderwerp(oid); } catch(e){ o = null; }
  return o ? oid : null;                                    // alleen als er ook echt een vraag is
}

function gwStart(id, stap){
  var opfris = gwOpfrisInPlaats(id, stap);
  if(opfris) return gwStart(opfris, 0);''')

    # -----------------------------------------------------------------------
    # 2. "je was hier gebleven" staat er altijd
    # -----------------------------------------------------------------------
    rep('''    (inFlow ? "<p class='muted' style='margin:-2px 0 8px; font-size:.83rem'>"+gramWaaromHtml(gwSess.id)+"</p>" : "")+''',
        '''    (inFlow ? "<p class='muted' style='margin:-2px 0 8px; font-size:.83rem'>"+gramWaaromHtml(gwSess.id)+"</p>" : "")+
    /* v23.172: en buiten de dagles ten minste waar je gebleven was. gramWaaromHtml() zegt dat wel,
       maar alleen in de flow, en alleen als je niet eerder in de fout-tak of de klaar-tak valt.
       Stefan opende een onderwerp op stap 4 zonder dat iets vertelde waarom. */
    (!inFlow && gwSess.stap > 0 ? "<p class='muted' style='margin:-2px 0 8px; font-size:.83rem'>"+
      ct("Hier was je gebleven: stap "+(gwSess.stap+1)+" van "+o.stappen.length+".",
         "This is where you left off: step "+(gwSess.stap+1)+" of "+o.stappen.length+".")+"</p>" : "")+''')

    # -----------------------------------------------------------------------
    # 3. de ledger: kijkt mee, beslist niets
    # -----------------------------------------------------------------------
    rep('''function gramBij(cid, goed){''',
        '''/* ================= DE LEDGER (v23.172) =================

   Wat er per dag per concept gebeurde, en via welke oefening. Hij verandert niets en beslist niets:
   dit is een week meekijken voordat er iets aan het herhaalritme verandert.

   Waarom hij er moet zijn. Zeven oefeningen schrijven naar hetzelfde doosje met onvergelijkbare
   eenheden: een toetsje van tien vragen telt als één schrijving met een drempel van 80 procent, een
   wizardvraag telt per vraag, een zin met vier afleiders telt vier keer en alleen fout, en
   Clasificador telt een verlopen klok als conceptfout. Daar moet gewogen worden in plaats van
   weggegooid, en wegen kan pas als je weet wat er werkelijk langskomt.

   En er is nooit een baseline geweest. Van geen enkel concept is bekend hoe vaak het op een dag
   voorbijkomt of via welk kanaal. Mijn eigen ontwerp van vandaag stond op de aanname dat het er
   vier per les waren, en die aanname stond op één anekdote.

   Vorm: S.gramLog[dag][cid] = {n, goed, k:{kanaal:[n, goed]}}. Zeven dagen diep, want dit is een
   meetinstrument en geen archief. */
var GRAMLOG_DAGEN = 7;
function gramLog(cid, kanaal, goed){
  if(!cid) return;
  try {
    var d = today();
    S.gramLog = S.gramLog || {};
    if(!S.gramLog[d]) S.gramLog[d] = {};
    var dag = S.gramLog[d];
    var r = dag[cid] || (dag[cid] = {n:0, goed:0, k:{}});
    r.n++;
    if(goed) r.goed++;
    var kn = r.k[kanaal] || (r.k[kanaal] = [0, 0]);
    kn[0]++;
    if(goed) kn[1]++;
    // ouder dan een week gaat weg; dit hoort in localStorage te passen naast al het andere
    var dagen = Object.keys(S.gramLog).sort();
    while(dagen.length > GRAMLOG_DAGEN) delete S.gramLog[dagen.shift()];
  } catch(e){}
}

/* Wat de ledger van vandaag weet, in leesbare vorm. Nog nergens aangeroepen behalve door de suite:
   dit is het venster waardoor we over een week naar Stefans echte cijfers kijken. */
function gramLogVandaag(){
  var d = today(), uit = [];
  try {
    var dag = (S.gramLog || {})[d] || {};
    Object.keys(dag).forEach(function(cid){
      var r = dag[cid];
      uit.push({cid:cid, n:r.n, goed:r.goed, kanalen:Object.keys(r.k),
                perKanaal:r.k, blokken:Object.keys(r.k).length});
    });
  } catch(e){}
  return uit.sort(function(a, b){ return b.n - a.n; });
}

function gramBij(cid, goed){''')

    # en de zeven aanroepplekken, elk met hun eigen kanaalnaam
    rep('''  gcConceptenVoorQuiz(qz).forEach(function(cid){ gramBij(cid, pct >= 0.8); });''',
        '''  gcConceptenVoorQuiz(qz).forEach(function(cid){ gramBij(cid, pct >= 0.8); gramLog(cid, "toets", pct >= 0.8); });''')

    rep('''      if(!t.echt && t.cid) gramBij(t.cid, false);''',
        '''      if(!t.echt && t.cid){ gramBij(t.cid, false); gramLog(t.cid, "tegels", false); }''')

    rep('''    if(fregel) gramBij(fregel.cid, false);''',
        '''    if(fregel){ gramBij(fregel.cid, false); gramLog(fregel.cid, "zin", false); }''')

    rep('''  gramBij(clSpel.c.id, false);''',
        '''  gramBij(clSpel.c.id, false); gramLog(clSpel.c.id, "clasificador", false);''')

    rep('''    gramBij(clSpel.c.id, true);''',
        '''    gramBij(clSpel.c.id, true); gramLog(clSpel.c.id, "clasificador", true);''')

    rep('''  gramBij(gcConceptVoorCorr(id), goed);''',
        '''  gramBij(gcConceptVoorCorr(id), goed); gramLog(gcConceptVoorCorr(id), "corrector", goed);''')

    rep('''  else if(o.concept) gramBij(o.concept, i === q.g);''',
        '''  else if(o.concept){ gramBij(o.concept, i === q.g);
    /* opfrisser en microles zijn hetzelfde concept maar een ander blok, en dat verschil is precies
       wat we willen kunnen zien. */
    gramLog(o.concept, o.opfris ? "opfris" : "microles", i === q.g); }''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
