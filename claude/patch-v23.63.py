#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.63: twee dingen kunnen kiezen is kiezen, vier dingen is zoeken.

Stefan, 12 aug, kijkend naar het scherm na een grammaticastap: "wat me hier echt opvalt zou de vele
call to actions, dat is verwarrend ook al is de primaire rood."

Geteld op zijn schermafdruk, stap 1 van 3 binnen de dagles:

    [ ON WITH YOUR SESSION → ]   rood
    [ Next step → ]
    [ Redo this step ]
    [ Skip → ]

Vier knoppen. In v23.60 hebben we vastgelegd dat er per moment één rode knop is, en dat klopt hier
ook. Maar Stefans punt gaat verder en hij heeft gelijk: het aantal keuzes is het probleem, niet
alleen hun kleur. Vier knoppen zijn geen keuze meer maar een zoekplaatje.

## En de rode knop wees de verkeerde kant op

Erger nog dan het aantal: je staat op stap 1 van 3, en de opvallendste knop zegt "verder met je
les". Dat is weggaan bij iets wat je net begonnen bent. "Next step" en "Skip" stonden er als gewone
knoppen naast, dus de app bood drie manieren om deze les te verlaten en één om hem af te maken, en
die laatste was de minst opvallende.

Dat is dezelfde fout als op het eindscherm in v23.58, waar "Klaar voor vandaag" de primaire knop was
en het antwoord op "en nu?" eronder stond.

## Wat het nu is

    binnen de dagles, nog stappen te gaan     [ Volgende stap → ]  [Verder met je les →]
                                              Deze stap opnieuw
    binnen de dagles, laatste stap            [ Verder met je les → ]
                                              Deze stap opnieuw
    los aan het oefenen                       [ Volgende stap → ]  [← Terug]
                                              Deze stap opnieuw

Twee knoppen en één tekstlink. De primaire knop is altijd het voortzetten van waar je mee bezig
bent; weggaan kan, maar het is de tweede knop. "Deze stap opnieuw" is een tekstlink geworden, want
het is geen stap vooruit maar een correctie op wat je net deed — dezelfde reden als bij de
moduskeuze in v23.60.

"Skip" is weg. Die deed hetzelfde als "verder met je les" en stond er twee keer met een ander woord.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.63"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.63" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_STAPKLAAR = '''      "<div class='row' style='margin-top:10px'>"+
        gwFlowKnopHtml()+
        "<button class='"+(inFlow ? "ghost" : "primary")+"' id='gwVolgendeStap'>"+(laatste ? ct("Afronden \\u2192","Wrap up \\u2192") : ct("Volgende stap \\u2192","Next step \\u2192"))+"</button>"+
        "<button class='ghost' id='gwHerhaal'>"+ct("Deze stap opnieuw","Redo this step")+"</button>"+
        "<button class='ghost' id='gwSluit'>"+gwTerugLabel()+"</button>"+
      "</div>" + voet;'''

if DOE_APP:
    if A_STAPKLAAR not in src:
        print("Deze index.html ziet er niet uit zoals verwacht; het knoppenblok van fase 'stapklaar'\n"
              "staat er niet zoals verwacht. Eerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_STAPKLAAR, '''      /* v23.63. Stefan: "wat me hier echt opvalt zou de vele call to actions, dat is verwarrend ook
         al is de primaire rood." Hier stonden er vier: "Verder met je les" (rood), "Volgende stap",
         "Deze stap opnieuw" en "Terug". Op stap 1 van 3 bood de app dus drie manieren om weg te gaan
         en één om door te gaan, en die laatste was de minst opvallende. Dezelfde fout als op het
         eindscherm vóór v23.58.

         Nu: de primaire knop is altijd doorgaan met waar je mee bezig bent, weggaan is de tweede
         knop, en "opnieuw" is een tekstlink — het is geen stap vooruit maar een correctie op wat je
         net deed. "Skip" is weg: die deed hetzelfde als "verder met je les". */
      "<div class='row' style='margin-top:10px'>"+
        (inFlow && laatste
          ? gwFlowKnopHtml()
          : "<button class='primary' id='gwVolgendeStap'>"+(laatste ? ct("Afronden \\u2192","Wrap up \\u2192") : ct("Volgende stap \\u2192","Next step \\u2192"))+"</button>"+
            (inFlow ? "<button class='ghost' id='gwFlowVerder'>"+ct("Verder met je les \\u2192","On with your session \\u2192")+"</button>"
                    : "<button class='ghost' id='gwSluit'>"+gwTerugLabel()+"</button>"))+
      "</div>"+
      "<button class='mini' id='gwHerhaal'>"+ct("Deze stap opnieuw","Redo this step")+"</button>" + voet;''')

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
