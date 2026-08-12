#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.66: vier woorden die niemand kan raden, krijgen hun uitleg erbij.

Stefan, 12 aug, over de kaart met de balk: "leuk statistieken maar hoe moet ik die lezen wat zeggen
die?"

In v23.64 is die kaart van het dagscherm gehaald. Maar hij is niet weg: hij staat op Voortgang, en
daar hoort hij ook. Alleen stond zijn legenda daar nog steeds zonder één woord uitleg:

    ● 1 bewezen vast   ● 7 onderweg   ● 266 geschat al gekend   ● 136 nog niet gezien

Dat zijn geen willekeurige woorden, het zijn namen van SRS-doosjes, en de definities zijn scherp:

    bewezen vast        doos 5, en die kost vijf goede beurten over minstens 25 dagen
                        (INTERVALS = [0,1,3,7,14,30]), plus een check die jij niet zelf beoordeelde
    onderweg            doos 3 of hoger: het woord staat op een herhaalinterval van een week of meer
    geschat al gekend   uit je peiling, dus niet gezien maar afgeleid
    nog niet gezien     wat het Cervantes op dit niveau telt en jij hier nog niet tegenkwam

Wie dat weet, leest de balk. Wie het niet weet, ziet vier getallen. Het stond nergens in de app,
alleen in de commentaren van de broncode en in het hoofd van degene die het bedacht.

## Waarom een uitklapper en geen alinea

Vier zinnen onder de balk maken van een blok waar je even naar kijkt een blok dat je moet lezen. De
vraag "wat betekent dit" stel je één keer, niet elke week. Dus staat het antwoord er wel, en staat
het dicht.

En er staat één regel bij die niet over definities gaat maar over rekenen: de vier tellen samen op
tot de noemer. Dat is te controleren met je ogen, en het is precies waarom de balk drie tinten heeft.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.66"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function vgLegendaUitlegHtml" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_NOEMER = '''    "<p class='muted' style='margin:5px 0 0; font-size:.8rem'>"+
      (sm.nivs.length > 1
        ? ct("van de "+n+" woorden op "+nivTxt, "of the "+n+" words in "+nivTxt)
        : ct("van de "+n+" "+niv+"-woorden", "of the "+n+" "+niv+" words"))+"</p>"+
    stap+'''

A_VOOR = '''function dagBasisStand(pct){'''

if DOE_APP:
    ontbreekt = [a for a in [A_NOEMER, A_VOOR] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.64. Eerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_VOOR, '''/* ================= WAT DIE VIER WOORDEN BETEKENEN (v23.66) =================
   Stefan over de balk: "leuk statistieken maar hoe moet ik die lezen wat zeggen die?" De legenda
   gebruikt vier namen van SRS-doosjes, en die zijn scherp gedefinieerd maar nergens uitgelegd.

   Dicht, want je stelt deze vraag één keer en niet elke week. En de laatste regel gaat niet over
   definities maar over rekenen: de vier tellen op tot de noemer, en dat kun je met je ogen
   controleren. Dat is de reden dat de balk drie tinten heeft in plaats van één. */
function vgLegendaRij(kop, uitleg){
  return "<p style='margin:8px 0 0; font-size:.84rem'><b>"+kop+"</b><br>"+
    "<span class='muted'>"+uitleg+"</span></p>";
}
function vgLegendaUitlegHtml(n){
  var top = INTERVALS.length - 1;
  var dagen = 0, i;
  for(i = 0; i < top; i++){ dagen += INTERVALS[i]; }
  var r = "";
  r += vgLegendaRij(ct("bewezen vast","proven solid"),
    ct("Je had dit woord "+top+" keer goed, verspreid over minstens "+dagen+" dagen, en de laatste "+
       "keer was een check die je niet zelf beoordeelde. Dat duurt dus lang: dit getal zegt net zo "+
       "goed hoe lang je bezig bent als hoeveel je kent.",
       "You got this word right "+top+" times, spread over at least "+dagen+" days, and the last "+
       "time was a check you did not grade yourself. That takes a while: this number says as much "+
       "about how long you have been at it as about how much you know."));
  r += vgLegendaRij(ct("onderweg","on the way"),
    ct("Het woord staat op een herhaalinterval van een week of langer. Het komt nog terug, en het "+
       "kan nog wegzakken.",
       "The word is on a review interval of a week or more. It still comes back, and it can still "+
       "slip away."));
  r += vgLegendaRij(ct("geschat al gekend","estimated already known"),
    ct("Afgeleid uit je peiling, niet uit wat je hier gedaan hebt. Waarschijnlijk waar, niet bewezen.",
       "Derived from your level check, not from what you did here. Probably true, not proven."));
  r += vgLegendaRij(ct("nog niet gezien","not seen yet"),
    ct("Woorden die het Cervantes op dit niveau meetelt en die jij hier nog niet bent tegengekomen.",
       "Words the Cervantes list counts at this level that you have not run into here yet."));
  r += "<p class='muted' style='margin:10px 0 0; font-size:.82rem'>"+
    ct("De vier tellen samen op tot "+n+". Daarom heeft de balk drie tinten: je kunt de som narekenen.",
       "The four add up to "+n+". That is why the bar has three shades: you can check the sum yourself.")+"</p>";
  return "<details style='margin-top:10px'><summary class='muted' style='cursor:pointer; font-size:.85rem'>"+
    ct("Wat betekenen deze woorden?","What do these words mean?")+"</summary>"+r+"</details>";
}
function dagBasisStand(pct){''')

    rep(A_NOEMER, '''    "<p class='muted' style='margin:5px 0 0; font-size:.8rem'>"+
      (sm.nivs.length > 1
        ? ct("van de "+n+" woorden op "+nivTxt, "of the "+n+" words in "+nivTxt)
        : ct("van de "+n+" "+niv+"-woorden", "of the "+n+" "+niv+" words"))+"</p>"+
    /* v23.66: staat de legenda er, dan staat de uitleg erbij. Op je profiel staat de legenda niet
       (daar staat de lange uitsplitsing eronder), dus daar ook geen uitklapper. */
    ((opt && opt.legenda === false) ? "" : vgLegendaUitlegHtml(n))+
    stap+''')

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
