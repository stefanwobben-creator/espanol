#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.49: de app biedt alleen de talen die hij echt spreekt.

Stefan testte v23.48 op zijn eigen telefoon, die op Duits staat, en kreeg dit:

    de balk            Heute · Wörter · Üben · Spielen · Mehr        Duits
    de schermtekst     How it works · 3 of 5 done · PLAY SOMETHING   Engels
    de woordbetekenis  de tuin · de badkamer · blauw                 Nederlands

Drie talen op één scherm. Stefan: "dit gaat denk ik naar het hart van de architectuur." Dat klopt.

## Wat er onder zit

Er zijn vier taalbronnen die niets van elkaar weten, met drie verschillende dekkingen:

    ct(nl, en)                927 aanroepen    2 talen
    tt(key) via TXT             9 aanroepen    4 talen
    TRANS (woordbetekenis)                     en 794 · fr 420 · de 420
    proefTaal() eigen tabel                    4 talen, los van de rest

Negenhonderdzevenentwintig tegen negen. De app is tweetalig en zijn keuzemenu belooft vier vlaggen.
Voor een Duitse bezoeker valt de balk terug op Duits (die zit in TXT), valt alle andere tekst terug
op Engels (want ct kent alleen nl en en), en valt de woordbetekenis terug op Nederlands (want
TRANS.de kende dat woord niet en wTrans eindigt op w.nl).

Geen van de drie is stuk. Ze zijn los van elkaar gegroeid, en `ct(nl, en)` maakt het goedkoop om
een Nederlandse en Engelse zin te schrijven en onmogelijk om een Duitse. De vorm van die functie
bepaalt hoeveel talen de app kan hebben, en dat is nooit bewust gekozen.

## Wat deze versie doet: snoeien tot wat waar is

Stefan, 11 aug: Nederlands en Engels, de rest weg.

1. **`UI_LANGS` houdt nl en en over.** De keuze toont twee vlaggen in plaats van vier, en `langRow`
   tekent zichzelf uit die lijst, dus dat volgt vanzelf.
2. **Beide plekken die de browsertaal lezen kiezen nu uit wat we hebben.** Een de-, fr-, es- of
   welke browser dan ook krijgt Engels: compleet, in plaats van een salade.
3. **`proefTaal()` doet hetzelfde.** PROEF_TXT houdt zijn vier talen (dat kost niets en de drie
   vaste woordjes zijn wél viertalig), maar hij kiest alleen nog nl of en, zodat het eerste scherm
   niet in een taal staat die het tweede scherm niet kan volgen.
4. **Bestaande profielen met de of fr worden omgezet naar en.** Anders houdt precies de groep die
   het probleem had het probleem: hun `S.lang` staat al op "de" en dat verandert niet vanzelf.
5. **De helling vraagt alleen woorden waarvan de betekenis in jouw taal bestaat.** Dat is de regel
   die de Nederlandse woorden uit een Engels scherm haalt.

## Waarom 5 bijna niets kost, en wat het niet oplost

Gemeten op de volle bak van 2184 woorden:

    en   794 vertalingen   36% van de bak
    de   420                19%
    fr   420                19%

Maar op de vijver waar de helling uit trekt (de 427 A1-sleutels):

    en   416 van 427   97%
    de   152 van 427   36%

De Engelse vertalingen zijn precies daar geschreven waar een beginner komt. De filter kost een
Engelse bezoeker dus elf van de 427 woorden in zijn eerste ronde, en dat is een prijs die niemand
merkt.

Wat het níét oplost: buiten de A1-kern ziet een Engelse gebruiker nog steeds Nederlandse
betekenissen, want `wTrans()` eindigt daar nog altijd op `w.nl`. Dat raakt het woordenboek en de
hogere niveaus. Dat is een eigen verhaal en het is groter dan deze: het vraagt ofwel 1390
vertalingen erbij, ofwel dezelfde filter op de hele leerlijn (en dan krimpt de app voor een Engelse
gebruiker van 2184 naar 794 woorden). Die keuze hoort niet op de avond voor een lancering.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.49"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function taalWeHebben" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = [
        'var APP_VERSIE = "v23.48";',
        'var UI_LANGS = {nl:{naam:"Nederlands", vlag:"🇳🇱", kort:"NL"}, en:{naam:"English", vlag:"🇬🇧", kort:"EN"}, fr:{naam:"Français", vlag:"🇫🇷", kort:"FR"}, de:{naam:"Deutsch", vlag:"🇩🇪", kort:"DE"}};',
        'function helVragen(n, weg){',
        '  if(!S.lang) S.lang = p.lang || "nl"; // moedertaal per profiel, synct mee via S',
    ]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:80] for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.48. Eerst die draaien, of eerst bijtrekken:\n"
              "\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.48";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. de lijst met talen, en één plek die de browsertaal vertaalt ----------
    rep('var UI_LANGS = {nl:{naam:"Nederlands", vlag:"🇳🇱", kort:"NL"}, en:{naam:"English", vlag:"🇬🇧", kort:"EN"}, fr:{naam:"Français", vlag:"🇫🇷", kort:"FR"}, de:{naam:"Deutsch", vlag:"🇩🇪", kort:"DE"}};',
        '''/* v23.49: hier stonden vier vlaggen. De app heeft er twee. Van de 936 schermteksten hangen er
   927 aan ct(nl, en), dus alles buiten die twee valt terug op Engels, terwijl de balk (die aan de
   viertalige TXT hangt) wél Duits of Frans wordt en de woordbetekenis terugvalt op Nederlands.
   Stefan kreeg op zijn Duitse telefoon alle drie tegelijk op één scherm. Twee vlaggen die kloppen
   zijn beter dan vier waarvan er twee half zijn. */
var UI_LANGS = {nl:{naam:"Nederlands", vlag:"🇳🇱", kort:"NL"}, en:{naam:"English", vlag:"🇬🇧", kort:"EN"}};
/* Eén plek die een browsertaal omzet naar een taal die we echt spreken. Er waren er drie, met elk
   hun eigen tabel, en dat is precies hoe ze uit elkaar konden lopen. */
function taalWeHebben(bl){
  try {
    var k = String(bl || "").slice(0, 2).toLowerCase();
    return UI_LANGS[k] ? k : "en";
  } catch(e){ return "en"; }
}
function browserTaal(){
  try { return taalWeHebben((typeof navigator !== "undefined" && navigator.language) || "nl"); }
  catch(e){ return "en"; }
}''')

    # ---------- 2. de twee autodetect-plekken ----------
    rep('''function proefTaal(){
  try{
    var bl = ((typeof navigator !== "undefined" && navigator.language) || "nl").slice(0, 2).toLowerCase();
    return PROEF_TXT[bl] ? bl : "en";
  }catch(e){ return "en"; }
}''',
        '''function proefTaal(){
  /* v23.49: hier stond PROEF_TXT[bl] ? bl : "en", en PROEF_TXT kent vier talen. Het eerste scherm
     kwam dus in het Duits terwijl het tweede dat niet kon volgen. De drie vaste proefwoorden
     blijven viertalig in de tabel staan (dat kost niets), maar we kiezen alleen wat de hele app
     aankan. */
  return browserTaal();
}''')

    rep('''    var bl = ((typeof navigator !== "undefined" && navigator.language) || "nl").slice(0, 2).toLowerCase();
    if(UI_LANGS[bl] && newLang === "nl") newLang = bl;''',
        '''    var bl = browserTaal();
    if(newLang === "nl") newLang = bl;''')

    # ---------- 3. bestaande profielen met de of fr ----------
    rep('  if(!S.lang) S.lang = p.lang || "nl"; // moedertaal per profiel, synct mee via S',
        '  if(!S.lang) S.lang = p.lang || "nl"; // moedertaal per profiel, synct mee via S\n'
        '  /* v23.49: wie eerder Duits of Frans koos (of kreeg, want de detectie deed dat vanzelf) zit\n'
        '     nog op een taal die de app maar voor negen van de 936 teksten kan waarmaken. Zonder deze\n'
        '     regel houdt precies de groep die het probleem had het probleem. Engels is voor hen de\n'
        '     complete versie. */\n'
        '  if(S.lang !== "nl" && S.lang !== "en"){ S.lang = "en"; if(p) p.lang = "en"; try{ saveProfiles(); }catch(e){} }')

    # ---------- 3b. vóór het aanmelden wist profLang() van niets ----------
    # Dit was de vierde taalbron, en de gemeenste: proefTaal() zette het scherm op Engels, maar
    # wTrans() vraagt profLang(), en die geeft zonder profiel altijd "nl". Dus stond de vraag in het
    # Engels en de antwoorden in het Nederlands. Zonder deze regel doet de filter hieronder niets.
    rep('''function profLang(){
  if(S && S.lang) return S.lang;
  var p = activeProfile();
  return (p && p.lang) || "nl";
}''',
        '''function profLang(){
  if(S && S.lang) return S.lang;
  var p = activeProfile();
  if(p && p.lang) return p.lang;
  /* v23.49: hier stond "nl", en dat is de vierde taalbron waar de drie andere niets van wisten.
     Vóór het eerste profiel zette proefTaal() het scherm op Engels terwijl wTrans() via deze regel
     Nederlandse betekenissen ophaalde: "el jardín" met "de tuin · de badkamer · blauw". newLang is
     wat het aanmeldscherm gebruikt en volgt de browsertaal, dus dat is het juiste antwoord zolang
     er nog geen profiel is. */
  return (typeof newLang !== "undefined" && newLang) ? newLang : "nl";
}''')

    # ---------- 4. de helling vraagt alleen wat hij kan vertalen ----------
    rep('''function helVragen(n, weg){
  var kand = geschud(peilKandidaten("A1")), uit = [], gehad = {}, i, w;
  (weg || []).forEach(function(id){ gehad[id] = 1; });
  for(i = 0; i < kand.length && uit.length < n; i++){
    w = peilWoordVoor(pcicKeysApp()["A1"][kand[i]]);
    if(!w || gehad[w.id]) continue;
    gehad[w.id] = 1;
    uit.push({key:kand[i], id:w.id, es:w.es, goed:wTrans(w), opties:peilOpties(w)});
  }
  return uit;
}''',
        '''function helVragen(n, weg){
  var kand = geschud(peilKandidaten("A1")), uit = [], gehad = {}, i, w;
  (weg || []).forEach(function(id){ gehad[id] = 1; });
  for(i = 0; i < kand.length && uit.length < n; i++){
    w = peilWoordVoor(pcicKeysApp()["A1"][kand[i]]);
    if(!w || gehad[w.id]) continue;
    /* v23.49: wTrans() eindigt op w.nl als er geen vertaling is, dus in een Engels scherm stonden
       Nederlandse betekenissen. Stefan zag "el jardín" met "de tuin · de badkamer · blauw". Een
       woord zonder vertaling in jouw taal hoort hier niet gevraagd te worden. Kost een Engelse
       bezoeker elf van de 427 A1-woorden; de Engelse vertalingen zijn juist voor deze kern
       geschreven (416 van 427). */
    if(!woordVertaald(w)) continue;
    gehad[w.id] = 1;
    uit.push({key:kand[i], id:w.id, es:w.es, goed:wTrans(w), opties:peilOpties(w)});
  }
  return uit;
}
// Heeft dit woord een betekenis in de taal die op het scherm staat? In het Nederlands altijd.
function woordVertaald(w){
  try {
    var l = profLang();
    if(l === "nl") return true;
    return !!(TRANS[l] && TRANS[l][w.id]) || !!w[l];
  } catch(e){ return true; }
}''')

    # en de afleiders komen uit dezelfde vijver, anders staan daar alsnog Nederlandse woorden
    rep('''function peilOpties(w){
  var goed = wTrans(w);
  var pool = WORDS.filter(function(x){ return x.id !== w.id && wTrans(x) !== goed; });''',
        '''function peilOpties(w){
  var goed = wTrans(w);
  /* v23.49: de afleiders moeten in dezelfde taal staan als het goede antwoord. Zonder deze filter
     kreeg een Engelse bezoeker "the garden" naast "de badkamer" en "blauw", en dan raad je niet op
     betekenis maar op taal. */
  var pool = WORDS.filter(function(x){ return x.id !== w.id && wTrans(x) !== goed && woordVertaald(x); });''')

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
