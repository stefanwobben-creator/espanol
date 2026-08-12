#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.67: de app zegt eindelijk wat er morgen gebeurt, en dat ze je niet komt halen.

Stefan, 12 aug, over het dagscherm: "niet duidelijk of je morgen een reminder krijgt of je morgen
terug moet komen voor een nieuwe les of je nu al door kan."

Nagemeten, en het is erger dan een onduidelijkheid:

    - `Notification`, `serviceWorker`, `showNotification` in de hele app:   0 keer
    - tekst over "morgen" op het dagscherm, in alle drie de toestanden:     geen

De app stuurt dus geen herinnering, en zegt dat nergens. Dat is precies de combinatie waar iemand
op wacht die denkt dat hij wel gepord zal worden. Er stond één zin over morgen in de hele app: op
het eindscherm van je állereerste les, en daarna nooit meer.

## Wat er nu staat

Op het eindscherm van elke les, en op de dagkaart zodra je klaar bent:

    Morgen komen er 7 woordjes terug.

Dat getal is niet verzonnen: het is dezelfde som die `dagPortie()` morgen maakt. Alles wat op of
vóór morgen op herhaling staat, met dezelfde bovengrens (`portieMax()`) en dezelfde ruimte die voor
nieuwe woorden wordt vrijgehouden. Staat er niets klaar, dan zegt hij dat ook, en dan zegt hij er
meteen bij dat je met nieuwe woorden begint.

En erachteraan, alleen in je eerste drie dagen:

    Je krijgt geen herinnering, dus kom terug wanneer het jou uitkomt.

Waarom alleen die eerste dagen: het is een feit dat je één keer moet horen. Elke dag herhalen dat
er niets gaat gebeuren is zelf een vorm van zeuren, en het is de soort regel die je na de derde keer
niet meer leest, waarna je ook de regel ernaast niet meer leest.

## Wat hier bewust niet gebeurt

Er komt geen herinnering bij. Dat zou een pushrecht, een servicewerker en een toestemmingsvraag op
dag 1 betekenen, en die vraag is precies het moment waarop een vreemde wegklikt. De eerlijke variant
is goedkoper: zeg dat je niet komt.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.67"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function morgenTerug" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_VOOR = '''function buildQueue(){'''

A_EERSTE = u'''    (eersteOoit ? "<p class='muted' style='margin:10px 0 0'><b>"+ct("Tot morgen?","See you tomorrow?")+"</b> "+ct("Dan komen de woordjes van vandaag precies op tijd terug: zó blijven ze plakken. Vijf minuutjes, meer niet.","Today's words will come back right on time — that's how they stick. Five minutes, no more.")+"</p>" : "")+'''

A_AFGESLOTEN = '''    (afgesloten
      ? "<p class='muted' style='margin:8px 0 0'><span id='btnDagToch' style='text-decoration:underline; cursor:pointer'>"+ct("toch nog een les doen","do another session anyway")+"</span></p>"'''

if DOE_APP:
    ontbreekt = [a for a in [A_VOOR, A_EERSTE, A_AFGESLOTEN] if a not in src]
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
    rep(A_VOOR, '''/* ================= WAT ER MORGEN GEBEURT (v23.67) =================
   Stefan: "niet duidelijk of je morgen een reminder krijgt of je morgen terug moet komen voor een
   nieuwe les of je nu al door kan." Geteld: nul aanroepen van Notification, serviceWorker of
   showNotification in de hele app, en geen enkele regel over morgen op het dagscherm.

   Het getal komt uit dezelfde som als dagPortie(): alles wat op of vóór morgen op herhaling staat,
   met dezelfde bovengrens en dezelfde ruimte die voor nieuwe woorden wordt vrijgehouden. Een getal
   dat morgen niet klopt is erger dan geen getal, want dan leer je dat de app maar wat zegt. */
function morgenTerug(){
  var m = addDays(today(), 1), due = 0, id, st;
  for(id in S.srs){
    st = S.srs[id];
    if(!st || typeof st !== "object") continue;
    if(st.due <= m) due++;
  }
  var ruimteNieuw = 0;
  try { ruimteNieuw = Math.min(nieuwPerDag(), nieuwPlafond()); } catch(e){ ruimteNieuw = 0; }
  var cap = 20;
  try { cap = portieMax(); } catch(e){ cap = 20; }
  return Math.min(due, Math.max(0, cap - ruimteNieuw));
}
/* De zin die daarbij hoort. De clausule over de herinnering staat er alleen in je eerste drie
   dagen: het is een feit dat je één keer moet horen, en elke dag melden dat er niets gaat gebeuren
   is zelf een vorm van zeuren. Regels die je niet meer leest, maken de regel ernaast ook onzichtbaar. */
function morgenZin(){
  var n = morgenTerug(), dg = 0;
  try { dg = dagenTotaal(); } catch(e){ dg = 0; }
  var z = n > 0
    ? ct("Morgen komen er "+n+" "+(n === 1 ? "woordje" : "woordjes")+" terug.",
         "Tomorrow "+n+" "+(n === 1 ? "word comes" : "words come")+" back.")
    : ct("Morgen staat er nog niets op herhaling, dus je begint met nieuwe woordjes.",
         "Nothing is due for review tomorrow, so you will start with new words.");
  if(dg <= 3){
    z += " " + ct("Je krijgt geen herinnering, dus kom terug wanneer het jou uitkomt.",
                  "You will not get a reminder, so come back whenever it suits you.");
  }
  return z;
}
function morgenZinHtml(marge){
  return "<p class='muted' style='margin:"+(marge || "8px")+" 0 0'>"+morgenZin()+"</p>";
}
function buildQueue(){''')

    rep(A_EERSTE, u'''    /* v23.67: hier stond alleen op je állereerste dag iets over morgen, en daarna nooit meer. De
       zin die er nu staat geldt elke dag en noemt het echte aantal; de "tot morgen"-belofte blijft
       op dag 1 staan, want die gaat over waarom herhalen werkt en niet over hoeveel. En het
       gedachtestreepje in de Engelse zin is een komma geworden: die staan hier verder nergens. */
    (eersteOoit ? "<p class='muted' style='margin:10px 0 0'><b>"+ct("Tot morgen?","See you tomorrow?")+"</b> "+ct("Dan komen de woordjes van vandaag precies op tijd terug: zó blijven ze plakken. Vijf minuutjes, meer niet.","Today's words will come back right on time, that's how they stick. Five minutes, no more.")+"</p>" : "")+
    morgenZinHtml(eersteOoit ? "4px" : "10px")+''')

    rep(A_AFGESLOTEN, '''    /* v23.67: klaar voor vandaag betekende tot nu toe: geen enkel bericht over morgen, op het
       scherm waar die vraag juist opkomt. */
    (afgesloten ? morgenZinHtml("8px") : "")+
    (afgesloten
      ? "<p class='muted' style='margin:8px 0 0'><span id='btnDagToch' style='text-decoration:underline; cursor:pointer'>"+ct("toch nog een les doen","do another session anyway")+"</span></p>"''')

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
