#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.146: Chispa zwijgt tijdens je les, en het foutenlogboek vergeet zijn fossielen.

Stefan, 20 aug: "Ja zodat we alleen het beste behouden." En eerder: "chispa die altijd iets leuks
zegt kan weg. nou heel veel dingen kunnen weg."

## 1. De banner wordt een strook

Dit draait iets terug dat er op zijn eigen verzoek in kwam, en dat hoort er expliciet bij te staan.

v19.49, Stefan: *"zou chispa ook in de interface terug komen bijv na de onboarding bij je eerste
les?"* Wat er toen bij kwam: een hele kaart boven élk scherm van de dagles, met haar kop, een
Spaanse regel per stap, de Nederlandse vertaling eronder, en een tik erop voor een toast met
dezelfde zin. Twaalf views, elke stap opnieuw, elke dag hetzelfde rijtje van vier zinnen.

Vier zinnen, twaalf plekken, zesentwintig dagen. Dat is de kern: een aanmoediging die altijd komt is
geen aanmoediging meer maar meubilair. En het duurste stuk schermruimte van de app, boven elke
oefening, ging eraan op.

Ze verdwijnt niet. Ze staat nog steeds op het dagscherm vóórdat je begint (één keer per dag; dat is
Fogg's prompt en die werkt juist door zijn plek), ze krijgt haar tapa als je klaar bent, en sinds
v23.144 kun je met haar praten. Alleen tíjdens je les zwijgt ze, en dan is het ook weer iets waard.

Wat ervoor terugkomt is precies wat de banner nooit gaf: waar je bent. De strook is de balk van
v23.142 plus één regel: "stap 3/5 · Toetsje".

Weg: `LESFLOW_CHISPA`, `LESFLOW_CHISPA_EERSTE`, `lesFlowChispaFrase()`, `lesFlowChispaKlik()`,
`lesFlowWireBanner()` en de twaalf aanroepen daarvan.

## 2. Het foutenlogboek vergeet wat niet meer bestaat

Uit de meting van 20 aug: in Stefans logboek staan 66 fouten op `dictado`, 10 op `husselen`, 4 op
`klemtoon` en 1 op `jaartal`. Dictado is in v21.4 verwijderd; de andere drie bestaan al langer niet.
Ze hebben geen datum (dat veld kwam in v22.0), dus ze zijn niet eens te dateren.

Ze doen geen schade aan je leren, maar wel aan het kijken: het foutenlogboek is de enige plek waar de
app registreert wat je deed, en een kwart van Stefans regels gaat over onderdelen die niet meer
bestaan. Wie ernaar kijkt om te beslissen wat weg kan, kijkt naar spoken.

Eenmalig opgeruimd bij het laden, en de lijst van levende soorten staat naast de plek die ze
aanmaakt, zodat de volgende verwijdering hem meeneemt.

Bewaakt door test/suites/pw-stilte.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.146"

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


def repre(patroon, nieuw, n):
    """Zelfde afspraak als rep(), maar met een reguliere uitdrukking: twaalf aanroepen van dezelfde
    functie staan met verschillende inspringing, en die één voor één als los anker opschrijven is
    twaalf kansen op een typefout."""
    global src
    if not DOE_APP:
        return
    gevonden = len(re.findall(patroon, src, flags=re.M))
    assert gevonden == n, "regexanker komt %d keer voor in plaats van %d: %s" % (gevonden, n, patroon)
    src = re.sub(patroon, nieuw, src, flags=re.M)


# ================= 1. de strook =================

rep(
    """  .ritme{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}""",
    """  .ritme{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}
  /* v23.146: de strook boven je les. Geen kaart meer, geen kop, geen tekstballon: alleen de balk
     van v23.142 en één regel die zegt waar je bent. */
  .lesstrook{margin:0 0 10px;}
  .lesstap{font-size:.74rem; color:var(--muted); text-transform:uppercase; letter-spacing:.06em;
           font-weight:700;}""",
)

rep(
    '''function lesFlowBannerHtml(){
  if(!lesFlow) return "";
  var f = lesFlowChispaFrase();
  return "<div class='card' style='margin-bottom:10px'>"+
    "<div class='lfrow'>"+
      "<button class='lfchispa' id='btnLesFlowChispa' title='Chispa'>"+chispaMiniSvg()+"</button>"+
      "<div class='lfmid'>"+
        "<span class='kicker'>\U0001f6a6 "+ct("Start je les","Start your session")+" \u00b7 "+ct("stap","step")+" "+lesFlowStapNum()+"/"+lesFlowStapTotaal()+" \u00b7 "+lesFlowStapNaam()+"</span>"+
        chispaZegHtml(f.es, ct(f.nl, f.en || f.nl))+
      "</div>"+
    "</div>"+
    /* v23.142: dezelfde balk als op Vandaag, met het blok waar je nu in zit vol. De kicker hierboven
       zegt "stap 4 van 5" in woorden; dit zegt waar dat vierde blok zit en hoe groot het is. */
    dagBalkHtml(lesFlow.stap, lesFlow.stappen)+
  "</div>";
}
/* v19.49 (Stefan: "zou chispa ook in de interface terug komen komen bijv na de onboarding bij je
   eerste les?"). Chispa zat opgesloten in haar eigen tabje. Nu loopt ze mee door de hele dagles:
   \u00e9\u00e9n plek in de banner, die vanuit twaalf views gerenderd wordt. Bij de allereerste les stelt
   ze zich nog even voor. */
var LESFLOW_CHISPA = {
  woorden:    {es:"\u00a1Vamos! Primero las palabras.",    nl:"Kom op! Eerst de woordjes.",         en:"Let's go! Words first."},
  grammatica: {es:"Ahora la gram\u00e1tica. Yo te espero.", nl:"Nu de grammatica. Ik wacht op je.",  en:"Now the grammar. I'll wait for you."},
  toetsjes:   {es:"Un test peque\u00f1o, nada m\u00e1s.",      nl:"E\u00e9n klein toetsje, verder niets.", en:"One small quiz, nothing more."},
  produceren: {es:"\u00a1Ahora hablas t\u00fa!",               nl:"En nu praat jij!",                   en:"Now you talk!"}
};
var LESFLOW_CHISPA_EERSTE = {es:"\u00a1Hola! Soy Chispa. Vamos juntos.", nl:"Hoi! Ik ben Chispa. We doen dit samen.", en:"Hi! I'm Chispa. We'll do this together."};''',
    '''/* ================= DE STROOK IN PLAATS VAN DE BANNER (v23.146) =================

   Stefan, 20 aug: "chispa die altijd iets leuks zegt kan weg. nou heel veel dingen kunnen weg."

   Dit draait iets terug dat er op zijn eigen verzoek in kwam, en dat hoort er expliciet bij te staan.
   v19.49, Stefan: "zou chispa ook in de interface terug komen bijv na de onboarding bij je eerste
   les?" Wat er toen bij kwam was een hele kaart boven \u00e9lk scherm van de dagles: haar kop, een Spaanse
   regel per stap, de Nederlandse vertaling eronder, en een tik erop voor een toast met dezelfde zin.

   Vier zinnen, twaalf plekken, zesentwintig dagen. Dat is de reden dat het weggaat: een aanmoediging
   die altijd komt is geen aanmoediging meer maar meubilair. En het duurste stuk schermruimte van de
   app, boven elke oefening, ging eraan op.

   Ze verdwijnt niet. Ze staat op het dagscherm v\u00f3\u00f3rdat je begint (\u00e9\u00e9n keer per dag, en dat is Fogg's
   prompt: die werkt juist door zijn plek), ze krijgt haar tapa als je klaar bent, en sinds v23.144
   kun je met haar praten. Tijdens je les zwijgt ze, en dan is het ook weer iets waard.

   Wat ervoor terugkomt is wat de banner nooit gaf: waar je bent. */
function lesFlowBannerHtml(){
  if(!lesFlow) return "";
  return "<div class='lesstrook'>"+
    dagBalkHtml(lesFlow.stap, lesFlow.stappen)+
    "<div class='lesstap'>"+ct("stap","step")+" "+lesFlowStapNum()+"/"+lesFlowStapTotaal()+
      " \u00b7 "+lesFlowStapNaam()+"</div></div>";
}''',
)

rep(
    '''function lesFlowChispaFrase(){
  if(!lesFlow) return LESFLOW_CHISPA.woorden;
  if(lesFlow.stap === "woorden" && typeof doneLessonCount === "function" && doneLessonCount() === 0) return LESFLOW_CHISPA_EERSTE;
  return LESFLOW_CHISPA[lesFlow.stap] || LESFLOW_CHISPA.woorden;
}
function chispaMiniSvg(){''',
    '''function chispaMiniSvg(){''',
)

rep(
    '''function lesFlowChispaKlik(){
  var f = lesFlowChispaFrase();
  var b = document.getElementById("btnLesFlowChispa");
  if(b) chispaMiniSpin(b);
  toast("\U0001f4ac " + f.es + " \u00b7 " + ct(f.nl, f.en || f.nl));
}
/* Stefan, 30 juli: "Het is een speelse instructie, geen actie of keuzemoment." De banner van stap 1
   had een 'Later verder'-knop, en die maakte van een aanmoediging een beslissing die je elke stap
   opnieuw moest nemen. Weg dus, inclusief lesFlowStop(): weglopen doe je met de navigatie, niet met
   een knop in Chispa's tekstballon. Chispa zelf blijft aanklikbaar, dat is spel en geen keuze. */
function lesFlowWireBanner(){
  var bc = document.getElementById("btnLesFlowChispa");
  if(bc) bc.onclick = lesFlowChispaKlik;
}

''',
    '''''',
)

# de twaalf aanroepen. Er valt niets meer aan te koppelen: de strook heeft geen knop.
repre(r"^[ \t]*try \{ lesFlowWireBanner\(\); \} catch\(e\)\{\}\n", "", 1)
repre(r"^[ \t]*lesFlowWireBanner\(\);\n", "", 11)

# ================= 2. het foutenlogboek vergeet zijn fossielen =================

rep(
    """function logError(id, type, tag, extra){""",
    """/* v23.146: welke soorten fouten bestaan er nog?

   Deze lijst staat naast de functie die ze aanmaakt, en niet ergens anders, zodat de volgende keer
   dat er een oefening verdwijnt de opruiming vanzelf meekomt.

   Gemeten in Stefans logboek op 20 aug: 66 fouten op dictado (verwijderd in v21.4), 10 op husselen,
   4 op klemtoon, 1 op jaartal. Geen van vieren heeft een datum, want dat veld kwam pas in v22.0. Ze
   doen je leren geen kwaad, maar het foutenlogboek is de enige plek waar de app noteert wat je deed,
   en een kwart van de regels ging over onderdelen die niet meer bestaan. Wie daarnaar kijkt om te
   beslissen wat weg kan, kijkt naar spoken. */
var FOUT_SOORTEN = ["woord", "zin", "quiz", "gramwiz", "conj", "verbo", "concept", "corrector", "escucha"];
function foutenOpschonen(s){
  if(!s || !s.errors) return 0;
  var weg = 0, k;
  for(k in s.errors){
    var soort = String(k).split(":")[0];
    if(FOUT_SOORTEN.indexOf(soort) === -1){ delete s.errors[k]; weg++; }
  }
  return weg;
}
function logError(id, type, tag, extra){""",
)

rep(
    """  s.xp = s.xp || {};
  s.streak = s.streak || {count:0, last:""};""",
    """  s.xp = s.xp || {};
  s.errors = s.errors || {};
  try { foutenOpschonen(s); } catch(e){}   // v23.146: fouten op oefeningen die niet meer bestaan
  s.streak = s.streak || {count:0, last:""};""",
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
