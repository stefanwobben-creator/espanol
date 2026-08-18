#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.125: de schoen. 22 onregelmatige werkwoorden zijn zes patronen.

## De meting

Stefan vroeg wat het beste is om Spaans te leren, bij de vraag waar de presente-route moet
beginnen. Ik dacht dat het antwoord "de -er/-ir-uitgangen" of "toegepaste zinnen" was. Geen van
beide. Ik heb de 33 werkwoorden in VERBOS doorgerekend:

    regelmatig in het presente   11
    onregelmatig                 22

Die 22 zien eruit als 22 dingen om uit je hoofd te leren. Uitgerekend zijn het er zes:

    de schoen  →ie    tener, querer, venir, empezar, pensar, sentir, preferir      7
    de schoen  →ue    poder, jugar, dormir, volver                                 4
    de schoen  →i     decir, pedir                                                 2
    eigen yo   -go    tener, hacer, decir, poner, salir, venir                     6
    eigen yo   -oy    ser, estar, ir, dar                                          4
    eigen yo   los    saber (sé), ver (veo)                                        2

tener, venir en decir staan in twee rijen: zij hebben én een schoen én een eigen yo. Zeven plus
vier plus twee plus drie plus vier plus twee is precies 22. Er valt niets buiten.

De schoen is de naam voor de vorm: de stam verandert bij yo, tú, él en ellos, en juist niet bij
nosotros en vosotros. Teken je dat in de tabel, dan krijg je de omtrek van een laars.

## Waarom dit de eerste stap van het presente is

1. Daar zit de massa. 22 van de 33, en het zijn de frequentste werkwoorden die er zijn: ser,
   estar, tener, ir, hacer, poder, querer, decir, venir, ver, saber.
2. Het verandert onthouden in rekenen. Zes patronen in plaats van 22 rijtjes, en een patroon
   draagt naar werkwoorden die je nooit gezien hebt. Dat is precies wat de overdrachtsstap
   (v23.118) meet.
3. Het betaalt twee keer. Eerder gemeten: de 22 onregelmatige van de subjuntivo ZIJN de 22 van
   het presente. Wie de schoen kent, kent hem daar ook.

## Wat er verandert

Eén ding: **een les hoeft geen tijd te zijn.** "De les" onderwees "één tijd tegelijk". Vanaf nu
onderwijst hij "één rij tegelijk", en een tijd is daar één soort van. De zes patronen zijn de
andere soort. Alle zes de stappen, de nakijker, de voortgang en de overdrachtsstap blijven exact
wat ze waren.

## Geen tabel

Niets van het bovenstaande staat als lijst in het bestand. conjPatroon() rekent het uit de
vormen die er al staan, net zoals conjRegelmatig() en conjRegelmatigIn() dat doen. Zet er morgen
een werkwoord bij, dan sorteert het zichzelf in de goede rij. De regel van 15 aug: staat een feit
in de data, dan schrijft geen enkele codeplek dat feit opnieuw.

Wat wél met de hand geschreven is, is de uitleg per patroon. Dat is geen feit uit de data maar
kennis, en die hoort in tekst.
"""

import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.125"

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


# ------------- 1. het patroon, uitgerekend uit de vormen

rep(
    '''function lesId(t){ return "les." + t; }''',
    '''/* ================= HET PATROON ACHTER DE 22 (v23.125) =================

   Gemeten in VERBOS: 11 van de 33 werkwoorden zijn regelmatig in het presente, 22 niet. Dat getal
   leest als 22 rijtjes om uit je hoofd te leren. Uitgerekend zijn het er zes:

       de schoen  \\u2192ie    tener, querer, venir, empezar, pensar, sentir, preferir      7
       de schoen  \\u2192ue    poder, jugar, dormir, volver                                 4
       de schoen  \\u2192i     decir, pedir                                                 2
       eigen yo   -go    tener, hacer, decir, poner, salir, venir                     6
       eigen yo   -oy    ser, estar, ir, dar                                          4
       eigen yo   los    saber (s\\u00e9), ver (veo)                                        2

   tener, venir en decir staan in twee rijen: die hebben \\u00e9\\u00e9n schoen \\u00e9n een eigen yo. 7+4+2+3+4+2
   = 22, dus er valt niets buiten.

   De schoen is de vorm: de stam verandert bij yo, t\\u00fa, \\u00e9l en ellos, en juist niet bij nosotros en
   vosotros. Omcirkel dat in de tabel en je hebt de omtrek van een laars.

   Niets hiervan staat als lijst in dit bestand. conjPatroon() leidt het af uit de vormen die er al
   staan, net als conjRegelmatig() hierboven. Wat w\\u00e9l met de hand geschreven is, is de uitleg per
   patroon: dat is geen feit uit de data maar kennis. */
function conjKaal(s){ return stripAcc(String(s || "")); }
/* De stam die uit de jij-vorm valt af te lezen. Null zodra de vorm niet op de gewone uitgang
   eindigt, want dan valt er niets af te lezen (ser: "eres"). */
function conjBootStam(v){
  var u = CONJ_UITGANGEN[conjGroep(v)];
  if(!u || !v.presente) return null;
  var tu = conjKaal(v.presente[1]), uit = conjKaal(u[1]);
  if(tu.length <= uit.length || tu.slice(-uit.length) !== uit) return null;
  return tu.slice(0, tu.length - uit.length);
}
var CONJ_WISSELS = [["e","ie"], ["o","ue"], ["u","ue"], ["e","i"]];
/* {regelmatig, wissel, yo}. wissel is de klinker die erbij komt ("ie"/"ue"/"i") en staat er alleen
   als nosotros en vosotros de infinitiefstam h\\u00f3uden: dat is wat een schoen een schoen maakt.
   yo is "go", "oy" of "los" zodra de yo-vorm noch uit de gewone stam noch uit de schoenstam volgt. */
function conjPatroon(v){
  var g = conjGroep(v), u = CONJ_UITGANGEN[g];
  var leeg = {regelmatig:false, wissel:null, yo:null};
  if(!u || !v.presente || v.presente.length !== 6) return leeg;
  var stam = conjKaal(v.inf.slice(0, -2));
  var vv = v.presente.map(conjKaal), reg = u.map(function(x){ return conjKaal(stam + x); });
  if(vv.join("|") === reg.join("|")) return {regelmatig:true, wissel:null, yo:null};

  var boot = conjBootStam(v), wissel = null;
  var schoen = boot && boot !== stam && vv[3] === reg[3] && vv[4] === reg[4];
  if(schoen){
    for(var i = 0; i < CONJ_WISSELS.length; i++){
      var a = CONJ_WISSELS[i][0], b = CONJ_WISSELS[i][1];
      /* van achter naar voren vervangen: de klinker die wisselt is de laatste in de stam
         (empezar \\u2192 empiez, niet \\u2192 iempez) */
      var k = stam.lastIndexOf(a);
      if(k >= 0 && stam.slice(0, k) + b + stam.slice(k + a.length) === boot){ wissel = b; break; }
    }
  }
  var yo = null;
  if(vv[0] !== reg[0] && (!boot || vv[0] !== boot + "o")){
    yo = /go$/.test(vv[0]) ? "go" : (/oy$/.test(vv[0]) ? "oy" : "los");
  }
  return {regelmatig:false, wissel:wissel, yo:yo};
}
/* De zes rijen. De volgorde is die van de omvang: het grootste patroon eerst, want dat is het
   patroon dat het vaakst iets oplevert. */
var CONJ_PATRONEN = [
  {id:"schoen.ie", soort:"schoen", sleutel:"ie", es:"la bota: e \\u2192 ie",
   nl:"de schoen: e wordt ie", en:"the boot: e becomes ie",
   doet:"Zeven werkwoorden waarin de e van de stam ie wordt. Niet overal: juist bij nosotros en vosotros blijft hij e. Teken je dat in de tabel, dan krijg je de omtrek van een laars.",
   doetEn:"Seven verbs where the stem e turns into ie. Not everywhere: at nosotros and vosotros it stays e. Draw that in the table and you get the outline of a boot.",
   vorm:"quiero, quieres, quiere, queremos, quer\\u00e9is, quieren. Vier keer ie, twee keer e.",
   vormEn:"quiero, quieres, quiere, queremos, quer\\u00e9is, quieren. Four times ie, twice e."},
  {id:"schoen.ue", soort:"schoen", sleutel:"ue", es:"la bota: o \\u2192 ue",
   nl:"de schoen: o wordt ue", en:"the boot: o becomes ue",
   doet:"Dezelfde laars, andere klinker: de o wordt ue, behalve bij nosotros en vosotros. Jugar hoort er ook bij, met een u in plaats van een o; dat is het enige werkwoord dat dat doet.",
   doetEn:"The same boot, another vowel: o becomes ue, except at nosotros and vosotros. Jugar belongs here too, with a u instead of an o; it is the only verb that does that.",
   vorm:"puedo, puedes, puede, podemos, pod\\u00e9is, pueden. En juego, jugamos.",
   vormEn:"puedo, puedes, puede, podemos, pod\\u00e9is, pueden. And juego, jugamos."},
  {id:"yo.go", soort:"yo", sleutel:"go", es:"yo op -go",
   nl:"de yo-vorm op -go", en:"the yo form in -go",
   doet:"Alleen de ik-vorm is anders: er komt een g in. De rest van het rijtje doet gewoon mee. Drie van deze zes hebben daarn\\u00e1ast ook nog een schoen (tener, venir, decir), en dat is precies waarom je ze los oefent.",
   doetEn:"Only the I-form differs: a g appears. The rest of the row behaves normally. Three of these six also have a boot (tener, venir, decir), which is exactly why you practise them separately.",
   vorm:"tengo, hago, digo, pongo, salgo, vengo. Steeds -go, en dan verder gewoon.",
   vormEn:"tengo, hago, digo, pongo, salgo, vengo. Always -go, and then on as usual."},
  {id:"yo.oy", soort:"yo", sleutel:"oy", es:"yo op -oy",
   nl:"de yo-vorm op -oy", en:"the yo form in -oy",
   doet:"Vier werkwoorden waarvan de ik-vorm op -oy eindigt. Het zijn er maar vier, en het zijn er vier die je elke dag nodig hebt.",
   doetEn:"Four verbs whose I-form ends in -oy. There are only four, and they are four you need every day.",
   vorm:"soy, estoy, voy, doy. Van ser, estar, ir en dar.",
   vormEn:"soy, estoy, voy, doy. From ser, estar, ir and dar."},
  {id:"schoen.i", soort:"schoen", sleutel:"i", es:"la bota: e \\u2192 i",
   nl:"de schoen: e wordt i", en:"the boot: e becomes i",
   doet:"De kleinste laars: de e wordt geen ie maar een enkele i. Twee werkwoorden, allebei op -ir, en allebei hebben ze daarnaast een yo op -go.",
   doetEn:"The smallest boot: the e becomes a single i, not ie. Two verbs, both -ir, and both also have a yo in -go.",
   vorm:"pido, pides, pide, pedimos, ped\\u00eds, piden.",
   vormEn:"pido, pides, pide, pedimos, ped\\u00eds, piden."},
  {id:"yo.los", soort:"yo", sleutel:"los", es:"de losse twee",
   nl:"de twee losse yo-vormen", en:"the two loose yo forms",
   doet:"Saber en ver volgen geen enkel patroon in hun ik-vorm. Twee vormen om gewoon te onthouden, en dat mag: twee is te doen, tweeëntwintig niet.",
   doetEn:"Saber and ver follow no pattern at all in their I-form. Two forms to simply memorise, and that is fine: two is doable, twenty-two is not.",
   vorm:"s\\u00e9 en veo. Verder doen ze allebei gewoon mee.",
   vormEn:"s\\u00e9 and veo. Otherwise they behave normally."}
];
function conjPatroonVan(id){
  for(var i = 0; i < CONJ_PATRONEN.length; i++) if(CONJ_PATRONEN[i].id === id) return CONJ_PATRONEN[i];
  return null;
}
function conjInPatroon(v, pat){
  var p = conjPatroon(v);
  return pat.soort === "schoen" ? p.wissel === pat.sleutel : p.yo === pat.sleutel;
}
function conjPatroonPool(id){
  var pat = conjPatroonVan(id);
  if(!pat) return [];
  return VERBOS.filter(function(v){ return conjInPatroon(v, pat); });
}

function lesId(t){ return "les." + t; }''',
)

# ------------- 2. een les is een rij, en een tijd is daar één soort van

rep(
    '''function lesWerkwoord(t){
  var x = conjTiempo(t);
  var naam = (x && x.les) || "hablar";
  var v = VERBOS.filter(function(w){ return w.inf === naam; })[0];
  return v || conjVerbPool(t)[0] || VERBOS[0];
}
function lesStart(t){
  var v = lesWerkwoord(t);
  lesSpel = {t:t, v:v, stap:0, i:0, goed:0, fout:0, gekozen:null, getypt:"", af:false, opties:null, over:null};
  return lesSpel;
}''',
    '''function lesWerkwoord(t){
  var x = conjTiempo(t);
  var naam = (x && x.les) || "hablar";
  var v = VERBOS.filter(function(w){ return w.inf === naam; })[0];
  return v || conjVerbPool(t)[0] || VERBOS[0];
}
/* v23.125: hier stond "\\u00e9\\u00e9n tijd tegelijk", en dat was te smal. Een les onderwijst \\u00e9\\u00e9n RIJ, en een
   tijd is daar \\u00e9\\u00e9n soort van; de zes patronen binnen het presente zijn de andere. De zes stappen,
   de nakijker en de voortgang weten van dat verschil niets: die krijgen een rij en een tijd, en
   verder is alles hetzelfde. Zie de toelichting bij conjPatroon(). */
function lesRij(id){
  var x = conjTiempo(id);
  if(x){
    return {id:id, t:id, tijd:true, es:x.es, nl:x.nl, en:x.en,
            doet:x.doet, doetEn:x.doetEn, vorm:x.vorm, vormEn:x.vormEn,
            vb:x.vb, vbNl:x.vbNl, vbEn:x.vbEn, v:lesWerkwoord(id),
            pool:function(lesV){ return lesOverdrachtPool(id, lesV); }};
  }
  var pat = conjPatroonVan(id);
  if(!pat) return null;
  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = pool[0];
  return {id:id, t:"presente", tijd:false, es:pat.es, nl:pat.nl, en:pat.en,
          doet:pat.doet, doetEn:pat.doetEn, vorm:pat.vorm, vormEn:pat.vormEn,
          vb:conjVorm(v0, 0, "presente"), vbNl:conjGloss(v0), vbEn:conjGloss(v0), v:v0,
          pool:function(lesV){ return pool.filter(function(w){ return w.inf !== lesV.inf; }); }};
}
/* Elke rij die de les vandaag kan onderwijzen: je open tijden, en daarna de patronen. De patronen
   staan achter de tijden omdat ze binnen het presente wonen en niet ernaast. */
function lesRijIds(){
  var uit = conjOpenTijden().slice();
  CONJ_PATRONEN.forEach(function(p){ if(conjPatroonPool(p.id).length) uit.push(p.id); });
  return uit;
}
function lesStart(t){
  var r = lesRij(t);
  if(!r) return null;
  lesSpel = {rij:r.id, t:r.t, v:r.v, stap:0, i:0, goed:0, fout:0, gekozen:null, getypt:"", af:false, opties:null, over:null};
  return lesSpel;
}''',
)

rep(
    '''function lesOverNu(){
  if(!lesSpel) return null;
  if(!lesSpel.over) lesSpel.over = lesOverdrachtRij(lesSpel.t, lesSpel.v);
  return lesSpel.over;
}''',
    '''function lesOverNu(){
  if(!lesSpel) return null;
  if(!lesSpel.over) lesSpel.over = lesOverdrachtRij(lesSpel.rij, lesSpel.v);
  return lesSpel.over;
}''',
)

rep(
    '''function lesOverdrachtRij(t, lesV){
  var pool = geschud(lesOverdrachtPool(t, lesV));''',
    '''function lesOverdrachtRij(rijId, lesV){
  var r = lesRij(rijId);
  var pool = geschud(r ? r.pool(lesV) : []);''',
)

rep(
    '''function lesStapAf(){
  if(!lesSpel) return;
  var st = brokLees(lesId(lesSpel.t));
  st.stapMax = Math.max(st.stapMax || 0, lesSpel.stap);
  st.laatst = today();
  S.brok = S.brok || {};
  S.brok[lesId(lesSpel.t)] = st;
  try { persist(); } catch(e){}
}''',
    '''function lesStapAf(){
  if(!lesSpel) return;
  var st = brokLees(lesId(lesSpel.rij));
  st.stapMax = Math.max(st.stapMax || 0, lesSpel.stap);
  st.laatst = today();
  S.brok = S.brok || {};
  S.brok[lesId(lesSpel.rij)] = st;
  try { persist(); } catch(e){}
}''',
)

# ------------- 3. het keuzescherm: de tijden, en daaronder de patronen

rep(
    '''  if(!lesSpel){
    var open = conjOpenTijden();
    var w = tijdvormTopVerwar();''',
    '''  if(!lesSpel){
    var open = lesRijIds();
    var w = tijdvormTopVerwar();''',
)

rep(
    '''      "<div id='lesKeuze' style='display:flex; flex-direction:column; gap:8px; margin-top:8px'>" +
        open.map(function(t){
          var x = conjTiempo(t);
          var st = brokLees(lesId(t));
          var merk = lesKlaar(t) ? " \\u2713" : (st.stapMax ? " \\u00b7 " + ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/" + LES_STAPPEN.length : "");
          return "<button type='button' class='" + (t === aanbevolen ? "primary" : "ghost") + " les-t' data-t='" + t + "' style='min-height:52px'>" +
            (x ? x.es : t) + merk + "<br><span class='muted' style='font-weight:400; font-size:.78rem'>" + (x ? ct(x.nl, x.en) : "") + "</span></button>";
        }).join("") + "</div>" +''',
    '''      "<div id='lesKeuze' style='display:flex; flex-direction:column; gap:8px; margin-top:8px'>" +
        open.map(function(t, i){
          var r = lesRij(t);
          if(!r) return "";
          var st = brokLees(lesId(t));
          var merk = lesKlaar(t) ? " \\u2713" : (st.stapMax ? " \\u00b7 " + ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/" + LES_STAPPEN.length : "");
          /* v23.125: de patronen staan onder een eigen kopje. Niet als versiering: zonder die
             regel lijkt "la bota: e \\u2192 ie" een zesde tijd, en dat is het niet. */
          var eerstePatroon = !r.tijd && (i === 0 || (lesRij(open[i - 1]) || {}).tijd);
          return (eerstePatroon
            ? "<p class='muted' id='lesPatroonKop' style='margin:10px 0 0; font-size:.85rem'><b>" +
                ct("Binnen het presente", "Inside the present tense") + "</b> \\u00b7 " +
                ct("de 22 onregelmatige zijn zes patronen", "the 22 irregulars are six patterns") + "</p>"
            : "") +
            "<button type='button' class='" + (t === aanbevolen ? "primary" : "ghost") + " les-t' data-t='" + t + "' style='min-height:52px'>" +
            r.es + merk + "<br><span class='muted' style='font-weight:400; font-size:.78rem'>" +
            ct(r.nl, r.en) + (r.tijd ? "" : " \\u00b7 " + conjPatroonPool(t).length + " " + ct("werkwoorden", "verbs")) +
            "</span></button>";
        }).join("") + "</div>" +''',
)

rep(
    '''  var L = lesSpel, x = conjTiempo(L.t), v = L.v;''',
    '''  var L = lesSpel, x = lesRij(L.rij), v = L.v;''',
)

# de kop van een patroonles noemt niet de tijd maar de rij
rep(
    '''  var kop = "<h2>" + (x ? x.es : L.t) + " \\ud83d\\udcd6</h2>" +''',
    '''  var kop = "<h2>" + (x ? x.es : L.rij) + " \\ud83d\\udcd6</h2>" +''',
)

# stap 0 toont bij een tijdles een voorbeeldzin; bij een patroonles is dat het modelwerkwoord
rep(
    '''      "<p class='muted' style='margin:0'><b>" + x.vb + "</b> = " + ct(x.vbNl, x.vbEn) + "</p></div>" +
      "<p class='muted' style='font-size:.85rem'>" +
        ct("Er komt hier geen vraag. Lees het, dan gaan we het rijtje bekijken.",
           "There is no question here. Read it, then we look at the row.") + "</p>" +''',
    '''      "<p class='muted' style='margin:0'><b>" + x.vb + "</b> = " + ct(x.vbNl, x.vbEn) + "</p>" +
      (x.tijd ? "" :
        "<p class='muted' style='margin:8px 0 0; font-size:.85rem'>" +
          ct("In deze rij: ", "In this row: ") +
          conjPatroonPool(L.rij).map(function(w){ return w.inf; }).join(", ") + "</p>") + "</div>" +
      "<p class='muted' style='font-size:.85rem'>" +
        ct("Er komt hier geen vraag. Lees het, dan gaan we het rijtje bekijken.",
           "There is no question here. Read it, then we look at the row.") + "</p>" +''',
)

# ------------- 4. de tekst op het keuzescherm klopte niet meer
#
# Hier stond nog "in vijf stappen" terwijl LES_STAPPEN er sinds v23.118 zes heeft. Ik had die
# regel in v23.124 aan het script toegevoegd nadat ik het al gedraaid had, dus hij is nooit
# uitgevoerd en stond wel in het script: script en app liepen uiteen. Die regel is daar weggehaald
# en staat nu hier, waar hij ook echt draait. Vijfde keer dat een getal in tekst achterliep op de
# data, en de eerste keer dat mijn eigen patchscript loog over wat het gedaan had.

rep(
    '''      "<p class='muted'>" + ct("E\\u00e9n tijd tegelijk, in vijf stappen. De eerste twee stellen geen vraag: eerst zien, dan pas ophalen.",
                               "One tense at a time, in five steps. The first two ask nothing: see it first, retrieve it later.") + "</p>" +''',
    '''      "<p class='muted'>" + ct("E\\u00e9n rijtje tegelijk, in " + LES_STAPPEN.length + " stappen. De eerste twee stellen geen vraag: eerst zien, dan pas ophalen.",
                               "One row at a time, in " + LES_STAPPEN.length + " steps. The first two ask nothing: see it first, retrieve it later.") + "</p>" +''',
)

rep(
    '''    {v:"les",     id:"ftLes",     e:"\\ud83d\\udcd6", gram:true,  t:ct("De les","The lesson"), s:ct("E\\u00e9n tijd tegelijk, in " + LES_STAPPEN.length + " stappen. De eerste twee stellen geen vraag.","One tense at a time, in " + LES_STAPPEN.length + " steps. The first two ask nothing."), gezien:false, verse:function(){ lesSpel = null; }},''',
    '''    {v:"les",     id:"ftLes",     e:"\\ud83d\\udcd6", gram:true,  t:ct("De les","The lesson"), s:ct("E\\u00e9n rijtje tegelijk, in " + LES_STAPPEN.length + " stappen: een tijd, of \\u00e9\\u00e9n van de zes patronen achter de onregelmatige werkwoorden.","One row at a time, in " + LES_STAPPEN.length + " steps: a tense, or one of the six patterns behind the irregular verbs."), gezien:false, verse:function(){ lesSpel = null; }},''',
)

# ------------- 5. het modelwerkwoord van een patroon mag niet twee patronen hebben

# tener stond als eerste in schoen.ie, maar tener heeft ook een yo op -go. De les toonde daardoor
# "tengo" als voorbeeld bij een les over e -> ie, en dat is precies het tegenvoorbeeld. Het model
# is nu het eerste werkwoord dat in maar één rij staat: querer, poder, hacer, ser, pedir, saber.
rep(
    '''function conjPatroonPool(id){
  var pat = conjPatroonVan(id);
  if(!pat) return [];
  return VERBOS.filter(function(v){ return conjInPatroon(v, pat); });
}''',
    '''function conjPatroonPool(id){
  var pat = conjPatroonVan(id);
  if(!pat) return [];
  return VERBOS.filter(function(v){ return conjInPatroon(v, pat); });
}
/* In hoeveel rijen staat dit werkwoord? Drie staan er in twee (tener, venir, decir). */
function conjPatroonAantal(v){
  var n = 0;
  CONJ_PATRONEN.forEach(function(p){ if(conjInPatroon(v, p)) n++; });
  return n;
}
/* Het werkwoord waarmee de les dit patroon voordoet. Nooit een werkwoord dat in twee rijen staat:
   tener stond vooraan in schoen.ie, en dan doet een les over e \u2192 ie zijn voorbeeld met "tengo".
   Dat is het tegenvoorbeeld, niet het voorbeeld. */
function conjPatroonModel(id){
  var pool = conjPatroonPool(id);
  for(var i = 0; i < pool.length; i++) if(conjPatroonAantal(pool[i]) === 1) return pool[i];
  return pool[0] || null;
}''',
)

rep(
    '''  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = pool[0];''',
    '''  var pool = conjPatroonPool(id);
  if(!pool.length) return null;
  var v0 = conjPatroonModel(id);''',
)

# ------------- 6. de terugknop zei "Speeltuin", en daar kom je sinds v23.124 niet meer uit

# eerst de dertig knoppen omzetten, dan pas de functie erbij: andersom zou de vervanging in de
# functie zelf terechtkomen.
rep('''fx("terug")''', '''funTerugLabel()''', n=30)

rep(
    '''function funTerug(){''',
    '''/* v23.125: op elk grammatica-scherm stond "\u2190 Speeltuin" op de terugknop, terwijl je sinds
   v23.124 op de Grammatica-tab uitkomt. Een knop die de verkeerde plek belooft is erger dan een
   knop zonder tekst. \u00c9\u00e9n plek die het weet, dezelfde plek die de knop ook echt afhandelt. */
function funTerugLabel(){
  return isGramView(funView) ? ct("\u2190 Grammatica", "\u2190 Grammar") : fx("terug");
}
function funTerug(){''',
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
