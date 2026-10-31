# patch-v23.257.py - Chispa kijkt mee tijdens het gesprek, en laat je het eerst zelf oplossen.
#
# WAT STEFAN ZEI
#
# "ja als chispa interactie wat beter of leuker is, andere vragen, ja dan is wel goed, maar hij zou
# direct op de eerste zin al feedback moeten geven met corrigeren, me echt helpen een goede zin te
# schrijven. nu doet ie dat helemaal niet."
#
# Dat klopt, en het is met opzet zo gebouwd. v23.144 schreef in de kop van het blok: "Een
# gesprekspartner die elke zin verbetert is er geen." v23.249 maakte dat af: de app stuurt
# alleenAntwoord:true, de server laat het veld naast dan weg, en alle feedback komt in een blok na
# afloop. Dat is een goed gesprek en een slechte leraar.
#
# WAT ER NU GEBEURT, EN WAAROM ZO
#
# Niet terug naar verbeteren in de beurt zelf. Lyster en Saito (2010) vergeleken correcties in
# echte klassen: een "prompt" (je wijst dat er iets mis is en laat de leerling het zelf herstellen)
# levert meer op dan een "recast" (je zegt het goed voor). Een recast hoor je aan en je bent hem
# kwijt; een prompt moet je zelf oplossen, en dat is het ophalen waar het leren in zit.
#
# Dus: onder je zin verschijnt dat er iets mis is, met een knop om het zelf opnieuw te doen. Lukt
# het de tweede keer niet, dan komt de uitleg er alsnog. Het gesprek loopt ondertussen gewoon door,
# want Chispa antwoordt op wat je bedoelde en niet op hoe je het schreef.
#
# GEEN SERVERWIJZIGING. Het oordeel komt van modus "nabespreking" met één zin erin: dat eindpunt
# geeft al {zin, oordeel, goed} terug, en goed is precies de boolean die hier nodig is. Het scheelt
# een deploy van de server, en de prompt die beoordeelt is dezelfde als die van de nabespreking,
# dus er kunnen geen twee verschillende oordelen over dezelfde zin bestaan.
#
# De prijs: een tweede aanroep per beurt. Die loopt naast de eerste en houdt het gesprek niet op.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "CHAT_POGINGEN" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# ---------------------------------------------------------------- 1. het oordeel ophalen

KEUR = '''/* ================= CHISPA KIJKT MEE (v23.257) =================

   Stefan: "hij zou direct op de eerste zin al feedback moeten geven met corrigeren, me echt helpen
   een goede zin te schrijven. nu doet ie dat helemaal niet."

   Wat hier NIET gebeurt: de correctie terugzetten in de beurt van Chispa. Een gesprekspartner die
   elke zin verbetert is er geen (v23.144), en dat blijft waar. Wat er wel gebeurt staat ernaast,
   en het is eerst een wenk en pas daarna een verbetering.

   Lyster en Saito (2010) vergeleken correctie in echte klassen: een prompt (wijzen dat er iets mis
   is, de leerling het zelf laten herstellen) doet meer dan een recast (het goed voorzeggen). Dus
   krijg je eerst te horen DAT er iets mis is, met een knop om het zelf opnieuw te doen. Pas bij de
   tweede poging komt de uitleg er vanzelf bij.

   Het oordeel komt van modus "nabespreking" met één zin erin. Dat eindpunt bestaat al en geeft
   {zin, oordeel, goed} terug; goed is de boolean die hier nodig is. Zo hoeft de server niet mee te
   veranderen, en kunnen er geen twee verschillende oordelen over dezelfde zin bestaan. */
var CHAT_POGINGEN = 2;   // zo vaak mag je het zelf proberen voordat de uitleg er vanzelf bij komt
function chatKeur(idx, zin){
  var s0 = chatStand(), b0 = s0.beurten[idx];
  if(!b0 || b0.van !== "jij") return;
  b0.keurBezig = true;
  persist(); renderChat();
  api("/api/ai/chat", "POST", {modus:"nabespreking", niveau:chatNiveau(), zinnen:[zin]})
    .then(function(res){
      var s1 = chatStand(), b = s1.beurten[idx];
      /* De beurt kan ondertussen herschreven zijn. Dan gaat dit oordeel over een zin die er niet
         meer staat, en liever geen oordeel dan een oordeel over de verkeerde zin (v23.249). */
      if(!b || b.van !== "jij" || b.es !== zin) return;
      b.keurBezig = false;
      var r = res && res.ok && res.regels && res.regels[0];
      if(!r || r.zin !== zin){
        /* Geen bruikbaar oordeel: dan zegt het blok daar niets over. De nabespreking na afloop
           komt er toch nog, en twee keer stilte is beter dan één keer raden. */
        b.goed = null; b.oordeel = ""; persist(); renderChat(); return;
      }
      b.goed = !!r.goed;
      b.oordeel = markdownWeg(r.oordeel || "");
      b.pogingen = (b.pogingen || 0) + 1;
      // bij de laatste poging komt de uitleg er vanzelf bij: twee keer zelf proberen is genoeg,
      // daarna is wachten op een ingeving geen oefening meer maar vastzitten.
      b.toon = b.goed || (b.pogingen >= CHAT_POGINGEN);
      persist(); renderChat();
    });
}
/* Je zin herschrijven. Dit maakt GEEN nieuwe beurt: het gesprek telt drie beurten (CHAT_BEURTEN) en
   een tweede poging op dezelfde zin is dezelfde beurt. Chispa heeft ook al geantwoord; ze gaat dat
   niet nog eens doen op een zin die hetzelfde bedoelt. */
var chatHerkansIdx = -1;
function chatHerkans(idx){
  var s0 = chatStand(), b = s0.beurten[idx];
  if(!b || b.van !== "jij") return;
  chatHerkansIdx = idx;
  renderChat();
  var inv = document.getElementById("chatInvoer");
  if(inv){ inv.value = b.es || ""; inv.focus(); try { inv.select(); } catch(e){} }
}
function chatToon(idx){
  var s0 = chatStand(), b = s0.beurten[idx];
  if(!b) return;
  b.toon = true; persist(); renderChat();
}
/* Wat er onder jouw zin staat. Vier toestanden, en ze zeggen alle vier iets anders:
   nog bezig, het klopt, er is iets mis (en jij bent aan zet), er is iets mis (en hier is het). */
function chatOordeelHtml(b, idx){
  if(b.naast) return "<div class='naast amber'>" + veiligHtml(markdownWeg(b.naast)) + "</div>";
  if(b.keurBezig) return "<div class='naast'><span class='muted'>" +
    ct("Chispa kijkt je zin na...", "Chispa is checking your sentence...") + "</span></div>";
  if(b.goed === true) return "<div class='naast' style='border-left-color:var(--green)'><span class='muted'>✓ " +
    veiligHtml(b.oordeel || ct("Die klopt.", "That one holds up.")) + "</span></div>";
  if(b.goed !== false) return "";
  if(b.toon) return "<div class='naast amber'>" + veiligHtml(b.oordeel) + "</div>";
  return "<div class='naast amber'>" +
    ct("Hier zit iets niet goed. Wil je het zelf nog een keer proberen?",
       "Something is off here. Want to try it yourself once more?") +
    "<div class='row' style='margin-top:6px'>" +
      "<button type='button' class='ghost' data-chatherkans='" + idx + "' style='font-size:.8rem; padding:5px 10px'>" +
        ct("Ik probeer het zelf", "Let me try") + "</button>" +
      "<button type='button' class='ghost' data-chattoon='" + idx + "' style='font-size:.8rem; padding:5px 10px'>" +
        ct("Laat maar zien", "Just show me") + "</button>" +
    "</div></div>";
}

'''

rep("function chatStuur(){", KEUR + "function chatStuur(){")

# ---------------------------------------------------------------- 2. chatStuur: herkansing of nieuwe beurt

OUD_STUUR = """  var st = chatStand();
  var mijnZin = tekst.slice(0, 300);
  st.beurten.push({van:"jij", es:mijnZin});"""
NIEUW_STUUR = """  var st = chatStand();
  var mijnZin = tekst.slice(0, 300);
  /* v23.257: een herkansing is dezelfde beurt. De zin wordt vervangen, het oordeel opnieuw
     opgehaald, en Chispa antwoordt niet nog een keer: ze heeft al gereageerd op wat je bedoelde,
     en dat bedoel je nog steeds. */
  if(chatHerkansIdx >= 0){
    var hb = st.beurten[chatHerkansIdx];
    if(hb && hb.van === "jij"){
      var hi = chatHerkansIdx;
      chatHerkansIdx = -1;
      hb.es = mijnZin; hb.goed = null; hb.oordeel = ""; hb.toon = false;
      if(inv) inv.value = "";
      persist(); renderChat();
      chatKeur(hi, mijnZin);
      return;
    }
    chatHerkansIdx = -1;
  }
  st.beurten.push({van:"jij", es:mijnZin});"""
rep(OUD_STUUR, NIEUW_STUUR)

OUD_API = """  addXP(3); chatBezig = true; persist(); renderChat();
  api("/api/ai/chat", "POST", {modus:"gesprek", niveau:chatNiveau(), zin:mijnZin, alleenAntwoord:true,"""
NIEUW_API = """  addXP(3); chatBezig = true; persist(); renderChat();
  // het oordeel loopt naast het gesprek en houdt het niet op: twee aanroepen, geen wachtrij
  chatKeur(idx, mijnZin);
  api("/api/ai/chat", "POST", {modus:"gesprek", niveau:chatNiveau(), zin:mijnZin, alleenAntwoord:true,"""
rep(OUD_API, NIEUW_API)

# ---------------------------------------------------------------- 3. de weergave

OUD_REND = """      h += "<div class='chatrij ik'><div class='bel ik'>"+veiligHtml(t.es)+"</div></div>";
      /* v23.249: naast staat er alleen nog als er iets MIS ging (geen model). Het oordeel over je
         zinnen komt na afloop in één blok; zie chatNabespreking. */
      if(b.naast) h += "<div class='naast amber'>"+veiligHtml(markdownWeg(b.naast))+"</div>";"""
NIEUW_REND = """      h += "<div class='chatrij ik'><div class='bel ik'>"+veiligHtml(t.es)+"</div></div>";
      /* v23.257: hier stond alleen b.naast, en dat is de melding als er geen model is. Het oordeel
         over je zin stond er sinds v23.249 niet meer bij, en dat is precies wat eraan ontbrak.
         Nu staat het er wel, en eerst als wenk: zie chatOordeelHtml. */
      h += chatOordeelHtml(b, chatIdxVan(st, b));"""
rep(OUD_REND, NIEUW_REND)

# een beurt moet weten waar hij staat, want chatOordeelHtml zet dat nummer in de knop
HULP = '''/* De plek van een beurt in de rij. De knoppen onder je zin moeten weten over welke beurt ze gaan,
   en dat is een nummer en geen verwijzing zodra het door veiligHtml heen moet. */
function chatIdxVan(st, b){
  try { return st.beurten.indexOf(b); } catch(e){ return -1; }
}
'''
rep("function renderChat(){", HULP + "function renderChat(){")

# ---------------------------------------------------------------- 4. de knoppen aansluiten

OUD_WIRE = """  b = document.getElementById("chatTerug"); if(b) b.onclick = function(){ chatStand().klaar = true; persist(); show("chispa"); };"""
NIEUW_WIRE = """  b = document.getElementById("chatTerug"); if(b) b.onclick = function(){ chatStand().klaar = true; persist(); show("chispa"); };
  /* v23.257: de twee knoppen onder een zin die nog niet klopt. */
  var wrap = document.getElementById("chatWrap");
  if(wrap){
    wrap.querySelectorAll("[data-chatherkans]").forEach(function(d){
      d.onclick = function(){ chatHerkans(+d.getAttribute("data-chatherkans")); };
    });
    wrap.querySelectorAll("[data-chattoon]").forEach(function(d){
      d.onclick = function(){ chatToon(+d.getAttribute("data-chattoon")); };
    });
  }"""
rep(OUD_WIRE, NIEUW_WIRE)

# ---------------------------------------------------------------- 5. het invoerveld zegt wat het nu is

OUD_INV = """    h += "<input type='text' id='chatInvoer' style='margin-top:10px' placeholder='"+
      ct("Schrijf je antwoord in het Spaans...","Write your answer in Spanish...")+"' autocomplete='off'>"+"""
NIEUW_INV = """    h += (chatHerkansIdx >= 0
        ? "<p class='muted' style='margin:10px 0 0; font-size:.82rem'>" +
          ct("Je herschrijft je eigen zin. Dit kost je geen beurt.",
             "You are rewriting your own sentence. This does not cost you a turn.") + "</p>"
        : "")+
      "<input type='text' id='chatInvoer' style='margin-top:10px' placeholder='"+
      (chatHerkansIdx >= 0 ? ct("Pas je zin aan...","Adjust your sentence...")
                           : ct("Schrijf je antwoord in het Spaans...","Write your answer in Spanish..."))+"' autocomplete='off'>"+"""
rep(OUD_INV, NIEUW_INV)

# het blok is pas klaar als het invoerveld er ook is bij een herkansing
OUD_KLAAR = """  if(!klaar || praatDoor){"""
NIEUW_KLAAR = """  if(!klaar || praatDoor || chatHerkansIdx >= 0){"""
rep(OUD_KLAAR, NIEUW_KLAAR)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
