#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.108: elke tijd heeft een Nederlandse naam, en die naam staat op precies één plek.

## Waar dit vandaan komt

Stefan, 15 augustus: "ik weet nog niet eens hoe de normale vorm heet omdat we die vertalingen
nooit leren of die definities maar een keer worden getoond."

Nagemeten, en het klopte:

  - conjTiempoLabel() gaf alleen Spaans terug. Geen ct(), geen Nederlands, nergens.
  - de spiekbrief "De tijden, vertaald naar Nederlandse termen" noemde presente, perfecto en
    indefinido. Imperfecto en subjuntivo stonden er niet in, terwijl je in de Conjugador wel
    tot fase 12 (subjuntivo) kunt komen.
  - CONJ_FASES noemt de fasen "verleden tijd 1", "hoe het was" en "de subjuntivo". Dat zijn
    bijnamen, geen namen. Je ziet "Fase 12/13 · de subjuntivo" en weet nog steeds niet welke
    tijd dat is, niet in het Spaans en niet in het Nederlands.

Drie plekken die alle drie hetzelfde feit opschrijven, en alle drie iets anders. Dat is precies
de architectuurregel van 15 augustus: staat een feit in de data, dan schrijft geen enkele
codeplek dat feit opnieuw.

## Waarom dit de eerste bouwronde is

Uit het ontwerpadvies: dit is de goedkoopste stap met het minste risico, en hij zit in laag A
van het drielagenmodel (de naam). Je kunt geen rijtje leren dat geen naam heeft, en je kunt niet
kiezen tussen twee tijden waarvan je er één niet kunt benoemen.

Bovendien is het de eerste plek waar regel R4 uit het advies landt: zet Nederlands en Spaans
expliciet naast elkaar. Bij McManus & Marsden was dat benoemde contrast de werkzame stof, niet
de oefening zelf. Vandaar de nieuwe alinea onder de tabel: het Nederlands heeft één verleden
tijd, het Spaans heeft er drie.

## Wat er verandert

  CONJ_TIEMPOS        nieuwe databron: id, Spaanse naam, Nederlandse naam, Engelse naam en een
                      voorbeeld met aprender. Vijf tijden.
  conjTiempoLabel()   leest nu uit die bron in plaats van zelf vijf namen op te schrijven
  conjTiempoNaam()    nieuw: "pretérito imperfecto (onvoltooid verleden tijd, achtergrond)"
  Conjugador          de vraagkaart toont beide namen in plaats van alleen het Spaans
  fasekaart           toont welke tijd de fase oefent, onder de bijnaam
  spiekbrief          de tabel wordt uit CONJ_TIEMPOS gebouwd, dus alle vijf de tijden staan
                      erin en ze kunnen niet meer uit elkaar lopen

Dit is één variabele: de naamgeving. Er verandert niets aan wat er geoefend wordt, aan de
volgorde, aan de SRS of aan de meting. Zo blijft de volgende ronde vergelijkbaar.

## Wat dit expres NIET doet

De uitleg over wanneer je welke tijd gebruikt blijft staan waar hij staat (eigen spiekkaarten).
Dit gaat alleen over hoe de dingen heten.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.108"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.108" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))
# versie.txt mag alleen vooruit. Zonder deze regel zet een oudere patch die je per ongeluk nog
# eens draait het versienummer terug, en dan denkt de app dat hij ouder is dan hij is.
DOE_VER = huidig_ver != NIEUW and (DOE_APP or _num(huidig_ver) < _num(NIEUW))

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    # Staat de app al op deze versie, dan is er niets te vervangen en loopt hoogstens versie.txt
    # nog achter (dat gebeurt als de avondrun er tussendoor een nieuwer nummer in heeft gezet).
    # Zonder deze regel valt een oudere patch om zodra er een nieuwere overheen is gegaan.
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ------------------------------------------------------- 1. de databron zelf
A_CHEAT = "var CHEATSHEET = ["
N_CHEAT = u'''/* ================= DE TIJDEN (v23.108) =================

   Eén bron voor de namen van de tijden. Hiervoor stonden ze op drie plekken: conjTiempoLabel()
   (alleen Spaans), de spiekbrieftabel (drie van de vijf) en CONJ_FASES (bijnamen als "verleden
   tijd 1"). Stefan kon de imperfecto daardoor nergens bij naam leren kennen, ook niet nadat de
   vorm er in v23.107 bij kwam.

   Architectuurregel 15 augustus: staat een feit in de data, dan schrijft geen enkele codeplek
   dat feit opnieuw. Een zesde tijd toevoegen is één regel hieronder; de spiekbrief, de
   Conjugador en de fasekaart volgen dan vanzelf.

   nl/en zijn met opzet niet alleen de schoolnaam. "onvoltooid verleden tijd" alleen zou voor
   indefinido en imperfecto twee keer hetzelfde opleveren, en dat is nou juist het probleem dat
   deze app moet oplossen: het Nederlands heeft één verleden tijd waar het Spaans er drie heeft. */
var CONJ_TIEMPOS = [
  {id:"presente",   es:"presente",
   nl:"tegenwoordige tijd (tt)",                    en:"present tense",
   vb:"aprendo",      vbNl:"ik leer",                     vbEn:"I learn"},
  {id:"perfecto",   es:"pret\\u00e9rito perfecto",
   nl:"voltooid tegenwoordige tijd (vtt)",          en:"present perfect",
   vb:"he aprendido", vbNl:"ik heb geleerd",              vbEn:"I have learned"},
  {id:"indefinido", es:"pret\\u00e9rito indefinido",
   nl:"verleden tijd, afgesloten",                  en:"simple past, finished",
   vb:"aprend\\u00ed",  vbNl:"ik leerde (toen, \\u00e9\\u00e9n keer)",    vbEn:"I learned (once, back then)"},
  {id:"imperfecto", es:"pret\\u00e9rito imperfecto",
   nl:"verleden tijd, achtergrond",                 en:"past continuous / used to",
   vb:"aprend\\u00eda", vbNl:"ik leerde (steeds, gewoonlijk)", vbEn:"I was learning / I used to learn"},
  {id:"subjuntivo", es:"presente de subjuntivo",
   nl:"aanvoegende wijs",                           en:"present subjunctive",
   vb:"aprenda",      vbNl:"(dat) ik leer",               vbEn:"(that) I learn"}
];
function conjTiempo(t){
  for(var i=0; i<CONJ_TIEMPOS.length; i++) if(CONJ_TIEMPOS[i].id === t) return CONJ_TIEMPOS[i];
  return null;
}
/* de tabel in de spiekbrief wordt hieruit gebouwd. Losse <table> in de spiekbrieftekst zou een
   tweede lijst met tijdnamen zijn, en dat is precies hoe de imperfecto er eerder uit viel. */
function tiemposTabelHtml(lang){
  var kop = lang === "nl"
    ? "<tr><th>Nederlands</th><th>Spaans</th><th>Voorbeeld</th></tr>"
    : "<tr><th>English</th><th>Spanish</th><th>Example</th></tr>";
  var rijen = CONJ_TIEMPOS.map(function(t){
    var naam = lang === "nl" ? t.nl : t.en;
    var vb   = lang === "nl" ? t.vbNl : t.vbEn;
    return "<tr><td>"+naam+": "+vb+"</td><td>"+t.es+"</td><td><b>"+t.vb+"</b></td></tr>";
  }).join("");
  return "<table>"+kop+rijen+"</table>";
}

var CHEATSHEET = ['''
rep(A_CHEAT, N_CHEAT)

# ------------------------------------------- 2. de spiekkaart leest uit de bron
A_KAART = (u''' {"titel":"De tijden, vertaald naar Nederlandse termen","titelEn":"Verb tenses, explained in familiar English terms",'''
           u'''"html":"<p>De namen die je op school kende, naast de Spaanse:</p><table><tr><th>Nederlands</th><th>Spaans</th><th>Voorbeeld</th></tr>'''
           u'''<tr><td>tegenwoordige tijd (tt): ik leer</td><td>presente</td><td><b>aprendo</b></td></tr>'''
           u'''<tr><td>voltooid tegenwoordige tijd (vtt): ik heb geleerd</td><td>pret\u00e9rito <b>perfecto</b></td><td><b>he aprendido</b></td></tr>'''
           u'''<tr><td>onvoltooid verleden tijd (ovt): ik leerde</td><td>pret\u00e9rito <b>indefinido</b></td><td><b>aprend\u00ed</b></td></tr></table>'''
           u'''<p><b>De keuzeregel:</b>''')
N_KAART = (u''' {"titel":"De tijden, vertaald naar Nederlandse termen","titelEn":"Verb tenses, explained in familiar English terms",'''
           u'''"html":"<p>De namen die je op school kende, naast de Spaanse:</p><!--TIEMPOS-->'''
           u'''<p><b>Let op het verschil met het Nederlands:</b> wij hebben \u00e9\u00e9n verleden tijd (\u201eik leerde\u201d), '''
           u'''het Spaans heeft er drie. Je gevoel voor het Nederlands helpt je hier dus niet: je moet per zin iets kiezen '''
           u'''wat het Nederlands nooit van je vraagt. Daar gaan de losse kaarten hieronder over.</p>'''
           u'''<p><b>De keuzeregel:</b>''')
rep(A_KAART, N_KAART)

A_KAART_EN = (u'''"htmlEn":"<p>The tense names you probably remember from school, next to the Spanish ones:</p>'''
              u'''<table><tr><th>English</th><th>Spanish</th><th>Example</th></tr>'''
              u'''<tr><td>present tense: I learn</td><td>presente</td><td><b>aprendo</b></td></tr>'''
              u'''<tr><td>present perfect: I have learned</td><td>pret\u00e9rito <b>perfecto</b></td><td><b>he aprendido</b></td></tr>'''
              u'''<tr><td>simple past: I learned</td><td>pret\u00e9rito <b>indefinido</b></td><td><b>aprend\u00ed</b></td></tr></table>'''
              u'''<p><b>The rule for choosing:</b>''')
N_KAART_EN = (u'''"htmlEn":"<p>The tense names you probably remember from school, next to the Spanish ones:</p><!--TIEMPOS-->'''
              u'''<p><b>Note how this differs from English:</b> English splits the past three ways too, but not along the same lines. '''
              u'''<i>Aprend\u00ed</i> covers \u201cI learned\u201d, and <i>aprend\u00eda</i> covers both \u201cI was learning\u201d and \u201cI used to learn\u201d. '''
              u'''The mapping is not one to one, so translating word for word will mislead you.</p>'''
              u'''<p><b>The rule for choosing:</b>''')
rep(A_KAART_EN, N_KAART_EN)

# de vervanger draait na de arraydefinitie: <!--TIEMPOS--> wordt de gebouwde tabel.
# Generiek over alle kaarten, zodat de kaart niet op indexnummer vastgepind zit.
A_NA_CHEAT = u'''/* ================= BEGINNERSTRACK ================= */'''
N_NA_CHEAT = u'''/* v23.108: de tijdentabel invullen. Dit draait één keer, direct na de definitie, en werkt
   op elke kaart die de markering bevat (nu één, in CHEATSHEET). Zo staat de spiekbrieftekst nog
   steeds gewoon in de data en staan de tijdnamen toch maar op één plek. */
(function(){
  [typeof CHEATSHEET !== "undefined" ? CHEATSHEET : [],
   typeof B_CHEATSHEET !== "undefined" ? B_CHEATSHEET : []].forEach(function(lijst){
    (lijst || []).forEach(function(c){
      if(c && c.html   && c.html.indexOf("<!--TIEMPOS-->")   !== -1) c.html   = c.html.replace("<!--TIEMPOS-->", tiemposTabelHtml("nl"));
      if(c && c.htmlEn && c.htmlEn.indexOf("<!--TIEMPOS-->") !== -1) c.htmlEn = c.htmlEn.replace("<!--TIEMPOS-->", tiemposTabelHtml("en"));
    });
  });
})();

/* ================= BEGINNERSTRACK ================= */'''
rep(A_NA_CHEAT, N_NA_CHEAT)

# ------------------------- 3. de oude naamlijst weg, want dat is dezelfde lijst
# Er stond al een CONJ_TIEMPOS: een kale lijst met tijd-ids, inclusief "mix". Die werd nergens
# gelezen (nagemeten: nul aanroepen), terwijl conjTiempoActief() vlak eronder dezelfde lijst nóg
# een keer opschrijft. Twee dode kopieën van hetzelfde feit, precies waar de architectuurregel
# over gaat. De naam gaat naar de nieuwe tabel en conjTiempoActief leest daaruit.
A_OUDE_LIJST = u'''var CONJ_TIEMPOS = ["presente","indefinido","imperfecto","perfecto","subjuntivo","mix"];
function conjTiempoKeuze(){ return conjFaseNu().tijd; }
function conjTiempoActief(){
  var k = conjTiempoKeuze();
  if(k !== "mix") return k;
  // v23.107: de imperfecto doet mee in de mix, want die fase is de eindstand: niet elke vorm los
  // kennen maar ze uit elkaar houden. En dat is precies waar indefinido tegenover imperfecto zit.
  var opts = ["presente","indefinido","imperfecto","perfecto","subjuntivo"];
  return opts[Math.floor(Math.random()*opts.length)];
}'''
N_OUDE_LIJST = u'''/* v23.108: hier stond een tweede CONJ_TIEMPOS (een kale lijst met ids) die nergens gelezen werd,
   en daaronder schreef conjTiempoActief dezelfde lijst nóg een keer op. De namen staan nu in de
   tabel bovenin het bestand; deze twee functies lezen daaruit. Een zesde tijd toevoegen doet
   vanaf nu vanzelf mee in de mix. */
function conjTiempoKeuze(){ return conjFaseNu().tijd; }
function conjTiempoActief(){
  var k = conjTiempoKeuze();
  if(k !== "mix") return k;
  // v23.107: de imperfecto doet mee in de mix, want die fase is de eindstand: niet elke vorm los
  // kennen maar ze uit elkaar houden. En dat is precies waar indefinido tegenover imperfecto zit.
  var opts = CONJ_TIEMPOS.map(function(t){ return t.id; });
  return opts[Math.floor(Math.random()*opts.length)];
}'''
rep(A_OUDE_LIJST, N_OUDE_LIJST)

# --------------------------------------------- 4. conjTiempoLabel leest de bron
A_LABEL = u'''function conjTiempoLabel(t){
  if(t === "subjuntivo") return "presente de subjuntivo";
  if(t === "indefinido") return "pret\\u00e9rito indefinido";
  if(t === "imperfecto") return "pret\\u00e9rito imperfecto";   // v23.107
  if(t === "perfecto") return "pret\\u00e9rito perfecto";
  return "presente";
}'''
N_LABEL = u'''/* v23.108: leest uit CONJ_TIEMPOS in plaats van de namen zelf op te schrijven. De terugval op
   "presente" blijft, want conjTiempoLabel wordt ook aangeroepen met undefined en met "mix". */
function conjTiempoLabel(t){
  var x = conjTiempo(t);
  return x ? x.es : "presente";
}
/* de volledige naam: Spaans plus de naam in de taal van de gebruiker. Geeft "" terug voor een
   tijd die niet bestaat (zoals "mix"), zodat de aanroeper hem kan weglaten in plaats van iets
   onwaars te tonen. */
function conjTiempoNaam(t){
  var x = conjTiempo(t);
  return x ? x.es + " (" + ct(x.nl, x.en) + ")" : "";
}'''
rep(A_LABEL, N_LABEL)

# ------------------------------------------ 5. de vraagkaart van de Conjugador
A_VRAAG = u'''      "<p class='muted' style='margin:0'><b>"+conjTiempoLabel(tR)+"</b></p>"+'''
N_VRAAG = u'''      /* id bewust NIET cjTiempo: dat was de id van de oude losse tijdknoppenrij, en pw-conjfase
         bewaakt dat die weg blijft ("de fase is de tijdkeuze"). Die check hoort te blijven staan. */
      "<p class='muted' style='margin:0' id='cjTiempoEs'><b>"+conjTiempoLabel(tR)+"</b></p>"+
      "<p class='muted' style='margin:0; font-size:0.82rem' id='cjTiempoNl'>"+ct(conjTiempo(tR) ? conjTiempo(tR).nl : "", conjTiempo(tR) ? conjTiempo(tR).en : "")+"</p>"+'''
rep(A_VRAAG, N_VRAAG)

# --------------------------------------------------- 6. de fasekaart noemt de tijd
A_FASEKOP = u'''    "<p class='muted' id='cjFaseKop' style='margin:0 0 2px; font-size:0.85rem'><b>"+ct("Fase ","Phase ")+(i+1)+"/"+CONJ_FASES.length+" \\u00b7 "+ct(f.nl, f.en)+"</b></p>"+
    "<p class='muted' id='cjFaseUit' style='margin:0 0 6px; font-size:0.85rem'>"+ct(f.uitNl, f.uitEn)+"</p>";'''
N_FASEKOP = u'''    "<p class='muted' id='cjFaseKop' style='margin:0 0 2px; font-size:0.85rem'><b>"+ct("Fase ","Phase ")+(i+1)+"/"+CONJ_FASES.length+" \\u00b7 "+ct(f.nl, f.en)+"</b></p>"+
    /* v23.108: de fasenaam is een bijnaam ("verleden tijd 1", "hoe het was"). Welke tijd je hier
       oefent stond nergens. De mix-fase heeft geen tijd, dus dan blijft deze regel leeg. */
    (conjTiempoNaam(f.tijd) ? "<p class='muted' id='cjFaseTijd' style='margin:0 0 2px; font-size:0.8rem'>"+conjTiempoNaam(f.tijd)+"</p>" : "")+
    "<p class='muted' id='cjFaseUit' style='margin:0 0 6px; font-size:0.85rem'>"+ct(f.uitNl, f.uitEn)+"</p>";'''
rep(A_FASEKOP, N_FASEKOP)

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
