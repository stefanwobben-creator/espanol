#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.147: Aventura eruit.

Stefan, 20 aug: "nou we moeten denk ik echt dingen schrappen ook al is het goedkoop en er moet een
balans zijn tussen makkelijk te doen (ontspanning, beloning, leuk daarom kruiswoord en
woordenzoeker) maar andere dingen aventure, letras, musica zijn denk ik overbodig."

## De regel die eronder ligt

Zijn zin bevat een ontwerpregel die de app niet had: er zijn twee lagen met verschillende
maatstaven. Wat in je les zit wordt beoordeeld op wat het je leert. Wat in de Speeltuin staat wordt
beoordeeld op of het rust geeft: kort, geen falen, geen nadenken, en goedkoop te onderhouden.

Een woordenzoeker leert je niets, en dat is precies waarom hij mag blijven: dat is niet zijn werk.
Zolang hij nooit meetelt voor je niveau en nooit in de dagles staat, is hij eerlijk over wat hij is.

Wat er dan uit moet, is wat in geen van beide lagen thuishoort.

## Aventura (2057 regels, 4,1 procent van het bestand)

Een Zelda-achtige mini-RPG: vier werelden, eenentwintig schermen, gevechten, drie eindbazen, een
slangenspel, galgje en bommen. Het grootste enkele onderdeel van de app.

Pedagogisch is het woordherhaling in een spelverpakking, en die herhaling doet de SRS beter, want
die weet wanneer je iets moet terugzien. In 26 dagen staat er van Aventura geen enkel gegeven, van
niemand. En het concurreert met de dagles om precies dezelfde tien minuten.

Twee dingen bleven staan omdat de rest van de app ze gebruikt: de geluidsmotor (Chispa's serenade
draait erop) en het kruiswoord, dat om historische redenen in de code van het spel woonde.

## Letras blijft, en dat is een correctie

Ik had Letras aan Stefan beschreven als "vorm zonder betekeniscue, dus als les zwak, en niet eens
ontspannend". Dat klopt geen van beide, en het stond al in het bestand: je krijgt zeven letters én
een lijst open plekken met de Nederlandse betekenis erbij. Je haalt dus een Spaans woord op vanuit
de betekenis, met de letters als steun. Dezelfde beweging als het kruiswoord, en precies de trede
tussen herkennen en zelf schrijven.

En hij is met opzet de rustige: geen klok, geen levens, geen game over. Hij is in v22.1 gebouwd als
antwoord op "die snelheid game is leuk maar nog wel te intensief, ik bedoel iets nog meer casual".
Dat is exact de laag waar Stefan om vraagt.

## Wat er NIET uitgaat

**Música niet.** Stefan noemde hem, en hier overrule ik hem, met een reden. Het is geen lijst met
videolinks: elk lied heeft een geoogste set uitdrukkingen met uitleg die aan je huidige grammatica
hangt, plus vragen. Dat is authentieke input met expliciete aandacht, en het is de enige plek met
echt gesproken Spaans op tempo. Wat er wel mis mee is, is de plek: het staat als tegel in de
Speeltuin, dus je moet eraan denken. Dat is hetzelfde probleem dat lezen had voor v23.140, en het
heeft dezelfde oplossing: het inputblok in. Dat is de volgende ronde.

**Palabra Duel niet, nog niet.** Die staat verspreid door het bestand en hangt aan de groepen. Zijn
probleem is ook geen pedagogisch maar een bezettingsprobleem: met drie gebruikers vindt niemand een
tegenstander. Eigen ronde.

Bewaakt door test/suites/pw-geschrapt.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.147"

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


def knip(begin, eind, vervang=""):
    """Haalt alles weg vanaf het begin van `begin` tot aan het begin van `eind`. Twee korte ankers in
    plaats van tweeduizend regels als anker; beide moeten precies een keer voorkomen en `eind` moet
    achter `begin` liggen, anders knipt hij het verkeerde stuk eruit."""
    global src
    if not DOE_APP:
        return
    assert src.count(begin) == 1, "beginanker %d keer: %s" % (src.count(begin), begin[:120])
    assert src.count(eind) == 1, "eindanker %d keer: %s" % (src.count(eind), eind[:120])
    i = src.index(begin)
    j = src.index(eind)
    assert j > i, "eindanker ligt voor het beginanker"
    src = src[:i] + vervang + src[j:]


NIEUW_BLOK = r"""/* ================= GELUID (v23.147, was de Aventura-motor) =================

   Aventura is er in v23.147 uitgegaan (2057 regels, geen enkel spoor van gebruik in 26 dagen). Twee
   dingen uit dat blok bleven staan omdat de rest van de app ze gebruikt.

   Dit is het eerste: de geluidsmotor. Chispa's serenade en de ritmes op de muziekpagina draaien
   erop. De namen beginnen nog met avt en dat is met opzet zo gelaten: ze zitten in twintig
   aanroepen verderop en in S.avtStil, dat op ieders toestel staat opgeslagen. Een naam veranderen
   die niemand ziet is risico zonder opbrengst; deze regel is de uitleg die de naam mist.

   Wat wel is weggehaald: van de negen geluidjes in avtSfx bleven er drie over. Hart, kist, stap,
   encuentro, boom en baas hoorden bij het gevecht en dat gevecht is er niet meer. */
var avtAC = null, avtMuziekTimer = null, avtMuziekFrase = 0;
function avtCtx(){
  try{
    var AC = (typeof window !== "undefined") && (window.AudioContext || window.webkitAudioContext);
    if(!AC) return null;
    if(!avtAC) avtAC = new AC();
    if(avtAC.state === "suspended") avtAC.resume();
    return avtAC;
  }catch(e){ return null; }
}
function avtNoot(freq, wanneer, duur, type, vol){
  var ac = avtCtx(); if(!ac || S.avtStil || !freq) return;
  try{
    var o = ac.createOscillator(), g = ac.createGain();
    o.type = type || "square"; o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, wanneer);
    g.gain.linearRampToValueAtTime(vol || 0.04, wanneer + 0.015);
    g.gain.exponentialRampToValueAtTime(0.0001, wanneer + duur);
    o.connect(g); g.connect(ac.destination);
    o.start(wanneer); o.stop(wanneer + duur + 0.05);
  }catch(e){}
}
/* Spaanse gitaar: getokkelde snaren (twee licht ontstemde zaagtanden door een filter) */
var AVT_N = {E3:164.81, F3:174.61, Gs3:207.65, A3:220, B3:246.94, C4:261.63, D4:293.66, E4:329.63, F4:349.23, Gs4:415.30, A4:440, E2:82.41, F2:87.31, A2:110};
function avtPluk(freq, wanneer, duur, vol){
  var ac = avtCtx(); if(!ac || S.avtStil || !freq) return;
  try{
    var g = ac.createGain();
    g.gain.setValueAtTime(vol, wanneer);
    g.gain.exponentialRampToValueAtTime(0.0001, wanneer + duur);
    var f = ac.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = Math.min(freq*4, 4200); f.Q.value = 1;
    [-4, 4].forEach(function(det){
      var o = ac.createOscillator(); o.type = "sawtooth"; o.frequency.value = freq; o.detune.value = det;
      o.connect(f); o.start(wanneer); o.stop(wanneer + duur + 0.05);
    });
    f.connect(g); g.connect(ac.destination);
  }catch(e){}
}
function avtPalmas(wanneer, vol){
  var ac = avtCtx(); if(!ac || S.avtStil) return;
  try{
    var n = Math.floor(ac.sampleRate * 0.045);
    var buf = ac.createBuffer(1, n, ac.sampleRate);
    var d = buf.getChannelData(0);
    for(var i=0;i<n;i++){ d[i] = (Math.random()*2 - 1) * Math.pow(1 - i/n, 2); }
    var src = ac.createBufferSource(); src.buffer = buf;
    var bp = ac.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 1900; bp.Q.value = 0.9;
    var g = ac.createGain(); g.gain.value = vol;
    src.connect(bp); bp.connect(g); g.connect(ac.destination); src.start(wanneer);
  }catch(e){}
}
/* Andalusische cadens Am-G-F-E met tresillo-ritme (3-3-2), het flamenco-DNA */
var AVT_CADENS = [
 {bas:110.00, mel:[659.26,0,523.25,0,440,0,493.88,523.25]},
 {bas:98.00,  mel:[493.88,0,392.00,0,587.33,523.25,493.88,440]},
 {bas:87.31,  mel:[440,0,349.23,0,523.25,493.88,440,415.30]},
 {bas:82.41,  mel:[415.30,440,493.88,415.30,329.63,0,415.30,0]}
];
var AVT_FALSETA = [659.26,587.33,523.25,493.88,440,415.30,349.23,329.63];
function avtMuziekStap(){
  if(funView !== "avt" || !avt || avt.victory){ avtMuziekStop(); return; }
  var ac = avtCtx(); if(!ac){ return; }
  var acht = (avt.gevecht && avt.gevecht.baas) ? 0.125 : 0.165;
  var t0 = ac.currentTime + 0.05;
  var falseta = avtMuziekFrase % 2 === 1;
  AVT_CADENS.forEach(function(bar, b){
    var tb = t0 + b * 8 * acht;
    [0,3,6].forEach(function(i){
      avtPluk(bar.bas, tb + i*acht, acht*2.8, 0.11);
      avtPluk(bar.bas*2, tb + i*acht, acht*1.6, 0.045);
      avtPalmas(tb + i*acht, i === 0 ? 0.10 : 0.055);
    });
    if(falseta && b === 3){
      AVT_FALSETA.forEach(function(f, i){ avtPluk(f, tb + i*acht*0.5, acht*1.1, 0.055); });
      avtPluk(329.63, tb + 4*acht, acht*3.6, 0.075);
      avtPalmas(tb + 4*acht, 0.09);
    } else {
      bar.mel.forEach(function(f, i){ if(f) avtPluk(f, tb + i*acht, acht*1.9, 0.06); });
    }
  });
  avtMuziekFrase++;
  avtMuziekTimer = setTimeout(avtMuziekStap, 4 * 8 * acht * 1000);
}
function avtMuziekStart(){ if(avtMuziekTimer || S.avtStil) return; avtMuziekStap(); }
function avtMuziekStop(){ if(avtMuziekTimer){ clearTimeout(avtMuziekTimer); avtMuziekTimer = null; } }
function avtSfx(naam){
  var ac = avtCtx(); if(!ac || S.avtStil) return;
  var t = ac.currentTime + 0.02;
  if(naam === "goed"){ avtPluk(AVT_N.A4,t,0.18,0.10); avtPluk(659.26,t+0.07,0.28,0.10); }
  if(naam === "fout"){ avtNoot(110,t,0.28,"sawtooth",0.07); avtNoot(103.8,t+0.05,0.25,"sawtooth",0.05); }
  if(naam === "win"){ [AVT_N.E4,AVT_N.Gs4,AVT_N.B3,AVT_N.A4,523.25,659.26,880].forEach(function(f,i){ avtPluk(f,t+i*0.11,0.3,0.09); avtPluk(f/2,t+i*0.11,0.35,0.07); }); avtPalmas(t+0.77,0.12); avtPalmas(t+0.99,0.12); }
}

/* ================= CRUCIGRAMA (v23.147) =================

   Het tweede dat uit Aventura bleef staan, en dat was bijna een ongeluk: het kruiswoord woonde in
   de code van het spel dat eruit ging. Stefan wil hem juist houden, en pedagogisch is hij van de
   lichte spellen de beste: een omschrijving vraagt het woord terug, dus je haalt betekenis naar
   vorm op. Dat is precies wat een woordenzoeker niet doet.

   Meeverhuisd en hernoemd, want de oude namen wezen naar een spel dat niet meer bestaat:
   avtKruisCellen -> kruisCellen, avtKruisBekend -> kruisBekend, avtSrsBij -> spelGetyptBij.

   spelGetyptBij() is de reden dat het kruiswoord meetelt en de woordenzoeker niet: je typt het
   woord, dus het is ophalen en niet herkennen, en dan mag het doosje ook echt omhoog (tot srsTop
   in plaats van tot SPEL_PLAFOND, zie spelSrsBij).

   De teksten kwamen uit AVT_TXT, de vertaaltabel van het spel. Die is weg, dus ze staan nu gewoon
   met ct() op hun plek. En de lupa (het voorwerp waarmee je in het spel een hint kocht) bestaat
   niet meer: de hint hangt nu alleen nog aan opts.hintAltijd. */
function spelGetyptBij(w, goed, getypt){
  var t = today();
  var st = S.srs[w.id];
  if(!st){ st = {box:0, due:t}; S.newIntro[t] = (S.newIntro[t]||0) + 1; }
  st.n = (st.n||0) + 1;
  if(goed){
    if(getypt) st.k = 1;
    if(st.bd !== t){
      st.bd = t;
      srsOmhoog(st, getypt ? srsTop() : zelfDrempel());   // v23.132, zie srsStap
      st.due = addDays(t, INTERVALS[st.box]);
    }
    addXP(2); trackPoging(false);
  } else {
    st.box = 0; st.due = t; st.f = (st.f||0) + 1;
    logError(w.id, "woord", w.tag, w.es);
    addXP(1);
  }
  S.srs[w.id] = st; persist(); updateBadge();
}
function kruisBouw(){
  var kandidaten = gameVoorrang(wsWoordPool()).filter(function(k){ return k.woord.length >= 4 && k.woord.length <= 8; });
  if(kandidaten.length < 4){ toast("📚 " + ct("Leer eerst wat meer woordjes voor een kruiswoord!", "Learn a few more words first for a crossword!")); return null; }
  var beste = null;
  for(var poging = 0; poging < 6 && !beste; poging++){
    var pool = kandidaten.slice(0, 18).sort(function(){ return Math.random() - 0.5; });
    var cellen = {}, woorden = [];
    function zet(k, x, y, dx, dy){
      for(var i = 0; i < k.woord.length; i++){ cellen[(x + dx*i) + "," + (y + dy*i)] = k.woord.charAt(i); }
      woorden.push({k:k, x:x, y:y, dx:dx, dy:dy, klaar:false, hint:false});
    }
    function past(k, x, y, dx, dy){
      var kruist = false;
      for(var i = 0; i < k.woord.length; i++){
        var cx = x + dx*i, cy = y + dy*i;
        var bez = cellen[cx + "," + cy];
        if(bez){
          if(bez !== k.woord.charAt(i)) return false;
          kruist = true;
        } else {
          if(dx && (cellen[cx + "," + (cy-1)] || cellen[cx + "," + (cy+1)])) return false;
          if(dy && (cellen[(cx-1) + "," + cy] || cellen[(cx+1) + "," + cy])) return false;
        }
      }
      if(cellen[(x - dx) + "," + (y - dy)]) return false;
      if(cellen[(x + dx*k.woord.length) + "," + (y + dy*k.woord.length)]) return false;
      return kruist;
    }
    zet(pool[0], 0, 0, 1, 0);
    for(var w = 1; w < pool.length && woorden.length < 6; w++){
      var kand = pool[w], geplaatst = false;
      for(var wi = 0; wi < woorden.length && !geplaatst; wi++){
        var pw = woorden[wi];
        var dx = pw.dx ? 0 : 1, dy = pw.dx ? 1 : 0;
        for(var a = 0; a < pw.k.woord.length && !geplaatst; a++){
          var ch = pw.k.woord.charAt(a);
          for(var b = 0; b < kand.woord.length && !geplaatst; b++){
            if(kand.woord.charAt(b) !== ch) continue;
            var nx = pw.x + pw.dx*a - dx*b, ny2 = pw.y + pw.dy*a - dy*b;
            if(past(kand, nx, ny2, dx, dy)){ zet(kand, nx, ny2, dx, dy); geplaatst = true; }
          }
        }
      }
    }
    if(woorden.length >= 4) beste = {cellen:cellen, woorden:woorden};
  }
  if(!beste){ toast("📚 " + ct("Leer eerst wat meer woordjes voor een kruiswoord!", "Learn a few more words first for a crossword!")); return null; }
  beste.sel = 0;
  return beste;
}
function kruisCellen(kr){
  var minX = 99, maxX = -99, minY = 99, maxY = -99;
  Object.keys(kr.cellen).forEach(function(key){
    var p = key.split(",");
    minX = Math.min(minX, +p[0]); maxX = Math.max(maxX, +p[0]);
    minY = Math.min(minY, +p[1]); maxY = Math.max(maxY, +p[1]);
  });
  return {minX:minX, maxX:maxX, minY:minY, maxY:maxY};
}
function kruisBekend(kr, x, y){
  for(var i = 0; i < kr.woorden.length; i++){
    var wo = kr.woorden[i];
    if(!wo.klaar) continue;
    for(var j = 0; j < wo.k.woord.length; j++){
      if(wo.x + wo.dx*j === x && wo.y + wo.dy*j === y) return wo.k.woord.charAt(j).toUpperCase();
    }
  }
  return null;
}
function renderKruisUI(el, kr, opts){
    var bnd = kruisCellen(kr);
    var cel = Math.min(28, Math.floor(340 / (bnd.maxX - bnd.minX + 1)));
    var kh = "<div style='text-align:center'><span class='kicker'>" + ct("La Biblioteca", "La Biblioteca") + " 📚</span>"+
      "<p class='muted' style='font-size:.85rem; margin:4px'>" + ct("Het kruiswoord van de bibliothecaris: jouw geleerde woorden, kriskras door elkaar.", "The librarian's crossword: your learned words, criss-crossed.") + "</p></div>";
    kh += "<div style='overflow-x:auto; text-align:center'><div style='display:inline-block; margin:4px auto'>";
    for(var ky = bnd.minY; ky <= bnd.maxY; ky++){
      kh += "<div style='display:flex'>";
      for(var kx = bnd.minX; kx <= bnd.maxX; kx++){
        var kch = kr.cellen[kx + "," + ky];
        if(!kch){ kh += "<div style='width:" + cel + "px; height:" + cel + "px'></div>"; continue; }
        var bek = kruisBekend(kr, kx, ky);
        var num = "";
        kr.woorden.forEach(function(wo, wi2){ if(wo.x === kx && wo.y === ky && !num) num = String(wi2 + 1); });
        kh += "<div style='width:" + cel + "px; height:" + cel + "px; border:1.5px solid var(--border); background:" + (bek ? "#f2fbe8" : "#fff") + "; position:relative; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:" + Math.floor(cel*0.55) + "px'>"+
          (num ? "<span class='muted' style='position:absolute; top:-1px; left:2px; font-size:8px; font-weight:600'>" + num + "</span>" : "")+
          (bek || "") + "</div>";
      }
      kh += "</div>";
    }
    kh += "</div></div>";
    kh += "<p class='muted' style='font-size:.8rem; margin:6px 0 2px'>" + ct("Kies een omschrijving en typ het Spaanse woord:", "Pick a clue and type the Spanish word:") + "</p><div style='display:flex; flex-wrap:wrap; gap:4px'>";
    kr.woorden.forEach(function(wo, wi3){
      kh += "<button class='ghost' data-avtkw='" + wi3 + "' style='font-size:.8rem; padding:5px 8px" + (wo.klaar ? "; opacity:.45" : (wi3 === kr.sel ? "; border-color:var(--accent); border-width:2px" : "")) + "'" + (wo.klaar ? " disabled" : "") + ">" + (wi3 + 1) + (wo.dx ? "→" : "↓") + " " + wo.k.nl + (wo.klaar ? " ✓" : "") + "</button>";
    });
    kh += "</div>";
    var selW = kr.woorden[kr.sel];
    var allesKlaar = kr.woorden.every(function(w4){ return w4.klaar; });
    if(selW && !selW.klaar){
      if(selW.hint){ kh += "<p style='text-align:center; letter-spacing:.15em; margin:6px 2px 0'><span class='muted'>🔍</span> " + selW.k.woord.charAt(0) + selW.k.woord.slice(1).replace(/./g, "·") + "</p>"; }
      kh += "<div class='row' style='margin-top:6px'><input id='avtInp' type='text' autocomplete='off' autocapitalize='off' placeholder='...' style='flex:1'></div>"+
        "<div class='row' style='margin-top:4px'><button class='primary' id='btnAvtKruisCheck'>" + ct("Check \u2713", "Check \u2713") + "</button>"+
        (opts.hintAltijd && !selW.hint ? "<button class='ghost' id='btnAvtKruisHint'>" + ct("\ud83d\udd0d Hint", "\ud83d\udd0d Hint") + "</button>" : "")+
        "<button class='ghost' id='btnAvtKruisWeg'>" + opts.tLabel + "</button></div>";
    } else {
      kh += "<div class='row' style='margin-top:8px'>" + (allesKlaar ? "<button class='primary' id='btnAvtKruisNieuw'>" + ct("Nieuw kruiswoord", "New crossword") + "</button>" : "") + "<button class='ghost' id='btnAvtKruisWeg'>" + opts.tLabel + "</button></div>";
    }
    el.innerHTML = kh;
    el.querySelectorAll("[data-avtkw]").forEach(function(b){
      b.onclick = function(){ kr.sel = +b.getAttribute("data-avtkw"); renderFun(); var ii = document.getElementById("avtInp"); if(ii) ii.focus(); };
    });
    var ki = document.getElementById("avtInp");
    if(ki){
      ki.focus();
      var kcheck = function(){
        var inp = ki.value || "";
        if(!norm(inp)) return;
        var wo = kr.woorden[kr.sel];
        var wOrig = WORDS.filter(function(x){ return x.id === wo.k.id; })[0];
        if(stripAcc(norm(inp)).replace(/[^a-z]/g, "") === wo.k.woord){
          wo.klaar = true;
          if(wOrig) spelGetyptBij(wOrig, true, true); else { addXP(2); updateBadge(); }
          avtSfx("goed");
          if(kr.woorden.every(function(w5){ return w5.klaar; })){
            opts.beloond();
          } else {
            for(var q = 0; q < kr.woorden.length; q++){ if(!kr.woorden[q].klaar){ kr.sel = q; break; } }
          }
          renderFun();
        } else {
          if(wOrig) spelGetyptBij(wOrig, false);
          avtSfx("fout");
          toast("🤔 " + ct("Nee... kijk nog eens goed.", "No... look again."));
        }
      };
      var kb = document.getElementById("btnAvtKruisCheck");
      if(kb) kb.onclick = kcheck;
      ki.addEventListener("keydown", function(e){ if(e.key === "Enter") kcheck(); });
    }
    var kht = document.getElementById("btnAvtKruisHint");
    if(kht) kht.onclick = function(){ kr.woorden[kr.sel].hint = true; renderFun(); };
    var knw = document.getElementById("btnAvtKruisNieuw");
    if(knw) knw.onclick = function(){ opts.nieuw(); };
    var kwg = document.getElementById("btnAvtKruisWeg");
    if(kwg) kwg.onclick = function(){ opts.weg(); };
}

var kruisLos = null;
function renderFunKruisLos(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(!kruisLos){
    kruisLos = kruisBouw();
    if(!kruisLos){ funView = null; renderFun(); return; }
  }
  renderKruisUI(el, kruisLos, {
    tLabel: funTerugLabel(),
    hintAltijd: true,
    weg: function(){ kruisLos = null; funView = null; renderFun(); },
    nieuw: function(){ kruisLos = kruisBouw(); renderFun(); },
    beloond: function(){
      var extra = "";
      if(S.kruisLosDag !== today()){
        S.kruisLosDag = today();
        S.monedas = (S.monedas||0) + 5;
        extra = " " + ct("+5 \ud83e\ude99 (dagbeloning)", "+5 \ud83e\ude99 (daily reward)");
        confetti(["📚","🪙"], 14);
      } else {
        confetti(["📚","✨"], 10);
      }
      persist();
      toast("🎉 " + ct("Kruiswoord opgelost!", "Crossword solved!") + extra);
    }
  });
}"""

# ================= 1. Aventura eruit, geluid en kruiswoord blijven =================

knip("/* ================= AVENTURA (Zelda-achtige mini-RPG) ================= */",
     "/* ================= RONDLEIDING (onboarding) ================= */",
     NIEUW_BLOK + "\n")

# ================= 2. Letras blijft, en dat is een correctie =================
#
# Ik had Letras beschreven als "vorm zonder betekeniscue, dus als les zwak, en het is niet eens
# ontspannend". Dat klopt geen van beide, en het stond al in dit bestand: je krijgt zeven letters
# EN een lijst open plekken met de Nederlandse betekenis erbij. Je haalt dus een Spaans woord op
# vanuit de betekenis, met de letters als steun. Dezelfde beweging als het kruiswoord, en precies
# de trede tussen herkennen en zelf schrijven.
#
# En hij is met opzet de rustige van de twee: geen klok, geen levens, geen game over. Hij is in
# v22.1 gebouwd als antwoord op "die snelheid game is leuk maar nog wel te intensief, ik bedoel iets
# nog meer casual". Dat is exact de laag waar Stefan om vraagt. Dus hij blijft.

# ================= 2b. wat er nog meer in dat blok woonde =================
#
# Twee helpers stonden in de Aventura-code en worden buiten dat spel gebruikt: woordGetypt() is de
# vergelijking "is dit hetzelfde woord, accenten daargelaten" en die doet het werk in de Laatste
# check van v20.0 (regel 9852). Zonder deze twee kwam een woord daar nooit meer in de bovenste doos,
# en dat merkte pw-echtecheck meteen.
#
# vormFeedback() en gramVormVraag() stonden ernaast en worden nergens anders aangeroepen, dus die
# gaan wel mee weg.

rep(
    """function stripAcc(""",
    """/* v23.147: verhuisd uit het Aventura-blok. Ze horen hier omdat de Laatste check ze gebruikt en
   niet het spel; dat ze daar woonden was toeval van de bouwvolgorde. */
function esVormen(es){
  var delen = es.split("/").map(function(s){ return s.trim(); }).filter(Boolean);
  if(delen.length > 1) delen.push(es);
  return delen;
}
function woordGetypt(inp, es){
  var geg = stripAcc(norm(inp));
  var vormen = esVormen(es);
  var los = vormen.some(function(v){ return stripAcc(norm(v)) === geg; });
  var exact = vormen.some(function(v){ return norm(v) === norm(inp); });
  return {goed:los, accentMis:los && !exact};
}
function stripAcc(""",
)

# ================= 3. de ingangen =================

rep(
    '''    {v:"avt",     id:"ftAvt",     e:"\\ud83d\\uddfa\\ufe0f",     t:"Aventura",              s:fx("avS"), gezien:false},
    {v:"musica",  id:"ftMusica",  e:"\\ud83c\\udfb5",            t:"M\\u00fasica",            s:fx("muS"), open:function(){ show("musica"); }},''',
    '''    {v:"musica",  id:"ftMusica",  e:"\\ud83c\\udfb5",            t:"M\\u00fasica",            s:fx("muS"), open:function(){ show("musica"); }},''',
)

rep(
    '''  if(funView === "avt"){ renderFunAvt(); return; }
''',
    '''''',
)

# de rotatie: Aventura stond vast vooraan, dus die plek komt vrij
rep(
    '''/* v23.145: welke drie staan er vooraan?

   Aventura is het grote spel en Música heeft geen materiaal nodig, dus die twee staan er altijd. De
   derde plek roteert.

   Palabra Duel staat in geen van beide: hij heeft een tweede speler nodig, dus vooraan zetten belooft
   iets dat je alleen niet kunt, en "het spel van vandaag" zou een doodlopende weg zijn. Hij staat
   achter de regel bij de rest. */
var SPEL_VAST = ["avt", "musica"];
var SPEL_ROTEERT_NIET = ["avt", "musica", "duel"];''',
    '''/* v23.145: welke staan er vooraan?

   Música heeft geen materiaal nodig, dus die kan op dag 1 al draaien en staat er altijd. De rest
   van de plekken roteert.

   Palabra Duel roteert niet mee: hij heeft een tweede speler nodig, dus vooraan zetten belooft iets
   dat je alleen niet kunt, en "het spel van vandaag" zou een doodlopende weg zijn. Hij staat achter
   de regel bij de rest.

   v23.147: Aventura stond hier ook, als "het grote spel". Dat spel is er niet meer. */
var SPEL_VAST = ["musica"];
var SPEL_ROTEERT_NIET = ["musica", "duel"];''',
)

rep(
    '''var DAGSPEL_UIT = {avt:1, duel:1};''',
    '''var DAGSPEL_UIT = {duel:1};   // v23.147: avt stond hier ook, dat spel bestaat niet meer''',
)

rep(
    '''  var keus = dagSpelKeuze(2);
  var knoppen = dagSpeelRij(spelInfoVan("avt"));
  keus.forEach(function(k){ knoppen += dagSpeelRij(k); });''',
    '''  /* v23.147: hier stond Aventura vast bovenaan en kwamen er twee wisselende bij. Nu drie
     wisselende, want die vaste plek hoorde bij een spel dat er niet meer is. */
  var keus = dagSpelKeuze(3);
  var knoppen = "";
  keus.forEach(function(k){ knoppen += dagSpeelRij(k); });''',
)

rep(
    '''  if(tabId !== "speeltuin" && typeof avtStopAlles === "function") avtStopAlles();''',
    '''  // v23.147: hier stond avtStopAlles(), dat het hele Aventura-scherm afbrak. Wat er nog moet
  // stoppen is de muziek, en die woont nu in het geluidsblok.
  if(tabId !== "speeltuin" && typeof avtMuziekStop === "function") avtMuziekStop();''',
)

# ================= 4. en de Speeltuin zegt waar hij voor is =================

rep(
    '''  el.innerHTML = "<h2>" + fx("kop") + "</h2><p class='muted'>" + fx("intro") + "</p>"+
    "<p class='muted' style='margin:-4px 0 10px; font-size:.86rem'>" + fx("meetelt") + "</p>"+''',
    '''  /* v23.147: deze pagina heeft een andere maatstaf dan de rest van de app, en dat stond er niet.
     Wat in je les zit wordt beoordeeld op wat het je leert; wat hier staat op of het rust geeft.
     Een woordenzoeker leert je niets, en dat is niet erg zolang dat ook zijn werk niet is. Het
     wordt pas oneerlijk als hij doet alsof. */
  el.innerHTML = "<h2>" + fx("kop") + "</h2><p class='muted'>" + fx("intro") + "</p>"+
    "<p class='muted' style='margin:-4px 0 10px; font-size:.86rem'>" + fx("meetelt") + "</p>"+
    "<p class='muted' style='margin:-6px 0 10px; font-size:.86rem'>"+
      ct("Dit is de ontspanningskant. Hoeft niet, telt niet mee, en dat is precies de bedoeling: het mag ook op een dag dat je geen zin hebt.",
         "This is the easy side. Optional, doesn't count, and that's the point: it's allowed on a day when you don't feel like it.")+"</p>"+''',
)

# ================= 5. de lus die alleen het spelscherm had =================

# De loopende gitaarmuziek draaide alleen op het Aventura-scherm: avtMuziekStap keek naar funView
# en naar de variabele avt, en die twee bestaan niet meer. Niemand start hem, dus hij kan mee weg.
# Wat blijft is de cadens zelf: Chispa's serenade speelt hem als losse doorloop.
rep(
    """function avtMuziekStap(){
  if(funView !== "avt" || !avt || avt.victory){ avtMuziekStop(); return; }
  var ac = avtCtx(); if(!ac){ return; }
  var acht = (avt.gevecht && avt.gevecht.baas) ? 0.125 : 0.165;""",
    """function avtMuziekStap(){
  var ac = avtCtx(); if(!ac){ return; }
  var acht = 0.165;""",
)

# ================= 6. en een gat dat hierdoor pas zichtbaar werd =================
#
# pw-taal loopt elk scherm langs in een Engels profiel en zoekt Nederlands. Aventura stond in die
# ronde; nu Aventura weg is, staat Letras op die plek, en toen viel hij meteen om.
#
# De oorzaak zat er al: de woordenlijst van Letras trekt naast WORDS ook uit FREQ, en FREQ heeft
# alleen een Nederlandse vertaling ([es, nl], geen Engels). In een Engels profiel kreeg je dus
# Spaanse woorden met een Nederlandse omschrijving. Dat viel niet op omdat het alleen gebeurt als de
# puzzel toevallig een FREQ-woord pakt.
#
# Zonder FREQ is de vijver kleiner, en dat is het goede antwoord: liever minder woorden dan woorden
# met een omschrijving die je niet leest.

rep(
    """  // FREQ staat op volgorde van hoe vaak een woord voorkomt, dus de horizon is gewoon een afkapping.
  (typeof FREQ !== "undefined" ? FREQ : []).slice(0, hor).forEach(function(r){ voeg(r[0], r[1]); });""",
    """  /* FREQ staat op volgorde van hoe vaak een woord voorkomt, dus de horizon is gewoon een afkapping.
     v23.147: alleen in een Nederlands profiel. FREQ is [es, nl] en heeft geen Engelse kolom, dus in
     een Engels profiel leverde deze regel Spaanse woorden met een Nederlandse omschrijving op. */
  if(profLang() === "nl"){
    (typeof FREQ !== "undefined" ? FREQ : []).slice(0, hor).forEach(function(r){ voeg(r[0], r[1]); });
  }""",
)

rep(
    """function ltWoordenboek(){
  var hor = ltHorizon();
  if(ltWbCache && ltWbHorizon === hor) return ltWbCache;""",
    """var ltWbTaal = null;   // v23.147: de vijver hangt nu ook aan de taal, dus de cache ook
function ltWoordenboek(){
  var hor = ltHorizon();
  if(ltWbCache && ltWbHorizon === hor && ltWbTaal === profLang()) return ltWbCache;
  ltWbTaal = profLang();""",
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
