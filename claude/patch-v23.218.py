#!/usr/bin/env python3
# v23.218 - muziek eruit
#
# Stefan, 31 aug, na het nameten: "helemaal eruit."
#
# WAAROM
#
# De aanleiding was dat drie van de zeventien liedjes een verzonnen taaloogst hadden: bij Orión
# stonden zeven uitdrukkingen met correcte uitleg (la estrella, el cielo, brillar, buscarte,
# extrañar, soñar con, la noche) en geen enkele daarvan komt in het nummer voor. De hele les was uit
# de titel afgeleid. Bij "Bachata en Fukuoka" en CHÉVERE hetzelfde patroon, herkenbaar aan dezelfde
# formulering in de intro: "de woordenschat die bij dit nummer hoort" in plaats van "die erin
# voorkomt". Alle drie van de nachttaak, alle drie van de afgelopen vier dagen.
#
# Dat had gerepareerd kunnen worden met een controle die elk oogstwoord aan een regel uit de
# songtekst koppelt. De vraag daarvóór is of het de moeite waard is, en die is nagemeten:
#
#   Ludke, Ferreira & Overy (2014, Memory & Cognition), 60 volwassenen, 20 Hongaarse uitdrukkingen:
#   zingen won van spreken op letterlijke gesproken productie en op een uitgesteld gesprekje. Op
#   herkenning, moedertaal-herinnering en een MEERKEUZE-WOORDENSCHATTOETS geen verschil.
#
#   Salcedo (2010), 94 beginners Spaans: directe navertelling significant beter bij twee van de drie
#   liedjes; na twee weken was dat verschil weg (p = 0,40). Wat bleef: 66,7% van de muziekgroep
#   kreeg het lied ongevraagd in het hoofd tegen 33,3% van de tekstgroep (p < 0,027).
#
#   Meta-analyse (Language, Culture and Curriculum 2022), 27 studies, 1.864 deelnemers: liedjes
#   verslaan andere instructie voor woordenschat, met de dosis-optimum tussen 199 en 600 minuten
#   luisteren.
#
# Wat muziek aantoonbaar levert is dus onvrijwillige herhaling en letterlijke gesproken productie,
# bij een dosis van uren. Wat dit scherm deed was: één keer kijken, zeven uitdrukkingen lezen, drie
# meerkeuzevragen. Dat is vier minuten, en precies de toetsvorm waarop zingen geen voordeel had.
# musVanDag() koos bovendien elke keer een NIEUW lied en zette een afgemaakt lied achteraan, dus met
# zeventien liedjes en één beurt per drie dagen duurde het 51 dagen voor je een lied een tweede keer
# zag. Variatie gemaximaliseerd, herhaling geminimaliseerd, en herhaling was het enige werkzame deel.
#
# WAT ER BLIJFT, EN DAT IS DE ENIGE REGEL DIE HIER ECHT TOE DOET
#
# Wat je zelf geoogst hebt blijft staan; wat er nog klaarlag verdwijnt.
#
# musOogstBij() schrijft via mijnBij() naar S.mijn, gesleuteld op de platte Spaanse tekst, en
# mijnWoordLijst() bouwt daar bij elke start opnieuw rijen van in de woordenpool. Dat loopt volledig
# langs de SONGS-array heen: geen enkel woord dat je al hebt opgepakt raakt zijn rij of zijn doosje
# kwijt. De proef pw-muziekweg.js toont dat aan in plaats van het te beweren.
#
# Wat wel verdwijnt: de 113 nog niet geoogste uitdrukkingen uit songWoordenLijst(), die het
# woordenboek doorzoekbaar maakte. Eenentwintig daarvan komen uit de drie verzonnen liedjes.
#
# ACHT PLEKKEN, WANT MUZIEK ZAT NIET IN ÉÉN TAB
#
#   de dagles         MUS_OM_DE = 3: eens per drie dagen wás je inputblok een lied
#   de speeltuin      SPEL_VAST = ["musica"]: het enige vaste tegeltje
#   Chispa            een wens "Hoy Chispa quiere música" plus drie aanroepen
#   het Meer-menu     "Liedjes met vragen erbij."
#   het woordenboek   songWoordenLijst() voerde de zoekfunctie
#   TABS en DOM       tab-musica, songList, songView
#   SONG_OOGST        een tweede, oudere liedwoordenlijst
#   de nachttaak      de song-tak in de geplande opdracht (buiten deze repo, zie hieronder)
#
# WAT DEZE PATCH NIET DOET
#
# S.musKlaar, S.mySongs en S.songHide blijven in opgeslagen profielen staan. Ze worden nergens meer
# gelezen en kosten een paar honderd bytes. Ze weghalen zou een migratie zijn, en een migratie die
# alleen opruimt is een risico zonder opbrengst.
#
# En de geplande nachttaak staat niet in deze repo. Daar staat nog "SONG_OOGST/SONGS VERWERKEN" in
# de opdracht. Zolang die regel er staat blijft de taak elke nacht zoeken naar liedverzoeken die
# nergens meer vandaan kunnen komen. Dat moet Stefan zelf aanpassen.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.218"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "var SONGS = [" in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

verwijderd = {}

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

def _blok(start, open_t, sluit_t):
    """Vanaf start het gebalanceerde blok vinden, met strings en commentaar overgeslagen."""
    d = 0; i = start; inStr = None; esc = False
    while i < len(src):
        c = src[i]
        if inStr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == inStr: inStr = None
            i += 1; continue
        if c in "\"'":
            inStr = c; i += 1; continue
        if c == "/" and src[i+1:i+2] == "/":
            i = src.index("\n", i); continue
        if c == "/" and src[i+1:i+2] == "*":
            i = src.index("*/", i) + 2; continue
        if c == open_t: d += 1
        elif c == sluit_t:
            d -= 1
            if d == 0: return i
        i += 1
    raise AssertionError("ongebalanceerd blok vanaf %d" % start)

def _kopErboven(a):
    """Een commentaarblok dat direct boven de definitie staat hoort erbij: commentaar dat een
       functie beschrijft die er niet meer is, stuurt de volgende lezer het bos in."""
    kop = src.rfind("\n", 0, a)
    while kop > 0:
        regelStart = src.rfind("\n", 0, kop) + 1
        regel = src[regelStart:kop].strip()
        if regel.startswith("/*") or regel.startswith("*") or regel.startswith("//") or regel.endswith("*/"):
            kop = regelStart - 1
            if regel.startswith("/*"): break
        else:
            break
    return max(0, kop + 1)

def knipFunctie(naam):
    global src
    m = re.search(r"^function " + re.escape(naam) + r"\(", src, re.M)
    assert m, "functie niet gevonden: " + naam
    a = _kopErboven(m.start())
    eind = _blok(m.start(), "{", "}")
    while src[eind:eind+1] in ("}", ";"): eind += 1
    if src[eind:eind+1] == "\n": eind += 1
    verwijderd[naam] = src[a:eind].count("\n")
    src = src[:a] + src[eind:]

def knipVarArray(naam):
    global src
    m = re.search(r"^var " + re.escape(naam) + r" = \[", src, re.M)
    assert m, "array niet gevonden: " + naam
    a = _kopErboven(m.start())
    eind = _blok(m.end() - 1, "[", "]")
    while src[eind:eind+1] in ("]", ";"): eind += 1
    if src[eind:eind+1] == "\n": eind += 1
    verwijderd[naam] = src[a:eind].count("\n")
    src = src[:a] + src[eind:]

def knipRegel(fragment, n=1):
    global src
    treffers = [r for r in src.split("\n") if fragment in r]
    assert len(treffers) == n, "regel %d keer (verwacht %d): %r" % (len(treffers), n, fragment)
    for r in treffers:
        src = src.replace(r + "\n", "", 1)
        verwijderd.setdefault("losse regels", 0)
        verwijderd["losse regels"] += 1

if DOE_APP:
    # =========================================================================================
    # 1. de data
    # =========================================================================================
    knipVarArray("SONGS")
    knipVarArray("SONG_OOGST")

    # =========================================================================================
    # 2. de functies
    # =========================================================================================
    for f in ["songOogstVoor", "renderSongs", "openSong", "renderSongQuiz",
              "musLijst", "musGedaan", "musVanDag", "musDagBeurt",
              "musPlat", "musTeLang", "musOogstDoel", "musOogstOpen", "musOogstBij",
              "musOogstRegelHtml", "musOogstGedaanTxt", "musOogstWire",
              "musHoorRij", "musStapKop", "musHoorHtml", "musHoorWire",
              "songWoordenLijst"]:
        knipFunctie(f)

    for r in ["var MUS_OM_DE = 3", "var MUS_MAX_WOORDEN = 5", "var MUS_HOOR_N = 3",
              "var MUS_HOOR_OPTIES = 3", "var musStap = 1", "var musHoorI = 0"]:
        knipRegel(r)

    # =========================================================================================
    # 3. het scherm
    # =========================================================================================
    rep("""  <section id="tab-musica" class="hidden">
    <div id="songList"></div>
    <div id="songView" class="hidden"></div>
  </section>

""", "")
    rep("""  {id:"musica", label:"Música", nav:false, soort:"overzicht"},\n""", "")

    # =========================================================================================
    # 4. de dagles
    #
    # lesFlowInputKeuze() koos eens per drie dagen een lied en viel anders terug op lezen of
    # luisteren. Die terugval was er al en blijft; er verdwijnt alleen de voorrangsregel.
    # =========================================================================================
    rep("""function lesFlowInputKeuze(){
  /* v23.148: eens per drie actieve dagen is het inputblok een lied. Dat gaat vóór de wisseling
     tussen lezen en luisteren, want die twee komen elke andere dag langs en het lied niet. */
  try { if(musDagBeurt()) return "musica"; } catch(e){}
  var lezen = null, audi = false;""",
"""function lesFlowInputKeuze(){
  /* v23.148 zette hier eens per drie dagen een lied vóór lezen en luisteren. Muziek is er sinds
     v23.218 niet meer, dus het inputblok wisselt weer tussen die twee. */
  var lezen = null, audi = false;""")

    rep("""  if(inputV){
    var musDag = inputV === "musica" ? musVanDag() : null;
    blokken.push({stap:"input", draad:ct("begrijpen","input"),
      naam: inputV === "musica" ? ct("Liedje","Song")
          : inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),
      wat: inputV === "musica" ? (musDag ? musDag.titel : "M\\u00fasica")
         : inputV === "lezen" ? ct("een stukje uit je boek","a piece from your book")
                              : ct("een gesprek","one conversation"),""",
"""  if(inputV){
    blokken.push({stap:"input", draad:ct("begrijpen","input"),
      naam: inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),
      wat: inputV === "lezen" ? ct("een stukje uit je boek","a piece from your book")
                              : ct("een gesprek","one conversation"),""")

    knipRegel("""  if(f.stap === "input" && f.vaardigheid === "musica") return ct("Liedje","Song");""")

    rep("""  if(v === "musica"){
    /* v23.148: het lied van vandaag. Het opent zijn eigen tabblad, net als lezen dat doet, en komt
       terug via de knop onder de quizuitslag. */
    var sgDag = musVanDag();
    if(sgDag){
      lesFlow.gekozenSpel = "musica";
      show("musica");
      openSong(sgDag, true);
      return;
    }
    v = lesFlow.vaardigheid = "luisteren";
  }
""", "")

    # =========================================================================================
    # 5. de speeltuin
    # =========================================================================================
    knipRegel("""    {v:"musica",  id:"ftMusica",""")
    rep("""var SPEL_VAST = ["musica"];
var SPEL_ROTEERT_NIET = ["musica", "duel"];""",
"""/* v23.218: hier stond ["musica"]. Muziek was het enige vaste tegeltje; nu is er geen vast
   tegeltje meer en toont de speeltuin alleen het spel van vandaag vooraan. */
var SPEL_VAST = [];
var SPEL_ROTEERT_NIET = ["duel"];""")
    rep("""  /* v23.65: Música staat sinds deze versie ook in de dagrotatie (op dag 1 is het naast Aventura het
     enige dat echt kan draaien). Maar het is geen speeltuinweergave: het heeft een eigen tabblad,
     en renderFun() kent geen tak voor "musica". Zonder deze regel landde je op het speeltuinmenu.
     De speeltuin zelf deed dit al goed, met show("musica") in zijn eigen draadje. */
  if(v === "musica"){ show("musica"); return; }
""", "")

    # =========================================================================================
    # 6. Chispa's wens: hernoemen, niet weghalen
    #
    # Eerst haalde deze patch de wens "Hoy Chispa quiere música" gewoon weg. Dat was fout, en de
    # poort ving het: CHISPA_WENSEN ging van drie naar twee en pw-v1949 werd rood.
    #
    # De wens heette naar het muziektabblad maar ging daar nooit over. Je vervulde hem door Chispa
    # te laten DANSEN: chispaBaila(), chispaFiesta() en chispaSerenade() zetten hem alle drie op
    # vervuld, en die drie animaties bestaan gewoon nog. Het commentaar in de lijst zei het al:
    # "de drie die overblijven kunnen alle drie: een tapa geven, laten dansen, aaien."
    #
    # Twee wensen betekent bovendien om de dag dezelfde wens, en dat is geen rotatie meer.
    # =========================================================================================
    rep('''  {id:"musica", e:"\U0001f3b6", es:"Hoy Chispa quiere música.",          nl:"Chispa wil vandaag muziek.",            en:"Chispa wants music today."},''',
        '''  /* v23.218: heette "musica", maar ging over dansen en niet over het muziektabblad. Je vervult
     hem met chispaBaila(), chispaFiesta() of chispaSerenade(), en die drie zijn er gewoon nog. */
  {id:"baile",  e:"\U0001f483", es:"Hoy Chispa quiere bailar.",         nl:"Chispa wil vandaag dansen.",            en:"Chispa wants to dance today."},''')
    rep('''  if(chispaWensDoe("musica")) chispaHerrenderStraks(4800);''',
        '''  if(chispaWensDoe("baile")) chispaHerrenderStraks(4800);''')
    rep('''  chispaWensDoe("musica");''', '''  chispaWensDoe("baile");''')
    rep('''  if(chispaWensDoe("musica")) chispaHerrenderStraks(duurMs + 400);''',
        '''  if(chispaWensDoe("baile")) chispaHerrenderStraks(duurMs + 400);''')

    # =========================================================================================
    # 7. het Meer-menu en het woordenboek
    # =========================================================================================
    knipRegel("""    {id:"musica", ico:"\\uD83C\\uDFB5", uit:ct("Liedjes met vragen erbij.", "Songs with questions alongside.")},""")

    rep("""  // woorden uit de liedjes (Música): groeit mee met elk liedverzoek — Stefans wens 29 juli dat het
  // woordenboek zich blijft aanvullen buiten de vaste leswoordenschat om. Staat hier al boven het
  // zoekblok omdat de dedup hieronder moet weten wat er verder al op het scherm komt.
  var songWs = songWoordenLijst();""",
"""  /* v23.218: hier stond de taaloogst van de liedjes (113 uitdrukkingen). Muziek is eruit, dus die
     bron is er niet meer. Wat Stefan al geoogst had staat gewoon in S.mijn en komt via
     mijnWoordenInPool() nog steeds in WORDS terecht; alleen de nog niet opgepakte uitdrukkingen
     zijn weg. De lege lijst blijft staan zodat de dedup en de zoekvolgorde hieronder hun vorm
     houden: die code gaat over meer dan alleen deze bron. */
  var songWs = [];""")

    # =========================================================================================
    # 8. de tien haken die buiten het muziekblok zaten
    #
    # Deze zijn de reden dat een verwijdering gevaarlijk is: ze staan verspreid over morgen-
    # berichten, de globale zoekfunctie, de terugknop-geschiedenis en een beheerrol uit v19.92.
    # De controle onderaan deze patch bestaat precies hiervoor: zij vond ze, niet ik.
    # =========================================================================================

    # het morgenbericht: "je zingt mee met ...". De hele try/catch eromheen gaat mee, anders blijft
    # er een leeg blok staan dat suggereert dat er iets gevangen wordt.
    rep("""  var morgenDatum = addDays(today(), 1);
  try {
    if((d % MUS_OM_DE) === 0){
      var sg = musVanDag(morgenDatum);
      if(sg) uit.push(ct("je zingt mee met "+sg.titel, "you sing along with "+sg.titel));
    }
  } catch(e){}
""", "")

    # de globale zoekfunctie kende liedjes als eigen soort
    rep("""  (typeof SONGS !== "undefined" ? SONGS : []).forEach(function(g){
    uit.push({soort:"lied", id:g.id, es:g.titel, nl:g.artiest || "", ico:"🎵",
              zoek:[g.titel, g.artiest || ""].map(zoekPlat)});
  });
""", "")
    rep("""  if(soort === "lied"){ show("musica"); return; }\n""", "")

    # show() tekende de liedjeslijst
    rep("""  if(tabId==="musica"){ renderSongs(); }\n""", "")

    # de terugknop kon in een lied terugkomen
    rep("""      } else if(st.t === "song"){
        show("musica", true);
        var sg = SONGS.filter(function(x){ return x.id === st.id; })[0] ||
                 (S.mySongs||[]).filter(function(x){ return x.id === st.id; })[0];
        if(sg) openSong(sg, true);
""", """""")
    rep("""      } else if(st.t === "fun"){""", """      } else if(st.t === "fun"){""")

    # het Meer-menu en de labeltabel
    rep("""["cursus","musica","chispa","perfil"]""", """["cursus","chispa","perfil"]""")
    knipRegel("""  musica:{nl:"Música",en:"Música",fr:"Música",de:"Música"},""")

    # de beheerrol uit v19.92: die bestond alleen om de liedjeslijst te mogen aanraken
    # het commentaarblok boven muziekBeheer staat los van de definitie (er zit een lege regel
    # tussen), dus knipFunctie() pakt hem niet mee. Expliciet dus.
    rep("""/* v19.92 - wie mag de liedjeslijst aanraken.
   De lijst SONGS staat in de broncode; niemand kan hem via de app veranderen. Wat wel kon was
   per bezoeker de video vervangen of een liedje wegstoppen, en dat zag eruit als beheer over
   iets gedeelds. Dat halen we weg voor iedereen behalve de beheerder. Dit is geen beveiliging
   (er valt niets te beveiligen, alles is lokaal), het is een rolverdeling die het scherm
   eerlijk maakt over wat je er kunt. Aanzetten met ?beheer=chispa achter de URL, eenmalig;
   het blijft in je profiel staan en reist dus mee met je sync-code. */
""", "")
    knipFunctie("muziekBeheer")
    knipFunctie("ytId")
    rep("""  // v19.92: de muziekbeheerrol en het speeltuinfilter.
  if(s.mbeheer === undefined) s.mbeheer = false;
""", """  // v19.92: het speeltuinfilter. De muziekbeheerrol die hier ook stond is met v23.218 weg.
""")
    rep("""  // v19.92: ?beheer=chispa pas hier verzilveren, want hierboven kwam S vers uit de opslag.
  if(pendingBeheer && S.mbeheer !== true){ S.mbeheer = true; pendingBeheer = false; }
""", "")
    knipRegel("""var pendingBeheer = false;""")
    knipRegel("""    if(bm && bm[1].toLowerCase() === "chispa") pendingBeheer = true;""")

    # het commentaarblok dat het liedje-van-vandaag uitlegde
    rep("""/* ================= HET LIEDJE VAN VANDAAG (v23.148) =================

   Stefan: "musica mag blijven maar dan moet er automatisch een liedje van de dag of om de x dagen
   komen. En de leeroutput moet ook hoger."

   Waarom eens per drie dagen en niet elke dag: een lied is vier minuten video plus de oogst lezen
   plus drie vragen. Dat is ruim twee keer een stukje hoofdstuk. Elke dag zou het inputblok laten
   uitdijen en de andere twee draden verdringen.

   Waarom vast per dag en niet willekeurig per klik: anders is "het liedje van vandaag" een ander
   lied als je twee keer kijkt, en dan betekent de naam niets. dagenTotaal() telt jouw actieve dagen,
   dus de teller loopt op jouw tempo en niet op de kalender. */
""", """/* ================= WAAR HET LIEDJE VAN VANDAAG STOND (v23.148, weg in v23.218) =================

   Stefan vroeg in augustus om "een liedje van de dag of om de x dagen, en de leeroutput moet ook
   hoger". Het eerste is gebouwd, het tweede nooit gehaald: het lied bleef vier minuten video, zeven
   uitdrukkingen en drie meerkeuzevragen.

   Op 31 augustus bleek dat drie van de zeventien liedjes een verzonnen taaloogst hadden, en bij het
   nameten van de vraag "is muziek dit waard" kwam eruit dat de gemeten winst van muziek (onvrijwillige
   herhaling, letterlijke gesproken productie) bij een dosis van uren zit, en dat meerkeuze precies
   de toetsvorm is waarop zingen géén voordeel heeft. musVanDag() koos bovendien elke keer een nieuw
   lied, dus je zag er een pas na 51 dagen terug: herhaling geminimaliseerd.

   Deze regel blijft hier staan zodat de volgende die "we moeten iets met muziek doen" denkt, weet
   dat het er is geweest en waarom het weg is. */
""")

if DOE_APP:
    # =========================================================================================
    # de controle: is er nog iets dat naar muziek wijst?
    # =========================================================================================
    # De controle kijkt naar CODE, niet naar commentaar: de historische notities hieronder mogen
    # musVanDag() bij naam noemen, want dat is juist het punt van zo'n notitie.
    zonderCommentaar = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    zonderCommentaar = re.sub(r"^\s*//.*$", "", zonderCommentaar, flags=re.M)
    resten = {}
    for naam in ["SONGS", "SONG_OOGST", "musVanDag", "musDagBeurt", "musOogstBij", "musGedaan",
                 "musLijst", "songOogstVoor", "musOogstGedaanTxt", "openSong", "renderSongs",
                 "renderSongQuiz", "MUS_OM_DE", "songWoordenLijst", "musHoorRij", "musStapKop",
                 "musPlat", "musTeLang", "musOogstOpen", "musOogstDoel", "musOogstRegelHtml",
                 "musOogstWire", "musHoorHtml", "musHoorWire", "musStap", "musHoorI",
                 "MUS_HOOR_N", "MUS_HOOR_OPTIES", "MUS_MAX_WOORDEN",
                 "tab-musica", "songList", "songView", "songQuiz", "btnAddSong",
                 "muziekBeheer", "mbeheer", "pendingBeheer", "ytId"]:
        n = len(re.findall(r"\b" + re.escape(naam) + r"\b", zonderCommentaar))
        if n: resten[naam] = n
    assert not resten, "er wijst nog iets naar muziek: %r" % resten
    # "musica" komt ook voor als gewoon Spaans woord in de leerstof; alleen als schermnaam telt.
    scherm = [f for f in ['show("musica"', 'tabId==="musica"', '"musica",', 'v:"musica"',
                          '{id:"musica"', "'musica'"] if f in zonderCommentaar]
    assert not scherm, "musica staat nog als schermnaam in: %r" % scherm

    n = sum(verwijderd.values())
    APP.write_text(src, encoding="utf-8")
    print("index.html: muziek eruit, %d regels weg" % n)
    for k in sorted(verwijderd, key=lambda x: -verwijderd[x])[:6]:
        print("   %-22s %4d" % (k, verwijderd[k]))
else:
    print("index.html: muziek stond er al niet meer")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
