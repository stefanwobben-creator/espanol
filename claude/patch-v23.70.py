#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.70: de app zegt waaróm de AI niet antwoordt, en dat is bijna nooit "onbereikbaar".

Van de lanceerlijst, punt 5: "Bij een geblokkeerde AI-aanroep zegt de app 'De AI is even niet
bereikbaar'. Sinds het slot op de server klopt dat niet meer: de echte reden staat in `res.fout` en
die is vriendelijker."

Twee dingen nagekeken, en allebei anders dan het briefje zei.

**Het veld heet niet `fout` maar `error`.** `server/index.js` regel 279:

    const bad = (res, code, msg) => res.status(code).json({ ok: false, error: msg });

Een patch die op `res.fout` had gemikt, had een leeg scherm opgeleverd. Dit is precies waarom er in
dit project gemeten wordt in plaats van onthouden.

**En de tekst is Nederlands, altijd.** De server heeft vier redenen om een AI-aanroep te weigeren
(`aiSlot()`), elk met een Nederlandse zin. De app spreekt sinds v23.49 twee talen. Een Engelse
bezoeker kreeg dus of een Nederlandse serverzin, of de onjuiste standaardzin.

## Wat er nu gebeurt

De server krijgt in `claude/patch-server-aireden.py` een `reden`-code mee in het antwoord
(`uit`, `herkomst`, `dagplafond`, `tempo`, `stuk`). De app vertaalt die code zelf:

    uit          De AI-hulp staat even uit. De rest van de app werkt gewoon.
    dagplafond   De AI-hulp is voor vandaag op. Morgen kan het weer.
    tempo        Even rustig aan met de AI-hulp. Over een uur kan het weer.
    herkomst     De AI-hulp doet het hier niet.
    stuk / rest  De AI kon dit even niet nakijken. Probeer het straks nog eens.

De volgorde van terugvallen is met opzet deze: eerst de code, dan `res.error` als de server iets
zinnigs stuurde, en pas dan de algemene zin. Daardoor kan deze versie van de app vóór de server live
en blijft hij daarna werken: een oude server stuurt geen `reden` en dan wordt `error` getoond, wat
nog altijd waarheidsgetrouwer is dan "onbereikbaar".

En de knop komt terug in plaats van te verdwijnen, behalve bij `uit` en `dagplafond`: dan is
opnieuw proberen zinloos, en een knop die je uitnodigt tot iets zinloos is een leugen met een rand
eromheen.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.70"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function aiFoutTekst" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_CHECK = u'''      if(!res || !res.ok){ af.innerHTML = "<div class='feedback bijna'>De AI is even niet bereikbaar, probeer het straks nog eens.</div>"; ba.disabled=false; ba.textContent="🤖 Is mijn variant ook goed?"; return; }'''

A_UITLEG = u'''      af.innerHTML = (res && res.ok) ? "<div class='uitleg'>🤖 "+res.uitleg+"</div>" :
        "<div class='feedback bijna'>De AI is even niet bereikbaar.</div>";'''

A_POPUP = u'''      b2.textContent = "AI even niet bereikbaar. Probeer het straks nog eens.";'''

A_PLEK = '''function verbPopup(term){'''

if DOE_APP:
    ontbreekt = [a for a in [A_CHECK, A_UITLEG, A_POPUP, A_PLEK] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_PLEK, '''/* ================= WAAROM DE AI NIET ANTWOORDT (v23.70) =================
   Er stond overal "De AI is even niet bereikbaar", en sinds het slot op de server (11 aug) is dat
   bijna nooit de reden. De server weigert om vier redenen, en drie daarvan kun je zelf oplossen of
   ze zijn tijdelijk op een manier die je wilt weten.

   Het veld heet `error` en niet `fout`; dat laatste stond in de werklijst en klopte niet. Zie
   server/index.js: `const bad = (res, code, msg) => res.status(code).json({ok:false, error:msg})`.

   De volgorde van terugvallen is met opzet: eerst de code die de server meestuurt, dan zijn eigen
   zin, en pas dan de algemene. Zo kan deze app vóór de server live: een oude server stuurt geen
   reden mee, en dan staat er nog altijd iets waars. */
var AI_REDEN_NL = {
  uit:        "De AI-hulp staat even uit. De rest van de app werkt gewoon.",
  dagplafond: "De AI-hulp is voor vandaag op. Morgen kan het weer.",
  tempo:      "Even rustig aan met de AI-hulp. Over een uur kan het weer.",
  herkomst:   "De AI-hulp doet het hier niet.",
  stuk:       "De AI kon dit even niet nakijken. Probeer het straks nog eens."
};
var AI_REDEN_EN = {
  uit:        "The AI help is switched off for now. The rest of the app works as usual.",
  dagplafond: "The AI help is used up for today. Tomorrow it works again.",
  tempo:      "Easy does it with the AI help. In an hour it works again.",
  herkomst:   "The AI help does not work here.",
  stuk:       "The AI could not check this just now. Try again later."
};
function aiFoutTekst(res){
  var r = res && res.reden;
  if(r && AI_REDEN_NL[r]) return ct(AI_REDEN_NL[r], AI_REDEN_EN[r]);
  if(res && res.error) return String(res.error);
  return ct(AI_REDEN_NL.stuk, AI_REDEN_EN.stuk);
}
/* Bij "uit" en "dagplafond" heeft opnieuw proberen geen zin tot morgen. Een knop die terugkomt
   nodigt uit tot iets wat gegarandeerd niet werkt, en dat is precies hoe je iemand leert dat de
   knoppen in deze app niets betekenen. */
function aiNogEensZin(res){
  var r = res && res.reden;
  return r !== "uit" && r !== "dagplafond";
}
function verbPopup(term){''')

    rep(A_CHECK, u'''      if(!res || !res.ok){
        /* v23.70: hier stond "De AI is even niet bereikbaar, probeer het straks nog eens." Dat was
           sinds het slot op de server bijna altijd onwaar. Zie aiFoutTekst(). */
        af.innerHTML = "<div class='feedback bijna'>\\ud83e\\udd16 "+aiFoutTekst(res)+"</div>";
        if(aiNogEensZin(res)){ ba.disabled=false; ba.textContent="🤖 Is mijn variant ook goed?"; }
        else { ba.classList.add("hidden"); }
        return;
      }''')

    rep(A_UITLEG, u'''      af.innerHTML = (res && res.ok) ? "<div class='uitleg'>🤖 "+res.uitleg+"</div>" :
        "<div class='feedback bijna'>\\ud83e\\udd16 "+aiFoutTekst(res)+"</div>";''')

    rep(A_POPUP, u'''      b2.textContent = aiFoutTekst(res);''')

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
