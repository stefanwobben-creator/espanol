#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.143: je maakt een grammatica-onderwerp af, en je ziet waarom je het krijgt.

Stefan, 20 aug: "De grammatica [lijkt] beetje random of niet een heel toetsje maar een deel van de
grammatica les, dat lijkt raar."

## Wat er mis was, en het is geen gevoel

Een conceptles is sinds v23.107 geen scherm maar een stapel: drie tot vijf stappen, elk met een paar
vragen. In je dagles krijg je één stap. Dat is met opzet zo: drie alinea's plus twaalf vragen is een
grammaticaboek en geen les van tien minuten.

Maar wát er daarna gebeurde was niet met opzet. `lesFlowGramId()` koos zijn onderwerp met
`gramVersKandidaat()`, en die filtert op `gramAangeraakt()`: alleen onderwerpen waar je nog nooit een
vraag van hebt beantwoord. Zodra je één stap had gedaan was het onderwerp aangeraakt, dus het kwam
nooit meer terug als "het onderwerp van vandaag". Wat er wél van terugkwam was de opfrisser uit de
wachtrij: één losse vraag.

Het gevolg, precies wat je beschrijft: elke dag stap 1 van een nieuw onderwerp, nooit stap 2. Je
verzamelt beginnetjes. En omdat het elke dag iets anders is, is er ook geen zichtbare reden waarom
je juist dit krijgt.

## Wat er nu gebeurt

**1. Afmaken gaat voor beginnen.** `gcOnafKandidaat()` komt vóór `gramVersKandidaat()`: is er een
onderwerp waarvan je stap 1 hebt gedaan maar de rest niet, dan is dat het onderwerp van vandaag.
Hoort het ook nog bij de les waar je nu in zit, dan gaat het voor; daarna telt wie het dichtst bij af
is. Zo loop je een onderwerp in drie of vier dagen uit in plaats van nooit.

Uithongering kan niet: een onderwerp heeft drie tot vijf stappen, dus na hooguit vier dagen is het
klaar en komt er weer iets nieuws. Dat is een bovengrens die uit de data komt, niet uit een teller.

**2. De les zegt waarom je dit krijgt.** Eén regel onder de titel, alleen in de dagles:

  * "Hier ging het twee keer mis, dus je krijgt de hele uitleg."
  * "Hier was je gebleven. Dit onderwerp maak je nu af."
  * "Nieuw, en het hoort bij les 3: En la ciudad."
  * "Het volgende onderwerp in je leervolgorde."

Dat is dezelfde regel als bij de meting onder de ketting (v23.101) en bij de minuten (v23.17): een
keuze mag alleen op het scherm staan met zijn herkomst erbij.

**3. Het plan zegt hoe ver je bent.** Het grammatica-blok op Vandaag zei "1 onderwerp". Nu staat er
"El of la · stap 2 van 4", en dat is precies het antwoord op "een deel van de grammatica les".

## Wat dit niet doet

De stap wordt geen hele les. Eén stap per dag blijft, want de dosis is het punt (Norris & Ortega
2000: expliciete instructie werkt, in kleine hoeveelheden). Wat verandert is dat de stappen op
elkaar volgen in plaats van elke dag ergens anders te beginnen.

Bewaakt door test/suites/pw-gramaf.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.143"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ------------- 1. het onderwerp dat je begon maar niet afmaakte

rep(
    """function gramVersKandidaat(les){""",
    """/* v23.143: afmaken gaat voor beginnen.

   gramVersKandidaat() hieronder filtert op gramAangeraakt(): alleen onderwerpen waar je nog nooit
   een vraag van beantwoord hebt. Zodra je in je dagles één stap deed was een onderwerp aangeraakt,
   dus het kwam nooit meer terug als onderwerp van de dag. Wat er wél van terugkwam was de opfrisser
   uit de wachtrij: één losse vraag. Resultaat: elke dag stap 1 van iets nieuws, nooit stap 2.

   Deze functie zoekt het omgekeerde: een onderwerp dat open staat, waarvan je minstens één stap
   afrondde, en dat nog niet klaar is. Hoort het bij de les waar je nu in zit, dan gaat het voor;
   daarna wint wie het dichtst bij af is, want dat is het onderwerp dat je het snelst uit hebt.

   Uithongering van nieuwe stof kan niet: een conceptles heeft drie tot vijf stappen (gcBouw), dus
   na hooguit vier dagen is er niets onafs meer en komt gramVersKandidaat() weer aan de beurt. */
function gcOnafKandidaat(les){
  var tk = (typeof gwTrackKey === "function") ? gwTrackKey() : "a2";
  var idxs = (les && les.spiek) || [];
  var beste = null, besteScore = -1;
  gcGeordend().forEach(function(c){
    if(!gcConceptOpen(c.id)) return;
    var v = gwVoortgangLees("concept-" + c.id);
    if(v.klaar) return;
    if(!(v.stap > 0)) return;          // nog geen stap af: dat is vers, niet onaf
    var o = null;
    try { o = gcOnderwerp("concept-" + c.id); } catch(e){ o = null; }
    if(!o || !o.stappen || !o.stappen.length) return;
    if(v.stap >= o.stappen.length) return;   // alles gehad, alleen het vinkje ontbreekt
    var lijst = (c.spiek && c.spiek[tk]) || [], bijLes = 0, i;
    for(i = 0; i < idxs.length; i++){ if(lijst.indexOf(idxs[i]) !== -1){ bijLes = 1; break; } }
    var score = bijLes * 100 + v.stap;
    if(score > besteScore){ besteScore = score; beste = c; }
  });
  return beste;
}
function gramVersKandidaat(les){""",
)

rep(
    """  var fout = gramFoutTop();
  if(fout && (fout.st.box || 0) === 0 && (fout.st.fout || 0) >= 2) return "concept-" + fout.c.id;

  // Daarna een concept uit de les van vandaag dat je hier nog nooit hebt gedaan. Nieuw voor je,
  // en het hoort bij de woorden die je net hebt geleerd.""",
    """  var fout = gramFoutTop();
  if(fout && (fout.st.box || 0) === 0 && (fout.st.fout || 0) >= 2) return "concept-" + fout.c.id;

  /* v23.143: eerst afmaken wat je begon. Zonder deze regel koos de dagles elke dag een onderwerp
     waar je nog nooit een vraag van had gezien, en bleef stap 2 altijd liggen. */
  var onaf = gcOnafKandidaat(les);
  if(onaf) return "concept-" + onaf.id;

  // Daarna een concept uit de les van vandaag dat je hier nog nooit hebt gedaan. Nieuw voor je,
  // en het hoort bij de woorden die je net hebt geleerd.""",
)

# ------------- 2. waarom je dit onderwerp krijgt

rep(
    """function gwTitel(o){ return ct(o.titel, o.titelEn); }""",
    """function gwTitel(o){ return ct(o.titel, o.titelEn); }
/* v23.143: waarom krijg je juist dit onderwerp?

   Stefan: "de grammatica lijkt beetje random." Dat was het niet, maar de reden stond nergens. Deze
   functie leidt hem af uit dezelfde toestand waarop lesFlowGramId() kiest, dus er is geen tweede
   waarheid die uit de pas kan gaan lopen: de fouten uit gramLees, de stand uit gwVoortgangLees, de
   spiekbrief van je huidige les. Staat er niets bijzonders, dan is het antwoord ook gewoon "dit is
   de volgende in de rij". */
function gramWaaromHtml(id){
  if(!id) return "";
  if(/^opfris-/.test(id)){
    return ct("Dit kwam vandaag terug om even op te frissen.",
              "This came back up today for a quick refresh.");
  }
  var cid = String(id).replace(/^concept-/, "");
  var st = null;
  try { st = gramLees(cid); } catch(e){ st = null; }
  if(st && (st.box || 0) === 0 && (st.fout || 0) >= 2){
    return ct("Hier ging het " + st.fout + " keer mis, dus je krijgt de hele uitleg.",
              "This went wrong " + st.fout + " times, so you get the full explanation.");
  }
  var v = gwVoortgangLees("concept-" + cid);
  if(v.stap > 0 && !v.klaar){
    return ct("Hier was je gebleven. Dit onderwerp maak je nu af.",
              "This is where you left off. You're finishing this topic now.");
  }
  var les = null;
  try { les = huidigeLes(); } catch(e){ les = null; }
  if(les){
    var tk = (typeof gwTrackKey === "function") ? gwTrackKey() : "a2";
    var c = null;
    try { c = gcConcept(cid); } catch(e){ c = null; }
    var lijst = (c && c.spiek && c.spiek[tk]) || [], idxs = les.spiek || [], i;
    for(i = 0; i < idxs.length; i++){
      if(lijst.indexOf(idxs[i]) !== -1){
        return ct("Nieuw, en het hoort bij les " + les.num + ": " + les.titel + ".",
                  "New, and it belongs to lesson " + les.num + ": " + les.titel + ".");
      }
    }
  }
  return ct("Het volgende onderwerp in je leervolgorde.",
            "The next topic in your learning order.");
}""",
)

rep(
    """    "<h2>"+o.icon+" "+ct(stap.kop, stap.kopEn)+"</h2>"+
    gwStapNavHtml(o);""",
    """    "<h2>"+o.icon+" "+ct(stap.kop, stap.kopEn)+"</h2>"+
    /* v23.143: in de dagles staat erbij waarom je dit onderwerp krijgt. Buiten de dagles koos je
       het zelf, en dan is de vraag niet aan de orde. */
    (inFlow ? "<p class='muted' style='margin:-2px 0 8px; font-size:.83rem'>"+gramWaaromHtml(gwSess.id)+"</p>" : "")+
    gwStapNavHtml(o);""",
)

# ------------- 3. het plan zegt hoe ver je in het onderwerp bent

rep(
    """    blokken.push({stap:"grammatica", naam:ct("Grammatica","Grammar"), draad:ct("leren","study"),
      wat:gram.length + " " + (gram.length === 1 ? ct("onderwerp","topic") : ct("onderwerpen","topics")),
      sec:gBeurten * sec});""",
    """    blokken.push({stap:"grammatica", naam:ct("Grammatica","Grammar"), draad:ct("leren","study"),
      wat:dagGramWat(gram), sec:gBeurten * sec});""",
)

rep(
    """function dagGramVragen(id){""",
    """/* v23.143: "1 onderwerp" zei niets. Nu staat er welk onderwerp, en hoe ver je erin bent, want dat
   is precies wat Stefan miste: "niet een heel toetsje maar een deel van de grammatica les". Een deel
   is prima, zolang je ziet welk deel en hoeveel er nog komt. */
function dagGramWat(ids){
  var n = (ids || []).length;
  if(!n) return "";
  var id = ids[n - 1];                 // de opfrisser staat vooraan; het onderwerp is de laatste
  var voor = n > 1 ? ct("opfrisser + ","refresher + ") : "";
  var o = null;
  try { o = gwOnderwerp(id); } catch(e){ o = null; }
  if(!o || !o.stappen || !o.stappen.length) return voor + "1 " + ct("onderwerp","topic");
  var stappen = o.stappen.length;
  if(stappen <= 1) return voor + gwTitel(o);
  var v = gwVoortgangLees(id);
  var s = Math.min((v.stap || 0) + 1, stappen);
  return voor + gwTitel(o) + " \\u00b7 " +
    ct("stap " + s + " van " + stappen, "step " + s + " of " + stappen);
}
function dagGramVragen(id){""",
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
