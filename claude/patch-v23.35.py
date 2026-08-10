#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.35: echte dansmuziek, en de dans loopt erop mee. Plus drie dingen weg.

Stefan: "de dansjes komen niet overeen met de muziekstijl. Het ritme is anders. Kunnen we met
elevenlabs dit echter maken?" En daarna: "die muziek wil ik nu, verder kan dit ook allemaal weg"
(de knoppenrij Fiesta/Serenade/Dagcadeautje, de plaquette El Gran Menú, en het figuurkiezertje).

DE MUZIEK
Wat er tot nu toe speelde was geen muziek maar synthese in de browser: per dans een patroon van
kick, tik, palma, bas en melodie. Op papier klopt dat ritme, in je oren niet, en dat is precies wat
hij hoorde. Eleven Music (POST /v1/music) maakt echte instrumentale tracks uit een tekstprompt, met
commercieel gebruik erbij. tools/generate-baile-audio.js maakt er acht, één per dans, en zet ze in
audio/baile/. Staat het bestand er niet, dan blijft de synthese doen wat hij deed: niemand hoort
stilte omdat een download niet lukte.

En dan het echte antwoord op "het ritme is anders". Elke dans krijgt een bpm, en de animatie duurt
vanaf nu een vast aantal slagen bij die bpm in plaats van een getal dat ik ooit op gevoel in de CSS
heb gezet. Dezelfde bpm gaat in de prompt waarmee de muziek gemaakt wordt. De dans loopt dus mee
omdat hij eruit gerekend is, niet omdat het toevallig klopt.

Wat dat verschuift, per dans (oude duur -> nieuwe):

  salsa      0.62s -> 0.63s  (2 slagen op 190)      flamenco  1.50s -> 2.00s  (6 slagen op 180)
  cumbia     1.35s -> 1.26s  (2 slagen op 95)       merengue  0.34s -> 0.45s  (1 slag op 132)
  bachata    1.70s -> 1.88s  (4 slagen op 128)      tango     2.10s -> 2.07s  (4 slagen op 116)
  reggaeton  0.50s -> 0.62s  (1 slag op 96)         jarabe    0.56s -> 0.45s  (1 slag op 132)

Merengue, reggaeton en jarabe verschuiven het meest, en dat is geen toeval: dat waren de drie die
het verst naast de maat liepen. Flamenco gaat naar zes slagen omdat de compás er twaalf heeft;
vierenhalve slag was nergens op gebaseerd.

WAT ER WEG GAAT
De knoppenrij, de plaquette en het figuurkiezertje. Twee gevolgen die je moet weten:

1. Het dagcadeautje leverde in tachtig procent van de gevallen één of twee tapas op. Dat is dus een
   bron van tapas die verdwijnt; wat overblijft is wat je met leren verdient. Dat lijkt me ook de
   bedoeling, maar het is een gevolg en geen bijzaak.
2. De wens "Chispa wil haar cadeautje openmaken" is daarmee niet meer te vervullen. Een wens die je
   niet kunt vervullen is erger dan geen wens, dus die is uit de lijst. De andere drie kunnen nog
   steeds: een tapa geven, muziek maken (dansen) en haar aaien.

petVorm() valt terug op "clásica", dus wie ooit iets anders koos houdt dat gewoon; het kiezertje is
weg, de keuze niet. Zelfde afspraak als bij momentTekst() in v23.31.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
MAP_S = os.path.join(WORTEL, "test", "suites")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function baileGeluid" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)
if 'var APP_VERSIE = "v23.34";' not in src:
    print("Deze index.html staat niet op v23.34. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ================================================================ 1. bpm en slagen per dans
BPM = {"salsa": (190, 2), "flamenco": (180, 6), "cumbia": (95, 2), "merengue": (132, 1),
       "bachata": (128, 4), "tango": (116, 4), "reggaeton": (96, 1), "jarabe": (132, 1)}
for bid, (bpm, slagen) in BPM.items():
    anker = '{id:"%s",' % bid
    aantal = src.count(anker)
    assert aantal >= 1, "dans-anker %s ontbreekt" % bid
    # alleen de regel in BAILES: die heeft ook een klas-veld
    i = src.index('var BAILES = [')
    j = src.index('function bailePorDia()')
    blok = src[i:j]
    assert blok.count(anker) == 1, "dans-anker %s komt %d keer voor in BAILES" % (bid, blok.count(anker))
    blok = blok.replace(anker, '{id:"%s", bpm:%d, slagen:%s,' % (bid, bpm, slagen), 1)
    src = src[:i] + blok + src[j:]

# ================================================================ 2. de animatie volgt de slag
rep(
    """function chispaMove(klas, ms, klaar){
  var box = chispaBox();
  if(!box || !box.classList){ if(klaar) klaar(); return false; }
  CHISPA_MOVES.forEach(function(k){ box.classList.remove(k); });
  box.classList.remove("petbounce");
  void(box.offsetWidth || 0);
  box.classList.add("chbezig");
  box.classList.add(klas);""",
    """/* v23.35: duur is de duur van de hele beweging, tempo is de lengte van één cyclus. Dat tempo stond
   tot nu toe in de CSS als een getal dat ik op gevoel had gekozen; nu komt het uit de bpm van de
   dans, dezelfde bpm waarmee de muziek gemaakt is. Geen tempo meegegeven, dan blijft de CSS staan
   en verandert er niets: alles wat niet danst raakt dit niet. */
function chispaMove(klas, ms, klaar, tempoSec){
  var box = chispaBox();
  if(!box || !box.classList){ if(klaar) klaar(); return false; }
  CHISPA_MOVES.forEach(function(k){ box.classList.remove(k); });
  box.classList.remove("petbounce");
  box.style.animationDuration = "";
  void(box.offsetWidth || 0);
  box.classList.add("chbezig");
  box.classList.add(klas);
  if(tempoSec) box.style.animationDuration = (Math.round(tempoSec * 1000) / 1000) + "s";""")

rep(
    """    chispaPodia(box).forEach(function(b2){ b2.classList.remove(klas); b2.classList.remove("chbezig"); });
    if(klaar) klaar();""",
    """    chispaPodia(box).forEach(function(b2){
      b2.classList.remove(klas); b2.classList.remove("chbezig");
      b2.style.animationDuration = "";
    });
    if(klaar) klaar();""")

# ================================================================ 3. echte muziek, met terugval
rep(
    """function chispaBaila(baile, stilBeeld){""",
    """/* v23.35: eerst de echte opname, en de synthese als die er niet is.

   De terugval hangt aan het foutsignaal van het audio-element en niet aan een lijstje van welke
   bestanden er zouden moeten zijn. Zo'n lijstje loopt namelijk uit de pas met wat er echt in de map
   staat, en dan hoor je stilte terwijl alles "klopt". Het kost wel een tel: de synthese begint pas
   als de browser zegt dat het bestand er niet is. Dat is de goedkope kant om fout te zitten. */
var chBaileAudio = null;
function baileStop(){
  if(!chBaileAudio) return;
  try { chBaileAudio.pause(); } catch(e){}
  chBaileAudio = null;
}
function baileGeluid(b, ms){
  if(S.chispaStil) return 0;
  baileStop();
  var terug = function(){ try { baileMuziek(b.id, ms); } catch(e){} };
  var a;
  try { a = new Audio("audio/baile/" + b.id + ".mp3"); } catch(e){ terug(); return 0; }
  a.volume = 0.5;
  a.addEventListener("error", terug);
  chBaileAudio = a;
  try {
    var p = a.play();
    if(p && p.catch) p.catch(terug);
  } catch(e){ terug(); }
  setTimeout(function(){
    if(chBaileAudio !== a) return;
    // uitfaden in plaats van afkappen: een track die middenin stopt klinkt als een storing
    var stap = 0;
    var t = setInterval(function(){
      stap++;
      try { a.volume = Math.max(0, 0.5 * (1 - stap / 8)); } catch(e){}
      if(stap >= 8){ clearInterval(t); baileStop(); }
    }, 60);
  }, Math.max(600, ms - 500));
  return ms;
}
function chispaBaila(baile, stilBeeld){""")

rep(
    """  chispaVloer(true);
  chispaReis(true, 4400);
  try { baileMuziek(b.id, 4400); } catch(e){}
  chispaNotas(6);""",
    """  /* De hele beweging duurt een heel aantal maten van deze dans, en niet 4400 milliseconden omdat
     dat een rond getal is. Zo eindigt ze op een tel en niet middenin een pas. */
  var tempo = (b.bpm && b.slagen) ? b.slagen * 60 / b.bpm : 0;
  var duur = tempo ? Math.round(4400 / (tempo * 1000) ) : 0;
  duur = tempo ? Math.max(1, duur) * tempo * 1000 : 4400;
  duur = Math.round(duur);
  chispaVloer(true);
  chispaReis(true, duur);
  try { baileGeluid(b, duur); } catch(e){}
  chispaNotas(6);""")

rep(
    """  if(b.id === "flamenco" || b.id === "jarabe") chispaProp("chguit", "🎸", 4600);
  if(b.id === "cumbia" || b.id === "merengue"){ chispaProp("chmar", "🪇", 4600); chispaProp("chmar2", "🪇", 4600); }
  chispaMove(b.klas, 4400, function(){ chispaVloer(false); chispaReis(false); });""",
    """  if(b.id === "flamenco" || b.id === "jarabe") chispaProp("chguit", "🎸", duur + 200);
  if(b.id === "cumbia" || b.id === "merengue"){ chispaProp("chmar", "🪇", duur + 200); chispaProp("chmar2", "🪇", duur + 200); }
  chispaMove(b.klas, duur, function(){ chispaVloer(false); chispaReis(false); }, tempo);""")

rep(
    """  if(gewekt) chispaSlaapHerstel(6100);   // daarna mag ze weer verder slapen""",
    """  if(gewekt) chispaSlaapHerstel(duur + 1700);   // daarna mag ze weer verder slapen""")

rep(
    """function chMuziekUit(){
  var ac = avtCtx();""",
    """function chMuziekUit(){
  baileStop();                       // v23.35: de opname hoort net zo goed te stoppen als de synthese
  var ac = avtCtx();""")

# ================================================================ 4. wat er weg gaat
rep(
    """    "<div class='row center'>"+
    "<button class='ghost' id='btnFiesta'>\\ud83c\\udf89 \\u00a1Fiesta!</button>"+
    "<button class='ghost' id='btnSerenade'>\\ud83c\\udfb6 Serenade</button>"+
    "<button class='ghost' id='btnCadeau' "+(cadeauGehad?"disabled style='opacity:.5'":"")+">\\ud83c\\udf81 "+(cadeauGehad?ct("Morgen weer","Back tomorrow"):ct("Dagcadeautje","Daily gift"))+"</button>"+
    "</div>"+
    "</div>";""",
    """    /* v23.35, op Stefans verzoek: de rij Fiesta/Serenade/Dagcadeautje is weg. Wat je met haar doet
       staat nu in de twee rijen erboven, en aaien doe je door haar aan te tikken. De functies
       blijven bestaan (het feestje komt nog vanzelf voorbij), alleen de knoppen niet. */
    "</div>";""")

rep(
    """  var bfi = document.getElementById("btnFiesta");
  if(bfi) bfi.onclick = function(){ chispaFiesta(); };
  var bs = document.getElementById("btnSerenade");
  if(bs) bs.onclick = chispaSerenade;
  var bc = document.getElementById("btnCadeau");
  if(bc && !cadeauGehad) bc.onclick = chispaCadeau;
""", """""")

rep(
    """      (S.tapaFinale ? "<div class='plaquette' id='tapaPlaquette'><b><span class='es'>El Gran Men\\u00fa</span></b>"+
        "<span>"+ct("alle "+TAPAS.length+" tapas geproefd \\u00b7 ","all "+TAPAS.length+" tapas tasted \\u00b7 ")+S.tapaFinale+"</span></div>" : "")+
""", """""")

rep(
    """  // Bewust "figuur" en niet "vorm": twee regels hoger staat "Vorm 7/8", en dat gaat over haar
  // leeftijd. Twee betekenissen van hetzelfde woord op dezelfde kaart is hoe je iemand kwijtraakt.
  html += "<p class='zorglabel' style='margin:12px 0 0'>"+ct("Haar figuur","Her build")+"</p>"+
    "<div class='vormrij' id='vormRij'>"+vr+"</div>";
""",
    """  /* v23.35: het figuurkiezertje is weg, op Stefans verzoek. petVorm() valt terug op "clásica", dus
     wie ooit iets anders koos houdt dat: de keuze verdwijnt niet, alleen het kiezertje. vr wordt
     hieronder niet meer gebruikt en blijft staan omdat PET_VORMEN nog de tekening voedt. */
""")

# de wens die niet meer te vervullen is
rep(
    """  {id:"regalo", e:"🎁", es:"Hoy Chispa quiere abrir su regalo.", nl:"Chispa wil haar cadeautje openmaken.",  en:"Chispa wants to open her gift."}
""", """""")

rep(
    """  {id:"mimos",  e:"🤗", es:"Hoy Chispa quiere mimos.",           nl:"Chispa wil vandaag geknuffeld worden.", en:"Chispa wants cuddles today."},
""",
    """  /* v23.35: de wens "haar cadeautje openmaken" is weg. Het dagcadeautje had een knop en die knop
     is weg, dus die wens was niet meer te vervullen, en een wens die je niet kunt vervullen is erger
     dan geen wens. De drie die overblijven kunnen alle drie: een tapa geven, laten dansen, aaien. */
  {id:"mimos",  e:"🤗", es:"Hoy Chispa quiere mimos.",           nl:"Chispa wil vandaag geknuffeld worden.", en:"Chispa wants cuddles today."}
""")

rep('var APP_VERSIE = "v23.34";', 'var APP_VERSIE = "v23.35";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
with io.open(PAD_VER, "w", encoding="utf-8") as f:
    f.write("v23.35\n")
print("v23.35 toegepast op", PAD)


# ================================================================ 5. de suites
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


suite("pw-chispakaarten.js", [
    ("""      knoppen: ['btnFiesta', 'btnSerenade', 'btnCadeau'].filter((i) => !!c.querySelector('#' + i)).length,""",
     """      knoppen: ['btnFiesta', 'btnSerenade', 'btnCadeau'].filter((i) => !!c.querySelector('#' + i)).length,
      mezcla: !!c.querySelector('#mezclaStrip'),"""),
    ("""  ok(pet.knoppen === 3, 'kaart 1: de drie dingen die je met haar kunt doen (' + pet.knoppen + ')');""",
     """  /* v23.35, op Stefans verzoek: de knoppenrij Fiesta/Serenade/Dagcadeautje is weg. Wat je met haar
     doet staat in de twee rijen (een tapa geven, laten dansen) en in de mezcla ertussen; aaien doe je
     door haar aan te tikken. Deze suite bewaakt vanaf nu dat er iets te doen is, niet dat er precies
     drie knoppen staan. */
  ok(pet.knoppen === 0, 'kaart 1: geen losse knoppenrij meer (' + pet.knoppen + ')');
  ok(pet.mezcla, 'kaart 1: de mezcla staat er wel, want dat is wat je hier doet');"""),
], "v23.35")

suite("pw-finale.js", [
    ("""  ok(plaq.erIs && plaq.inVitrine, 'de plaquette staat bij Chispa, waar de verzameling staat');
  ok(/Gran Men/i.test(plaq.tekst), 'met dezelfde naam als de ceremonie');
  ok(plaq.datum, 'en de datum waarop je het afmaakte staat erop');""",
     """  /* v23.35, op Stefans verzoek: de plaquette is weg. De ceremonie zelf blijft en komt één keer,
     op het moment dat je de laatste tapa geeft; wat er daarna van overblijft is de volle rij tapas,
     en dat is een prima bewijs. S.tapaFinale blijft bewaard, zodat de ceremonie niet opnieuw komt. */
  ok(!plaq.erIs, 'de plaquette staat er niet meer');""")
], "v23.35")

suite("pw-eigen.js", [
    ("""  // --- 2. Twee betekenissen van "vorm" naast elkaar zou niemand snappen ---
  ok(/Vorm \d\/8|Form \d\/8/.test(aanbod.tekst), 'de groeiteller heet nog steeds Vorm n/8 (dat is haar leeftijd)');
  ok(/figuur|build/i.test(aanbod.tekst), 'en de figuurkeuze heet daarom géén vorm');""",
     """  // --- 2. De groeiteller heet Vorm n/8, en dat gaat over haar leeftijd ---
  ok(/Vorm \d\/8|Form \d\/8/.test(aanbod.tekst), 'de groeiteller heet nog steeds Vorm n/8 (dat is haar leeftijd)');
  /* v23.35: hier stond dat de figuurkeuze géén "vorm" mocht heten, omdat twee betekenissen van
     hetzelfde woord op één kaart iemand kwijtraken. Dat probleem is opgelost door het kiezertje weg
     te halen, dus de eis vervalt met het ding waar hij over ging. */"""),
    ("""  await page.click("#vormRij button[data-vorm='esbelta']");
  await page.waitForTimeout(300);
  const naVorm = await page.evaluate(() => ({ id: petVorm().id, svg: document.getElementById('petBox').innerHTML }));
  ok(naVorm.id === 'esbelta', 'en een klik op esbelta verandert haar figuur');
  ok(naVorm.svg !== na.svg, 'ook dat zie je aan de tekening, niet alleen aan de knop');""",
     """  /* Het kiezertje is weg, maar de figuren moeten nog wel dóórwerken in de tekening: wie ooit
     esbelta koos heeft dat nog staan, en die tekening hoort er dan ook anders uit te zien. Dus
     zetten we hem hier rechtstreeks, precies zoals een oud profiel hem heeft staan. */
  await page.evaluate(() => { S.petVorm = 'esbelta'; try { persist(); } catch (e) {} renderPet(); });
  await page.waitForTimeout(300);
  const naVorm = await page.evaluate(() => ({ id: petVorm().id, svg: document.getElementById('petBox').innerHTML }));
  ok(naVorm.id === 'esbelta', 'een profiel dat ooit esbelta koos, heeft dat nog steeds');
  ok(naVorm.svg !== na.svg, 'en dat zie je nog steeds aan de tekening');"""),
    ("""    knoppenV: document.querySelectorAll('#vormRij button[data-vorm]').length,""",
     """    knoppenV: document.querySelectorAll('#vormRij button[data-vorm]').length,
    vormRij: !!document.getElementById('vormRij'),"""),
    ("""  ok(aanbod.knoppenV === aanbod.vormen.length, 'elk figuur heeft een eigen knop');""",
     """  /* v23.35, op Stefans verzoek: het figuurkiezertje is weg van het scherm. PET_VORMEN blijft
     bestaan, want die voedt de tekening, en petVorm() valt terug op clásica. Wie ooit iets anders
     koos houdt dat: de keuze is niet weggegooid, alleen het kiezertje. Wat hier nu vastligt is dat
     die terugval echt werkt, want anders zou een verwijderd kiezertje een lege tekening opleveren. */
  ok(!aanbod.vormRij, 'het figuurkiezertje staat niet meer op het scherm');
  ok(aanbod.vormen.length === 3 && aanbod.vNu === 'clasica',
     'maar de drie figuren bestaan nog en de terugval is clásica (' + aanbod.vNu + ')');"""),
], "v23.35")

suite("pw-v1949.js", [
    ("""  ok(wens.aantal >= 4 && /^¡/.test(wens.es) === false && /Chispa/.test(wens.es), 'de wens staat in het Spaans (' + wens.es + ')');""",
     """  /* v23.35: de wens "haar cadeautje openmaken" is weg omdat de knop weg is, en een wens die je niet
     kunt vervullen is erger dan geen wens. Er blijven er drie, en die kunnen alle drie: een tapa
     geven, laten dansen, aaien. */
  ok(wens.aantal >= 3 && /^¡/.test(wens.es) === false && /Chispa/.test(wens.es), 'de wens staat in het Spaans (' + wens.es + ')');"""),
], "v23.35")
