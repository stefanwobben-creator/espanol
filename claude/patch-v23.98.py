#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.98: Woordenzoeker en Memory tellen mee, en de Speeltuin zegt wat een spel oplevert
(punt 25 en 24).

## Punt 25: twee spellen die niets deden met wat je deed

Stefan, 14 augustus: "woordenzoeker klopt niet, helemaal, want het herkennen van het woord versterkt
de opname in je geheugen." Dat klopt, en ik had het te absoluut afgeschreven.

Wat er speelde: `wsWoordPool()` en `memPool()` zetten allebei netjes `id: w.id` in hun pool, en
`wsStart()` en `memStart()` gooiden dat id daarna weg bij het bouwen van het speelveld. De app wist
dus precies welk woord je had gevonden en deed er niets mee. Je speelde, en je voortgang bewoog niet.

Nu gaat het id mee en gaat een gevonden woord door `spelSrsBij()`. Dat is met opzet de lichte weg:

  - `SPEL_PLAFOND` is 3, dus een spel kan een woord nooit verder dan doos 3 brengen. De laatste twee
    dozen zijn voor typen, en de allerlaatste voor de check die je zelf moet schrijven.
  - de dagrem van v23.92 geldt: hoogstens één doos per dag per woord, hoe je ook oefent.
  - `st.sp` wordt gezet, zodat "werkt de app" en "werkt spelen" apart te lezen blijven.

Herkennen is echte winst en het is een andere winst dan produceren. Nu telt het als het eerste en
niet als het tweede.

## Punt 24: de Speeltuin beloofde niets

Bij Oefenen staat wél wat een oefening oplevert, in de Speeltuin niet: daar stond alleen "Leren,
vermomd als spelen. Kies je vermaak." Je kon dus niet weten welk spel je verder helpt en welk puur
vermaak is, terwijl dat verschil er wel degelijk is en nu ook klopt.

Er staat nu één regel onder de kop die zegt wat er meetelt en tot hoever.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.98"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.98" not in src
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


# ---------------------------------------------------------------- punt 25: Woordenzoeker
A_WS_PUSH = '''      geplaatst.push({woord:g.woord, nl:g.nl, es:g.es, found:false, hint:false});'''
N_WS_PUSH = '''      // v23.98: het id gaat mee. wsWoordPool() zette het er netjes in en hier werd het weggegooid,
      // dus de app wist welk woord je vond en deed er niets mee.
      geplaatst.push({woord:g.woord, nl:g.nl, es:g.es, id:g.id, found:false, hint:false});'''

A_WS_HIT = '''  if(hit){
    hit.found = true;
    cells.forEach(function(k){ ws.foundCells[k] = true; });
    addXP(2);'''
N_WS_HIT = '''  if(hit){
    hit.found = true;
    cells.forEach(function(k){ ws.foundCells[k] = true; });
    /* v23.98: herkennen versterkt wel degelijk, alleen anders dan produceren. spelSrsBij() is met
       opzet de lichte weg: SPEL_PLAFOND is 3, dus hier kom je nooit verder dan doos 3, de dagrem van
       v23.92 geldt, en st.sp blijft aan zodat "werkt de app" en "werkt spelen" apart leesbaar zijn. */
    if(hit.id){ try{ spelSrsBij(hit.id); }catch(e){} }
    addXP(2);'''

# ---------------------------------------------------------------- punt 25: Memory
A_MEM_START = '''  mem = {cards:cards, open:[], matched:{}, beurten:0, lock:false, klaar:false};'''
N_MEM_START = '''  // v23.98: de paren blijven bewaard, want de kaartjes dragen alleen nog een pid en de tekst.
  // Zonder deze regel weet memClick() niet welk wóórd er zojuist gematcht is.
  mem = {cards:cards, paren:paren, open:[], matched:{}, beurten:0, lock:false, klaar:false};'''

A_MEM_HIT = '''      mem.matched[mem.open[0]] = true; mem.matched[mem.open[1]] = true;
      mem.open = [];
      addXP(2);'''
N_MEM_HIT = '''      mem.matched[mem.open[0]] = true; mem.matched[mem.open[1]] = true;
      mem.open = [];
      // v23.98: zelfde als bij de Woordenzoeker, en om dezelfde reden. Zie spelSrsBij().
      var mp = (mem.paren || [])[a.pid];
      if(mp && mp.id){ try{ spelSrsBij(mp.id); }catch(e){} }
      addXP(2);'''

# ---------------------------------------------------------------- punt 24
A_SPEEL_NL = '''     wsT:"Woordenzoeker", wsS:"puzzel met jouw geleerde woorden",'''
A_SPEEL_INTRO_NL = '''intro:"Leren, vermomd als spelen. Kies je vermaak:",'''
N_SPEEL_INTRO_NL = '''intro:"Leren, vermomd als spelen. Kies je vermaak:", meetelt:"Alles hier telt mee voor je woorden, maar niet even zwaar: spellen waarin je het Spaans zelf intikt brengen een woord het verst, herkennen brengt het tot halverwege.",'''

A_SPEEL_INTRO_EN = '''intro:"Learning, disguised as play. Pick your fun:",'''
N_SPEEL_INTRO_EN = '''intro:"Learning, disguised as play. Pick your fun:", meetelt:"Everything here counts towards your words, but not equally: games where you type the Spanish yourself take a word furthest, recognising takes it halfway.",'''

A_SPEEL_TOON = '''  el.innerHTML = "<h2>" + fx("kop") + "</h2><p class='muted'>" + fx("intro") + "</p>"+'''
N_SPEEL_TOON = '''  /* v23.98: er stond niet wat een spel oplevert, terwijl Oefenen dat wel zegt. Je kon dus niet
     weten welk spel je verder helpt en welk puur vermaak is, en dat verschil is er wel degelijk:
     zie spelSrsBij() en SPEL_PLAFOND. */
  el.innerHTML = "<h2>" + fx("kop") + "</h2><p class='muted'>" + fx("intro") + "</p>"+
    "<p class='muted' style='margin:-4px 0 10px; font-size:.86rem'>" + fx("meetelt") + "</p>"+'''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("de woordenzoeker-lijst", A_WS_PUSH), ("het gevonden woord", A_WS_HIT),
        ("memStart", A_MEM_START), ("het gematchte paar", A_MEM_HIT),
        ("de Nederlandse speeltuintekst", A_SPEEL_INTRO_NL),
        ("de Engelse speeltuintekst", A_SPEEL_INTRO_EN),
        ("de speeltuinkop", A_SPEEL_TOON)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.97. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_WS_PUSH, N_WS_PUSH)
    rep(A_WS_HIT, N_WS_HIT)
    rep(A_MEM_START, N_MEM_START)
    rep(A_MEM_HIT, N_MEM_HIT)
    rep(A_SPEEL_INTRO_NL, N_SPEEL_INTRO_NL)
    rep(A_SPEEL_INTRO_EN, N_SPEEL_INTRO_EN)
    rep(A_SPEEL_TOON, N_SPEEL_TOON)

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
