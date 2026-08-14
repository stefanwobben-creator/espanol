#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.94: vijf tellers die de waarheid niet vertelden (punt 3, 6, 7, 10 en 11).

## Punt 3: één nieuw woord per dag

`dagPortie()` deelt nieuwe woorden uit in twee stapels: wat binnen je poortrang valt, plus precies
één woord van daarbuiten. Die ene is bedoeld als kruimel voor wie nog aan zijn basis werkt, en dat
werkt zolang er lessen open staan, want leswoorden gaan altijd door de poort.

Stefan heeft alle lessen af. Dan is de eerste stapel leeg en levert de portie één woord per dag,
terwijl zijn instelling er twintig belooft. Geen woorden is geen voortgang, en dat verklaart precies
wat hij voelde: hard werken zonder dat de teller beweegt.

Nu: is er binnen de poort minder te halen dan je dagbudget, dan wordt er van buiten aangevuld tot dat
budget vol is. `fresh` is al op niveau gesorteerd, dus je krijgt automatisch de makkelijkste eerst en
belandt niet in zeldzame woorden. De poort blijft doen waar hij voor is; hij mag alleen niet meer
uithongeren.

## Punt 6: een fout bleef voor altijd staan

`S.errors` had één schrijfplek en geen enkele afbouw. Eén typefout zette een zin voorgoed in
tegelmodus en liet hem 40 procent van de tijd terugkomen, ook als je hem al twintig keer daarna goed
had. De ladder ging maar één kant op.

Nu telt een fout drie goede beurten af. Daarna is hij weg. Drie en niet één, want één keer goed kan
geluk zijn; drie keer achter elkaar niet.

## Punt 7: je werd gestraft voor een goed antwoord

De volgorde was: fout noteren, dán pas mag je vragen "is mijn variant ook goed?". Zei het model ja,
dan kreeg je punten, ging de zin op `done`, en bleef de fout gewoon staan. Voorgoed, want zie punt 6.
Nu wordt de foutregistratie teruggedraaid zodra de variant wordt goedgekeurd. Het was tenslotte geen
fout.

## Punt 10: het chipje telde met drie getallen tegelijk

Teller uit `newToday()`, noemer uit `dagPortieVloer()`, en het maximum uit `nieuwPlafond()`. Bij dertig
minuten stond er zoiets als "5/12 (max 23)" terwijl de portie er vijftien geeft. Drie functies, drie
antwoorden, één chipje. Nu één bron: wat je vandaag beloofd is, en hoeveel daarvan je hebt gehad.

## Punt 11: de teller telde wat je claimde

Bij het instellen zeg je welk niveau je al hebt. `niveauClaim()` zet daar rijen voor neer met
`claim:1`, en `voortgangTellers()` telde die mee als "ooit geoefend". Een paar honderd woorden die je
nooit hebt gezien. Nu tellen ze pas mee zodra je ze echt een keer hebt gehad.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.94"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.94" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- punt 3
A_PORTIE = '''    fresh = binnen.concat(buiten.slice(0, 1));'''
N_PORTIE = '''    /* v23.94: hier stond `buiten.slice(0, 1)` — precies één woord van buiten de poort per dag.
       Dat klopt zolang er lessen open staan (leswoorden gaan altijd door de poort), maar wie zijn
       lespad af heeft, houdt een lege eerste stapel over en krijgt dan één nieuw woord per dag
       terwijl zijn instelling er twintig belooft. Gemeten bij Stefan: 814 woorden geleerd, nul dagen
       voorraad, één nieuw woord per dag.
       Nu vullen we aan tot het dagbudget. fresh is al op niveau gesorteerd, dus dat zijn automatisch
       de makkelijkste van buiten, en niet zomaar zeldzame woorden. Er blijft altijd minstens die ene
       kruimel, ook als je dagbudget nul zou zijn. */
    var ruimte = Math.max(1, Math.min(nieuwPerDag(), newAllowance()) - binnen.length);
    fresh = binnen.concat(buiten.slice(0, ruimte));'''

# ---------------------------------------------------------------- punt 6 en 7: de fout mag slijten
A_LOGERR = '''  var k = type+":"+id;
  if(!S.errors[k]) S.errors[k] = {id:id, type:type, tag:tag, count:0, laatst:"", dag:""};
  S.errors[k].count++;'''
N_LOGERR = '''  var k = type+":"+id;
  if(!S.errors[k]) S.errors[k] = {id:id, type:type, tag:tag, count:0, laatst:"", dag:""};
  S.errors[k].count++;
  S.errors[k].goed = 0;   // v23.94: een nieuwe fout zet de teller van goede beurten terug op nul'''

A_LOGERR_EIND = '''  logOpnameMisschien();
  persist();'''
N_LOGERR_EIND = '''  logOpnameMisschien();
  persist();'''

A_HAAK = '''function logError(id, type, tag, extra){'''
N_HAAK = '''/* v23.94: fouten mochten slijten, en dat konden ze niet.

   S.errors had één schrijfplek (logError) en geen enkele afbouw. Eén typefout zette een zin voorgoed
   in tegelmodus (zie sModus) en liet hem 40 procent van de tijd terugkomen (zie de zinnenpool), ook
   als je hem daarna twintig keer goed had. Dat is geen leersysteem maar een strafregister.

   Drie goede beurten en de fout is weg. Drie en niet één: één keer goed kan geluk zijn, drie keer
   achter elkaar niet. Wie opnieuw de fout in gaat, begint weer bij nul (zie logError).

   foutWeg() is de harde variant, voor het geval dat er helemaal geen fout wás: het taalmodel dat
   zegt dat jouw variant ook goed Spaans is. Zie punt 7. */
function foutGoedeBeurt(id, type){
  var k = type + ":" + id, e = S.errors && S.errors[k];
  if(!e) return;
  e.goed = (e.goed || 0) + 1;
  if(e.goed >= 3) delete S.errors[k];
}
function foutWeg(id, type){
  var k = type + ":" + id;
  if(S.errors && S.errors[k]) delete S.errors[k];
}
function logError(id, type, tag, extra){'''

A_GOEDWOORD = '''  if(good){
    // v20.0: de laatste doos hoort bij een check die je niet zelf beoordeelt. Zonder die check
    // blijft een woord op de een-na-laatste staan, hoe vaak je ook "wist ik" zegt. Zodra hij daar
    // staat biedt renderWord de check aan; zie wCheckNodig.
    st.box = Math.min(st.box+1, st.k ? INTERVALS.length-1 : INTERVALS.length-2);'''
N_GOEDWOORD = '''  if(good){
    foutGoedeBeurt(wCur.id, "woord");   // v23.94: drie goede beurten en de oude fout is weg
    // v20.0: de laatste doos hoort bij een check die je niet zelf beoordeelt. Zonder die check
    // blijft een woord op de een-na-laatste staan, hoe vaak je ook "wist ik" zegt. Zodra hij daar
    // staat biedt renderWord de check aan; zie wCheckNodig.
    st.box = Math.min(st.box+1, st.k ? INTERVALS.length-1 : INTERVALS.length-2);'''

A_ZINGOED = '''    S.done[s.id] = true; gehaald = true; addXP(xpExact);'''
N_ZINGOED = '''    S.done[s.id] = true; gehaald = true; addXP(xpExact);
    foutGoedeBeurt(s.id, "zin");   // v23.94'''

A_ZINLOOSE = '''    S.done[s.id] = true; gehaald = true; addXP(4); compMark("schrijven", s.id); trackPoging(false);'''
N_ZINLOOSE = '''    S.done[s.id] = true; gehaald = true; addXP(4); compMark("schrijven", s.id); trackPoging(false);
    foutGoedeBeurt(s.id, "zin");   // v23.94'''

A_AI_GOED = '''      if(res.goed){
        S.done[s.id] = true; addXP(4); persist(); checkLessonComplete();'''
N_AI_GOED = '''      if(res.goed){
        /* v23.94: en de fout die drie regels eerder is genoteerd gaat weg. Je variant was goed
           Spaans, dus er was geen fout. Tot nu toe bleef die staan, en sinds S.errors nergens werd
           afgebouwd betekende dat: voorgoed in tegelmodus, voor een antwoord dat klopte. */
        foutWeg(s.id, "zin");
        S.done[s.id] = true; addXP(4); persist(); checkLessonComplete();'''

# ---------------------------------------------------------------- punt 10
A_CHIP = '''  if(rel.chipNieuw) chipsHtml += chip(nieuw >= dagPortieVloer(), ct("nieuwe woorden ","new words ")+nieuw+"/"+dagPortieVloer()+" (max "+nieuwPlafond()+")");'''
N_CHIP = '''  /* v23.94: dit chipje telde met drie getallen tegelijk. De teller kwam uit newToday(), de noemer
     uit dagPortieVloer() en het maximum uit nieuwPlafond(). Bij dertig minuten stond er "5/12
     (max 23)" terwijl de portie er vijftien geeft: drie functies, drie antwoorden, één chipje.
     Nu één bron: wat je vandaag beloofd is, en hoeveel daarvan je hebt gehad. */
  if(rel.chipNieuw){
    var beloofd = Math.max(1, Math.min(nieuwPerDag(), nieuwPlafond()));
    chipsHtml += chip(nieuw >= beloofd, ct("nieuwe woorden ","new words ")+Math.min(nieuw, beloofd)+"/"+beloofd);
  }'''

# ---------------------------------------------------------------- punt 11
A_GEOEFEND = '''    if(!st || typeof st !== "object") continue;
    geoefend++;'''
N_GEOEFEND = '''    if(!st || typeof st !== "object") continue;
    /* v23.94: een geclaimde rij is geen geoefend woord. niveauClaim() zet bij het instellen een paar
       honderd rijen neer met claim:1, en die telden hier gewoon mee als "ooit geoefend". Bij Stefan
       scheelde dat ruim vierhonderd. answerWord haalt de vlag weg zodra je het woord echt een keer
       hebt gehad, dus vanaf dat moment telt hij wel. */
    if(st.claim && !(st.n > 0)) continue;
    geoefend++;'''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("dagPortie", A_PORTIE), ("logError", A_LOGERR), ("de haak voor logError", A_HAAK),
        ("het goede antwoord bij een woord", A_GOEDWOORD), ("de exacte zin", A_ZINGOED),
        ("de zin op accenten na", A_ZINLOOSE), ("de AI-goedkeuring", A_AI_GOED),
        ("het chipje", A_CHIP), ("voortgangTellers", A_GEOEFEND)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.93. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_PORTIE, N_PORTIE)
    rep(A_HAAK, N_HAAK)
    rep(A_LOGERR, N_LOGERR)
    rep(A_GOEDWOORD, N_GOEDWOORD)
    rep(A_ZINGOED, N_ZINGOED)
    rep(A_ZINLOOSE, N_ZINLOOSE)
    rep(A_AI_GOED, N_AI_GOED)
    rep(A_CHIP, N_CHIP)
    rep(A_GEOEFEND, N_GEOEFEND)

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
