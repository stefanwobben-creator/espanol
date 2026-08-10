#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.37: één maat op de voortgangspagina.

Stefan zette er twaalf plakbriefjes op. Zeven ervan gaan over hetzelfde: de pagina meet in drie
eenheden door elkaar en zegt bij geen van drieën welke het is. Dit is die zeven.

WAT ER FOUT WAS, EN VAN MIJ

1. "Waar je staat" stond er twee keer. Bovenaan het blok van v23.32, en verderop nog eens omdat
   renderStats() via basisHtml() diezelfde balk zelf ook tekent. Ik heb de cijferpagina naar het
   nieuwe scherm verhuisd zonder zijn eigen kopie eruit te halen. Precies de fout waar dit hele
   hoofdstuk over gaat, door mij opnieuw gemaakt. Weg, samen met "Jouw ontwikkeling", dat dezelfde
   getallen nog een derde keer in een zin zette.

2. "+4 woorden erbij deze week" was de aanwas van bewezen vast. Daar zitten vijfentwintig dagen
   tussen per woord, dus als weekcijfer meet het vooral hoe lang je al bezig bent. Stefans eigen
   voorstel is het goede: het aantal woorden dat je die week geoefend hebt. Dat stond al in de
   weekmeting (geoefend), ik gebruikte alleen het verkeerde veld.

3. De lijn tekende bewezen vast (0 naar 4) onder een kop van 357. Een grafiek die een ander getal
   tekent dan de kop erboven is erger dan geen grafiek, en zijn vraag "wat is de juiste schaal voor
   de y-as" is het bewijs: die schaal hoorde bij een getal dat er niet stond.

   De lijn tekent nu wat je actief bijhoudt, dezelfde maat als de kop en de balk. Dat kan pas vanaf
   nu: de weekmeting bewaarde alleen dek (bewezen vast) en niet dekw (onderweg), dus die gaat er
   vanaf deze versie bij. Tot er twee weken met dat veld liggen staat er geen lijn maar één regel
   die zegt vanaf wanneer hij komt. Geen lijn is beter dan een lijn in de verkeerde eenheid.

4. Je doel vroeg 30,8 stevige woorden per week terwijl je er 1 haalt. Dat klopt en het is nutteloos:
   het legt je doel langs de traagste teller die de app heeft, en dan kun je nooit zien of je op
   koers ligt. Doel en tempo rekenen nu in dezelfde maat als de balk. Je ziet daardoor andere
   getallen dan gisteren, en die zijn niet mooier gemaakt: ze meten alleen eindelijk hetzelfde als
   waar de rest van de pagina over gaat.

5. "school, 18 van de 18 woorden gehad, 10%" leest als een score en is het niet: het is hoe ver die
   woorden in de doosjes staan. Bij "Ser of estar, 1 fout van 7 beurten, 0%" is het erger, want daar
   staat 0% terwijl je zes van de zeven goed had (één fout zet een regel terug naar doosje nul). Er
   staat nu bij wat het getal is, en bij de regels staat het doosje in plaats van een percentage.

6. Sterke punten kreeg je nooit te zien. Ik had er een drempel van 50% in gezet om te voorkomen dat
   er "sterk: 0%" zou staan, maar het gevolg was dat de hele kaart verdween. Nu staat er altijd waar
   je het verst bent, en de regel eronder zegt eerlijk of dat al iets voorstelt.

Wat blijft staan voor de volgende ronde: de waaier bij "waar je straks staat" (nu nog tekst), de
lange cijferlijst, en de twee kleine getallen (15 nieuwe woorden per dag zonder zijn totaal, en
"20 dagen erbij geweest" zonder erbij vanaf wanneer).

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
MAP_S = os.path.join(WORTEL, "test", "suites")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function vgWeekGroei" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)
if 'var APP_VERSIE = "v23.36";' not in src:
    print("Deze index.html staat niet op v23.36. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


def snijd(begin, eind, nieuw, maxlen):
    """Alles tussen twee merktekens vervangen. Voor blokken die te lang zijn om als anker uit te
    schrijven; de lengtegrens is de veiligheid, zodat een verschoven merkteken niet stilletjes het
    halve bestand opeet."""
    global src
    assert src.count(begin) == 1, "beginmerk komt %d keer voor" % src.count(begin)
    i = src.index(begin)
    j = src.index(eind, i)
    lengte = j + len(eind) - i
    assert lengte <= maxlen, "blok is %d tekens, verwacht hoogstens %d" % (lengte, maxlen)
    src = src[:i] + nieuw + src[j + len(eind):]


# ================================================================ 1. de dubbele balk en de prozazin
snijd(
    """  var koersHtml = basisHtml(actief14) + "<h2>"+ct("Jouw ontwikkeling""",
    """    koersHtml += bandHtml("A1");
  }""",
    """  /* v23.37: hier stonden twee dingen die de voortgangspagina al boven zich heeft staan. basisHtml()
     tekende "Waar je staat" een tweede keer (Stefan: "kan weg en is dubbel"), en "Jouw ontwikkeling"
     zette dezelfde getallen nog eens in een zin (Stefan: "dit voelt overbodig of verwarrend, denk
     dat we dit al hebben"). Allebei weg. basisHtml() en bandHtml() blijven bestaan; ze worden alleen
     hier niet meer aangeroepen. */
  var koersHtml = "";""",
    5200)

# ================================================================ 2. de week telt geoefende woorden
rep(
    """/* ---------- 1. Je week ---------- */
function vgWeekHtml(c){
  var t = today(), i, d, dagen = 0;
  for(i = 0; i < 7; i++){ d = addDays(t, -i); if((S.xp || {})[d] > 0) dagen++; }
  var wk = vgWeken(c.samen.nivs);
  var groei = wk.length > 1 ? wk[wk.length-1].vast - wk[wk.length-2].vast : null;
  var lessen = afgemaakt7(), tv = tijdVenster(7);""",
    """/* ---------- 1. Je week ---------- */
/* v23.37: de aanwas van geoefende woorden, niet van bewezen vast. Stefan: "hoezo maar +4 woorden
   erbij? dit zijn gegronde woorden denk ik, maar die gaan heel langzaam dus beter hier aantal
   nieuwe woorden geoefend." Precies: bewezen vast vraagt vijf goede beurten over vijfentwintig
   dagen, dus als weekcijfer meet dat vooral hoe lang je al bezig bent. Geoefend beweegt met wat je
   die week echt gedaan hebt, en staat al in elke weekmeting. */
function vgWeekGroei(wk){
  if(wk.length < 2) return null;
  return Math.max(0, wk[wk.length-1].geoefend - wk[wk.length-2].geoefend);
}
function vgWeekHtml(c){
  var t = today(), i, d, dagen = 0;
  for(i = 0; i < 7; i++){ d = addDays(t, -i); if((S.xp || {})[d] > 0) dagen++; }
  var wk = vgWeken(c.samen.nivs);
  var groei = vgWeekGroei(wk);
  var tv = tijdVenster(7);""")

rep(
    """  } else {
    h += "<div class='vgKop'><div class='vgGroot'>"+(groei >= 0 ? "+" : "")+groei+"</div>"+
      "<div class='vgBij'>"+ct("woorden erbij deze week","words added this week")+"</div></div>";
  }
  h += "<div class='statgrid' style='margin-top:8px'>"+
    "<div class='stat'><b>"+dagen+"/7</b><span class='muted'>"+ct("dagen geoefend","days practised")+"</span></div>"+
    "<div class='stat'><b>"+lessen+"</b><span class='muted'>"+ct("lessen afgemaakt","sessions finished")+"</span></div>"+
    "</div>";""",
    """  } else {
    h += "<div class='vgKop'><div class='vgGroot'>"+(groei >= 0 ? "+" : "")+groei+"</div>"+
      "<div class='vgBij'>"+ct("woorden geoefend deze week","words practised this week")+"</div></div>";
  }
  /* v23.37: minuten in plaats van lessen. Stefan: "lessen is hier beetje verwarrend, misschien hier
     totale tijd per week?" Die tijd wordt al gemeten (uit de gaten tussen je antwoorden), hij stond
     alleen nergens per week. Zonder gemeten tijd staat er niets in plaats van een nul. */
  var minuten = tv.sec ? Math.round(tv.sec / 60) : null;
  h += "<div class='statgrid' style='margin-top:8px'>"+
    "<div class='stat'><b>"+dagen+"/7</b><span class='muted'>"+ct("dagen geoefend","days practised")+"</span></div>"+
    (minuten !== null
      ? "<div class='stat'><b>"+minuten+"</b><span class='muted'>"+ct("minuten deze week","minutes this week")+"</span></div>"
      : "<div class='stat'><b>"+afgemaakt7()+"</b><span class='muted'>"+ct("lessen afgemaakt","sessions finished")+"</span></div>")+
    "</div>";""")

rep(
    """  var los = [];
  los.push("\\ud83d\\udd25 " + streakNow() + " " + ct("dagen op rij","days in a row"));
  if(tv.perDag !== null) los.push(tv.perDag + " " + ct("minuten per dag","minutes a day"));""",
    """  var los = [];
  los.push("\\ud83d\\udd25 " + streakNow() + " " + ct("dagen op rij","days in a row"));
  los.push(afgemaakt7() + " " + ct("lessen","sessions"));""")

# ================================================================ 3. de weekmeting bewaart ook onderweg
rep(
    """    S.meting[w] = {d:t, stevig:c.stevig, bijna:c.bijna, geoefend:c.geoefend,
                 dek:c.dek, txp:S.txp || 0, spel:sp, spelw:spw, pog:pog, fout:fout};""",
    """    /* v23.37: dekw erbij. De weekmeting bewaarde alleen dek (bewezen vast), en dat is de traagste
       teller die de app heeft; elke grafiek die erop staat kruipt. dekw is wat je actief bijhoudt,
       dezelfde maat als de balk en de kop, en vanaf nu is die dus ook terug te kijken. */
    S.meting[w] = {d:t, stevig:c.stevig, bijna:c.bijna, geoefend:c.geoefend,
                 dek:c.dek, dekw:c.dekw, txp:S.txp || 0, spel:sp, spelw:spw, pog:pog, fout:fout};""")

rep(
    """    uit.push({week:ws[i], d:m.d, vast:vgSomDek(m, nivs), geoefend:m.geoefend || 0,
              pog:m.pog || 0, fout:m.fout || 0});""",
    """    uit.push({week:ws[i], d:m.d, vast:vgSomDek(m, nivs), geoefend:m.geoefend || 0,
              /* actief is null voor weken van vóór v23.37: die metingen kennen dekw niet. Null en
                 niet nul, want nul zou een lijn naar beneden trekken die nooit gebeurd is. */
              actief:m.dekw ? vgSomVeld(m.dekw, nivs) : null,
              pog:m.pog || 0, fout:m.fout || 0});""")

rep(
    """function vgSomDek(m, nivs){
  var s = 0, i;
  for(i = 0; i < nivs.length; i++) s += ((m && m.dek) || {})[nivs[i]] || 0;
  return s;
}""",
    """function vgSomVeld(veld, nivs){
  var s = 0, i;
  for(i = 0; i < nivs.length; i++) s += (veld || {})[nivs[i]] || 0;
  return s;
}
function vgSomDek(m, nivs){ return vgSomVeld(m && m.dek, nivs); }""")

# ================================================================ 4. de lijn tekent dezelfde maat
rep(
    """function vgLijnHtml(c){
  var wk = vgWeken(c.samen.nivs);
  if(wk.length < 2) return "";""",
    """function vgLijnHtml(c){
  /* v23.37: de lijn tekent wat je actief bijhoudt, dezelfde maat als de kop erboven. Tot v23.36
     tekende hij bewezen vast, en dan loopt er een lijn naar 4 onder een kop van 357. Weken van vóór
     deze versie hebben dat veld niet, dus die doen niet mee; staan er nog geen twee, dan staat er
     één regel in plaats van een grafiek. Geen lijn is beter dan een lijn in de verkeerde eenheid. */
  var wk = vgWeken(c.samen.nivs).filter(function(x){ return x.actief !== null; });
  if(wk.length < 2){
    return "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>"+
      ct("De lijn hierbij komt zodra er twee weekmetingen liggen die dit getal bewaren. Tot v23.36 "+
         "bewaarden ze alleen het bewezen deel, en dat is een ander getal dan hierboven staat.",
         "The line here appears once two weekly measurements store this number. Until v23.36 they "+
         "only stored the proven part, which is a different number than the one above.")+"</p>";
  }""")

rep(
    """  var top = 0, i, x, y, d = "", pad = "";
  for(i = 0; i < wk.length; i++) top = Math.max(top, wk[i].vast);""",
    """  var top = 0, i, x, y, d = "", pad = "";
  for(i = 0; i < wk.length; i++) top = Math.max(top, wk[i].actief);""")

rep(
    """    y = T + (H - T - B) * (1 - wk[i].vast / top);""",
    """    y = T + (H - T - B) * (1 - wk[i].actief / top);""")

rep(
    """    "<circle cx='"+Math.round(W - R)+"' cy='"+Math.round(T + (H-T-B) * (1 - wk[wk.length-1].vast/top))+""",
    """    "<circle cx='"+Math.round(W - R)+"' cy='"+Math.round(T + (H-T-B) * (1 - wk[wk.length-1].actief/top))+""")

rep(
    """      ct("Bewezen vast, van <b>"+wk[0].vast+"</b> op "+datumUit(wk[0].d)+" naar <b>"+
         wk[wk.length-1].vast+"</b> nu, over "+wk.length+" weekmetingen.",
         "Proven solid, from <b>"+wk[0].vast+"</b> on "+datumUit(wk[0].d)+" to <b>"+
         wk[wk.length-1].vast+"</b> now, across "+wk.length+" weekly measurements.")+"</p>";""",
    """      ct("Wat je actief bijhoudt, van <b>"+wk[0].actief+"</b> op "+datumUit(wk[0].d)+" naar <b>"+
         wk[wk.length-1].actief+"</b> nu. De schaal loopt tot "+top+", je eigen hoogste punt.",
         "What you actively keep up, from <b>"+wk[0].actief+"</b> on "+datumUit(wk[0].d)+" to <b>"+
         wk[wk.length-1].actief+"</b> now. The scale runs to "+top+", your own highest point.")+"</p>";""")

# ================================================================ 5. doel en tempo in dezelfde maat
rep(
    """  var reeks = ws.map(function(w){ return (S.meting[w].dek || {})[niveau] || 0; });""",
    """  /* v23.37: het tempo rekent met wat je actief bijhoudt, net als de balk en het doel. Op dek
     (bewezen vast) gerekend kwam er 1 woord per week uit terwijl er tientallen bewegen, en dan is
     elke uitspraak over koers onbruikbaar. Weken zonder dekw vallen terug op dek: dat is wat we van
     die weken weten, en het alternatief is ze weggooien. */
  var reeks = ws.map(function(w){
    var m = S.meting[w] || {};
    return (m.dekw || {})[niveau] || (m.dek || {})[niveau] || 0;
  });""")

rep(
    """  var tel = voortgangTellers();
  var nu = tel.dek[niv] || 0, noemer = PCIC_NOEMER[niv] || 0;""",
    """  var tel = voortgangTellers();
  // v23.37: dezelfde maat als de balk: bewezen vast plus onderweg
  var nu = Math.max(tel.dek[niv] || 0, (tel.dekw && tel.dekw[niv]) || 0);
  var noemer = PCIC_NOEMER[niv] || 0;""")

# ================================================================ 6. sterk en zwak zeggen wat ze meten
rep(
    """var VG_STERK = 50;
function vgSterkHtml(){
  var z = zwakkePunten();
  var sterk = z.themas.filter(function(x){ return x.kracht >= VG_STERK; }).slice(-3).reverse();
  if(sterk.length < 2) return "";""",
    """/* v23.37: de kaart verdween als er niets boven de vijftig stond, en dus zag Stefan hem nooit
   ("ik mis sterke punten"). De drempel was bedoeld tegen "sterk: 0%", maar het middel was erger dan
   de kwaal. Nu staat er altijd waar je het verst bent, en de regel eronder zegt of dat al iets
   voorstelt. */
var VG_STERK = 50;
function vgSterkHtml(){
  var z = zwakkePunten();
  var sterk = z.themas.slice(-3).reverse();
  if(sterk.length < 2) return "";
  var echtSterk = sterk[0] && sterk[0].kracht >= VG_STERK;""")

rep(
    """    sterk.map(function(x){
      return vgRij(x.naam, ct(x.gehad+" van de "+x.n+" woorden gehad", x.gehad+" of "+x.n+" words seen"),
                   x.kracht, x.kracht+"%", "sterk");
    }).join("")+
    "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>"+
      ct("Deze hoef je even niet te doen. Dat is ook informatie.",
         "You can leave these alone for now. That's information too.")+"</p></div>";""",
    """    sterk.map(function(x){
      return vgRij(x.naam, ct(x.gehad+" van de "+x.n+" woorden gehad", x.gehad+" of "+x.n+" words seen"),
                   x.kracht, x.kracht+"%", "sterk");
    }).join("")+
    "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>"+
      (echtSterk
        ? ct("Het percentage is hoe ver deze woorden in je doosjes staan, niet hoeveel je er goed had. "+
             "Deze hoef je even niet te doen.",
             "The percentage is how far these words sit in your boxes, not how many you got right. "+
             "You can leave these alone for now.")
        : ct("Hier ben je het verst, maar nog niet ver: het percentage is hoe ver deze woorden in je "+
             "doosjes staan, niet hoeveel je er goed had.",
             "This is where you are furthest along, but not far yet: the percentage is how far these "+
             "words sit in your boxes, not how many you got right."))+"</p></div>";""")

rep(
    """  var wankel = z.regels.filter(function(x){ return x.kracht < 60; });
  if(wankel.length >= 2){
    h += wankel.slice(0, 3).map(function(x){
      return vgRij(x.naam, ct(x.fout+" fout van "+x.beurten+" beurten", x.fout+" wrong of "+x.beurten+" turns"),
                   x.kracht, x.kracht+"%", "zwak");
    }).join("");
  }""",
    """  var wankel = z.regels.filter(function(x){ return x.kracht < 60; });
  if(wankel.length >= 2){
    /* v23.37: bij een regel stond een percentage, en dat leest als een score. "Ser of estar, 1 fout
       van 7 beurten, 0%" terwijl je er zes goed had: die nul is het doosje, niet je uitslag. Eén
       fout zet een regel terug naar doosje nul, en dat is precies wat er staat als je het doosje
       noemt in plaats van een percentage. */
    var dozen = GRAM_INTERVALS.length - 1;
    h += wankel.slice(0, 3).map(function(x){
      var doos = Math.round(x.kracht / 100 * dozen);
      return vgRij(x.naam,
                   ct(x.fout+" fout van "+x.beurten+" beurten", x.fout+" wrong of "+x.beurten+" turns"),
                   x.kracht, ct("doosje "+doos+"/"+dozen, "box "+doos+"/"+dozen), "zwak");
    }).join("");
  }""")

rep(
    """    ct("Van alle woorden die dit thema op jouw niveau heeft: hoe ver ze in de doosjes staan. Woorden "+
       "die je nooit zag tellen voor nul. Niet op fouten geteld, want een thema dat je vaak oefent "+
       "verzamelt vanzelf de meeste fouten.",""",
    """    ct("Het percentage is geen score. Het is hoe ver de woorden van dit thema in je doosjes staan, "+
       "van alle woorden die het thema op jouw niveau heeft; woorden die je nooit zag tellen voor "+
       "nul. Niet op fouten geteld, want een thema dat je vaak oefent verzamelt vanzelf de meeste "+
       "fouten.",""")

rep('var APP_VERSIE = "v23.36";', 'var APP_VERSIE = "v23.37";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
with io.open(PAD_VER, "w", encoding="utf-8") as f:
    f.write("v23.37\n")
print("v23.37 toegepast op", PAD)

# ================================================================ 7. de suites
# Hele bestanden in plaats van knipwerk: er verandert in elk maar één assertie, maar die assertie
# staat midden in een blok dat ik in dezelfde versie ook aanpas, en dan is knippen fragieler dan
# neerzetten wat er moet staan.

VOORTGANG = r'''// v23.32: Voortgang is een eigen scherm, in de volgorde die Stefan gaf.
//
// Wat deze suite vastlegt, en waarom precies dit:
//   - de zes blokken staan er, in zijn volgorde. Een volgorde die niemand bewaakt is een volgorde
//     die bij de volgende versie omvalt, en dan is het weer het scherm van de bouwer.
//   - de cijfers op dit scherm komen uit voortgangCijfers(). Dat is de hele afspraak van dit
//     hoofdstuk: één functie levert de getallen, alle schermen roepen hem aan.
//   - wat hier weg is bij Profiel, is daar niet verstopt maar staat er met een knop erheen.
//   - sterk en zwak staan hier één keer, niet ook nog onderaan bij de cijfers.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Voort' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  // een profiel met genoeg geschiedenis om alle blokken iets te laten zeggen
  await page.evaluate(() => {
    const map = pcicMap(), niv = pcicNiv();
    const a1 = Object.keys(map).filter((k) => (map[k] || []).some((s) => niv[s] === 'A1'));
    a1.slice(0, 120).forEach((k) => { S.srs[k] = { box: 5, k: 1, due: addDays(today(), 30), n: 9 }; });
    a1.slice(120, 200).forEach((k) => { S.srs[k] = { box: 3, due: addDays(today(), 3), n: 3 }; });
    /* Sterk en zwak gaan over thema's, en die hangen aan de tag van een leswoord. Zonder dit stukje
       heeft dit profiel wel Cervantes-sleutels maar geen thema's, en dan staan blok 5 en 6 er
       terecht niet. Twee tags helemaal vast, twee tags net begonnen: dat is precies het verschil dat
       die twee kaarten horen te laten zien. */
    const perKey = {};
    WORDS.forEach((w) => {
      if (!themaMeetelt(w.tag)) return;
      const k = themaSleutel(w.tag);
      (perKey[k] = perKey[k] || []).push(w);
    });
    // op tag groeperen werkt niet: de tag van een woord en de sleutel van een thema zijn niet
    // hetzelfde, en "familie" komt als tag wel voor maar als thema niet
    const keys = Object.keys(perKey).filter((k) => perKey[k].length >= 8);
    keys.slice(0, 2).forEach((k) => perKey[k].forEach((w) => {
      S.srs[w.id] = { box: 5, k: 1, due: addDays(today(), 30), n: 9 };
    }));
    keys.slice(2, 4).forEach((k) => perKey[k].forEach((w) => {
      S.srs[w.id] = { box: 1, due: addDays(today(), 1), n: 1 };
    }));
    const t = today();
    for (let i = 0; i < 10; i++) S.xp[addDays(t, -i)] = 20;
    for (let i = 0; i < 5; i++) S.lesFlow[addDays(t, -i)] = true;
    S.meting = {
      '2026-W30': { d: addDays(t, -21), dek: { A1: 40 }, stevig: 40, geoefend: 90, pog: 200, fout: 60 },
      '2026-W31': { d: addDays(t, -14), dek: { A1: 78 }, stevig: 78, geoefend: 150, pog: 220, fout: 55 },
      '2026-W32': { d: addDays(t, -7), dek: { A1: 120 }, stevig: 120, geoefend: 200, pog: 240, fout: 50 }
    };
    try { persist(); } catch (e) {}
  });

  console.log('\n-- het scherm bestaat en is bereikbaar vanaf Vandaag --');
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(400);
  const knop = await page.evaluate(() => !!document.getElementById('btnLijnMeer'));
  ok(knop, 'op Vandaag staat de knop naar je cijfers');
  await page.evaluate(() => { document.getElementById('btnLijnMeer').click(); });
  await page.waitForTimeout(500);
  const open = await page.evaluate(() => ({
    zichtbaar: !document.getElementById('tab-voortgang').classList.contains('hidden'),
    profiel: !document.getElementById('tab-perfil').classList.contains('hidden')
  }));
  ok(open.zichtbaar, 'de knop brengt je op het voortgangsscherm');
  ok(!open.profiel, 'en niet meer op je profiel');

  console.log('\n-- de zes blokken staan in Stefans volgorde --');
  const volgorde = await page.evaluate(() => {
    const kop = [...document.querySelectorAll('#voortgangCard .kicker')].map((k) => k.innerText.trim());
    return kop;
  });
  const wil = ['Je week', 'Je doel', 'Waar je staat', 'Onderweg', 'Sterke punten', 'Zwakke plekken'];
  // de kickers staan in kapitalen op het scherm (text-transform), dus vergelijken zonder hoofdletters
  wil.forEach((w, i) => {
    ok((volgorde[i] || '').toLowerCase().indexOf(w.toLowerCase()) === 0,
      'blok ' + (i + 1) + ' is "' + w + '" (' + (volgorde[i] || 'niets') + ')');
  });

  console.log('\n-- de getallen komen uit voortgangCijfers --');
  const cijf = await page.evaluate(() => {
    const c = voortgangCijfers();
    const kaart = document.getElementById('vgVastKaart');
    return { samen: JSON.parse(JSON.stringify(c.samen)),
             tekst: (kaart ? kaart.innerText : '').replace(/\s+/g, ' ') };
  });
  ok(cijf.tekst.indexOf(String(cijf.samen.actief)) !== -1,
    'wat je actief bijhoudt staat er (' + cijf.samen.actief + ')');
  ok(cijf.tekst.indexOf(String(cijf.samen.noem)) !== -1,
    'en de noemer erbij (' + cijf.samen.noem + ')');

  console.log('\n-- je week rekent met het verschil, niet met de stand --');
  const week = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][0];
    return (k ? k.innerText : '').replace(/\s+/g, ' ');
  });
  /* v23.37: de week telt geoefende woorden, niet bewezen vast. De fixture gaat van 150 naar 200
     geoefend, dus +50. Bewezen vast ging van 78 naar 120; dat is wat hier eerst stond, en precies
     de teller waarvan Stefan zei dat hij als weekcijfer niets zegt. */
  ok(/\+50/.test(week), 'de aanwas is die van geoefende woorden (+50)');
  ok(/\/7/.test(week), 'met het aantal dagen dat je er was');

  console.log('\n-- sterk en zwak staan er één keer --');
  const dubbel = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    return { sterk: (t.match(/Sterke punten/g) || []).length,
             zwak: (t.match(/Zwakke plekken/g) || []).length,
             oud: (t.match(/Dit beheers je/g) || []).length };
  });
  ok(dubbel.sterk <= 1 && dubbel.zwak <= 1, 'niet twee keer hetzelfde blok op één scherm');
  ok(dubbel.oud === 0, 'en het oude gecombineerde blok is weg, niet blijven staan');

  console.log('\n-- weggelaten is niet verstopt --');
  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(400);
  const prof = await page.evaluate(() => ({
    knop: !!document.getElementById('btnNaarVoortgang'),
    stats: !!document.querySelector('#tab-perfil #statsCard')
  }));
  ok(prof.knop, 'op je profiel staat een knop naar je voortgang');
  ok(!prof.stats, 'en de cijfers staan er niet ook nog een keer');

  const echt = errors.filter((e) => !/Failed to load resource|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten (' + echt.length + ')');
  if (echt.length) echt.forEach((e) => console.log('  -> ' + e));

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
'''

MEZCLA = r'''// v23.34: la mezcla. Een tapa plus een dans wordt een naam, en die naam buigt mee.
//
// Wat hier vastligt:
//   - het bijvoeglijk naamwoord volgt het lidwoord van de tapa. Dit is het hele punt: het spelletje
//     drilt de overeenkomst tussen zelfstandig en bijvoeglijk naamwoord, en een fout hierin leert
//     iemand precies verkeerd. Vier vormen worden op de letter nagerekend.
//   - de bestaande gebaren veranderen niet. Een tapa aantikken voert haar nog steeds, een dans
//     aantikken laat haar nog steeds dansen; de mezcla ontstaat ernaast.
//   - een gevonden mezcla blijft staan, en de teller kan nooit boven zijn noemer uitkomen (zie de
//     tapateller van v23.33 en de luisterteller van v22.10: dat is hier een terugkerende fout).
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Mez' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true; S.tapas = 20;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de vier vormen, op de letter --');
  const vormen = await page.evaluate(() => ({
    pulpo: mezclaMaak('pulpo', 'flamenco').es,
    aceitunas: mezclaMaak('aceitunas', 'salsa').es,
    tortilla: mezclaMaak('tortilla', 'tango').es,
    calamares: mezclaMaak('calamares', 'reggaeton').es,
    jarabe: mezclaMaak('bravas', 'jarabe').es,
    onzin: mezclaMaak('bestaat-niet', 'salsa')
  }));
  ok(vormen.pulpo === 'el pulpo flamenco', 'el (m enkelvoud): ' + vormen.pulpo);
  ok(vormen.aceitunas === 'las aceitunas salseras', 'las (v meervoud): ' + vormen.aceitunas);
  ok(vormen.tortilla === 'la tortilla tanguera', 'la (v enkelvoud): ' + vormen.tortilla);
  ok(vormen.calamares === 'los calamares reggaetoneros', 'los (m meervoud): ' + vormen.calamares);
  ok(vormen.jarabe === 'las patatas tapatías', 'en de kern zonder zijn staart: ' + vormen.jarabe);
  ok(vormen.onzin === null, 'een tapa die niet bestaat levert niets op, geen halve naam');

  console.log('\n-- alle 144 combinaties leveren een naam op --');
  const alle = await page.evaluate(() => {
    let n = 0, stuk = [];
    TAPAS.forEach((t) => BAILES.forEach((b) => {
      const m = mezclaMaak(t.id, b.id);
      if (!m || !/^(el|la|los|las) \S+ \S+$/.test(m.es)) stuk.push(t.id + '+' + b.id + ': ' + (m ? m.es : 'null'));
      else n++;
    }));
    return { n: n, stuk: stuk.slice(0, 4), totaal: TAPAS.length * BAILES.length };
  });
  ok(alle.n === alle.totaal, 'alle ' + alle.totaal + ' combinaties geven een lidwoord, een kern en een bijvoeglijk naamwoord ('
     + alle.n + ')' + (alle.stuk.length ? ' -- ' + alle.stuk.join(' | ') : ''));

  console.log('\n-- de strip staat tussen de tapas en de dansen --');
  await page.evaluate(() => show('chispa'));
  await page.waitForTimeout(600);
  const plek = await page.evaluate(() => {
    const s = document.getElementById('mezclaStrip');
    const t = document.getElementById('tapaMenuRij');
    const b = document.getElementById('baileRij');
    if (!s || !t || !b) return null;
    const y = (e) => e.getBoundingClientRect().top;
    return { inPet: !!s.closest('#petCard'), tussen: y(t) < y(s) && y(s) < y(b),
             leeg: s.querySelectorAll('.mezVak.leeg').length };
  });
  ok(plek && plek.inPet, 'de strip staat in de kaart van Chispa');
  ok(plek && plek.tussen, 'tussen de tapas en de dansen in');
  ok(plek && plek.leeg === 2, 'met twee lege vakjes om te beginnen (' + (plek ? plek.leeg : '-') + ')');

  console.log('\n-- aantikken doet nog steeds wat het deed, en vult het vakje --');
  const voor = await page.evaluate(() => ({ tapas: S.tapas || 0, bailes: (S.bailes || []).length }));
  await page.locator('#tapaMenuRij button.tapachip').first().click();
  await page.waitForTimeout(500);
  const naTapa = await page.evaluate(() => ({
    tapas: S.tapas || 0, gehad: (S.tapaMenu || []).length,
    vakken: document.querySelectorAll('#mezclaStrip .mezVak.leeg').length
  }));
  ok(naTapa.tapas === voor.tapas - 1, 'een tapa aantikken voert haar nog steeds (' + voor.tapas + ' -> ' + naTapa.tapas + ')');
  ok(naTapa.vakken === 1, 'en er is nog één vakje leeg (' + naTapa.vakken + ')');

  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(700);
  const naBaile = await page.evaluate(() => ({
    bailes: (S.bailes || []).length,
    mezclas: (S.mezcla || []).length,
    tekst: (document.getElementById('mezclaStrip') || {}).innerText || '',
    tel: (document.getElementById('mezclaTel') || {}).innerText || '',
    // op het woord "nieuw" zoeken kan niet: de knop ernaast heet "opnieuw". Dus op de markering zelf.
    nieuw: !!document.querySelector('#mezclaStrip .mezNieuw')
  }));
  ok(naBaile.bailes > voor.bailes, 'een dans aantikken laat haar nog steeds dansen');
  ok(naBaile.mezclas === 1, 'en samen leveren ze één gevonden mezcla op (' + naBaile.mezclas + ')');
  ok(/\S+ \S+/.test(naBaile.tekst) && !/\?/.test(naBaile.tekst), 'de uitkomst staat in de strip: ' + naBaile.tekst.replace(/\n/g, ' | '));
  ok(naBaile.nieuw, 'met erbij dat hij nieuw is');

  console.log('\n-- de tapa danst mee, op haar formaat en in haar tempo --');
  /* Eerst haar in beeld schuiven. Staat de kaart weggescrold, dan danst ze in de meeloopbalk en is
     alles daar kleiner; dan meet deze test twee verschillende podia tegen elkaar en valt hij om op
     iets wat klopt. */
  await page.evaluate(() => {
    const b = document.getElementById('petBox');
    if (b && b.scrollIntoView) b.scrollIntoView({ block: 'center' });
    try { chispaBalkCheck(); } catch (e) {}
  });
  await page.waitForTimeout(300);
  await page.evaluate(() => { mezclaWis(); document.querySelectorAll('.chmez').forEach((e) => e.remove()); });
  await page.evaluate(() => { mezclaKies('tapa', TAPAS[0].id); mezclaKies('baile', BAILES[0].id); });
  await page.waitForTimeout(400);
  /* v23.36: hij krijgt dezelfde klasse en dezelfde animatieduur als Chispa. Dat is het punt: een
     eigen animatie die er ongeveer op lijkt kan uit de pas lopen, deze niet. */
  const mee = await page.evaluate(() => {
    const el = document.querySelector('.chmez');
    if (!el) return null;
    const b = BAILES.filter((x) => x.id === mezclaBaile)[0];
    /* Niet vergelijken met chispaBox().style: welke box er danst hangt ervan af of je naar haar
       kijkt of naar de meeloopbalk, en dat wisselt tijdens het scrollen. Wat vastligt is de bron:
       de duur hoort de slagen-per-bpm van deze dans te zijn, en geen eigen benadering. */
    const hoort = b ? Math.round(b.slagen * 60 / b.bpm * 1000) / 1000 : null;
    const zij = document.getElementById('petBox');
    return {
      klas: el.className,
      danst: !!(b && el.classList.contains(b.klas)),
      duur: el.style.animationDuration,
      hoort: hoort === null ? null : hoort + 's',
      hoogEl: Math.round(el.getBoundingClientRect().height),
      hoogZij: zij ? Math.round(zij.getBoundingClientRect().height) : 0
    };
  });
  ok(mee, 'er staat een meedanser naast haar');
  ok(mee && mee.danst, 'met dezelfde dansklasse als Chispa (' + (mee ? mee.klas : '-') + ')');
  ok(mee && mee.duur && mee.duur === mee.hoort,
     'en met de duur die uit de bpm van deze dans volgt (' + (mee ? mee.duur + ' tegenover ' + mee.hoort : '-') + ')');
  ok(mee && mee.hoogZij > 0 && mee.hoogEl > mee.hoogZij * 0.3 && mee.hoogEl < mee.hoogZij * 1.2,
     'ongeveer even groot als zij (' + (mee ? mee.hoogEl + ' tegenover ' + mee.hoogZij : '-') + ')');

  console.log('\n-- ook als je de tapa als laatste aantikt, danst hij --');
  await page.evaluate(() => { mezclaWis(); document.querySelectorAll('.chmez').forEach((e) => e.remove()); });
  await page.locator('#baileRij button.bailechip').nth(1).click();
  await page.waitForTimeout(400);
  await page.locator('#tapaMenuRij button.tapachip').nth(1).click();
  await page.waitForTimeout(600);
  const andersom = await page.evaluate(() => ({
    mee: !!document.querySelector('.chmez'),
    bezig: !!(chispaBox() && chispaBox().classList.contains('chbezig'))
  }));
  ok(andersom.mee, 'de meedanser staat er ook als de tapa het laatste tikje was');
  ok(andersom.bezig, 'en Chispa danst dan zelf ook, in plaats van alleen de naam te zeggen');

  console.log('\n-- dezelfde nog eens telt niet dubbel --');
  const voorHerhaling = await page.evaluate(() => { mezclaWis(); return (S.mezcla || []).length; });
  await page.locator('#tapaMenuRij button.tapachip').first().click();
  await page.waitForTimeout(300);
  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(500);
  const weer = await page.evaluate(() => ({
    mezclas: (S.mezcla || []).length,
    nieuw: !!document.querySelector('#mezclaStrip .mezNieuw')
  }));
  ok(weer.mezclas === voorHerhaling, 'dezelfde combinatie telt niet twee keer (' + weer.mezclas + ')');
  ok(!weer.nieuw, 'en hij doet ook niet alsof hij nieuw is');

  console.log('\n-- de teller kan niet boven zijn noemer uitkomen --');
  const tel = await page.evaluate(() => {
    S.mezcla = (S.mezcla || []).concat(['bestaat-niet|salsa']);
    mezclaTeken(false);
    const t = (document.getElementById('mezclaTel') || {}).innerText || '';
    const m = t.match(/(\d+)\D+(\d+)/);
    return { tekst: t, gevonden: m ? +m[1] : -1, totaal: m ? +m[2] : -1, echt: TAPAS.length * BAILES.length };
  });
  ok(tel.totaal === tel.echt, 'de noemer is achttien maal acht (' + tel.totaal + ')');
  ok(tel.gevonden <= tel.totaal, 'en de teller blijft eronder (' + tel.tekst.replace(/\n/g, ' ') + ')');

  console.log('\n-- opnieuw maakt de vakjes leeg --');
  await page.evaluate(() => { mezclaTapa = 'pulpo'; mezclaBaile = 'tango'; mezclaTeken(false); });
  await page.waitForTimeout(200);
  await page.click('#btnMezWis');
  await page.waitForTimeout(300);
  const leeg = await page.evaluate(() => document.querySelectorAll('#mezclaStrip .mezVak.leeg').length);
  ok(leeg === 2, 'na "opnieuw" staan er weer twee lege vakjes (' + leeg + ')');

  const echt = errors.filter((e) => !/Failed to load resource|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten (' + echt.length + ')');
  if (echt.length) echt.forEach((e) => console.log('  -> ' + e));

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
'''

CIJFERBUGS = r'''// v22.10: de twee rekenfouten op het voortgangsscherm, elk met een test die ze niet terug laat komen.
//
// 1. Luisteren stond op "Escuchar · 55/6 · 100%". Tot v21.2 schreef Dictado zijn zinnen in
//    S.comp.luisteren; die oude ids staan bij bestaande profielen nog in de state en werden meegeteld
//    tegen een noemer van zes luisterscenes. pct() knipt op 100, dus de fout zag eruit als een score.
// 2. Het tempo meldde "15,9 nieuwe woorden per dag (het maximum is 15)". S.newIntro telt élk nieuw
//    woord, ook uit de spellen en het boek; die 15 ging alleen over de dagportie in de les.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwCb' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  // ---- 1. de teller van Luisteren kan zijn eigen noemer niet meer voorbij ----
  const vervuild = await page.evaluate(() => {
    S.comp = S.comp || {};
    S.comp.luisteren = {};
    // vijftig oude Dictado-zinnen, precies zoals ze in een profiel van voor v21.2 staan
    for (let i = 1; i <= 50; i++) S.comp.luisteren['s' + i] = true;
    // plus twee echte luisterscenes
    S.comp.luisteren[AUDICIONES[0].id] = true;
    S.comp.luisteren[AUDICIONES[1].id] = true;
    const c = berekenCompetenties();
    return { teller: c.luisteren.teller, noemer: c.luisteren.noemer, pct: c.luisteren.pct,
             scenes: AUDICIONES.length };
  });
  ok(vervuild.noemer === vervuild.scenes, 'de noemer is het aantal luisterscenes: ' + vervuild.noemer);
  ok(vervuild.teller === 2, 'alleen echte scenes tellen mee, de 50 oude zin-ids niet: ' + vervuild.teller);
  ok(vervuild.teller <= vervuild.noemer, 'de teller kan de noemer niet meer voorbij');
  ok(vervuild.pct === Math.round(2 / vervuild.scenes * 100), 'en het percentage klopt dus ook: ' + vervuild.pct + '%');

  const alles = await page.evaluate(() => {
    S.comp.luisteren = {};
    AUDICIONES.forEach((sc) => { S.comp.luisteren[sc.id] = true; });
    return berekenCompetenties().luisteren;
  });
  ok(alles.pct === 100 && alles.teller === alles.noemer, 'alle scenes gedaan is nog steeds gewoon 100%');

  // ---- 1b. en ze worden ook echt uit je profiel gegooid, niet alleen bij het rekenen genegeerd ----
  const opgeruimd = await page.evaluate(() => {
    // v22.11: de losse vlag compOpgeruimd is vervangen door het schemanummer. Een state zonder
    // nummer is er een van voor die versie, dus de migratie draait.
    const vuil = { comp: { luisteren: {}, schrijven: { s1: true } } };
    for (let i = 1; i <= 50; i++) vuil.comp.luisteren['s' + i] = true;
    vuil.comp.luisteren[AUDICIONES[0].id] = true;
    const schoon = normaliseerState(vuil);
    return {
      over: Object.keys(schoon.comp.luisteren),
      vlag: schoon.schema,
      schrijvenIntact: Object.keys(schoon.comp.schrijven).length
    };
  });
  ok(opgeruimd.over.length === 1, 'de vijftig oude sleutels zijn echt weg uit de state: ' + opgeruimd.over.length + ' over');
  ok(opgeruimd.over[0] && /^esc|^aud|.+/.test(opgeruimd.over[0]), 'de echte luisterscene staat er nog: ' + opgeruimd.over[0]);
  ok(opgeruimd.vlag === 2, 'en het schemanummer staat op 2, zodat dit niet elke keer opnieuw hoeft');
  ok(opgeruimd.schrijvenIntact === 1, 'comp.schrijven wordt niet aangeraakt: daar is de geldige verzameling niet bekend');

  const tweedeKeer = await page.evaluate(() => {
    const al = { schema: SCHEMA, comp: { luisteren: { s99: true }, schrijven: {} } };
    return Object.keys(normaliseerState(al).comp.luisteren).length;
  });
  ok(tweedeKeer === 1, 'een profiel dat al opgeruimd is wordt niet nog eens doorgespit');

  // ---- 2. de tempozin belooft geen maximum meer dat niet begrenst ----
  const zin = await page.evaluate(() => {
    const t = today();
    S.newIntro = {}; S.xp = {};
    // twee actieve dagen, 40 nieuwe woorden: een tempo dat ver boven de dagportie ligt
    S.newIntro[t] = 25; S.xp[t] = 100;
    const g = new Date(Date.now() - 86400000);
    const gis = g.getFullYear() + '-' + String(g.getMonth() + 1).padStart(2, '0') + '-' + String(g.getDate()).padStart(2, '0');
    S.newIntro[gis] = 15; S.xp[gis] = 100;
    const el = document.createElement('div');
    // v23.32: de cijfers staan op hun eigen scherm, niet meer onder Profiel
    try { show('voortgang'); } catch (e) {}
    return { tekst: (document.getElementById('statsCard') || el).innerText || '', portie: nieuwPerDag() };
  });
  await page.waitForTimeout(400);
  const tekst = await page.evaluate(() => {
    try { show('voortgang'); } catch (e) {}
    return (document.getElementById('statsCard') || {}).innerText || '';
  });
  ok(!/maximum is 15/.test(tekst), 'de zin belooft geen hardgecodeerd maximum van 15 meer');
  ok(!/het maximum is/.test(tekst), 'en ook geen ander maximum dat het gemeten getal niet begrenst');
  /* v23.37: de zin die dit droeg is weg. Hij stond in het blok "Jouw ontwikkeling", dat dezelfde
     getallen nog een derde keer in proza zette en dat Stefan om die reden liet vervallen. Wat deze
     suite bewaakt blijft overeind en wordt zelfs breder: nergens op dit scherm mag een hardgecodeerd
     maximum staan dat het gemeten getal niet begrenst. Daarom kijkt hij nu naar het hele scherm en
     niet alleen naar de cijferkaart. */
  const heleScherm = await page.evaluate(() => (document.getElementById('tab-voortgang') || {}).innerText || '');
  ok(!/maximum is/.test(heleScherm), 'ook nergens anders op het scherm staat een hardgecodeerd maximum');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
'''

for _naam, _inhoud in [("pw-voortgang.js", VOORTGANG), ("pw-mezcla.js", MEZCLA),
                       ("pw-cijferbugs.js", CIJFERBUGS)]:
    _pad = os.path.join(MAP_S, _naam)
    with io.open(_pad, encoding="utf-8") as f:
        _oud = f.read()
    if "v23.37" in _oud:
        print("  " + _naam + ": al bijgewerkt")
        continue
    with io.open(_pad, "w", encoding="utf-8") as f:
        f.write(_inhoud)
    print("  " + _naam + ": bijgewerkt")
