#!/usr/bin/env python3
# v23.177 (alleen gereedschap) - één slechte zin gooide de hele nacht weg
#
# De avondrun van 23 augustus (run #25) mislukte. De hartslag zegt precies wat er gebeurde:
#
#   beloofd: 2 gaten, 1 toetsje, 1 kale tijd, 1 nieuwe les
#   geleverd: null
#   AFGEKEURD:
#    - zin 6 (s260): uitleg legt niets uit; noem een Spaans woord uit de zin of de regel bij naam
#    - zin 10 (s264): kale zin met een tijdsaanduiding erin (una vez)
#
# Tien zinnen gemaakt, acht daarvan goed, en er is er nul weggeschreven. lib.pasToe() valideert de
# hele levering als één blok, en main() doet daar `if (!res.ok) return 1`. Eén zin waarvan de uitleg
# niets uitlegt kost dus ook de negen zinnen die wel deugen, plus het toetsje dat al goedgekeurd was.
#
# DAT IS MIJN FOUT, EN OP TWEE MANIEREN
#
# 1. De alles-of-niets-poort stond er al, maar hij ging zelden af. Met v23.175 heb ik er twee nieuwe
#    manieren bij gezet om hem te laten afgaan (een tijdsaanduiding, een ontbrekende situatieregel),
#    op zinnen die uit een gloednieuwe prompt komen. Dat maakt afkeuren van uitzondering tot regel,
#    en dan is alles-of-niets geen strengheid meer maar een storing.
# 2. De controle zelf deed het goed. "una vez" ís een tijdsaanduiding en die zin hoorde eruit. Het
#    probleem is niet de afkeuring maar wat de afkeuring meesleurde.
#
# WAT ER VERANDERT
#
# A. PER ZIN AFKEUREN. Voor pasToe() gaat elke zin apart door valideer(). Wat zakt, gaat eruit; wat
#    staat, gaat door. De batchcontrole van pasToe() blijft er gewoon achter staan, want die vangt
#    wat een zin op zichzelf niet kan zien (dubbele ids binnen één levering). Faalt hij dán nog, dan
#    is er echt iets mis en hoort de nacht rood te zijn.
#
#    Een verwijderde zin verdwijnt ook uit reparatie.lessen, anders wijst een les naar een id dat
#    nergens bestaat. Dat is het soort fout dat pas weken later opvalt.
#
# B. DE KALE ZINNEN WORDEN GEZEEFD VOOR DE TEGENLEZER. Een zin met "una vez" erin hoeft niet door een
#    tweede model nagelezen te worden om afgekeurd te worden; dat weet de lijst zelf al. Scheelt geld
#    en het houdt de tegenlezer bij het werk waar hij goed in is.
#
# C. HET AANTAL GEWEIGERDE ZINNEN GAAT IN DE HARTSLAG. Stil weggooien is net zo erg als alles
#    weggooien: als er drie nachten op rij vier van de vier kale zinnen sneuvelen, dan is de lijst te
#    streng of de prompt te vaag, en dat hoort zichtbaar te zijn zonder de logs te openen.
#
# D. DE PROMPT NOEMT DE VALKUILEN BIJ NAAM. "una vez", "los sábados" en "de repente" waren niet
#    genoemd in de prompt en staan wel in de lijst. Dat is oneerlijk tegenover het model.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
CUR = W / "tools" / "curriculum.js"
cur = CUR.read_text(encoding="utf-8")

DOE = "zeefZinnen" not in cur

def rep(bron, anker, nieuw, n=1):
    c = bron.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    return bron.replace(anker, nieuw, n)

ZEEF = r'''
/* ---------- de zeef (v23.177) ----------

   Aanleiding: run #25 van 23 augustus. Tien zinnen gemaakt, twee afgekeurd, nul weggeschreven.
   pasToe() valideert de hele levering als één blok en main() gooide bij één fout alles weg.

   Waarom dit nu pas opviel: de poort stond er al, maar hij ging zelden af. v23.175 zette er twee
   nieuwe manieren bij om hem te laten afgaan, op zinnen uit een gloednieuwe prompt. Toen werd
   afkeuren van uitzondering tot regel, en dan is alles-of-niets geen strengheid meer maar storing.

   Wat hier NIET gebeurt: de batchcontrole van pasToe() weghalen. Die vangt wat een losse zin niet
   kan zien, zoals twee gelijke ids binnen één levering. Faalt hij ná deze zeef alsnog, dan is er
   echt iets mis en hoort de nacht rood te zijn. */
function zeefZinnen(reparatie, inv) {
  const goed = [], weg = [];
  (reparatie.sentences || []).forEach(s => {
    const f = lib.valideer({ sentences: [s] }, inv);
    if (f.length) weg.push({ id: s.id, fouten: f }); else goed.push(s);
  });
  if (weg.length) {
    console.error(`— ${weg.length} zin(nen) uit de levering gehaald, de rest gaat gewoon door —`);
    weg.forEach(w => console.error(`  ${w.id}: ${w.fouten.join(" | ")}`));
  }
  const wegIds = new Set(weg.map(w => w.id));
  reparatie.sentences = goed;
  /* Ook uit de lesindeling halen. Zonder dit wijst een les naar een zin-id dat nergens bestaat, en
     dat is het soort fout dat pas weken later opvalt. */
  Object.keys(reparatie.lessen || {}).forEach(lid => {
    const b = reparatie.lessen[lid];
    b.sents = (b.sents || []).filter(id => !wegIds.has(id));
    if (!(b.sents || []).length && !((b.words || []).length)) delete reparatie.lessen[lid];
  });
  return weg.length;
}

/* Een kale zin met een tijdsaanduiding erin hoeft niet door een tweede model om afgekeurd te
   worden: de lijst weet dat zelf al. Eruit halen vóór de tegenlezer scheelt een betaalde aanroep en
   houdt de tegenlezer bij het werk waar hij wél voor nodig is. */
function zeefKaal(items) {
  const goed = [], weg = [];
  items.forEach(z => {
    const tw = lib.tijdsaanduidingen(z.es);
    if (tw.length) weg.push(`${z.id} (${tw.join(", ")})`); else goed.push(z);
  });
  if (weg.length) console.error(`    tijdsaanduiding gevonden, dus eruit vóór de tegenlezer: ${weg.join(", ")}`);
  return goed;
}
'''

if DOE:
    cur = rep(cur, "/* ================= 4. uitvoeren ================= */",
              ZEEF.strip("\n") + "\n\n/* ================= 4. uitvoeren ================= */")

    # A: de zeef voor pasToe
    cur = rep(cur,
        '  let versie = null;\n'
        '  if (reparatie.sentences.length || reparatie.quizzes.length) {\n'
        '    const res = lib.pasToe(reparatie, { droog: OPT.droog });',
        '  /* v23.177: eerst zeven, dan pas de batchcontrole. Zie de kop bij zeefZinnen(). */\n'
        '  const geweigerd = zeefZinnen(reparatie, inv);\n'
        '  HART.staat.geweigerd = geweigerd;\n'
        '  let versie = null;\n'
        '  if (reparatie.sentences.length || reparatie.quizzes.length) {\n'
        '    const res = lib.pasToe(reparatie, { droog: OPT.droog });')

    # B: de kale zeef voor de tegenlezer
    cur = rep(cur,
        '    const ruw = await maakZinnen(gat, n, inv, reparatie.sentences, motor);\n'
        '    const goed = await keurZinnen(ruw, motor);\n'
        '    if (!goed.length) console.error(`    ${gat.tag}: niets overgebleven`);',
        '    const ruw = zeefKaal(await maakZinnen(gat, n, inv, reparatie.sentences, motor));\n'
        '    const goed = await keurZinnen(ruw, motor);\n'
        '    if (!goed.length) console.error(`    ${gat.tag}: niets overgebleven`);')

    # D: de prompt noemt de valkuilen bij naam
    cur = rep(cur,
        'DE EIS DIE ALLES BEPAALT: in de Spaanse zin staat GEEN ENKELE tijdsaanduiding. Geen "ayer", geen\n'
        '"todos los días", geen "cuando era niño", geen "ya", geen "hace dos años", geen dagen van de week.\n'
        'De werkwoordsuitgang moet het enige zijn dat vertelt wanneer het gebeurde.',
        'DE EIS DIE ALLES BEPAALT: in de Spaanse zin staat GEEN ENKELE tijdsaanduiding. De\n'
        'werkwoordsuitgang moet het enige zijn dat vertelt wanneer het gebeurde.\n'
        '\n'
        'Verboden, en dit is een greep uit de lijst waarop machinaal wordt afgekeurd: ayer, hoy, mañana,\n'
        'anoche, ahora, antes, después, luego, entonces, siempre, nunca, ya, todavía, mientras, pronto,\n'
        'de repente, a veces, a menudo, una vez, dos veces, por primera vez, al principio, al final,\n'
        'por fin, todos los días, cada día, la semana pasada, el año pasado, hace dos años, cuando era\n'
        'niño, de pequeño, esta mañana, este año, en ese momento, en aquella época, en combinatie met een\n'
        'lidwoord ook alle dagen van de week (el lunes, los sábados).')

    # C: en de weigeringen in het slotverslag
    cur = rep(cur,
        '  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, kale zinnen compleet, voorraad ruim genoeg";',
        '  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, kale zinnen compleet, voorraad ruim genoeg";\n'
        '  /* v23.177: stil weggooien is net zo erg als alles weggooien. Staat hier drie nachten op rij\n'
        '     een hoog getal, dan is de lijst te streng of een prompt te vaag, en dat hoort zichtbaar te\n'
        '     zijn zonder de logs te openen. */\n'
        '  if (HART.staat.geweigerd) console.log(`  ${HART.staat.geweigerd} zin(nen) geweigerd door de zeef; zie hierboven welke en waarom`);')

# ---------------------------------------------------------------- de zelftest van de zeef
#
# De zeef is de reparatie van precies dat wat er misging, en dus hoort er een controle bij die
# rood wordt als hij niet meer werkt. Hij draait in de avondrun naast de zelftest van de
# contentbibliotheek, elke nacht, met de twee zinnen van 23 augustus als proefmateriaal.
ZELF = r"""
/* ---------- zelftest van de zeef (v23.177) ----------
   Draait in de avondrun, met precies de twee zinnen die run #25 lieten klappen. */
function zelftestZeef() {
  const inv = lib.inventaris();
  const idS = lib.volgendeId(inv.sentences, "s");
  let mis = 0;
  const proef = (goed, wat) => { console.log((goed ? "  ok   " : "  FOUT ") + wat); if (!goed) mis++; };

  const goedeZin = (i, extra) => Object.assign({
    id: idS(i), lvl: 2, nl: "Ik at paella met mijn zus.", en: "I ate paella with my sister.",
    es: "Comí paella con mi hermana.", alt: ["comi paella con mi hermana"],
    uitleg: "comí is de yo-vorm van comer in het indefinido.",
    ue: "comí is the yo form of comer in the indefinido.", tag: "zelftest"
  }, extra || {});

  /* De levering van 23 augustus, nagebouwd: acht die deugen, twee die zakken. */
  const rep = {
    sentences: [
      goedeZin(1), goedeZin(2), goedeZin(3), goedeZin(4),
      goedeZin(5, { uitleg: "Deze zin gaat over eten.", ue: "This sentence is about food." }),  // legt niets uit
      goedeZin(6), goedeZin(7),
      goedeZin(8, { tag: "kaal-indefinido", sit: "je vertelt over die ene avond",
                    es: "Una vez comí paella con mi hermana.",
                    alt: ["una vez comi paella con mi hermana"] }),                              // una vez
      goedeZin(9), goedeZin(10)
    ],
    lessen: { [inv.perLes[0].id]: { sents: [idS(5), idS(8), idS(9)] } }
  };
  const weg = zeefZinnen(rep, inv);
  proef(weg === 2, "twee zinnen eruit (nu: " + weg + ")");
  proef(rep.sentences.length === 8, "acht zinnen blijven staan (nu: " + rep.sentences.length + ")");
  proef(!rep.sentences.some(s => s.id === idS(5) || s.id === idS(8)), "en de twee slechte zitten er niet meer bij");
  const b = rep.lessen[inv.perLes[0].id];
  proef(!!b && b.sents.length === 1 && b.sents[0] === idS(9),
    "de lesindeling wijst niet meer naar een verwijderde zin (nu: " + JSON.stringify(b && b.sents) + ")");
  /* HET CONTROLEGEVAL. Dit is met één regel groen te krijgen door zeefZinnen() alles te laten
     weggooien, en dan levert de avondrun voor altijd niets meer. */
  const schoon = { sentences: [goedeZin(1), goedeZin(2)], lessen: {} };
  proef(zeefZinnen(schoon, inv) === 0 && schoon.sentences.length === 2,
    "CONTROLE: een levering zonder fouten blijft compleet");
  /* En de goedkope zeef ervoor: die haalt de tijdsaanduiding eruit vóór de betaalde tegenlezer. */
  const kaal = zeefKaal([
    { id: "a", es: "Una vez comí paella." },
    { id: "b", es: "Comí paella con mi hermana." },
    { id: "c", es: "Los sábados salimos a cenar." }
  ]);
  proef(kaal.length === 1 && kaal[0].id === "b", "zeefKaal houdt alleen de kale zin over");

  console.log(mis ? "\nzeef: " + mis + " fout" : "\nzeef: alles goed");
  return mis ? 1 : 0;
}
"""

if DOE:
    cur = rep(cur, "/* ================= 4. uitvoeren ================= */",
              ZELF.strip("\n") + "\n\n/* ================= 4. uitvoeren ================= */")
    cur = rep(cur,
        'const OPT = { analyse: heeft("--analyse"), droog: heeft("--droog"), stub: heeft("--stub"),\n'
        '              nieuweLes: heeft("--nieuwe-les"), max: getal("--max", 2) };',
        'const OPT = { analyse: heeft("--analyse"), droog: heeft("--droog"), stub: heeft("--stub"),\n'
        '              zelftest: heeft("--zelftest"),\n'
        '              nieuweLes: heeft("--nieuwe-les"), max: getal("--max", 2) };')
    cur = rep(cur,
        "async function main() {\n  const inv = lib.inventaris();",
        "async function main() {\n"
        "  if (OPT.zelftest) return zelftestZeef();   // v23.177\n"
        "  const inv = lib.inventaris();")
    # de zelftest mag de hartslag niet aanraken
    cur = rep(cur,
        "  if (OPT.analyse || OPT.droog) return;                 // kijken verandert niets, ook niet hier",
        "  /* v23.177: --zelftest erbij. Zonder deze regel schrijft de zelftest in de avondrun een lege\n"
        "     hartslag over de echte heen, nog voordat de run begonnen is, en dan staat er 's ochtends\n"
        "     een toestand in het bestand die van niemand is. */\n"
        "  if (OPT.analyse || OPT.droog || OPT.zelftest) return;   // kijken verandert niets, ook niet hier")

# ---------------------------------------------------------------- de avondrun draait hem ook
YML = W / ".github" / "workflows" / "curriculum.yml"
yml = YML.read_text(encoding="utf-8")
if "curriculum.js --zelftest" not in yml:
    a = "      - name: Zelftest van de contentbibliotheek\n        run: node tools/content-lib.js --zelftest\n"
    assert yml.count(a) == 1
    yml = yml.replace(a, a +
        "\n"
        "      # v23.177: de zeef is de reparatie van de nacht die op 23 augustus klapte, en dus hoort\n"
        "      # er een controle bij die rood wordt zodra hij niet meer werkt. Hij draait met precies\n"
        "      # de twee zinnen die run #25 lieten stranden.\n"
        "      - name: Zelftest van de zeef\n        run: node tools/curriculum.js --zelftest\n")
    YML.write_text(yml, encoding="utf-8")
    print(".github/workflows/curriculum.yml: zelftest van de zeef toegevoegd")
else:
    print(".github/workflows/curriculum.yml: stond er al")

CUR.write_text(cur, encoding="utf-8")
print("tools/curriculum.js: " + ("zeef toegevoegd" if DOE else "stond er al"))
