#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.33: de tapas en de dansen staan waar je ze geeft.

Stefan, na het scherm te hebben opengeslagen: "de tapas in de vitrine direct integreren bovenin waar
nu geef tapas staat, en daaronder ook direct de dansjes. Kijk ceremonie terug kan weg."

Dat draait een besluit van v19.70 om, en dat mag: toen zijn de verzamelingen bewust weggehaald bij
Chispa zelf, omdat er tussen haar voeten een kledingkast, een kamer, een tapateller en een
straattaalles stonden. Dat was terecht. Maar het kind ging mee met het badwater: sindsdien staat de
handeling (een tapa geven, laten dansen) twee kaarten lager dan het dier waar hij over gaat, en op
haar eigen kaart staat een knop "Geef een tapa" die een willekeurige tapa geeft terwijl je er een
mag kiezen.

Nu staan de twee rijen direct onder haar, en de knop "Geef een tapa" is weg. Niet omdat er een
functie verdwijnt maar omdat hij er twee waren: sinds v19.81 is aantikken al geven, en een knop
ernaast die hetzelfde doet maar zonder keuze is de slechtere van de twee.

De vitrinekaart is daarmee leeg en verdwijnt. De plaquette (El Gran Menú) verhuist mee naar boven,
zonder de knop "Kijk de ceremonie terug".

En een fout die op zijn scherm stond en die niemand had gezien: "Chispa proefde 29 van de 18 tapas".
Precies dezelfde fout als de luisterteller van v22.10: S.tapaMenu bewaart ids, de lijst TAPAS is
sindsdien veranderd, en de teller telde alles wat er ooit in kwam. Nu telt hij alleen ids die nu nog
een tapa zijn. Niet met een migratie: dan zou een oude sleutel bij de een wel en bij de ander niet
verdwijnen, afhankelijk van wanneer hij de app opent.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
MAP_S = os.path.join(WORTEL, "test", "suites")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function chVerzamelHtml" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)
if 'var APP_VERSIE = "v23.32";' not in src:
    print("Deze index.html staat niet op v23.32. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de teller klopt weer
rep(
    """function tapaMenuState(){ if(!S.tapaMenu) S.tapaMenu = []; return S.tapaMenu; }""",
    """function tapaMenuState(){ if(!S.tapaMenu) S.tapaMenu = []; return S.tapaMenu; }
/* v23.33: "Chispa proefde 29 van de 18 tapas". Dezelfde fout als de luisterteller van v22.10:
   S.tapaMenu bewaart ids, TAPAS is sinds die ids veranderd, en de teller telde alles wat er ooit in
   kwam. Een sleutel die geen tapa meer is telt niet mee. Bewust geen migratie die S.tapaMenu
   opschoont: dan hangt het van het moment van openen af of iemands geschiedenis nog compleet is, en
   dit is een teller, geen archief. */
function tapaMenuGehad(){
  var m = tapaMenuState(), bekend = {}, i, n = 0;
  for(i = 0; i < TAPAS.length; i++) bekend[TAPAS[i].id] = 1;
  for(i = 0; i < m.length; i++) if(bekend[m[i]]) n++;
  return n;
}""")

# ---------------------------------------------------------------- 2. de twee rijen als eigen blok
rep(
    """function renderVitrine(){
  var el = document.getElementById("vitrineCard");
  if(!el) return;
  var tapaHoy = tapaVolgende();
  var tapaGehad = tapaMenuState().length;
  var tapaKlaar = tapaAllemaal();
  var bd = bailePorDia();
  var bekend = baileState();
  var bailHtml = "";
  BAILES.forEach(function(b){
    bailHtml += "<button class='bailechip"+(b.id===bd.id?" hoy":"")+(bekend.indexOf(b.id)>=0?" gehad":"")+"' data-baile='"+b.id+"' title='"+b.land+"'>"+
      b.e+" <span class='es'>"+b.es+"</span></button>";
  });
  el.innerHTML = "<h2>"+ct("De vitrine","The display case")+" \\ud83c\\udf7d\\ufe0f</h2>"+
    "<p class='muted' style='margin:0 0 12px'>"+ct("Twee verzamelingen die alleen maar kunnen groeien. Wegblijven kost je hier niets.","Two collections that can only grow. Staying away never costs you anything here.")+"</p>"+
    "<div class='vitrinevak'>"+
      (S.tapaFinale ? "<div class='plaquette' id='tapaPlaquette'><b><span class='es'>El Gran Men\\u00fa</span></b>"+
        "<span>"+ct("alle "+TAPAS.length+" tapas geproefd \\u00b7 ","all "+TAPAS.length+" tapas tasted \\u00b7 ")+S.tapaFinale+"</span>"+
        "<button class='ghost' id='btnFinaleTerug'>"+ct("Kijk de ceremonie terug","Watch the ceremony again")+"</button></div>" : "")+
      "<p class='bailehoy' id='tapaHoy'><span class='es'>"+(tapaKlaar ? "La tapa del d\\u00eda" : "La pr\\u00f3xima tapa")+"</span>: "+tapaHoy.e+" <span class='es'>"+tapaHoy.es+"</span> <span class='muted'>\\u00b7 "+ct(tapaHoy.nl, tapaHoy.en)+
        (tapaKlaar ? "" : " \\u00b7 "+ct("na je volgende les","after your next session"))+"</span></p>"+
      tapaMenuHtml()+
      "<p class='zorglabel' id='tapaTel'>"+ct("Chispa proefde "+tapaGehad+" van de "+TAPAS.length+" tapas \\u00b7 tik er een aan om hem te geven","Chispa has tasted "+tapaGehad+" of "+TAPAS.length+" tapas \\u00b7 tap one to feed it to her")+"</p>"+
    "</div>"+
    "<div class='vitrinevak'>"+
      "<p class='bailehoy' id='baileHoy'><span class='es'>El baile del d\\u00eda</span>: <span class='es'>"+bd.es+"</span> <span class='muted'>\\u00b7 "+bd.land+"</span></p>"+
      "<div class='bailerij' id='baileRij'>"+bailHtml+"</div>"+
      "<p class='zorglabel' id='baileTel'>"+ct("Je kent "+bekend.length+" van de "+BAILES.length+" dansen \\u00b7 tik er een aan","You know "+bekend.length+" of "+BAILES.length+" dances \\u00b7 tap one")+
        " <button class='muziekchip"+(S.chispaStil?" stil":"")+"' id='btnChMuziek' type='button' title='"+chMuziekTitel()+"'>"+chMuziekLabel()+"</button></p>"+
    "</div>";
  tapaMenuWire(el);
  var bt = document.getElementById("btnFinaleTerug");
  if(bt) bt.onclick = function(){ tapaFinaleTonen(); };
  el.querySelectorAll("button.bailechip").forEach(function(bb){""",
    """/* v23.33: de twee verzamelingen staan nu bij Chispa zelf, want daar geef je ze aan. Ze staan hier
   als eigen functie zodat er precies één versie van is: hij werd uit de vitrinekaart gehaald en niet
   overgeschreven. De plaquette gaat mee, zonder de knop "Kijk de ceremonie terug" (Stefans verzoek);
   de plaquette zelf blijft, want die is het bewijs en niet de herhaling. */
function chVerzamelHtml(){
  var tapaHoy = tapaVolgende();
  var tapaGehad = tapaMenuGehad();
  var tapaKlaar = tapaAllemaal();
  var bd = bailePorDia();
  var bekend = baileState();
  var bailHtml = "";
  BAILES.forEach(function(b){
    bailHtml += "<button class='bailechip"+(b.id===bd.id?" hoy":"")+(bekend.indexOf(b.id)>=0?" gehad":"")+"' data-baile='"+b.id+"' title='"+b.land+"'>"+
      b.e+" <span class='es'>"+b.es+"</span></button>";
  });
  return "<div class='vitrinevak'>"+
      (S.tapaFinale ? "<div class='plaquette' id='tapaPlaquette'><b><span class='es'>El Gran Men\\u00fa</span></b>"+
        "<span>"+ct("alle "+TAPAS.length+" tapas geproefd \\u00b7 ","all "+TAPAS.length+" tapas tasted \\u00b7 ")+S.tapaFinale+"</span></div>" : "")+
      "<p class='bailehoy' id='tapaHoy'><span class='es'>"+(tapaKlaar ? "La tapa del d\\u00eda" : "La pr\\u00f3xima tapa")+"</span>: "+tapaHoy.e+" <span class='es'>"+tapaHoy.es+"</span> <span class='muted'>\\u00b7 "+ct(tapaHoy.nl, tapaHoy.en)+
        (tapaKlaar ? "" : " \\u00b7 "+ct("na je volgende les","after your next session"))+"</span></p>"+
      tapaMenuHtml()+
      "<p class='zorglabel' id='tapaTel'>"+
        ct("Chispa proefde "+tapaGehad+" van de "+TAPAS.length+" tapas \\u00b7 tik er een aan om hem te geven",
           "Chispa has tasted "+tapaGehad+" of "+TAPAS.length+" tapas \\u00b7 tap one to feed it to her")+
        " \\u00b7 \\ud83e\\uded2 "+(S.tapas || 0)+"</p>"+
    "</div>"+
    "<div class='vitrinevak'>"+
      "<p class='bailehoy' id='baileHoy'><span class='es'>El baile del d\\u00eda</span>: <span class='es'>"+bd.es+"</span> <span class='muted'>\\u00b7 "+bd.land+"</span></p>"+
      "<div class='bailerij' id='baileRij'>"+bailHtml+"</div>"+
      "<p class='zorglabel' id='baileTel'>"+ct("Je kent "+bekend.length+" van de "+BAILES.length+" dansen \\u00b7 tik er een aan","You know "+bekend.length+" of "+BAILES.length+" dances \\u00b7 tap one")+
        " <button class='muziekchip"+(S.chispaStil?" stil":"")+"' id='btnChMuziek' type='button' title='"+chMuziekTitel()+"'>"+chMuziekLabel()+"</button></p>"+
    "</div>";
}
function chVerzamelWire(el){
  if(!el) return;
  tapaMenuWire(el);
  el.querySelectorAll("button.bailechip").forEach(function(bb){""")

rep(
    """  var mz = document.getElementById("btnChMuziek");
  if(mz) mz.onclick = function(){
    S.chispaStil = !S.chispaStil;
    if(S.chispaStil){ try { chMuziekUit(); } catch(e){} }
    try { persist(); } catch(e){}
    mz.textContent = chMuziekLabel();
    mz.title = chMuziekTitel();
    mz.className = "muziekchip" + (S.chispaStil ? " stil" : "");
  };
}""",
    """  var mz = document.getElementById("btnChMuziek");
  if(mz) mz.onclick = function(){
    S.chispaStil = !S.chispaStil;
    if(S.chispaStil){ try { chMuziekUit(); } catch(e){} }
    try { persist(); } catch(e){}
    mz.textContent = chMuziekLabel();
    mz.title = chMuziekTitel();
    mz.className = "muziekchip" + (S.chispaStil ? " stil" : "");
  };
}
/* De vitrinekaart is leeg sinds de twee rijen naar boven zijn gegaan. Hij blijft als element staan
   (schermen en suites verwijzen ernaar) maar hij toont niets meer en gaat uit beeld. Een lege kaart
   met een kop erboven is erger dan geen kaart. */
function renderVitrine(){
  var el = document.getElementById("vitrineCard");
  if(!el) return;
  el.innerHTML = "";
  el.classList.add("hidden");
}""")

# ---------------------------------------------------------------- 3. in de kaart van Chispa zelf
rep(
    """    "<p class='muted' style='font-size:.82rem; margin:8px 0 8px; text-align:center'>"+deco.txt+"</p>"+
    "<div class='row center'>"+
    "<button class='primary' id='btnFeed' "+((S.tapas||0)<1?"disabled style='opacity:.5'":"")+">"+(slaapt?ct("Stil een tapa neerzetten ","Quietly leave a tapa "):ct("Geef een tapa ","Give a tapa "))+"\\ud83e\\uded2 "+(S.tapas||0)+"</button>"+
    "<button class='ghost' id='btnFiesta'>\\ud83c\\udf89 \\u00a1Fiesta!</button>"+""",
    """    "<p class='muted' style='font-size:.82rem; margin:8px 0 8px; text-align:center'>"+deco.txt+"</p>"+
    /* v23.33: de tapas en de dansen staan hier, direct onder haar. De knop "Geef een tapa" is weg:
       sinds v19.81 is een tapa aantikken al geven, en een knop ernaast die hetzelfde doet maar de
       keuze voor je maakt is de slechtere van de twee. Hoeveel tapas je hebt staat nu bij de rij
       waar je ze uitgeeft. */
    chVerzamelHtml()+
    "<div class='row center'>"+
    "<button class='ghost' id='btnFiesta'>\\ud83c\\udf89 \\u00a1Fiesta!</button>"+""")

rep(
    """  var b = document.getElementById("btnFeed");
  if(b) b.onclick = feedPet;
  var bfi = document.getElementById("btnFiesta");""",
    """  chVerzamelWire(el);
  var bfi = document.getElementById("btnFiesta");""")

rep('var APP_VERSIE = "v23.32";', 'var APP_VERSIE = "v23.33";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
with io.open(PAD_VER, "w", encoding="utf-8") as f:
    f.write("v23.33\n")
print("v23.33 toegepast op", PAD)


# ---------------------------------------------------------------- 4. de suites
def suite(naam, paren, sleutel):
    pad = os.path.join(MAP_S, naam)
    with io.open(pad, encoding="utf-8") as f:
        s = f.read()
    if sleutel in s:
        print("  " + naam + ": al bijgewerkt")
        return
    for anker, nieuw in paren:
        aantal = s.count(anker)
        assert aantal == 1, "%s: anker komt %d keer voor:\n%s" % (naam, aantal, anker[:140])
        s = s.replace(anker, nieuw, 1)
    with io.open(pad, "w", encoding="utf-8") as f:
        f.write(s)
    print("  " + naam + ": bijgewerkt")


FINALE_OUD = """  ok(plaq.erIs && plaq.inVitrine, 'de plaquette hangt in de vitrine, waar de verzameling staat');
  ok(/Gran Men/i.test(plaq.tekst), 'met dezelfde naam als de ceremonie');
  ok(plaq.datum, 'en de datum waarop je het afmaakte staat erop');
  ok(plaq.knop, 'er zit een knop bij om de ceremonie terug te kijken');

  // --- 4. Terugkijken kan, en verandert niets aan je stand ---
  await page.click('#btnFinaleTerug');
  await page.waitForTimeout(600);
  const terug = await page.evaluate(() => {
    const w = document.getElementById('finaleWrap');
    return { zichtbaar: !!(w && w.getClientRects().length > 0), datum: S.tapaFinale,
             tapas: w ? w.querySelectorAll('.finaletapa').length : 0 };
  });
  ok(terug.zichtbaar, 'uitgespeeld betekent niet weg: je kunt hem terugkijken');
  ok(terug.tapas === bijna.n, 'met dezelfde achttien tapas (' + terug.tapas + ')');
  ok(terug.datum === laatste.datum, 'en de oorspronkelijke datum blijft staan, niet die van vandaag');

  await page.click('#btnFinaleSluit');
  await page.waitForTimeout(400);
  const weg = await page.evaluate(() => {
    const w = document.getElementById('finaleWrap');
    return { dicht: !(w && w.getClientRects().length > 0),
             chispa: !document.getElementById('tab-chispa').classList.contains('hidden'),
             chips: document.querySelectorAll('#vitrineCard .tapachip.gehad').length };
  });
  ok(weg.dicht, 'de knop doet hem weer dicht');
  ok(weg.chispa, 'en je staat weer op Chispa\\'s pagina');
  ok(weg.chips === bijna.n, 'de vitrine staat vol (' + weg.chips + ')');"""

FINALE_NIEUW = """  ok(plaq.erIs && plaq.inVitrine, 'de plaquette staat bij Chispa, waar de verzameling staat');
  ok(/Gran Men/i.test(plaq.tekst), 'met dezelfde naam als de ceremonie');
  ok(plaq.datum, 'en de datum waarop je het afmaakte staat erop');
  /* v23.33, op Stefans verzoek: de knop "Kijk de ceremonie terug" is weg. De plaquette blijft, want
     die is het bewijs; de herhaling was iets anders. Een ceremonie die je op afroep kunt herhalen is
     na de tweede keer geen ceremonie meer, en de datum erop doet het werk. */
  ok(!plaq.knop, 'en er zit geen knop meer bij om de ceremonie te herhalen');

  // --- 4. De stand blijft staan, ook zonder herhaling ---
  const weg = await page.evaluate(() => {
    const w = document.getElementById('finaleWrap');
    return { dicht: !(w && w.getClientRects().length > 0),
             chispa: !document.getElementById('tab-chispa').classList.contains('hidden'),
             datum: S.tapaFinale,
             chips: document.querySelectorAll('#petCard .tapachip.gehad').length };
  });
  ok(weg.dicht, 'de ceremonie staat niet opnieuw open');
  ok(weg.chispa, 'je staat op Chispa\\'s pagina');
  ok(weg.datum === laatste.datum, 'de oorspronkelijke datum blijft staan, niet die van vandaag');
  ok(weg.chips === bijna.n, 'en de verzameling staat vol (' + weg.chips + ')');"""

suite("pw-chispakaarten.js", [
    ("""  ok(bouw.gevuld.every(Boolean), 'en ze zijn alle vier echt gevuld (' + bouw.gevuld.join(',') + ')');""",
     """  /* v23.33: de vitrinekaart is leeg sinds de twee verzamelingen bij Chispa zelf staan. Hij blijft
     als element bestaan (schermen en suites verwijzen ernaar) maar hij toont niets. */
  ok(bouw.gevuld[0] && bouw.gevuld[1] && bouw.gevuld[3],
    'het dier, haar groei en haar kamer zijn gevuld (' + bouw.gevuld.join(',') + ')');
  ok(!bouw.gevuld[2], 'en de vitrinekaart is leeg, want zijn inhoud staat nu bij haar');"""),

    ("""    const voor = document.querySelectorAll('#vitrineCard .tapachip.gehad').length;
    S.tapaMenu = [TAPAS[0].id, TAPAS[1].id, TAPAS[2].id];
    renderChispaPagina();
    return { voor: voor, na: document.querySelectorAll('#vitrineCard .tapachip.gehad').length };
  });
  ok(samen.voor === 0 && samen.na === 3, 'een gegroeide verzameling is meteen zichtbaar in de vitrine (' + samen.voor + ' -> ' + samen.na + ')');""",
     """    const voor = document.querySelectorAll('#petCard .tapachip.gehad').length;
    S.tapaMenu = [TAPAS[0].id, TAPAS[1].id, TAPAS[2].id];
    renderChispaPagina();
    return { voor: voor, na: document.querySelectorAll('#petCard .tapachip.gehad').length };
  });
  ok(samen.voor === 0 && samen.na === 3, 'een gegroeide verzameling is meteen zichtbaar (' + samen.voor + ' -> ' + samen.na + ')');"""),

    ("""      knoppen: ['btnFeed', 'btnFiesta', 'btnSerenade', 'btnCadeau'].filter((i) => !!c.querySelector('#' + i)).length,""",
     """      knoppen: ['btnFiesta', 'btnSerenade', 'btnCadeau'].filter((i) => !!c.querySelector('#' + i)).length,"""),

    ("""  ok(pet.knoppen === 4, 'kaart 1: de vier dingen die je met haar kunt doen (' + pet.knoppen + ')');
  ok(pet.tapachips === 0 && pet.bailechips === 0, 'kaart 1: geen verzamelingen meer tussen haar voeten');
  ok(pet.shopitems === 0 && pet.badge === 0, 'kaart 1: geen kledingkast, geen kamer, geen tapateller');""",
     """  ok(pet.knoppen === 3, 'kaart 1: de drie dingen die je met haar kunt doen (' + pet.knoppen + ')');
  /* v23.33 draait v19.70 op dit punt om, en dat is een besluit en geen slordigheid. Toen zijn de
     verzamelingen bij Chispa weggehaald omdat er tussen haar voeten ook een kledingkast, een kamer
     en een straattaalles stonden; dat blijft weg. Maar de tapas en de dansen zijn precies de twee
     dingen die je mét haar doet, en die stonden twee kaarten lager dan het dier waar ze over gaan.
     Wat deze suite nu bewaakt is de grens die er echt toe doet: doen mag hier, bezit en beheer niet. */
  ok(pet.tapachips >= 12 && pet.bailechips >= 4,
     'kaart 1: de tapas en de dansen staan bij haar, want daar geef je ze (' + pet.tapachips + '/' + pet.bailechips + ')');
  ok(pet.shopitems === 0 && pet.badge === 0, 'kaart 1: geen kledingkast, geen kamer, geen tapateller');"""),

    ("""  // --- 4. Kaart 3 is de vitrine: twee verzamelingen, twee vakken, twee tellers ---
  const vit = await page.evaluate(() => {
    const c = document.getElementById('vitrineCard');
    return {
      vakken: c.querySelectorAll('.vitrinevak').length,
      tapas: c.querySelectorAll('.tapachip').length,
      bailes: c.querySelectorAll('.bailechip').length,
      tapaTel: !!c.querySelector('#tapaTel'),
      baileTel: !!c.querySelector('#baileTel'),
      hoy: c.querySelectorAll('.tapachip.hoy').length + c.querySelectorAll('.bailechip.hoy').length,
      shopitems: c.querySelectorAll('.shopitem').length
    };
  });
  ok(vit.vakken === 2, 'kaart 3: twee vakken naast elkaar (' + vit.vakken + ')');
  ok(vit.tapas >= 12 && vit.bailes >= 4, 'kaart 3: alle tapas en alle dansen staan er (' + vit.tapas + '/' + vit.bailes + ')');
  ok(vit.tapaTel && vit.baileTel, 'kaart 3: elke verzameling heeft een eigen teller');
  ok(vit.hoy === 2, 'kaart 3: de tapa én de dans van vandaag zijn aangewezen (' + vit.hoy + ')');
  ok(vit.shopitems === 0, 'kaart 3: hier valt niets te kopen, alleen te kijken');""",
     """  // --- 4. De verzamelingen: twee vakken, twee tellers, nu in kaart 1 ---
  const vit = await page.evaluate(() => {
    const c = document.getElementById('petCard');
    const leeg = document.getElementById('vitrineCard');
    return {
      vakken: c.querySelectorAll('.vitrinevak').length,
      tapas: c.querySelectorAll('.tapachip').length,
      bailes: c.querySelectorAll('.bailechip').length,
      tapaTel: !!c.querySelector('#tapaTel'),
      baileTel: !!c.querySelector('#baileTel'),
      hoy: c.querySelectorAll('.tapachip.hoy').length + c.querySelectorAll('.bailechip.hoy').length,
      shopitems: c.querySelectorAll('.shopitem').length,
      vitrineLeeg: !!leeg && leeg.classList.contains('hidden') && leeg.innerText.trim() === '',
      teller: (c.querySelector('#tapaTel') || {}).innerText || ''
    };
  });
  ok(vit.vakken === 2, 'twee vakken onder elkaar (' + vit.vakken + ')');
  ok(vit.tapas >= 12 && vit.bailes >= 4, 'alle tapas en alle dansen staan er (' + vit.tapas + '/' + vit.bailes + ')');
  ok(vit.tapaTel && vit.baileTel, 'elke verzameling heeft een eigen teller');
  ok(vit.hoy === 2, 'de tapa én de dans van vandaag zijn aangewezen (' + vit.hoy + ')');
  ok(vit.shopitems === 0, 'hier valt niets te kopen, alleen te geven');
  ok(vit.vitrineLeeg, 'de oude vitrinekaart is leeg en uit beeld, niet blijven staan met een kop erboven');
  /* v23.33: op Stefans scherm stond "Chispa proefde 29 van de 18 tapas". S.tapaMenu bewaart ids en
     TAPAS is sindsdien veranderd; de teller telde alles wat er ooit in kwam. Dezelfde fout als de
     luisterteller van v22.10, en hij ziet er als een prestatie uit, dus je merkt hem nooit. */
  const gek = await page.evaluate(() => {
    S.tapaMenu = (S.tapaMenu || []).concat(['bestaat-niet-1', 'bestaat-niet-2']);
    renderPet();
    const t = (document.getElementById('tapaTel') || {}).innerText || '';
    const m = t.match(/(\\d+)\\D+(\\d+)/);
    return { tekst: t, gehad: m ? +m[1] : -1, totaal: m ? +m[2] : -1, tapas: TAPAS.length };
  });
  ok(gek.totaal === gek.tapas && gek.gehad <= gek.totaal,
     'de teller kan nooit boven zijn eigen noemer uitkomen (' + gek.tekst.slice(0, 60) + ')');"""),
], "v23.33")

suite("pw-finale.js", [
    ("""      inVitrine: !!(p && p.closest('#vitrineCard')),""",
     """      inVitrine: !!(p && p.closest('#petCard')),   // v23.33: de plaquette staat bij Chispa zelf"""),
    (FINALE_OUD, FINALE_NIEUW),
], "v23.33")
