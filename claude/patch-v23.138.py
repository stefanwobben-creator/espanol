#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.138: na de les zie je wat er verschoven is.

Stefan, 20 aug: "nadat je een les hebt gedaan wil je ook live feedback op je ontwikkeling."

## Wat er stond

Het eindscherm zei: "¡Muy bien! Chispa is blij met je" en "+2 tapas". Daarna een knop om Chispa haar
tapa te geven, en drie voorstellen. Geen enkel getal over wat je zojuist hebt gedaan.

Dat is niet een vergeten regel maar een gat in de meting: **de app hield nergens bij wat er op een
dag aan je woorden veranderde.** `st.box` gaat omhoog en dat is alles; er is geen datum bij, dus na
afloop is niet te zeggen welke woorden vandaag zijn opgeschoven.

## Wat er nu staat

Eén veld erbij: `st.od`, de dag waarop een woord een doosje opschoof. Drie plekken zetten hem, en
dat zijn precies de drie plekken waar een doos omhoog gaat: `srsOmhoog()` (sinds v23.132 de enige
weg voor de woordtrainer en Aventura), `wCheckAntwoord()` (de Laatste stap) en `spelSrsBij()` (de
spellen).

Daaruit rekent `dagVerschoven()` vier dingen, en alle vier zijn ze waar of ze staan er niet:

  * **kaartjes een doosje omhoog** · komen nu later terug in plaats van morgen
  * **woorden gered** · woorden die je eerder fout had en vandaag weer goed
  * **nieuw vandaag** · uit je dagportie en uit wat je tijdens het lezen aantikte
  * **vast geworden** · met het woord erbij, en hoeveel dagen het duurde

En de trede van de zinnenladder, als die vandaag bewoog. Daarvoor onthoudt `vertBij()` sinds deze
versie waar je aan de dag begon.

## Waarom "bewezen vast" er niet als teller staat

Dat getal verandert na één les bijna nooit: het vraagt vijf goede beurten over minstens 25 dagen.
Een teller die stilstaat terwijl je aan het werk bent is demotiverend, en het is precies de fout die
dit scherm al drie keer heeft gemaakt (zie v23.18). Wat er wél staat is het gebeurtenisbericht: is er
vandaag een woord vast geworden, dan staat dat er met naam en met het aantal dagen erbij. Dat komt
niet elke dag voor, en juist daarom is het iets waard.

## Wat er niet is

Als er niets verschoof staat er niets. Een lijstje met vier nullen is erger dan geen lijstje.

Bewaakt door test/suites/pw-verschoven.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.138"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ------------- 1. de drie plekken waar een doos omhoog gaat, zetten de datum

rep(
    '''function srsOmhoog(st, mag){
  st.box = Math.min(Math.max(0, st.box || 0) + srsStap(st), mag);
  return st.box;
}''',
    '''function srsOmhoog(st, mag){
  var voor = Math.max(0, st.box || 0);
  st.box = Math.min(voor + srsStap(st), mag);
  /* v23.138: de dag waarop dit woord opschoof. Zonder dit veld is na afloop van een les niet te
     zeggen wat er is veranderd, want st.box draagt geen datum. Alleen zetten als hij echt steeg:
     een beurt die tegen het plafond loopt heeft niets verschoven. */
  if(st.box > voor) st.od = today();
  return st.box;
}''',
)

rep(
    '''    st.k = 1;
    st.box = stevigDrempel();''',
    '''    st.k = 1;
    if(stevigDrempel() > (st.box || 0)) st.od = today();   // v23.138, zie srsOmhoog
    st.box = stevigDrempel();''',
)

rep(
    '''  st.box = Math.min((st.box || 0) + 1, SPEL_PLAFOND);''',
    '''  if(SPEL_PLAFOND > (st.box || 0)) st.od = today();      // v23.138, zie srsOmhoog
  st.box = Math.min((st.box || 0) + 1, SPEL_PLAFOND);''',
)

# ------------- 2. de ladder onthoudt waar de dag begon

rep(
    '''function vertBij(goed){
  var v = vertStand(), voor = v.trede;''',
    '''function vertBij(goed){
  var v = vertStand(), voor = v.trede;
  // v23.138: waar stond de ladder aan het begin van vandaag? Anders is na afloop niet te zeggen of
  // hij vandaag bewoog, alleen waar hij nu staat.
  if(v.d !== today()){ v.d = today(); v.dagStart = v.trede; }''',
)

# ------------- 3. wat er vandaag verschoof

rep(
    '''function lesFlowKlaarBonus(){''',
    '''/* ================= WAT ER VANDAAG VERSCHOOF (v23.138) =================

   Stefan, 20 aug: "nadat je een les hebt gedaan wil je ook live feedback op je ontwikkeling."

   Vier getallen, en alle vier zijn ze waar of ze staan er niet. Wat er met opzet NIET staat is
   "bewezen vast" als teller: dat vraagt vijf goede beurten over minstens 25 dagen en verandert na
   één les bijna nooit. Een teller die stilstaat terwijl je werkt is demotiverend, en dat is precies
   de fout die dit scherm al drie keer heeft gemaakt (zie de kop van voortgangCijfers, v23.18).

   Wél als gebeurtenis: is er vandaag een woord vast geworden, dan staat dat er met naam en met het
   aantal dagen dat het kostte. Dat gebeurt niet elke dag, en juist daarom is het iets waard. */
function dagVerschoven(){
  var t = today(), omhoog = 0, gered = 0, vast = [], id, st, w;
  for(id in (S.srs || {})){
    st = S.srs[id];
    if(!st || typeof st !== "object" || st.od !== t) continue;
    omhoog++;
    if((st.f || 0) > 0) gered++;
    if((st.box || 0) >= stevigDrempel() && st.k && vast.length < 2){
      w = null;
      for(var i = 0; i < WORDS.length; i++){ if(WORDS[i].id === id){ w = WORDS[i]; break; } }
      if(w) vast.push({es:w.es, n:st.n || 0});
    }
  }
  var nieuw = 0;
  try { nieuw = newToday(); } catch(e){ nieuw = 0; }
  var uitLezen = 0, k, m = S.mijn || {};
  for(k in m){ if(m[k] && m[k].d === t) uitLezen++; }
  var v = null;
  try { v = S.vert && S.vert.d === t && typeof S.vert.dagStart === "number" ? S.vert : null; } catch(e){ v = null; }
  return {omhoog:omhoog, gered:gered, nieuw:nieuw, uitLezen:uitLezen, vast:vast,
          tredeVoor: v ? v.dagStart : null, tredeNa: v ? v.trede : null};
}
function dagMetingRij(n, kop, uitleg){
  return "<div style='display:flex; align-items:baseline; gap:10px; padding:5px 0; border-bottom:1px solid var(--border)'>"+
    "<b style='font-size:1.3rem; min-width:1.8em; text-align:right'>"+n+"</b>"+
    "<span style='font-size:.88rem'>"+kop+
      "<span style='display:block; font-size:.78rem; color:var(--muted)'>"+uitleg+"</span></span></div>";
}
function dagVerschovenHtml(){
  var d = dagVerschoven(), r = "";
  if(d.omhoog){
    r += dagMetingRij(d.omhoog, ct("kaartjes een doosje omhoog","cards moved up a box"),
      ct("die komen nu later terug in plaats van morgen","they come back later now instead of tomorrow"));
  }
  if(d.gered){
    r += dagMetingRij(d.gered, ct("woorden gered","words rescued"),
      ct("die had je eerder fout en vandaag weer goed","you had these wrong before and right again today"));
  }
  if(d.nieuw || d.uitLezen){
    r += dagMetingRij(d.nieuw + d.uitLezen, ct("nieuw vandaag","new today"),
      d.uitLezen ? ct("waarvan "+d.uitLezen+" die je zelf aantikte tijdens het lezen",
                      "of which "+d.uitLezen+" you tapped yourself while reading")
                 : ct("uit je dagportie","from today's portion"));
  }
  if(d.tredeNa !== null && d.tredeNa !== d.tredeVoor){
    r += dagMetingRij((d.tredeNa > d.tredeVoor ? "+" : "") + (d.tredeNa - d.tredeVoor),
      ct("op de ladder van zelf maken","on the writing ladder"),
      ct("je staat nu op trede "+d.tredeNa+" van "+VERT_TREDES.length,
         "you are now on step "+d.tredeNa+" of "+VERT_TREDES.length));
  }
  /* Geen lijstje met nullen. Deed je vandaag alleen dingen die niets verschoven, dan is dat het
     eerlijke antwoord en hoort er niets te staan. */
  if(!r) return "";
  var kop = "<div class='card'><span class='kicker'>"+ct("Wat er vandaag verschoof","What moved today")+"</span>"+r+"</div>";
  if(d.vast.length){
    kop += "<div class='card' style='background:var(--green-soft); border-color:#bfe0cd'>"+
      "<span class='kicker'>"+ct("Vast","Solid")+"</span>"+
      d.vast.map(function(x){
        return "<p style='margin:0 0 2px'><span class='es' style='font-weight:700'>"+x.es+"</span> "+
          ct("staat nu vast.","is solid now.")+"</p>"+
          "<p class='muted' style='margin:0 0 6px; font-size:.83rem'>"+
          ct(x.n+" beurten, en de laatste was een check die je niet zelf beoordeelde. Die zie je pas over twee maanden terug.",
             x.n+" turns, and the last one was a check you did not grade yourself. You will not see it again for two months.")+"</p>";
      }).join("")+"</div>";
  }
  return kop;
}

function lesFlowKlaarBonus(){''',
)

# ------------- 4. en hij staat op het eindscherm

rep(
    '''  el.innerHTML = "<div class='card celebrate'><span class='kicker'>"+ct("Les afgerond","Session complete")+" 🎉</span>"+
    "<p class='big' style='margin:6px 0'>"+ct("¡Muy bien! Chispa is blij met je.","¡Muy bien! Chispa is happy with you.")+"</p>"+''',
    '''  el.innerHTML = dagVerschovenHtml()+   /* v23.138: eerst wat er verschoof, dan de viering */
    "<div class='card celebrate'><span class='kicker'>"+ct("Les afgerond","Session complete")+" 🎉</span>"+
    "<p class='big' style='margin:6px 0'>"+ct("¡Muy bien! Chispa is blij met je.","¡Muy bien! Chispa is happy with you.")+"</p>"+''',
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
