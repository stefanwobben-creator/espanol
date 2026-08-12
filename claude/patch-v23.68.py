#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.68: op dag 1 spreekt Chispa eerst jouw taal.

Stefan, 12 aug, over de begroeting op zijn dagscherm: "onduidelijk wat 'cinco minutos....' dit doet
en waarom dat hier staat."

Wat er stond, in deze volgorde en in deze maten:

    Cinco minutos y ya está.        rood, vet, 0,86 rem
    Vijf minuutjes en het staat er.  grijs, 0,78 rem

De opvallendste regel op het scherm was dus een zin in een taal die je nog niet kent, en de vertaling
stond eronder in het formaat waarin je de kleine lettertjes zet. Voor wie Spaans leest is dat leuk.
Voor wie de app net heeft geïnstalleerd is het een plaatje: je ziet dat er iets staat, je weet niet
wat, en je leest het niet.

## De omkering

De eerste zeven dagen staat de regel die je kunt lezen boven, in het grote formaat, en de Spaanse
eronder in het kleine. Daarna draait het om, want dan is Spaans-eerst juist de bedoeling: je hebt de
vertaling dan zeven keer onder dezelfde zin zien staan, en de zin doet zijn werk pas als hij je
eerst laat proberen.

Zeven dagen en niet drie, en niet altijd: drie is te kort om een zin te leren herkennen, en altijd
zou betekenen dat een taalapp zijn eigen taal wegstopt.

Het geldt op allebei de plekken waar Chispa iets zegt: op de dagkaart en in de banner die door je
hele les meeloopt. Anders zou de banner de zin nog steeds als plaatje tonen.

## Wat niet verandert

De zinnen zelf, de kleur en het feit dat er Spaans staat. Alleen de volgorde en het formaat.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.68"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function chispaZegHtml" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_BANNER = '''        "<p class='lfsay'><span class='es'>"+f.es+"</span><span class='nl'>"+ct(f.nl, f.en || f.nl)+"</span></p>"+'''

A_KAART = u'''        "<p class='lfsay'><span class='es'>"+(afgesloten ? "Hasta mañana." : hervat ? "Seguimos donde lo dejamos." : gedaanVandaag ? "¡Muy bien!" : groet.es)+"</span>"+
          "<span class='nl'>"+(afgesloten ? ct("Je bent klaar. Chispa slaapt zo lekker.","You're done. Chispa's off to sleep happy.")
            : hervat ? ct("We gaan verder waar we gebleven waren.","We pick up where we left off.")
            : gedaanVandaag ? ct("Chispa is trots op je.","Chispa is proud of you.")
            : ct(groet.nl, groet.en))+"</span></p>"+'''

A_CSS = '''  .lfsay .nl{display:block; color:var(--muted); font-size:.78rem; font-weight:400;}'''

A_VOOR = '''function lesFlowBannerHtml(){'''

if DOE_APP:
    ontbreekt = [a for a in [A_BANNER, A_KAART, A_CSS, A_VOOR] if a not in src]
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
    rep(A_VOOR, '''/* ================= CHISPA SPREEKT EERST JOUW TAAL (v23.68) =================
   Stefan over "Cinco minutos y ya está." op zijn dagscherm: "onduidelijk wat 'cinco minutos....'
   dit doet en waarom dat hier staat." De Spaanse zin stond rood, vet en op 0,86 rem; de vertaling
   eronder grijs op 0,78 rem. De opvallendste regel van het scherm was dus onleesbaar voor wie hier
   net binnenkomt, en de leesbare regel stond in het formaat van de kleine lettertjes.

   De eerste zeven dagen draait dat om. Daarna niet meer: Spaans-eerst is de bedoeling van een
   taalapp, en dan heb je de vertaling zeven keer onder dezelfde zin zien staan.

   Zeven en niet drie, want drie dagen is te kort om een zin te leren herkennen. En niet altijd,
   want dan verstopt een taalapp zijn eigen taal. */
function chispaOmgekeerd(){
  try { return dagenTotaal() <= 7; } catch(e){ return false; }
}
function chispaZegHtml(es, nl){
  var om = chispaOmgekeerd();
  return "<p class='lfsay"+(om ? " omgekeerd" : "")+"'>"+
    (om ? "<span class='nl'>"+nl+"</span><span class='es'>"+es+"</span>"
        : "<span class='es'>"+es+"</span><span class='nl'>"+nl+"</span>")+"</p>";
}
function lesFlowBannerHtml(){''')

    rep(A_BANNER, '''        chispaZegHtml(f.es, ct(f.nl, f.en || f.nl))+''')

    rep(A_KAART, u'''        chispaZegHtml(
          (afgesloten ? "Hasta mañana." : hervat ? "Seguimos donde lo dejamos." : gedaanVandaag ? "¡Muy bien!" : groet.es),
          (afgesloten ? ct("Je bent klaar. Chispa slaapt zo lekker.","You're done. Chispa's off to sleep happy.")
            : hervat ? ct("We gaan verder waar we gebleven waren.","We pick up where we left off.")
            : gedaanVandaag ? ct("Chispa is trots op je.","Chispa is proud of you.")
            : ct(groet.nl, groet.en)))+''')

    rep(A_CSS, '''  .lfsay .nl{display:block; color:var(--muted); font-size:.78rem; font-weight:400;}
  /* v23.68: de eerste zeven dagen staat de regel die je kunt lezen boven en in het grote formaat.
     Zelfde zinnen, zelfde kleur, alleen de volgorde en de maat draaien om. */
  .lfsay.omgekeerd .nl{display:block; color:var(--ink); font-size:.9rem; font-weight:700;}
  .lfsay.omgekeerd .es{display:block; font-size:.8rem; font-weight:400; margin-top:2px;}''')

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
