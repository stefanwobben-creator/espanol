#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.31: de balk telt alles wat je hebt, en Vandaag wordt stiller.

Vier dingen van Stefan, na het zien van zijn eigen scherm.

1. De balk telde alleen A2: 50 van de 403, en het getal aan het eind van de balk was 50. Twee
   problemen in een. Het getal aan het eind hoort de noemer te zijn (dat is wat een balk aan het
   eind hoort te hebben, anders zegt de streep niets), en alles wat hij op A1 heeft opgebouwd stond
   nergens. Dat laatste is de vervelendste: op de dag dat je A1 haalt, wordt je balk leeg. Precies
   op het moment dat je iets bereikt.

   Nu telt de balk alle niveaus tot en met het jouwe bij elkaar op: 812 woorden op A1 en A2, met
   vast, onderweg en geschat samengeteld. Stefan: "ik kijk naar het totaal, de uitsplitsing maakt
   mij niet uit."

   Het streepje van je eerste peiling gaat weg. Dat markeerde waar je stond bij je eerste peiling
   op dit ene niveau; op een samengetelde schaal is er geen enkel eerste punt om te markeren en zou
   het streepje ergens staan zonder te kunnen uitleggen waarom. De zin eronder blijft wel, want die
   gaat over je huidige niveau en zegt precies wat hij meet.

2. De twee uitlegregels onder de tegels weg. Ze legden uit hoe de weging werkt en hoeveel
   weekmetingen er nog nodig zijn. Allebei waar, allebei niet iets waar je 's ochtends op wacht.
   De uitleg over de weging staat nog bij je cijfers, waar de uitsplitsing zelf ook staat.

3. Op de leskaart weg: het dagdoel-chipje en "Jouw moment".

   Het dagdoel stond twee keer op hetzelfde scherm: bovenin ("9/90 taco's") en nog eens als chipje.
   Dat is precies de fout die dit hele project aan het opruimen was.

   "Jouw moment ... wijzigen" is erger dan dubbel: die link doet niets. De momentkaart is in v22.1
   opgeheven, en sindsdien zet "wijzigen" alleen nog momentOpen op true, wat door niemand meer
   gelezen wordt. Een knop die niets doet is slechter dan geen knop, want je hebt hem al aangetikt
   voordat je het merkt. momentTekst() blijft bestaan voor wie hem ooit heeft ingevuld.

4. Het weekbericht van de wall af. Het komt terug als een rapport dat je een keer per week krijgt
   en dat je kunt delen; tot die tijd staat de knop nog gewoon onder Groepen, dus er verdwijnt geen
   functie, alleen een kaart die elke zondag op je dagscherm kwam staan.

Drie suites bij: pw-context (de noemer bij A2 is nu de samengetelde, en het dagdoel staat nog maar
op een plek), pw-samen (met een maatje staat er op Vandaag geen kaart meer, ook niet op zondag; die
test hing tot nu toe aan de dag waarop hij toevallig draaide). pw-a1vandaag hoeft niet: op A1 telt
de samentelling alleen A1, dus daar staat exact dezelfde zin als eerst.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
MAP_S = os.path.join(WORTEL, "test", "suites")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function voortgangSamen" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)
if 'var APP_VERSIE = "v23.30";' not in src:
    print("Deze index.html staat niet op v23.30. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ================================================================ 1. de samentelling
rep(
    """function voortgangCijfers(){""",
    """/* v23.31: alle niveaus tot en met het jouwe bij elkaar. Het staat als eigen functie naast
   voortgangCijfers en niet erin verstopt, want dit is de telling waar de balk op Vandaag op staat en
   die hoort net zo goed op een plek te wonen als de rest.

   Waarom optellen: de balk telde alleen het niveau waar je nu aan werkt. Dat betekent dat op de dag
   dat je A1 haalt, alles wat je daar hebt opgebouwd van je scherm verdwijnt en de balk bij nul
   opnieuw begint. Precies op het moment dat je iets bereikt hebt.

   De schatting van elk niveau telt mee zoals hij ook op zijn eigen niveau meetelde: als laag boven
   wat je hebt bewezen, nooit eronder. Een niveau dat je voorbij bent staat dus niet automatisch vol;
   er staat wat de peiling ervan zegt, en dat is eerlijker dan een streep die zichzelf volmaakt. */
function voortgangSamen(tel, niv){
  var uit = {noem:0, vast:0, actief:0, geschat:0, nivs:[]}, i, n, v, a, s;
  for(i = 0; i < NIV_NAAM.length; i++){
    n = NIV_NAAM[i];
    uit.nivs.push(n);
    uit.noem += PCIC_NOEMER[n] || 0;
    v = (tel.dek && tel.dek[n]) || 0;
    a = Math.max(v, (tel.dekw && tel.dekw[n]) || 0);
    s = null;
    try { s = niveauSchatting(n); } catch(e){ s = null; }
    uit.vast += v;
    uit.actief += a;
    uit.geschat += s ? Math.max(0, s.punt - a) : 0;
    if(n === niv) break;
  }
  uit.onderweg = Math.max(0, uit.actief - uit.vast);
  uit.ongezien = Math.max(0, uit.noem - uit.actief - uit.geschat);
  return uit;
}
// A1 en A2 samen heet "A1 en A2"; een niveau in je eentje heet gewoon zichzelf.
function samenNivTekst(nivs){
  if(nivs.length < 2) return nivs[0] || "";
  return nivs.slice(0, -1).join(", ") + (profLang() === "nl" ? " en " : " and ") + nivs[nivs.length - 1];
}
function voortgangCijfers(){""")

rep(
    """  return {
    dozen: dozen,
    kracht: Math.round(kr),
    niv: niv,
    noem: noem,""",
    """  return {
    dozen: dozen,
    kracht: Math.round(kr),
    niv: niv,
    noem: noem,
    samen: voortgangSamen(tel, niv),                // v23.31: alle niveaus tot en met het jouwe""")

# ================================================================ 2. de balk
rep(
    """function dagBasisRegelHtml(opt){
  var c = voortgangCijfers();
  var niv = c.niv;
  var n = c.noem || 390;
  var d = c.vast;
  var w = c.actief;
  var sch = c.schat, aanbod = null;
  try { aanbod = peilAanbod(); } catch(e){ aanbod = null; }
  if(w <= 0 && !sch && !aanbod) return "";
  var pctD = n ? Math.round(100 * d / n) : 0;
  var pctW = n ? Math.round(100 * (w - d) / n) : 0;""",
    """function dagBasisRegelHtml(opt){
  var c = voortgangCijfers();
  var niv = c.niv;
  /* v23.31: de getallen komen uit de samentelling, niet meer uit het ene niveau. Zie
     voortgangSamen(). c.vast en c.actief blijven bestaan voor de schermen die wel over een enkel
     niveau gaan; hier zou dat betekenen dat je A1 kwijtraakt op de dag dat je hem haalt. */
  var sm = c.samen;
  var n = sm.noem || 390;
  var d = sm.vast;
  var w = sm.actief;
  var sch = c.schat, aanbod = null;
  try { aanbod = peilAanbod(); } catch(e){ aanbod = null; }
  if(w <= 0 && !sch && !aanbod) return "";
  var pctD = n ? Math.round(100 * d / n) : 0;
  var pctW = n ? Math.round(100 * (w - d) / n) : 0;""")

rep(
    """  var kop = pctD, pctS = 0, merk = "", stap = "";
  if(sch){
    kop = Math.round(100 * sch.punt / n);
    pctS = Math.max(0, kop - pctD - pctW);
    var e0 = peilEerste(niv);
    if(e0) merk = "<i class='merk' style='left:"+Math.max(0, Math.min(99, Math.round(100 * e0.punt / n)))+"%'></i>";
    stap = dagBasisStapHtml(niv, sch, d);
  }""",
    """  /* v23.31: de geschatte laag komt uit de samentelling. Het streepje van je eerste peiling is weg:
     dat markeerde je beginpunt op een schaal van een niveau, en op een samengetelde schaal zou het
     ergens staan zonder te kunnen uitleggen waarom. De zin eronder blijft, want die gaat wel over
     je huidige niveau en zegt zelf welk niveau hij meet. */
  var pctS = n ? Math.round(100 * sm.geschat / n) : 0, merk = "", stap = "";
  if(sch) stap = dagBasisStapHtml(niv, sch, c.vast);""")

rep(
    """  var lgOnderweg = Math.max(0, w - d);
  var lgSchat = sch ? Math.max(0, sch.punt - w) : 0;
  var lgRest = Math.max(0, n - d - lgOnderweg - lgSchat);""",
    """  var lgOnderweg = sm.onderweg;
  var lgSchat = sm.geschat;
  var lgRest = sm.ongezien;
  var nivTxt = samenNivTekst(sm.nivs);""")

# Gevonden door naar het scherm te kijken en niet door te lezen: de geschatte laag zat wel in de
# balk maar viel uit de legenda, omdat die regel nog aan sch hing en dus aan de peiling van je
# huidige niveau. A2 is niet peilbaar (de app heeft 266 van de 403 sleutels, onder de drempel van
# 80 procent), dus sch is daar null, en dan telde de legenda 2 + 43 + 395 = 440 op terwijl er 812
# boven stond. Een legenda die niet optelt is erger dan geen legenda.
rep(
    """      (sch && lgSchat > 0 ? "<span><i class='vgDot vgSchat'></i><b>"+lgSchat+"</b> "+ct("geschat al gekend","estimated already known")+"</span>" : "")+""",
    """      (lgSchat > 0 ? "<span><i class='vgDot vgSchat'></i><b>"+lgSchat+"</b> "+ct("geschat al gekend","estimated already known")+"</span>" : "")+""")

rep(
    """    "<div class='boxrow' id='dagBasisBalk'><span style='width:34px'>"+niv+"</span>"+
      "<div class='bar duo'><div style='width:"+bD+"%'></div>"+
        "<div class='marge' style='width:"+bW+"%'></div>"+
        "<div class='schat' style='width:"+bS+"%'></div>"+merk+"</div>"+
      "<b style='width:44px; text-align:right'>"+w+"</b></div>"+""",
    """    /* Links waar de balk over gaat, rechts waar hij ophoudt. Daar stond tot v23.30 hetzelfde
       getal als in de kop, en dan is de streep maatloos: je ziet een balk die voor een derde vol
       staat en het getal ernaast zegt niet waarvan. */
    "<div class='boxrow' id='dagBasisBalk'><span style='width:52px'>"+
        (sm.nivs.length > 1 ? sm.nivs[0]+"-"+sm.nivs[sm.nivs.length-1] : niv)+"</span>"+
      "<div class='bar duo'><div style='width:"+bD+"%'></div>"+
        "<div class='marge' style='width:"+bW+"%'></div>"+
        "<div class='schat' style='width:"+bS+"%'></div>"+merk+"</div>"+
      "<b style='width:44px; text-align:right'>"+n+"</b></div>"+""")

rep(
    """    "<p class='muted' style='margin:5px 0 0; font-size:.8rem'>"+
      ct("van de "+n+" "+niv+"-woorden", "of the "+n+" "+niv+" words")+"</p>"+""",
    """    "<p class='muted' style='margin:5px 0 0; font-size:.8rem'>"+
      (sm.nivs.length > 1
        ? ct("van de "+n+" woorden op "+nivTxt, "of the "+n+" words in "+nivTxt)
        : ct("van de "+n+" "+niv+"-woorden", "of the "+n+" "+niv+" words"))+"</p>"+""")

# ================================================================ 3. de uitleg onder de tegels weg
rep(
    """  if(!tegels) return "";
  return "<div class='statgrid' style='margin-top:10px'>"+tegels+"</div>"+
    (c.geoefend > 0 ? "<p class='muted' style='margin:6px 0 0; font-size:.8rem'>"+
      /* Bewust zonder de woorden week en maand erin, ook al zijn dat de doosjes waar het over gaat.
         pw-a1vandaag bewaakt dat er op dit scherm geen enkele belofte over tijd staat, en die wacht
         houdt geen rekening met de bedoeling van een zin. Dat is maar goed ook: het is precies het
         soort zin waar per ongeluk een voorspelling in sluipt. De uitleg met de intervallen erin
         staat op je profiel, bij de uitsplitsing zelf. */
      ct("Hoe verder een woord in de doosjes staat, hoe zwaarder het meetelt. De uitsplitsing staat "+
         "bij je cijfers.",
         "The further a word sits in the boxes, the heavier it counts. The breakdown is with your "+
         "numbers.")+"</p>" : "")+
    (c.fout7.pct === null ? "" :
      "<p class='muted' style='margin:6px 0 0; font-size:.8rem'>"+
        ct(weekMetingZin(c.weken)+" Vanaf ongeveer "+MEET_WEKEN+" kan de app uit je eigen reeks "+
           "aflezen wat voor jou een goede stand is; tot die tijd staat er geen oordeel bij.",
           weekMetingZin(c.weken)+" From about "+MEET_WEKEN+" on the app can read from "+
           "your own series what a good rate is for you; until then no verdict is attached.")+"</p>");
}""",
    """  if(!tegels) return "";
  /* v23.31: hier stonden twee uitlegregels onder de tegels, over de weging en over hoeveel
     weekmetingen er nog nodig zijn. Allebei waar, allebei niets waar je 's ochtends op zit te
     wachten, en samen langer dan de cijfers zelf. Ze staan nog waar ze horen: bij de uitsplitsing
     op je profiel, waar de doosjes ook staan. */
  return "<div class='statgrid' style='margin-top:10px'>"+tegels+"</div>";
}""")

# ================================================================ 4. de leskaart
rep(
    """  if(rel.chipDoel) chipsHtml += chip(xp >= dagdoel(), ct("dagdoel ","daily goal ")+Math.min(xp,dagdoel())+"/"+dagdoel()+" "+xpw());""",
    """  /* v23.31: het dagdoel-chipje weg. Datzelfde getal staat bovenin het scherm al in de strook
     ("9/90 taco's"), en twee weergaven van een getal is de fout waar dit hele scherm mee bezig was.
     rel.chipDoel blijft bestaan; hij wordt op andere plekken gelezen. */""")

rep(
    """    // v19.58: je eigen afspraak, elke dag terug te zien op de plek waar je hem uitvoert. Een
    // implementatie-intentie werkt doordat het moment de handeling oproept, dus moet het moment
    // in beeld staan en niet weggestopt in instellingen.
    ((S.ritme && S.ritme.wanneer)
      ? "<p class='muted' style='margin:8px 0 0'>\U0001f4cc "+(afgesloten ? ct("Morgen: ","Tomorrow: ") : ct("Jouw moment: ","Your moment: "))+"<b>"+momentTekst()+"</b> · "+
        "<span id='momentRegel' style='text-decoration:underline; cursor:pointer'>"+ct("wijzigen","change")+"</span></p>"
      : "")+
    chipsHtml+"</div>";""",
    """    /* v23.31: "Jouw moment ... wijzigen" is weg. Niet omdat de gedachte niet klopt (een
       implementatie-intentie werkt doordat het moment de handeling oproept), maar omdat die link
       sinds v22.1 niets meer doet: de momentkaart is toen opgeheven en "wijzigen" zet alleen nog
       een vlaggetje dat niemand meer leest. Een knop die niets doet is slechter dan geen knop, want
       je hebt hem al aangetikt voordat je het merkt. momentTekst() blijft staan voor wie hem ooit
       heeft ingevuld. */
    chipsHtml+"</div>";""")

# ================================================================ 5. het weekbericht van de wall
rep(
    """  if(maatjeStuurMoment()) return maatjeStuurKaart();
  if(uitnodigMoment(2)) return uitnodigKaart(compact);""",
    """  /* v23.31: het weekbericht staat niet meer op Vandaag. Stefan wil het als rapport dat een keer
     per week binnenkomt en dat je kunt delen, niet als kaart die elke zondag tussen je les en je
     spelletjes gaat staan. maatjeStuurMoment() en maatjeStuurKaart() blijven bestaan, en onder
     Groepen staat "Stuur je week" gewoon nog: er verdwijnt geen functie, alleen een kaart. */
  if(uitnodigMoment(2)) return uitnodigKaart(compact);""")

rep('var APP_VERSIE = "v23.30";', 'var APP_VERSIE = "v23.31";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
with io.open(PAD_VER, "w", encoding="utf-8") as f:
    f.write("v23.31\n")
print("v23.31 toegepast op", PAD)


# ================================================================ 6. de suites
def patch_suite(naam, paren, sleutel):
    pad = os.path.join(MAP_S, naam)
    with io.open(pad, encoding="utf-8") as f:
        s = f.read()
    if sleutel in s:
        print("  " + naam + ": al bijgewerkt")
        return
    for anker, nieuw in paren:
        aantal = s.count(anker)
        assert aantal == 1, "%s: anker komt %d keer voor:\n%s" % (naam, aantal, anker[:160])
        s = s.replace(anker, nieuw, 1)
    with io.open(pad, "w", encoding="utf-8") as f:
        f.write(s)
    print("  " + naam + ": bijgewerkt")


patch_suite("pw-context.js", [
    ("""  const noemA2 = await page.evaluate(() => PCIC_NOEMER.A2);
  ok(noemA2 !== noemA1 && naA2.tekst.indexOf('van de ' + noemA2 + ' A2-woorden') !== -1,
     'en de noemer is die van A2, niet die van A1 (' + noemA2 + ' tegenover ' + noemA1 + ')');""",
     """  /* v23.31: de balk telt vanaf nu alle niveaus tot en met het jouwe bij elkaar op, dus op A2 is
     de noemer A1 plus A2. Wat deze test bewaakt is niet veranderd: de noemer moet zichtbaar zijn en
     hij moet meegroeien met het niveau, want anders meet de balk iets anders dan de lezer denkt.
     Erbij: wat je op A1 hebt opgebouwd mag niet van het scherm verdwijnen op de dag dat je A1
     haalt, en dat is precies wat een noemer van 403 zou betekenen. */
  const samenA2 = await page.evaluate(() => PCIC_NOEMER.A1 + PCIC_NOEMER.A2);
  ok(samenA2 !== noemA1 && naA2.tekst.indexOf('van de ' + samenA2 + ' woorden op A1 en A2') !== -1,
     'de noemer is A1 en A2 samen (' + samenA2 + ' tegenover ' + noemA1 + ' op A1)');
  ok(naA2.tekst.indexOf('403') === -1,
     'en niet alleen A2: het losse niveaugetal staat er niet meer');"""),

    ("""  ok(eenDag.ritme && /dagdoel/i.test(eenDag.tekst), 'het dagdoel-chipje staat er wel, want daar staat iets in');""",
     """  /* v23.31: het dagdoel-chipje is weg van de leskaart. Het stond twee keer op hetzelfde scherm,
     want bovenin staat dezelfde stand al in de strook. Deze test bewaakt vanaf nu dat het bij die
     ene plek blijft: eentje op het dagscherm, niet nul en niet twee. */
  const doelPlekken = await page.evaluate(() => ({
    lijst: /dagdoel/i.test((document.getElementById('lessonList') || {}).innerText || ''),
    kop: ((document.getElementById('goalTxt') || {}).innerText || '')
  }));
  ok(!doelPlekken.lijst, 'het dagdoel-chipje staat niet meer op de leskaart');
  ok(/\\d+\\/\\d+/.test(doelPlekken.kop),
     'en de stand staat nog wel bovenin, op die ene plek ("' + doelPlekken.kop + '")');"""),
], "v23.31")

patch_suite("pw-tellersweg.js", [
    ("""  // en het chipje voor het dagdoel komt terug zodra er iets in staat
  const metDoel = await page.evaluate(() => {
    S.xp[today()] = (S.xp[today()] || 0) + 5;
    show('lessen');
    const el = document.querySelector('.ritme');
    return el ? el.innerText : '';
  });
  ok(/dagdoel|daily goal/i.test(metDoel), 'zodra je vandaag punten hebt staat het dagdoel er wel ("' + metDoel.replace(/\\n/g, ' | ') + '")');""",
     """  /* v23.31: het dagdoel-chipje op de leskaart is weg. Niet omdat een saldo terugkwam (daar gaat
     deze suite over en dat blijft zo), maar omdat dezelfde stand bovenin al in de strook staat en
     twee weergaven van een getal de fout is die dit scherm aan het opruimen was. Wat hier vanaf nu
     vastligt is precies dat: de stand staat er, en op een plek. */
  const metDoel = await page.evaluate(() => {
    S.xp[today()] = (S.xp[today()] || 0) + 5;
    show('lessen');
    const el = document.querySelector('.ritme');
    return { ritme: el ? el.innerText : '',
             kop: (document.getElementById('goalTxt') || {}).innerText || '' };
  });
  ok(/\\d+\\/\\d+/.test(metDoel.kop),
    'zodra je vandaag punten hebt staat je stand bovenin ("' + metDoel.kop + '")');
  ok(!/dagdoel|daily goal/i.test(metDoel.ritme),
    'en niet ook nog eens als chipje op de leskaart ("' + metDoel.ritme.replace(/\\n/g, ' | ') + '")');"""),
], "v23.31")

patch_suite("pw-peiling.js", [
    ("""      knopKaart: knop && knop.closest('.card') ? (knop.closest('.card').id || '') : '',
      tekst: kaart ? kaart.innerText.replace(/\\s+/g, ' ') : ''""",
     """      knopKaart: knop && knop.closest('.card') ? (knop.closest('.card').id || '') : '',
      // v23.31: de kop en het getal aan het eind van de balk zijn twee verschillende dingen
      // geworden. De kop is wat je actief bijhoudt, het getal rechts is de noemer.
      kopGroot: kaart ? ((kaart.querySelector('.vgGroot') || {}).innerText || '') : '',
      tekst: kaart ? kaart.innerText.replace(/\\s+/g, ' ') : ''"""),

    ("""  ok(bal.merk === 1, 'en een streepje waar je eerste peiling stond (' + bal.merk + ')');
  const kop = parseInt(bal.kop, 10);""",
     """  /* v23.31: het streepje van je eerste peiling is weg. Het stond op een schaal van een niveau, en
     de balk telt nu alle niveaus tot en met het jouwe bij elkaar op; op die schaal is er geen enkel
     beginpunt om te markeren. Wat het streepje deed (laten zien dat je vooruit bent gegaan sinds je
     eerste peiling) doet de zin eronder, en die wordt verderop in deze suite gecontroleerd. */
  ok(bal.merk === 0, 'geen streepje meer op de samengetelde balk (' + bal.merk + ')');
  const kop = parseInt(bal.kopGroot, 10);"""),

    ("""  const opweg = await page.evaluate(() => {
    const t = voortgangTellers();
    return Math.max((t.dekw && t.dekw.A1) || 0, (t.dek && t.dek.A1) || 0);
  });
  ok(kop === opweg, 'de kop is geen percentage meer maar wat je actief bijhoudt (' + bal.kop + ' vs ' + opweg + ')');""",
     """  /* v23.31: het scherm mag geen eigen sommetje maken. Dus wordt hier niet nagerekend wat de kop
     hoort te zijn, maar vergeleken met wat voortgangCijfers().samen zegt: dat is de enige plek waar
     dit getal wordt uitgerekend, en als het scherm daarvan afwijkt is er een tweede telling bij
     gekomen. Precies waar dit hele hoofdstuk over ging. */
  const sm = await page.evaluate(() => JSON.parse(JSON.stringify(voortgangCijfers().samen)));
  const opweg = sm.actief;
  ok(kop === opweg, 'de kop is wat je actief bijhoudt, uit voortgangCijfers (' + bal.kopGroot + ' vs ' + opweg + ')');
  ok(parseInt(bal.kop, 10) === sm.noem,
     'en het getal aan het eind van de balk is de noemer (' + bal.kop + ' vs ' + sm.noem + ')');
  ok(sm.vast + sm.onderweg + sm.geschat + sm.ongezien === sm.noem,
     'de vier lagen tellen op tot de noemer (' + [sm.vast, sm.onderweg, sm.geschat, sm.ongezien].join('+') + ' = ' + sm.noem + ')');"""),

    ("""  ok(met.merk === 1, 'en het streepje verschuift mee naar het beginpunt');""",
     """  ok(met.tekst.indexOf('Sinds je eerste peiling') < met.tekst.indexOf('Alle cijfers') ||
     met.tekst.indexOf('Alle cijfers') === -1,
    'en de stapzin staat in dezelfde kaart als de balk, niet in een blok eronder');"""),
], "v23.31")

patch_suite("pw-samen.js", [
    ("""  ok(volgorde.metMaatje === (volgorde.stuurMoment ? 'maatjeKaart' : 'geen'),
    'met een maatje verdwijnt de werving; het weekbericht staat er alleen zo/ma (' + volgorde.metMaatje + ')');""",
     """  /* v23.31: het weekbericht staat niet meer op Vandaag; het komt terug als rapport dat je een
     keer per week krijgt en kunt delen. Met een maatje staat er dus geen kaart meer, ook niet op
     zondag. Deze test hing tot nu toe aan de dag waarop hij toevallig draaide (op zondag verwachtte
     hij een kaart, doordeweeks niet); dat is nu weg en dat is winst op zich. */
  ok(volgorde.metMaatje === 'geen',
    'met een maatje staat er op Vandaag geen kaart meer, ook niet op zondag (' + volgorde.metMaatje + ')');"""),
], "v23.31")
