#!/usr/bin/env python3
# v23.161 - het rijtje van vandaag volgt je fouten
#
# Stefan, 21 aug, op de vraag of het misgaat bij de keuze tussen de tijden of bij het ophalen van de
# vorm: "soms vorm vooral bijv Indefinido en imperfecto maar ook het ophalen van de rijtjes en de
# onregematige zinnen."
#
# Het vormenblok van v23.160 koos zijn rijtje van boven af uit lesRijIds(), en die lijst begint bij
# het presente. Voor iemand die het presente allang kan is dat elke tweede dag een stap in een tijd
# waar geen werk ligt, terwijl indefinido en imperfecto onderaan staan te wachten. Gemeten op een
# proefprofiel: de eerste rij was "presente, stap 1 van 6". Precies niet waar hij om vroeg.
#
# HET ANTWOORD STOND AL IN DE APP
#
# S.errors houdt per vorm bij wat er misging: conj:tener-2-indefinido. Zo'n regel verdwijnt daar pas
# na drie goede beurten (srsGoedBij, regel 8958), dus wat er nog in staat is per definitie open
# werk. Tel het per tijd op, en de rij met de meeste openstaande fouten is de rij waar je vandaag
# hoort te zijn. Geen nieuwe meting, geen nieuwe voorkeur, geen instelling: een teller die er al was
# en door niemand gelezen werd.
#
# WAAROM FOUTEN VOOR "WAAR JE MEE BEZIG BENT" GAAN
#
# Andersom lag meer voor de hand: een halve les afmaken voordat je een nieuwe begint. Maar dat is
# precies de volgorde die Stefan hierboven afkeurt, want dan blijf je in de rij waar je toevallig
# begonnen bent. Binnen een rij hervat je altijd op je eigen stap (vormStapVandaag), dus wisselen
# kost geen voortgang; het vlecht alleen twee rijen door elkaar heen, en dat is geen bijwerking maar
# een bekend voordeel. En de keuze slingert niet van dag tot dag: een fout heeft drie goede beurten
# nodig om te verdwijnen.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.161"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    rep('''/* Welk rijtje vandaag. Eerst waar je al aan begonnen bent en nog niet af is (een halve les afmaken
   gaat voor een nieuwe beginnen), dan wat "Welke tijd is dit?" als struikelblok gemeten heeft, dan
   gewoon de eerste die nog niet af is. Geen nieuwe volgorde: lesRijIds() bepaalt hem al. */
function vormRijVandaag(){
  var ids = [];
  try { ids = lesRijIds(); } catch(e){ ids = []; }
  var open = ids.filter(function(t){ return !lesKlaar(t); });
  if(!open.length) return null;
  var bezig = open.filter(function(t){
    var st = brokLees(lesId(t));
    return (st.stapMax || 0) > 0;
  });
  if(bezig.length) return bezig[0];
  var w = null;
  try { w = tijdvormTopVerwar(); } catch(e){ w = null; }
  if(w && w.getoond && open.indexOf(w.getoond) !== -1) return w.getoond;
  return open[0];
}''',
        '''/* v23.161: waar zitten je fouten? S.errors houdt per vorm bij wat er misging (conj:tener-2-
   indefinido), en zo'n regel verdwijnt daar pas na drie goede beurten. Wat er nog in staat is dus
   per definitie open werk. Opgeteld per tijd is dat het antwoord op "welk rijtje vandaag".

   Geen nieuwe meting en geen nieuwe voorkeur: deze teller lag er al en werd door niemand gelezen. */
function vormFoutenPerTijd(){
  var uit = {};
  try {
    for(var k in S.errors){
      var e = S.errors[k];
      if(!e || e.type !== "conj") continue;
      /* De sleutel is inf-persoon of inf-persoon-tijd (zie conjErrKey); zonder tijd is het het
         presente, want dat is de tijd die de oude sleutels van vóór v19.44 droegen. */
      var m = /^(.+)-([0-5])(?:-([a-z]+))?$/.exec(String(e.id || ""));
      if(!m) continue;
      var t = m[3] || "presente";
      uit[t] = (uit[t] || 0) + (e.count || 1);
    }
  } catch(err){}
  return uit;
}
/* Welk rijtje vandaag. Eerst waar je fouten zitten, dan waar je al mee bezig was, dan wat "Welke
   tijd is dit?" als struikelblok mat, dan gewoon de eerste die nog niet af is. Geen nieuwe
   volgorde: lesRijIds() bepaalt hem al, dit kiest er alleen uit.

   v23.161: "waar je fouten zitten" stond er niet en "waar je mee bezig was" stond vooraan, dus de
   lijst werd van boven af afgelopen en die begint bij het presente. Stefan: "soms vorm vooral bijv
   Indefinido en imperfecto." Precies de tijden die zo achteraan bleven staan.

   Waarom fouten vóór afmaken gaan: andersom blijf je in de rij waar je toevallig begonnen bent.
   Binnen een rij hervat je altijd op je eigen stap, dus wisselen kost geen voortgang; het vlecht
   twee rijen door elkaar, en dat is geen bijwerking maar het punt. Slingeren doet het niet: een
   fout heeft drie goede beurten nodig om te verdwijnen. */
function vormRijVandaag(){
  var ids = [];
  try { ids = lesRijIds(); } catch(e){ ids = []; }
  var open = ids.filter(function(t){ return !lesKlaar(t); });
  if(!open.length) return null;
  var f = vormFoutenPerTijd(), beste = null, max = 0;
  open.forEach(function(id){
    var r = null;
    try { r = lesRij(id); } catch(e){ r = null; }
    var n = r ? (f[r.t] || 0) : 0;
    if(n > max){ max = n; beste = id; }
  });
  if(beste) return beste;
  var bezig = open.filter(function(t){
    var st = brokLees(lesId(t));
    return (st.stapMax || 0) > 0;
  });
  if(bezig.length) return bezig[0];
  var w = null;
  try { w = tijdvormTopVerwar(); } catch(e){ w = null; }
  if(w && w.getoond && open.indexOf(w.getoond) !== -1) return w.getoond;
  return open[0];
}''')

    # Het plan zegt nu ook waaróm dit rijtje: anders is "indefinido, losse cel" een willekeurige
    # opdracht in plaats van een antwoord op je eigen fouten.
    rep('''function vormWat(){
  var t = vormRijVandaag();
  if(!t) return "";
  var r = lesRij(t), s = LES_STAPPEN[vormStapVandaag(t)] || {};
  return (r ? r.es : t) + " \\u00b7 " + ct(s.nl || "", s.en || "");
}''',
        '''function vormWat(){
  var t = vormRijVandaag();
  if(!t) return "";
  var r = lesRij(t), s = LES_STAPPEN[vormStapVandaag(t)] || {};
  /* v23.161: er stond alleen wát je doet. Waaróm juist dit rijtje is het verschil tussen een
     willekeurige opdracht en een antwoord op je eigen fouten, en de app weet het antwoord. */
  var f = vormFoutenPerTijd(), n = r ? (f[r.t] || 0) : 0;
  return (r ? r.es : t) + " \\u00b7 " + ct(s.nl || "", s.en || "") +
    (n ? " \\u00b7 " + ct(n + (n === 1 ? " fout staat open" : " fouten staan open"),
                          n + (n === 1 ? " mistake still open" : " mistakes still open")) : "");
}''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
