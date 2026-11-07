# patch-v23.271.py - Rompecabezas legt uit wat je aan het bouwen bent.
#
# WAT STEFAN ZEI
#
# "bij de rompecabezas mis ik soms nog wat meer uitleg per oefening (wat zijn de vormen,
# voorbeelden, lijstjes en dan oefenen)."
#
# WAT ER STOND
#
# Eén regel boven het bord: "Bouw echte vormen: kies een stam, kies een uitgang." En na een zet een
# oordeel: of de vorm bestaat, en zo niet wat het bij die persoon had moeten zijn. Dat is een
# scheidsrechter, geen uitleg. Wie niet weet dat -emos bij nosotros hoort, leert dat hier door zes
# keer mis te gokken, en dat is precies de rijtjesdrill die dit spel moest vervangen.
#
# WAT ERBIJ KOMT, EN WAAROM GEEN LETTER NIEUWE CONTENT
#
# Alles wat nodig is ligt er al: RV_UITGANG heeft de drie rijtjes, RV_PERSOON de zes personen, en
# rvIndex() kent van elk werkwoord op het bord de volledige presente, gesplitst in stam en uitgang.
# De uitleg wordt daar dus uit gerekend en niet geschreven, en kan daarmee ook niet verouderen.
#
#   1. DE REGEL, met één uitgewerkt voorbeeld uit het potje dat voor je ligt.
#   2. DE DRIE RIJTJES, als tabel: -ar, -er en -ir naast elkaar, zes personen onder elkaar. Dat is
#      het lijstje waar Stefan om vraagt, en het staat open terwijl je speelt in plaats van in een
#      spiekbrief twee tabbladen verderop.
#   3. DE STAMMEN VAN DIT POTJE. Per stam: van welk werkwoord, wat het betekent, en bij welke
#      personen die stam hoort. Bij een wisselwerkwoord staat de hele schoen erbij, met de
#      wisselende stam vet, zodat te zien is waarom nosotros en vosotros eruit vallen.
#
# Het paneel staat open bij je eerste potje en daarna dichtgeklapt, met een knop. De keuze wordt
# bewaard. Dat is dezelfde afspraak als de route op de grammaticatab (v20.7): het complete overzicht
# mag er zijn, maar niet elke keer ongevraagd.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "rvUitlegHtml" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


UITLEG = r'''/* ================= DE UITLEG BIJ HET BORD (v23.271) =================

   Stefan: "bij de rompecabezas mis ik soms nog wat meer uitleg per oefening (wat zijn de vormen,
   voorbeelden, lijstjes en dan oefenen)."

   Er stond één regel spelregel en verder alleen een scheidsrechter achteraf. Wie niet weet dat
   -emos bij nosotros hoort, leert dat zo door zes keer mis te gokken, en dat is de rijtjesdrill
   die dit spel juist moest vervangen.

   Geen letter nieuwe content: RV_UITGANG heeft de drie rijtjes, RV_PERSOON de zes personen, en
   rvIndex() kent van elk werkwoord op het bord de volledige presente in stam en uitgang. Alles
   hieronder wordt daaruit gerekend, en kan dus ook niet verouderen als VERBOS verandert. */
function rvUitlegOpen(){
  try { return S.rvUitleg === undefined ? !S.rvBest : !!S.rvUitleg; } catch(e){ return true; }
}
/* De drie rijtjes naast elkaar. Dit is het lijstje waar om gevraagd werd, en het hoort naast het
   bord te staan en niet in een spiekbrief twee tabbladen verderop. */
function rvRijtjesHtml(){
  var rijen = RV_PERSOON.map(function(p, i){
    return "<tr><td style='color:var(--muted)'>" + p + "</td>" +
      ["ar", "er", "ir"].map(function(t){
        return "<td><b>-" + RV_UITGANG[t][i] + "</b></td>";
      }).join("") + "</tr>";
  }).join("");
  return "<table style='width:100%; border-collapse:collapse; font-size:.86rem; margin:8px 0'>" +
    "<tr><th style='text-align:left'></th><th style='text-align:left'>-ar</th>" +
    "<th style='text-align:left'>-er</th><th style='text-align:left'>-ir</th></tr>" + rijen + "</table>";
}
/* De schoen van één werkwoord: alle zes de vormen, met de stam vet. Bij een wisselwerkwoord zie je
   zo in één oogopslag waarom nosotros en vosotros eruit vallen; bij een regelmatig werkwoord zie je
   dat de stam nergens verandert, en dat is ook iets waard. */
function rvSchoenHtml(inf){
  var p = null;
  try { p = rvIndex().perVerb[inf]; } catch(e){ p = null; }
  if(!p) return "";
  return "<div style='display:grid; grid-template-columns:1fr 1fr; gap:2px 10px; margin:4px 0 0; font-size:.84rem'>" +
    p.delen.map(function(d){
      return "<div><span style='color:var(--muted)'>" + RV_PERSOON[d.persoon] + "</span> " +
        "<b>" + d.stam + "</b>" + d.uitgang + "</div>";
    }).join("") + "</div>";
}
function rvUitlegHtml(){
  if(!rvSpel) return "";
  var open = rvUitlegOpen();
  var knop = "<button type='button' class='ghost' id='rvUitlegKnop' style='font-size:.82rem; padding:5px 10px; margin-top:6px'>" +
    (open ? ct("Uitleg dichtklappen", "Hide the explanation") : ct("Hoe werkt dit? →", "How does this work? →")) + "</button>";
  if(!open) return knop;

  /* Het voorbeeld komt uit het potje dat voor je ligt. Een voorbeeld met een werkwoord dat niet op
     het bord staat is een voorbeeld uit een boek; dit is er een dat je zo kunt naspelen. */
  var vb = "";
  try {
    var sk = rvSpel.stammen[0];
    var d = rvIndex().perVerb[sk.inf];
    var eerste = d.delen.filter(function(x){ return x.stam === sk.stam; })[0] || d.delen[0];
    vb = "<p style='margin:6px 0'>" +
      ct("Bijvoorbeeld van dit bord: ", "From this board, for instance: ") +
      "<b>" + eerste.stam + "</b> + <b>" + eerste.uitgang + "</b> = <b>" + eerste.vorm + "</b>, " +
      ct("en dat is ", "and that is ") + RV_PERSOON[eerste.persoon] + " " + ct("van", "of") + " " +
      sk.inf + " (" + rvGloss(sk.inf) + ").</p>";
  } catch(e){ vb = ""; }

  var gehad = {};
  var stammen = rvSpel.stammen.map(function(sk){
    var p = null;
    try { p = rvIndex().perVerb[sk.inf]; } catch(e){ p = null; }
    if(!p) return "";
    var personen = p.delen.filter(function(x){ return x.stam === sk.stam; })
      .map(function(x){ return RV_PERSOON[x.persoon]; });
    var kop = "<p style='margin:8px 0 0'><b>" + sk.stam + "-</b> " +
      "<span class='muted'>" + ct("van", "of") + " " + sk.inf + ", " + rvGloss(sk.inf) + "</span>" +
      (sk.wissel ? " ★" : "") + "</p>" +
      "<p class='muted' style='margin:2px 0 0; font-size:.84rem'>" +
        ct("hoort bij: ", "goes with: ") + personen.join(", ") + "</p>";
    /* De hele schoen hoort er één keer per werkwoord bij te staan en niet één keer per stam:
       anders staat dezelfde tabel er twee keer onder elkaar bij poder en pod-. */
    if(gehad[sk.inf]) return kop;
    gehad[sk.inf] = 1;
    return kop + rvSchoenHtml(sk.inf);
  }).join("");

  return "<div class='gwkern' style='margin:8px 0'>" +
    "<p style='margin:0'><b>" + ct("Een vorm is stam plus uitgang.", "A form is stem plus ending.") + "</b> " +
    ct("De stam zegt welk werkwoord het is, de uitgang zegt wie het doet.",
       "The stem says which verb it is, the ending says who is doing it.") + "</p>" + vb +
    "<p style='margin:10px 0 0'><b>" + ct("De drie rijtjes", "The three sets of endings") + "</b></p>" +
    rvRijtjesHtml() +
    "<p style='margin:10px 0 0'><b>" + ct("De stammen op dit bord", "The stems on this board") + "</b></p>" +
    stammen +
    "<p class='muted' style='margin:10px 0 0; font-size:.84rem'>★ " +
      ct("Een wisselwerkwoord wisselt een klinker in de stam, maar niet bij nosotros en vosotros: " +
         "daar valt de klemtoon op de uitgang en blijft de stam gewoon staan. Dat is de val van dit spel.",
         "A stem-changing verb changes a vowel in the stem, but not at nosotros and vosotros: there the " +
         "stress falls on the ending and the stem stays as it was. That is the trap in this game.") +
    "</p></div>" + knop;
}

'''

rep("function renderFunRompecabezas(){", UITLEG + "function renderFunRompecabezas(){")

# het paneel inhangen, tussen de spelregel en het bord
rep('''                             "Build real forms: pick a stem, pick an ending. Each ending can be used once, even if it misses.") + "</p>" +
    "<div class='dsleep-bank'>"''',
    '''                             "Build real forms: pick a stem, pick an ending. Each ending can be used once, even if it misses.") + "</p>" +
    // v23.271: de uitleg staat bij het bord en niet in een spiekbrief twee tabbladen verderop
    rvUitlegHtml() +
    "<div class='dsleep-bank' style='margin-top:10px'>"''')

# de knop aansluiten
rep('''  el.querySelectorAll("[data-rvs]").forEach(function(b){
    b.onclick = function(){
      rvSpel.kiesStam = parseInt(b.getAttribute("data-rvs"), 10);
      renderFunRompecabezas();
    };
  });''',
    '''  var uk = document.getElementById("rvUitlegKnop");
  if(uk) uk.onclick = function(){ S.rvUitleg = !rvUitlegOpen(); persist(); renderFunRompecabezas(); };
  el.querySelectorAll("[data-rvs]").forEach(function(b){
    b.onclick = function(){
      rvSpel.kiesStam = parseInt(b.getAttribute("data-rvs"), 10);
      renderFunRompecabezas();
    };
  });''')

# en na de ronde: de schoenen van de werkwoorden die langskwamen
rep('''        : "<p class='muted'>" + ct("Geen enkele vorm gemaakt. Volgende keer beter.","No forms built. Next time.") + "</p>") +''',
    '''        : "<p class='muted'>" + ct("Geen enkele vorm gemaakt. Volgende keer beter.","No forms built. Next time.") + "</p>") +
      /* v23.271: en dan de werkwoorden die langskwamen, compleet. Dit is het moment waarop je ze
         wilt nakijken: je hebt net zelf geprobeerd ze te bouwen, dus je weet welke vorm je miste.
         Rohrer en Bjork: terugkijken na een poging levert meer op dan vooraf lezen. */
      (function(){
        var gehad = {}, uit = [];
        (rvSpel.stammen || []).forEach(function(sk){
          if(gehad[sk.inf]) return;
          gehad[sk.inf] = 1;
          uit.push("<p style='margin:10px 0 0'><b>" + sk.inf + "</b> <span class='muted'>" +
            rvGloss(sk.inf) + (sk.wissel ? " \\u2605" : "") + "</span></p>" + rvSchoenHtml(sk.inf));
        });
        return uit.length
          ? "<div class='gwkern' style='margin:10px 0'><p style='margin:0'><b>" +
              ct("De werkwoorden van dit potje, compleet", "This round's verbs, in full") + "</b></p>" +
              uit.join("") + "</div>"
          : "";
      })() +''')

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
