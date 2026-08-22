#!/usr/bin/env python3
# v23.171 - één geweigerde stem sleept de andere drie niet meer mee
#
# Stefan, 22 aug: "die key staat gewoon in github actions en werkt (dus ik vermoed dat er wat anders
# mis gaat)." Hij had gelijk, en mijn diagnose van vanmiddag ("het zit in de sleutel") was fout.
#
# WAT ER WERKELIJK GEBEURT
#
# In tools/audio-lib.js staat een proefaanroep vóór het inspreken:
#
#     for(const p of paren){
#       try { await spreekUit(cfg, "Hola", p.stem, null); }
#       catch(e){ meldProefFout(p, e); process.exit(1); }
#     }
#
# `paren` is ontdubbeld op stem, en er zijn er vier: dictado en dialogo-a delen er een, plus
# dialogo-b, boek en hist. Wordt één van die vier geweigerd, dan sterft de hele stap voordat er één
# bestand is ingesproken. De 279 dictado-zinnen hadden prima gekund.
#
# En het is een process.exit(1), geen exception. Dus:
#   - main().catch() draait niet
#   - schrijfUit("audio=0") wordt nooit bereikt, dus $GITHUB_OUTPUT krijgt geen audio-regel
#   - de commitregel toont geen "(+N opnames)"
#   - continue-on-error laat de workflow gewoon doorlopen
#   - het enige spoor is een console.error diep in het log
#
# Sleutel goed, geen opnames, geen melding. Precies wat Stefan zag.
#
# EN WAAROM MIJN DROOGLOOP GROEN WAS
#
# leesConfig() doet `if(opties.droog) return c;` vóór de sleutelcontrole, en controleerVooraf()
# draait alleen in de echte run. Mijn --droog test sloeg dus precies de stap over die het begaf.
# Dat is dezelfde fout als de vorige twee keer vandaag: een controle die de voordeur overslaat
# bewijst niets over de voordeur.
#
# WAT ER VERANDERT
#
# 1. proefStemmen() is nieuw en gaat niet dood. Hij probeert elke stem, geeft terug welke het doen
#    en welke niet, en met welk antwoord. controleerVooraf() gebruikt hem en behoudt zijn harde
#    exit, want de handscripts zijn interactief: daar wíl je stoppen en de uitleg lezen.
# 2. De nachtrun gebruikt proefStemmen() rechtstreeks en slaat alleen de kapotte groepen over. De
#    rest wordt gewoon ingesproken.
# 3. De reden komt in GITHUB_STEP_SUMMARY, dus op de overzichtspagina van de run in plaats van
#    alleen in het log. En audio=0 wordt altijd weggeschreven, ook als alles faalt.
#
# WAT DIT NIET DOET
#
# Uitzoeken wélke stem geweigerd wordt. Dat weet alleen ElevenLabs, en het antwoord staat vanaf nu
# in de samenvatting van de nachtrun. Dit maakt de storing zichtbaar en beperkt de schade; de
# oorzaak zelf ligt aan de andere kant van de API.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
LIB = W / "tools" / "audio-lib.js"
RUN = W / "tools" / "avondrun-audio.js"

lib = LIB.read_text(encoding="utf-8")
run = RUN.read_text(encoding="utf-8")

DOE = "function proefStemmen(" not in lib

def rep(bron, anker, nieuw, n=1):
    c = bron.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:80])
    return bron.replace(anker, nieuw, n)

if DOE:
    # -----------------------------------------------------------------------
    # 1. proefStemmen(): probeert alles, gaat niet dood
    # -----------------------------------------------------------------------
    lib = rep(lib, '''async function controleerVooraf(cfg, groepen){
  const paren = [];
  (groepen || ALLE_GROEPEN).forEach(function(g){
    const s = stemVoor(g, cfg);
    if(!s) return;
    // twee groepen met dezelfde stem hoeven maar één proef
    if(paren.some(function(p){ return p.stem === s; })) return;
    paren.push({ groep: g, stem: s });
  });

  for(const p of paren){
    try{
      await spreekUit(cfg, "Hola", p.stem, null);
    }catch(e){
      meldProefFout(p, e);
      process.exit(1);
    }
  }
  console.log("(Proefaanroep gelukt: sleutel en " + (paren.length === 1 ? "stem doen" : "stemmen doen") + " het.)");
}''',
'''/* v23.171: de proef, zonder dat hij ergens dood neervalt.
 *
 * Hier stond alleen controleerVooraf(), en die deed process.exit(1) zodra één stem werd geweigerd.
 * Er zijn vier verschillende stemmen in gebruik (dictado en dialogo-a delen er een, plus dialogo-b,
 * boek en hist), dus één kapotte stem hield alle vier de groepen tegen. Bij Stefan sloeg dat toe
 * terwijl zijn sleutel gewoon werkte: geen opnames, en geen melding, want een process.exit is geen
 * exception en de audio=0-regel werd daardoor ook nooit weggeschreven.
 *
 * Geeft { ok: {stem: true}, stuk: [{groep, stem, fout}] } terug. Wie wil stoppen doet dat zelf. */
async function proefStemmen(cfg, groepen){
  const paren = [];
  (groepen || ALLE_GROEPEN).forEach(function(g){
    const s = stemVoor(g, cfg);
    if(!s) return;
    // twee groepen met dezelfde stem hoeven maar één proef
    if(paren.some(function(p){ return p.stem === s; })) return;
    paren.push({ groep: g, stem: s });
  });

  const ok = {}, stuk = [];
  for(const p of paren){
    try{
      await spreekUit(cfg, "Hola", p.stem, null);
      ok[p.stem] = true;
    }catch(e){
      stuk.push({ groep: p.groep, stem: p.stem, fout: e });
    }
  }
  return { ok: ok, stuk: stuk, paren: paren };
}

/* De interactieve variant, voor de handscripts. Daar wíl je stoppen: je staat erbij, je leest de
   uitleg en je zet je stem opnieuw. Alleen de nachtrun heeft er niets aan om te sterven. */
async function controleerVooraf(cfg, groepen){
  const uit = await proefStemmen(cfg, groepen);
  if(uit.stuk.length){
    meldProefFout(uit.stuk[0], uit.stuk[0].fout);
    process.exit(1);
  }
  console.log("(Proefaanroep gelukt: sleutel en " + (uit.paren.length === 1 ? "stem doet" : "stemmen doen") + " het.)");
}''')

    lib = rep(lib, '''module.exports = { leesZinnen, leesHoofdstukken, leesReeksen, leesHoofdstukkenPerMap, leesDialogos, leesOpties, leesConfig, controleerVooraf, verwerk, slotwoord, stemVoor, ALLE_GROEPEN, MANIFEST_PAD };''',
'''module.exports = { leesZinnen, leesHoofdstukken, leesReeksen, leesHoofdstukkenPerMap, leesDialogos, leesOpties, leesConfig, controleerVooraf, proefStemmen, verwerk, slotwoord, stemVoor, ALLE_GROEPEN, MANIFEST_PAD };''')

    # -----------------------------------------------------------------------
    # 2. de nachtrun slaat alleen de kapotte groepen over
    # -----------------------------------------------------------------------
    run = rep(run, '''  await lib.controleerVooraf(cfg, GROEPEN);

  const delen = [];
  for(const g of GROEPEN){
    if(!items[g].length) continue;
    delen.push(await lib.verwerk(g, items[g], opties, cfg, 250));
  }''',
'''  /* v23.171: de proef mag de nacht niet slopen.
     Hier stond controleerVooraf(), en die deed process.exit(1) zodra één van de vier stemmen werd
     geweigerd. Dan werd er niets ingesproken, in geen enkele groep, en werd audio=0 niet eens
     weggeschreven omdat een process.exit geen exception is. Zie de kop van patch-v23.171.py.
     Nu: elke groep waarvan de stem het doet gaat gewoon door, en wat niet lukt wordt gemeld op de
     overzichtspagina van de run in plaats van alleen diep in het log. */
  const proef = await lib.proefStemmen(cfg, GROEPEN);
  const stukkeStem = {};
  proef.stuk.forEach(function(s){ stukkeStem[s.stem] = s.fout && s.fout.message ? s.fout.message : "geweigerd"; });

  let stukMelding = "";
  if(proef.stuk.length){
    const regels = proef.stuk.map(function(s){
      return "- stem `" + s.stem + "` (o.a. groep " + s.groep + "): " +
        String(s.fout && s.fout.message ? s.fout.message : "geweigerd").slice(0, 300);
    });
    console.error("Geweigerde stemmen bij de proefaanroep:");
    regels.forEach(function(r){ console.error("  " + r); });
    /* Die staartzin pas nadat we weten of er überhaupt iets doorging: "de rest is wél ingesproken"
       onder een lijst waarin álles faalde is precies het soort geruststelling dat niet klopt. */
    stukMelding = "### Stemmen die het niet doen\\n\\n" + regels.join("\\n") +
      "\\n\\nDit is bijna altijd een voice-id die niet meer in de bibliotheek staat, of het tegoed.";
  }

  const overgeslagen = [];
  const delen = [];

  for(const g of GROEPEN){
    if(!items[g].length) continue;
    const stem = lib.stemVoor(g, cfg);
    if(stukkeStem[stem]){ overgeslagen.push(g); continue; }
    delen.push(await lib.verwerk(g, items[g], opties, cfg, 250));
  }
  if(overgeslagen.length){
    console.error("Overgeslagen groepen: " + overgeslagen.join(", "));
  }
  if(stukMelding && delen.length){
    schrijfSamenvatting(stukMelding + "\\n\\nDe groepen met een werkende stem zijn wél ingesproken (" +
      GROEPEN.filter(function(g){ return overgeslagen.indexOf(g) === -1; }).join(", ") + ").");
  }
  if(!delen.length){
    /* Alles overgeslagen. Dit is de tak die vroeger een process.exit was, en het verschil is dat er
       nu een getal en een reden uit komen in plaats van stilte. */
    console.error("Geen enkele groep had een werkende stem. Er is niets ingesproken.");
    if(stukMelding) schrijfSamenvatting(stukMelding + "\\n\\nEr is vannacht niets ingesproken.");
    schrijfUit("audio=0");
    schrijfUit("audiotekens=0");
    process.exitCode = 0;
    return;
  }''')

    LIB.write_text(lib, encoding="utf-8")
    RUN.write_text(run, encoding="utf-8")
    print("tools/audio-lib.js en tools/avondrun-audio.js: bijgewerkt")
else:
    print("al toegepast")
