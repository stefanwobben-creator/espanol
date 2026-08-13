#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.80: wat het eerst opengaat, staat bovenaan.

Met zes scenes viel het niet op. Met vijftien wel. De plank sorteert op open, klaar, dicht, en
binnen "dicht" op de volgorde waarin de scenes toevallig in de lijst staan. Op een vers profiel
leest dat zo:

    Bij de dokter      Gaat open als je nog 3 scenes afmaakt
    Een ontmoeting     Gaat open als je nog 2 scenes afmaakt
    Las Fallas         Gaat open als je nog 3 scenes afmaakt

Een lijst van twaalf sloten waarin de dichtstbijzijnde niet vooraan staat, is een lijst waarin je
moet zoeken naar het antwoord op de enige vraag die je stelt: wat komt er hierna? Dat is precies de
vraag die de plank hoort te beantwoorden.

plankHtml() krijgt daarom een optioneel veld `wacht`: een getal dat zegt hoe ver weg iets is.
Binnen de dichte groep wordt daarop gesorteerd, laag eerst. Wie het niet meegeeft, houdt de oude
volgorde; de sortering is stabiel, dus dat verandert niets voor de planken die dit niet gebruiken.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.80"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.80" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_SORT = '''    var orde = {open:0, klaar:1, dicht:2};
    lijst = lijst.map(function(it, i){ return {it:it, i:i}; }).sort(function(a, b){
      var d = (orde[a.it.staat] || 0) - (orde[b.it.staat] || 0);
      return d || (a.i - b.i);
    }).map(function(x){ return x.it; });'''

A_ITEM = '''      knop: gehad ? ct("Nog eens","Again") : ct("Luisteren","Listen")
    };'''

if DOE_APP:
    ontbreekt = [n for n, a in (("de sortering van plankHtml", A_SORT), ("audPlankItems", A_ITEM)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.79. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_SORT, '''    var orde = {open:0, klaar:1, dicht:2};
    /* v23.80: binnen "dicht" op afstand, dichtstbijzijnde eerst. Met zes scenes viel dat niet op,
       met vijftien wel: dan lees je een lijst van twaalf sloten waarin de scene die je morgen kunt
       doen ergens in het midden staat. `wacht` is optioneel; wie het niet meegeeft houdt de oude
       volgorde, want de sortering is stabiel op de oorspronkelijke index. */
    lijst = lijst.map(function(it, i){ return {it:it, i:i}; }).sort(function(a, b){
      var d = (orde[a.it.staat] || 0) - (orde[b.it.staat] || 0);
      if(d) return d;
      if(a.it.staat === "dicht" && typeof a.it.wacht === "number" && typeof b.it.wacht === "number"
         && a.it.wacht !== b.it.wacht) return a.it.wacht - b.it.wacht;
      return a.i - b.i;
    }).map(function(x){ return x.it; });''')

    rep(A_ITEM, '''      wacht: nodig,
      knop: gehad ? ct("Nog eens","Again") : ct("Luisteren","Listen")
    };''')

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
