#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.244 - het voortgangsscherm rangschikt
#
# Stefan, met een schermafbeelding van zijn hele voortgangsscherm: "kan je hier nog een leuker
# visueler dashboard van maken?" En na het voorstel: "ja top maak maar."
#
# EERST WAT ER AL GOED WAS, WANT DAT SCHEELT EEN VERBOUWING
#
# In het voorstel tekende ik een gestapelde balk met bewezen vast, onderweg en nog niet gezien, met
# het grote getal ernaast. Die staat er al: dagBasisRegelHtml() maakt precies dat, met drie lagen en
# een legenda die elke laag zijn naam en zijn getal geeft. De kop van dat blok is er ook al.
#
# Dat blok is dus niet het probleem. Het probleem is dat het op plek DRIE staat.
#
# WAT ER WEL MIS IS, EN DAT IS RANGSCHIKKING EN GEEN OPMAAK
#
#   1. DE VOLGORDE. "Je week" en "Je doel" staan boven "Waar je staat". Je week is een tussenstand,
#      je doel is een instelling; waar je staat is het antwoord op de vraag waarvoor je dit scherm
#      opent. Die volgorde was Stefans eigen keuze uit v23.32, en hij vraagt er nu zelf om terug te
#      komen, dus de proef die hem vastlegt gaat mee.
#
#   2. STERK EN ZWAK STAAN IN TWEE LOSSE KAARTEN. Dat was v23.37 met een reden ("je gaat een zwakke
#      plek pas oefenen als hij niet tussen goed nieuws staat"), maar het gevolg is dat je zes
#      thema's op één scherm hebt die je niet kunt vergelijken: drie in de ene kaart oplopend, drie
#      in de andere aflopend, met dezelfde eenheid. Nu één lijst, oplopend, met een merkje. De zwakke
#      staan daarmee nog steeds bovenaan, dus de reden van v23.37 blijft overeind.
#
#   3. DE DOOSJESVERDELING IS ACHT REGELS TEKST. Het langste blok van het scherm, en het zegt één
#      ding: waar je stapel zit. Dat is een grafiek en geen lijst. De regels blijven eronder staan,
#      want daar staat het gewicht per doosje in, en dat is de onderbouwing van het getal op Vandaag.
#
#   4. "ALLES IN CIJFERS" STOND OPEN. Twintig regels met hetzelfde gewicht als alles erboven. Dat is
#      een ander publiek en een ander moment: dat lees je als je iets wilt controleren. Achter één
#      klik, dicht bij binnenkomst.
#
# WAT ER NIET VERANDERT
#
# Geen enkel getal wordt hier opnieuw uitgerekend. Alles komt uit voortgangCijfers(), zwakkePunten()
# en krachtGewicht(), precies zoals daarvoor. Dit is een verbouwing van de volgorde en de vorm; wie
# hier een som ziet staan die er eerder niet stond, heeft een fout gevonden.
#
# En Chispa en de knop "Wat betekenen deze woorden?" blijven staan waar ze staan. Stefan heeft die
# vraag niet beantwoord en niets weggehaald is dan het veilige antwoord.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.244"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function vgThemasHtml(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------------------------------------------------------------- 1. de volgorde
    rep("""  el.innerHTML =
    vgWeekHtml(c) +
    vgDoelHtml() +
    "<div class='card' id='vgVastKaart'>"+dagBasisRegelHtml({legenda:true})+vgLijnHtml(c)+"</div>" +
    vgOnderwegHtml(c) +
    vgSterkHtml() +
    vgZwakHtml() +
    vgMetingHtml();""",
"""  /* v23.244: WAAR JE STAAT GAAT VOOROP.
     De volgorde hieronder was die van Stefan uit v23.32: je week, je doel, wat je vasthoudt. Hij
     vroeg op 7 november om een scherm dat rangschikt, en dan hoort het antwoord op de vraag waarvoor
     je dit scherm opent bovenaan te staan. Je week is een tussenstand en je doel is een instelling;
     allebei nuttig, geen van beide de kop van de pagina.
     Sterk en zwak zijn één lijst geworden, zie vgThemasHtml(). */
  el.innerHTML =
    "<div class='card' id='vgVastKaart'>"+dagBasisRegelHtml({legenda:true})+vgLijnHtml(c)+"</div>" +
    vgWeekHtml(c) +
    vgThemasHtml() +
    vgDoelHtml() +
    vgOnderwegHtml(c) +
    vgMetingHtml();""")

    # ---------------------------------------------------------------- 2. sterk en zwak worden één lijst
    rep("""function vgSterkHtml(){""",
"""/* ================= ÉÉN LIJST IN PLAATS VAN TWEE KAARTEN (v23.244) =================

   Sterk en zwak stonden sinds v23.37 in twee losse kaarten, met een reden: "je gaat een zwakke plek
   pas oefenen als hij niet tussen goed nieuws staat." Die reden klopt, maar het middel leverde zes
   thema's op één scherm op die je niet kunt vergelijken: drie oplopend in de ene kaart, drie
   aflopend in de andere, in dezelfde eenheid.

   Nu één lijst, oplopend gesorteerd, met een merkje per regel. De zwakke staan daarmee nog steeds
   bovenaan en de reden van v23.37 blijft dus overeind; wat erbij komt is dat je ze naast elkaar
   ziet. De telling is niet veranderd: zwakkePunten() doet hem nog steeds, en de drempels
   (minstens drie woorden gehad, VG_STERK) staan waar ze stonden. */
function vgThemasHtml(){
  var z = zwakkePunten();
  /* Alleen thema's waar je aan begonnen bent. Een thema dat je nooit zag staat op nul procent en
     kwam daardoor bovenaan te staan terwijl er niets zwaks aan is: je bent er gewoon nog niet
     geweest. Dat is een aanbod en geen tekort. Drie gehad is de ondergrens; daaronder meet je ruis. */
  var aangeraakt = z.themas.filter(function(x){ return x.gehad >= 3; });
  if(aangeraakt.length < 2) return "";
  var zwak = aangeraakt.slice(0, 3);
  var sterk = aangeraakt.slice(-3).filter(function(x){
    return zwak.indexOf(x) === -1;
  });
  var rijen = zwak.concat(sterk).sort(function(a, b){ return a.kracht - b.kracht; });
  var h = rijen.map(function(x){
    var soort = x.kracht >= VG_STERK ? "sterk" : "zwak";
    return vgRij("<span class='vgMerk vg" + soort + "'>" +
                   (soort === "sterk" ? ct("sterk","strong") : ct("zwak","weak")) + "</span> " + x.naam,
                 ct(x.gehad+" van de "+x.n+" woorden gehad", x.gehad+" of "+x.n+" words seen"),
                 x.kracht, x.kracht+"%", soort);
  }).join("");
  /* De wankele grammaticaregels horen hier ook: het is dezelfde vraag ("waar moet ik heen") in een
     andere eenheid. Ze stonden in de zwakke kaart en blijven staan waar ze stonden, onder de
     thema's. */
  var wankel = z.regels.filter(function(x){ return x.kracht < 60; });
  if(wankel.length >= 2){
    /* v23.37: bij een regel stond een percentage, en dat leest als een score. "Ser of estar, 1 fout
       van 7 beurten, 0%" terwijl je er zes goed had: die nul is het doosje, niet je uitslag. */
    var dozen = GRAM_INTERVALS.length - 1;
    h += wankel.slice(0, 3).map(function(x){
      var doos = Math.round(x.kracht / 100 * dozen);
      return vgRij(x.naam,
                   ct(x.fout+" fout van "+x.beurten+" beurten", x.fout+" wrong of "+x.beurten+" turns"),
                   x.kracht, ct("doosje "+doos+"/"+dozen, "box "+doos+"/"+dozen), "zwak");
    }).join("");
  }
  return "<div class='card'><span class='kicker'>"+ct("Waar het werk ligt","Where the work is")+"</span>"+h+
    "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>"+
    ct("Het percentage is geen score. Het is hoe ver de woorden van dit thema in je doosjes staan, "+
       "van alle woorden die het thema op jouw niveau heeft; woorden die je nooit zag tellen voor "+
       "nul. Niet op fouten geteld, want een thema dat je vaak oefent verzamelt vanzelf de meeste "+
       "fouten.",
       "The percentage is not a score. It is how far this topic's words sit in your boxes, out of "+
       "all the words the topic has at your level; words you never saw count as zero. Not counted "+
       "on mistakes: a topic you practise a lot collects the most.")+
    "</p></div>";
}
/* v23.244: hieronder staan vgSterkHtml en vgZwakHtml nog, want de rest van het bestand mag ze
   aanroepen. renderVoortgang doet dat niet meer. */
function vgSterkHtml(){""")

    # het merkje
    rep("""  .boxrow{display:flex; align-items:center; gap:8px; margin:4px 0; font-size:.88rem;}""",
"""  /* v23.244: het merkje voor de thema-lijst. Sterk en zwak staan in één lijst, dus het onderscheid
     moet in de regel zelf zitten en niet in de kop van de kaart erboven. */
  .vgMerk{font-size:.62rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
          padding:2px 5px; border-radius:5px; margin-right:5px; white-space:nowrap;}
  .vgMerk.vgzwak{background:var(--red-soft); color:var(--red);}
  .vgMerk.vgsterk{background:var(--green-soft); color:var(--green);}
  .kolommen{display:flex; align-items:flex-end; gap:5px; height:104px; margin:10px 0 2px;}
  .kolommen > div{flex:1; display:flex; flex-direction:column; justify-content:flex-end;
                  align-items:center; gap:4px; min-width:0;}
  .kolommen .kbar{width:100%; background:var(--accent); border-radius:4px 4px 0 0; min-height:2px;}
  .kolommen .klab{font-size:.64rem; color:var(--muted); white-space:nowrap;}
  .kolommen .kval{font-size:.68rem; font-weight:700; font-variant-numeric:tabular-nums;}
  .boxrow{display:flex; align-items:center; gap:8px; margin:4px 0; font-size:.88rem;}""")

    # ---------------------------------------------------------------- 3. de doosjes als grafiek
    rep("""  if(!r) return "";
  return "<p class='muted' style='margin-top:8px'>"+""",
"""  if(!r) return "";
  /* v23.244: er komt een grafiek boven de regels. Acht regels tekst waren het langste blok van dit
     scherm en ze zeggen samen één ding: waar je stapel zit. Dat is een vorm voor een beeld. De
     regels blijven eronder staan, want daar staat het gewicht per doosje, en dat is de onderbouwing
     van het getal op Vandaag. */
  var hoog = 0, gi;
  for(gi = 1; gi < c.dozen.length; gi++) if(c.dozen[gi] > hoog) hoog = c.dozen[gi];
  var kol = "";
  for(gi = 1; gi < c.dozen.length; gi++){
    if(!c.dozen[gi]) continue;
    kol += "<div><span class='kval'>"+c.dozen[gi]+"</span>"+
      "<span class='kbar' style='height:"+(hoog ? Math.round(100 * c.dozen[gi] / hoog) : 0)+"%'></span>"+
      "<span class='klab'>"+lab[gi]+"</span></div>";
  }
  return (kol ? "<div class='kolommen' id='krachtKolommen'>"+kol+"</div>" : "")+
    "<p class='muted' style='margin-top:8px'>"+""")

    # ---------------------------------------------------------------- 4. de cijferlijst achter een klik
    rep("""function cijferLijstHtml(){
  var c = voortgangCijfers(), r = "";""",
"""/* v23.244: deze lijst stond open. Twintig regels met hetzelfde gewicht als alles erboven, terwijl
   het een ander publiek en een ander moment is: dit lees je als je iets wilt controleren, niet als
   je even wilt zien hoe je ervoor staat. Hij zit nu achter één klik en de inhoud is niet veranderd.
   Weggelaten is niet verstopt; dicht is niet weg. */
function cijferLijstOmhulsel(binnen){
  if(!binnen) return "";
  return "<details id='cijferVouw'><summary>"+ct("Alles in cijfers","Every number")+"</summary>"+
    "<div class='inner'>"+binnen+"</div></details>";
}
function cijferLijstHtml(){
  var c = voortgangCijfers(), r = "";""")

if DOE_APP:
    # de aanroeper van cijferLijstHtml verpakken
    m = re.search(r"([A-Za-z0-9_\.\+\" ]*)cijferLijstHtml\(\)", src[src.index("function renderStats("):])
    assert m, "cijferLijstHtml wordt nergens aangeroepen"
    hoofd = src.index("function renderStats(")
    stuk = src[hoofd:]
    assert stuk.count("cijferLijstHtml()") == 1, "meer dan een aanroeper in renderStats"
    src = src[:hoofd] + stuk.replace("cijferLijstHtml()", "cijferLijstOmhulsel(cijferLijstHtml())", 1)

    for nodig in ["function vgThemasHtml(", "vgThemasHtml() +", "function cijferLijstOmhulsel(",
                  "cijferLijstOmhulsel(cijferLijstHtml())", "class='kolommen'", ".vgMerk{"]:
        assert nodig in src, "ontbreekt: " + nodig
    # waar je staat gaat vooraan, en je week erachter
    blok = src[src.index("function renderVoortgang("):]
    blok = blok[:blok.index("\n}\n")]
    # Commentaar eruit voordat we naar volgorde kijken: de toelichting noemt de functies die eronder
    # staan, en een controle die zijn eigen uitleg leest, controleert niets. Vierde keer deze week.
    blok = re.sub(r"/\*.*?\*/", "", blok, flags=re.S)
    assert blok.index("vgVastKaart") < blok.index("vgWeekHtml"), "waar je staat staat niet vooraan"
    assert blok.index("vgWeekHtml") < blok.index("vgThemasHtml"), "je week staat niet voor de thema's"
    assert "vgSterkHtml()" not in blok and "vgZwakHtml()" not in blok, \
        "de twee losse kaarten worden nog steeds getekend"
    APP.write_text(src, encoding="utf-8")
    print("index.html: het scherm rangschikt (volgorde, een themalijst, een grafiek, een vouw)")
else:
    print("index.html: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
