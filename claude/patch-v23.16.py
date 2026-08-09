#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.16: de dagportie luistert naar je instelling en naar of je hem afmaakt.

De vraag was of de app de golf van 198 nieuwe A2-woorden moet afremmen of laten komen. Het antwoord
is dat hij al afremt, alleen op de verkeerde dingen.

Ten eerste stond het plafond op een vast getal: MAX_NEW_PER_DAY = 15. En dagPortieNieuw() is
doelMinuten() maal 0,5, dus bij dertig minuten is dat precies 15. Het plafond zat op de instelling
zelf. Wie 45 of 60 minuten koos kreeg geen woord extra, en Stefans les was in vier minuten klaar
terwijl er dertig stonden ingesteld. Een instelling die niets doet is erger dan geen instelling.

Ten tweede regelde het foutpercentage het tempo: onder de 15 procent erbij, boven de 25 eraf. Die
twee grenzen zijn verzonnen, en het getal waar ze aan hangen mengt nieuwe woorden, herhalingen,
dictado en toetsjes door elkaar. Dat is precies het geleende getal waar dit project al drie keer op
is vastgelopen.

Wat er nu stuurt is of je je portie afmaakt. Dat is geen afgeleide en geen schatting: het staat in
S.lesFlow, het gaat direct over de vraag of de portie past, en het is voor iedereen hetzelfde te
lezen. Zes van de zeven dagen afgemaakt betekent dat er ruimte is. Drie of minder betekent dat hij te
groot is. Daartussen blijft hij staan.

En de golf zelf mag je zien. Als de poort opengaat staat er een regel bij het nieuws dat er woorden
zijn bijgekomen. Zien is niet hetzelfde als slikken: de portie blijft even groot, alleen weet je nu
dat de plank weer vol ligt.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function nieuwPlafond()" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. het plafond volgt je minuten
rep(
    """var MAX_NEW_PER_DAY = 15, MIN_NEW_PER_DAY = 5;""",
    """var MAX_NEW_PER_DAY = 15, MIN_NEW_PER_DAY = 5;
/* v23.16. MAX_NEW_PER_DAY stond op 15 en dagPortieNieuw() is doelMinuten() maal 0,5. Bij dertig
   minuten zijn die twee dus precies gelijk, en dat is de stand die Stefan had staan. Gevolg: het
   plafond zat bovenop zijn eigen instelling, en 45 of 60 minuten kiezen leverde geen enkel woord
   extra op. Zijn les was in vier minuten klaar met dertig minuten ingesteld.
   Het plafond hoort niet vast te staan maar bij je instelling te horen. De 60 erboven is de echte
   bovengrens: meer dan zestig nieuwe woorden op een dag is geen leren meer maar doorbladeren, en
   dat blijft de app weigeren ook als je hem erom vraagt. */
function nieuwPlafond(){
  return Math.max(MIN_NEW_PER_DAY, Math.min(60, Math.round(doelMinuten() * 0.75)));
}
/* Hoe vaak maakte je je dagportie de laatste week af? Dit stuurt het tempo, in plaats van het
   foutpercentage dat er tot v23.15 aan hing. Twee redenen. Het foutpercentage telt nieuwe woorden,
   herhalingen, dictado en toetsjes bij elkaar op, dus het zegt niet of jouw portie past. En de
   grenzen eraan (onder 15 procent erbij, boven 25 eraf) waren verzonnen getallen.
   Of je afmaakt wat je krijgt is geen afgeleide. Het is de vraag zelf. */
function afgemaakt7(){
  var t = today(), n = 0, i;
  for(i = 0; i < 7; i++){ if(S.lesFlow && S.lesFlow[addDays(t, -i)]) n++; }
  return n;
}""")

rep(
    """function newAllowance(){ return Math.max(0, MAX_NEW_PER_DAY - newToday()); }""",
    """function newAllowance(){ return Math.max(0, nieuwPlafond() - newToday()); }""")

# ---------------------------------------------------------------- 2. het tempo volgt je afmaken
rep(
    """  var nieuw = dagPortieNieuw(), cap = dagPortieCap();
  var k = leerKpi().recent;
  if(k.pog >= 40 && k.pct !== null){
    if(k.pct < 15){ nieuw = dagPortieNieuw() + 2; cap = dagPortieCap() + 6; }
    else if(k.pct > 25){ nieuw = Math.round(dagPortieNieuw() / 2); }
  }""",
    """  var nieuw = dagPortieNieuw(), cap = dagPortieCap();
  /* v23.16: hier hing het tempo aan het foutpercentage, met 15 en 25 procent als grenzen. Zie de
     toelichting bij afgemaakt7() voor waarom dat het verkeerde getal was. Nu stuurt of je je portie
     afmaakt, en dat vraagt een week aan dagen voordat het iets zegt: onder de zeven dagen blijft de
     portie staan zoals hij is, want een nieuwe gebruiker heeft nog niets afgemaakt en hoort daar
     niet voor gestraft te worden. */
  var af = afgemaakt7(), dgn = dagenTotaal();
  if(dgn >= 7){
    if(af >= 6){ nieuw = dagPortieNieuw() + 3; cap = dagPortieCap() + 8; }
    else if(af <= 3){ nieuw = Math.round(dagPortieNieuw() / 2); }
  }""")

rep(
    """  S.tempo = {d:t, n:Math.min(nieuw, MAX_NEW_PER_DAY), cap:cap, pct:(k.pct === null ? -1 : k.pct)};""",
    """  S.tempo = {d:t, n:Math.min(nieuw, nieuwPlafond()), cap:cap, pct:af};""")

# ---------------------------------------------------------------- 3. de teksten die het plafond noemen
rep(
    """        ? ct("Er "+(capRest.length===1?"wacht nog 1 nieuw woord":"wachten nog "+capRest.length+" nieuwe woorden")+" achter je dagmaximum van "+MAX_NEW_PER_DAY+". Morgen komen ze vanzelf, of doe ze nu.",
             capRest.length===1?"1 new word is waiting behind your daily max of "+MAX_NEW_PER_DAY+". It'll come tomorrow, or do it now.":capRest.length+" new words are waiting behind your daily max of "+MAX_NEW_PER_DAY+". They'll come tomorrow, or do them now.")
        : ct("Dit was je portie voor vandaag: "+MAX_NEW_PER_DAY+" nieuwe woordjes per dag blijven beter plakken dan honderd in een keer. Morgen staan de volgende klaar.",
             "That was your round for today: "+MAX_NEW_PER_DAY+" new words a day stick better than a hundred at once. The next ones are ready tomorrow."))""",
    """        ? ct("Er "+(capRest.length===1?"wacht nog 1 nieuw woord":"wachten nog "+capRest.length+" nieuwe woorden")+" achter je dagmaximum van "+nieuwPlafond()+". Morgen komen ze vanzelf, of doe ze nu.",
             capRest.length===1?"1 new word is waiting behind your daily max of "+nieuwPlafond()+". It'll come tomorrow, or do it now.":capRest.length+" new words are waiting behind your daily max of "+nieuwPlafond()+". They'll come tomorrow, or do them now.")
        : ct("Dit was je portie voor vandaag: "+nieuwPlafond()+" nieuwe woordjes per dag blijven beter plakken dan honderd in een keer. Morgen staan de volgende klaar.",
             "That was your round for today: "+nieuwPlafond()+" new words a day stick better than a hundred at once. The next ones are ready tomorrow."))""")

rep(
    """  if(rel.chipNieuw) chipsHtml += chip(nieuw >= dagPortieVloer(), ct("nieuwe woorden ","new words ")+nieuw+"/"+dagPortieVloer()+" (max "+MAX_NEW_PER_DAY+")");""",
    """  if(rel.chipNieuw) chipsHtml += chip(nieuw >= dagPortieVloer(), ct("nieuwe woorden ","new words ")+nieuw+"/"+dagPortieVloer()+" (max "+nieuwPlafond()+")");""")

# ---------------------------------------------------------------- 4. de golf mag je zien
rep(
    """function dagNieuwsRegels(){
  var och = dagSnapOchtend();
  var nu = dagSnapNu();
  var r = [];""",
    """/* v23.16. Ging de poort open, dan kwam er in stilte een hele voorraad woorden bij. Stefan zag
   daar niets van: dezelfde portie, dezelfde knop, alleen andere woorden erin. Dat is precies het
   moment waarop een app kan laten merken dat er iets verdiend is.
   Wat hier bewust niet gebeurt is de portie vergroten. Zien dat de plank vol ligt is iets anders
   dan hem in een keer op je bord krijgen, en de portie is niet voor niets klein en voorspelbaar. */
function poortNieuws(){
  var po = S && S.poortOpen;
  if(!po || po.dag !== today()) return null;          // alleen op de dag zelf, daarna is het oud nieuws
  var r = po.rang;
  if(!(r > 0)) return null;
  var niv = NIV_NAAM[Math.min(r, NIV_NAAM.length - 1)], n = 0, i, w;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    if(S.srs[w.id]) continue;
    if(woordNiveau(w.id) === r) n++;
  }
  return {rang:r, niv:niv, aantal:n};
}
function dagNieuwsRegels(){
  var och = dagSnapOchtend();
  var nu = dagSnapNu();
  var r = [];
  var pn = poortNieuws();
  if(pn){
    r.push({e:"\\ud83d\\udd13", go:"perfil",
      t:ct("<b>"+NIV_NAAM[Math.max(0, pn.rang - 1)]+" staat.</b> Er staan "+pn.aantal+" nieuwe "+pn.niv+"-woorden klaar",
           "<b>"+NIV_NAAM[Math.max(0, pn.rang - 1)]+" is in place.</b> "+pn.aantal+" new "+pn.niv+" words are ready")});
  }""")

rep(
    """function dagNieuwsHtml(){
  var r = dagNieuwsRegels();""",
    """function dagNieuwsHtml(){
  /* De stand onthouden gebeurt hier en niet in dagNieuwsRegels(), want die wordt ook als stille
     lezer aangeroepen vanuit dagRelevantie() en een lezer hoort niets te veranderen. De eerste keer
     wordt de stand stil gezet: een nieuwe gebruiker heeft niets ontgrendeld en hoort geen felicitatie
     te krijgen voor het openen van de app. */
  try {
    var pr = poortRang();
    if(S.poortGezien === undefined || S.poortGezien === null){ S.poortGezien = pr; persist(); }
    else if(pr > S.poortGezien){ S.poortOpen = {rang:pr, dag:today()}; S.poortGezien = pr; persist(); }
  } catch(e){}
  var r = dagNieuwsRegels();""")

# ---------------------------------------------------------------- 5. versie
rep('var APP_VERSIE = "v23.15";', 'var APP_VERSIE = "v23.16";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.16 toegepast op", PAD)
