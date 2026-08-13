#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.74: de uitklapper in de les is een vooruitblik op je eigen les, en gaat weg.

Stefan, 13 aug: "de spiekbriefje is beetje veel tekst, dat kan korter of gedoseerder en dan kan de
les met klap spiekbrief in of uit ook weg."

Gemeten wat die uitklapper is:

    stappen met een uitklapper "De rest van de spiekbrief"   60 van 61
    gemiddelde lengte van de stap zelf                      135 tekens
    gemiddelde lengte van de uitklapper                     250 tekens
    verhouding                                              1,9 keer zo lang als de les

En belangrijker dan de lengte is wat erin zit. Sinds v23.61 bevat hij niet meer wat je al ziet, maar
precies de blokken die **niet** op deze stap staan. En die blokken staan op de andere stappen van
diezelfde microles. De uitklapper is dus geen verdieping maar een vooruitblik op je eigen les, twee
keer zo lang als de les.

Weg ermee kost geen informatie: alles wat erin stond krijg je in stap twee of drie, en de hele kaart
staat sowieso op het grammaticascherm.

## En de kaart zelf

Het grammaticascherm is op dag 1 **2010 pixels** hoog (2,4 schermen) terwijl er maar drie
onderwerpen open staan. De 23 kaarten zijn samen 1412 woorden; gemiddeld 61 per kaart, de langste 87,
en elf ervan hebben een tabel tot zeven rijen.

De maat die daar telt is niet hoeveel er staat maar hoeveel je in één keer krijgt. De microles knipt
een kaart al in stappen; wat overbleef was dat elke stap de rest er nog eens bij aanbood. Dat is nu
weg, en daarmee is de dosering van de microles ook echt de dosering.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.74"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.74" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_REST = '''    /* v23.61: diep was c.html, de héle kaart, op élke stap. Dus de stap die de tabel toont had
       diezelfde tabel er nog een keer onder staan in de uitklapper. Gemeten: 81 van 81 stappen.
       Een uitklapper die belooft dat er meer is en dan hetzelfde geeft, leert je hem nooit meer
       open te doen. Nu staat er alleen in wat niet al op deze stap staat, en is hij er niet als
       dat niets is. */
    var rest = [], restEn = [];
    for(var j = 0; j < blokken.length; j++){
      if(idx.indexOf(j) !== -1) continue;
      rest.push(blokken[j]);
      restEn.push(zelfdeVorm ? blokkenEn[j] : blokken[j]);
    }
    var s = {
      kop: gwKopUit(blokken[eerste], i, false),
      kopEn: gwKopUit((zelfdeVorm ? blokkenEn : blokken)[eerste], i, true),
      uitleg: eigen,
      uitlegEn: eigenEn,
      vragen: vragen.slice(vGroep[i][0], vGroep[i][1])
    };
    if(rest.length){
      s.diepKop = "De rest van de spiekbrief";
      s.diepKopEn = "The rest of the cheat sheet";
      s.diep = rest.join("");
      s.diepEn = restEn.join("");
    }
    return s;
  });'''

if DOE_APP:
    if A_REST not in src:
        print("Deze index.html ziet er niet uit zoals verwacht; het stappenblok van gwVanSpiek()\n"
              "staat er niet zoals verwacht. Deze patch bouwt op v23.61. Eerst bijtrekken:\n\n"
              "    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_REST, '''    /* v23.61 haalde de dubbeling uit deze uitklapper: hij bevatte daarna alleen nog de blokken die
       níét op deze stap staan.

       v23.74 haalt hem helemaal weg, en de reden is precies die inhoud. Wat er níét op deze stap
       staat, staat op de andere stappen van dezelfde microles. De uitklapper was dus een
       vooruitblik op je eigen les, en gemeten 1,9 keer zo lang als de stap zelf (250 tegen 135
       tekens, op 60 van de 61 stappen).

       Stefan, 13 aug: "de spiekbriefje is beetje veel tekst, dat kan korter of gedoseerder en dan
       kan de les met klap spiekbrief in of uit ook weg." Er gaat niets verloren: je krijgt het in
       stap twee of drie, en de hele kaart staat op het grammaticascherm. */
    var s = {
      kop: gwKopUit(blokken[eerste], i, false),
      kopEn: gwKopUit((zelfdeVorm ? blokkenEn : blokken)[eerste], i, true),
      uitleg: eigen,
      uitlegEn: eigenEn,
      vragen: vragen.slice(vGroep[i][0], vGroep[i][1])
    };
    return s;
  });''')

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
