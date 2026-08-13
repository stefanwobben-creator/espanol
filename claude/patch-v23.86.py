#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.86: waar iemand vandaan kwam, één keer vastgelegd.

Stefan, 13 aug: eerst "wat wil je als eerste weten van een vreemde" -> "terugkomt op dag 2", en
daarna "ja ik ga het op linkedin delen".

Die twee bijten elkaar, en dat is niet erg zolang je het weet. Een LinkedIn-klik is nieuwsgierigheid:
iemand scrolt, ziet iets, kijkt, en is weg. Een link die je iemand persoonlijk geeft is een afspraak.
Allebei tellen ze straks als "starter", en dan is de terugkomst op dag 2 een gemiddelde van twee
groepen die niets met elkaar te maken hebben. Dat getal kun je niet repareren en ook niet geloven:
zakt het, dan weet je niet of de app tegenvalt of dat er gewoon veel nieuwsgierigen langskwamen.

Het scheiden is klein werk zolang je het vóór de post doet. Daarna is het te laat, want de eerste
groep is dan al binnen zonder etiket.

## Wat er wordt vastgelegd, en wat niet

`S.bron`, één keer, bij het eerste bezoek, en daarna nooit meer aangeraakt:

  - `?van=li` in de link  -> "li". Zelf te kiezen, dus je kunt LinkedIn, een appje en een mailtje
    uit elkaar houden zonder iets te bouwen.
  - anders de host van document.referrer, alleen de host: "linkedin.com", "google.com".
  - anders "direct" (ingetypt, bladwijzer, of een app die de referrer wegpoetst).

Alleen de host, nooit het volledige adres. Dat is precies genoeg om twee groepen te scheiden en
niets meer; welke pagina iemand daarvoor las gaat mij niets aan en de app ook niet.

Het gaat mee in de state die toch al naar de server gaat via /api/sync, dus er is geen nieuw
verzoek, geen nieuw endpoint en geen extra opslag. /api/admin/terugkomst groepeert er voortaan op.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.86"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.86" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_PENDING = '''var pendingGroep = null;
var pendingDuel = null; // v19.57: een duel-uitnodiging is nu ook een link, niet alleen een code
var pendingBeheer = false; // v19.92: de muziekbeheerrol, pas toepassen als S geladen is'''

# persist() is de plek waar de state wordt weggeschreven; daar staat S zeker klaar.
A_HOOK = None
for kandidaat in ('function persist(){', 'function persist() {'):
    if kandidaat in src:
        A_HOOK = kandidaat
        break

if DOE_APP:
    ontbreekt = []
    if A_PENDING not in src:
        ontbreekt.append("het blok met pendingGroep")
    if not A_HOOK:
        ontbreekt.append("persist()")
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.85. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_PENDING, A_PENDING + '''

/* v23.86: waar kwam iemand vandaan? Eén keer, bij het eerste bezoek, en daarna nooit meer.

   Stefan deelt de app op LinkedIn en wil weten of mensen terugkomen op dag 2. Die twee bijten
   elkaar: een LinkedIn-klik is nieuwsgierigheid, een link die je iemand persoonlijk geeft is een
   afspraak. Zonder etiket is de terugkomst een gemiddelde van twee groepen die niets met elkaar te
   maken hebben, en dan weet je bij een tegenvallend getal niet of de app tegenviel of dat er veel
   nieuwsgierigen langskwamen.

   Alleen de host van de verwijzer, nooit het volledige adres. Dat is genoeg om twee groepen te
   scheiden en niets meer; welke pagina iemand daarvoor las gaat de app niets aan. Met ?van=... in
   de link kun je het zelf benoemen, zodat een appje en een mailtje ook uit elkaar te houden zijn. */
function bronNu(){
  try{
    var m = (location.search || "").match(/[?&]van=([a-z0-9_-]{1,16})/i);
    if(m) return m[1].toLowerCase();
    var r = document.referrer || "";
    if(!r) return "direct";
    var h = r.split("/")[2] || "";
    h = h.replace(/^www\\./, "").toLowerCase();
    if(!h || h === location.hostname) return "direct";
    return h.slice(0, 40);
  }catch(e){ return "direct"; }
}''')

    # De haak in persist(): daar staat S gegarandeerd klaar, en het kost één vergelijking per
    # opslagbeurt. Bewust niet in boot(): die heeft meerdere ingangen en dan mis je er een.
    rep(A_HOOK, A_HOOK + '''
  // v23.86: één keer vastleggen en daarna met rust laten. Wie hem al heeft, houdt hem.
  if(S && !S.bron){ try{ S.bron = bronNu(); }catch(e){} }''')

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
