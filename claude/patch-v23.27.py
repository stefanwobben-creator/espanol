#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.27: de geschiedenisreeks krijgt een eigen verteller.

Stefan wil de nieuwe stem (YKrm0N1EAM9Bw27j8kuD) voor de Franco-hoofdstukken, en Chispa houden zoals
hij klinkt. Dat kan niet met een stem per script, want het manifest kent de stem per groep, en beide
boeken zaten in de groep "boek". Wisselen zou betekenen dat alle dertien Chispa-hoofdstukken als
"andere stem" gelden en opnieuw ingesproken worden, en daar betaal je per teken voor.

Dus een derde groep: hist. Eigen omgevingsvariabele, eigen regel in het manifest, eigen map
audio/hist/. Chispa blijft in audio/boek/ en verandert niet.

Het is ook inhoudelijk beter. Chispa is een verhaal dat je wil blijven horen; de geschiedenisreeks is
iemand die je iets vertelt. Dat mogen twee verschillende mensen zijn, en de steminstelling verschilt
mee: iets stabieler, want bij jaartallen en namen wil je geen verteller die improviseert.

Raakt drie bestanden: audio-lib.js (de groep), generate-boek-audio.js (welke hoofdstukken waarheen)
en index.html (waar de app het bestand zoekt).

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD_APP = os.path.join(WORTEL, "index.html")
PAD_LIB = os.path.join(WORTEL, "tools", "audio-lib.js")
PAD_GEN = os.path.join(WORTEL, "tools", "generate-boek-audio.js")


def lees(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def schrijf(p, s):
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s)


if 'ELEVENLABS_VOICE_HIST' in lees(PAD_LIB):
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(src, anker, nieuw, n=1):
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    return src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de groep
lib = lees(PAD_LIB)
lib = rep(lib,
    """  "dialogo-a": "ELEVENLABS_VOICE_DIALOGO_A",
  "dialogo-b": "ELEVENLABS_VOICE_DIALOGO_B"
};""",
    """  "dialogo-a": "ELEVENLABS_VOICE_DIALOGO_A",
  "dialogo-b": "ELEVENLABS_VOICE_DIALOGO_B",
  /* v23.27: de geschiedenisreeks is een eigen groep, met een eigen verteller. Niet om het mooi te
     maken maar om het betaalbaar te houden: het manifest houdt de stem per groep bij, dus zonder
     eigen groep zou een andere stem voor de nieuwe hoofdstukken betekenen dat alle Chispa-
     hoofdstukken als gewijzigd gelden en opnieuw ingesproken worden. */
  hist: "ELEVENLABS_VOICE_HIST"
};""")

lib = rep(lib,
    """  "dialogo-a": { stability: 0.55, similarity_boost: 0.8 },
  "dialogo-b": { stability: 0.55, similarity_boost: 0.8 }
};""",
    """  "dialogo-a": { stability: 0.55, similarity_boost: 0.8 },
  "dialogo-b": { stability: 0.55, similarity_boost: 0.8 },
  // Iets stabieler dan het verhaal: bij jaartallen, plaatsnamen en cijfers wil je geen verteller
  // die improviseert. Het is iemand die je iets vertelt, geen voorlezer van een sprookje.
  hist: { stability: 0.55, similarity_boost: 0.78 }
};""")
schrijf(PAD_LIB, lib)

# ---------------------------------------------------------------- 2. welke hoofdstukken waarheen
gen = lees(PAD_GEN)
gen = rep(gen,
    """async function main(){
  const opties = lib.leesOpties(process.argv);
  const cfg = lib.leesConfig(opties, ["boek"]);
  const hoofdstukken = lib.leesHoofdstukken();
  if(!opties.droog){
    await lib.controleerVooraf(cfg, ["boek"]);
    console.log("Stem: " + lib.stemVoor("boek", cfg) + " · model: " + cfg.model);
  }
  const r = await lib.verwerk("boek", hoofdstukken, opties, cfg, 400);
  lib.slotwoord([r], cfg, opties);
}""",
    """/* v23.27: BOOK bevat sinds v23.23 twee reeksen. Chispa (boek-*) houdt zijn verteller, de
   geschiedenisreeks (hist-*) krijgt een eigen stem en een eigen map. De verdeling gebeurt op het
   id-voorvoegsel, want dat is hoe de app ze zelf ook uit elkaar houdt. */
function groepVan(id){ return String(id).indexOf("hist-") === 0 ? "hist" : "boek"; }

async function main(){
  const opties = lib.leesOpties(process.argv);
  const alle = lib.leesHoofdstukken();
  const perGroep = { boek: [], hist: [] };
  alle.forEach(function(h){ perGroep[groepVan(h.id)].push(h); });
  const groepen = ["boek", "hist"].filter(function(g){ return perGroep[g].length; });
  const cfg = lib.leesConfig(opties, groepen);
  if(!opties.droog){
    await lib.controleerVooraf(cfg, groepen);
    groepen.forEach(function(g){
      console.log("Stem (" + g + "): " + lib.stemVoor(g, cfg) + " · model: " + cfg.model);
    });
  }
  const uit = [];
  for(const g of groepen){
    console.log("\\n== " + g + " (" + perGroep[g].length + " hoofdstukken) ==");
    uit.push(await lib.verwerk(g, perGroep[g], opties, cfg, 400));
  }
  lib.slotwoord(uit, cfg, opties);
}""")
schrijf(PAD_GEN, gen)

# ---------------------------------------------------------------- 3. de app zoekt in de goede map
app = lees(PAD_APP)
app = rep(app,
    """function boekSpreek(h){
  boekStop();
  try{
    var a = new Audio("audio/boek/" + h.id + ".mp3");""",
    """function boekSpreek(h){
  boekStop();
  try{
    /* v23.27: de geschiedenisreeks heeft een eigen verteller en dus een eigen map. Het voorvoegsel
       van het id bepaalt waar we zoeken, net zoals de boekenplank er de reeks aan herkent. Ontbreekt
       het bestand, dan valt de app terug op de voorleesstem van de browser; dat was al zo. */
    var map = String(h.id).indexOf("hist-") === 0 ? "hist" : "boek";
    var a = new Audio("audio/" + map + "/" + h.id + ".mp3");""")
app = rep(app, 'var APP_VERSIE = "v23.26";', 'var APP_VERSIE = "v23.27";')
schrijf(PAD_APP, app)

print("v23.27 toegepast op", WORTEL)
