#!/usr/bin/env python3
# v23.204 - de nacht rekent zijn eigen beloftes na, per stuk
# (gebouwd als v23.199; hernummerd naar v23.204 omdat de nachtrun v23.199 onder ons uit main pakte)
#
# Stefan, 27 aug: "laten we maar even focus houden op verbeteren wat we hebben."
#
# WAT ER MIS WAS
#
# Sinds v23.175 kan de nachtrun kale zinnen schrijven: zinnen zonder tijdsaanduiding, waar de
# uitgang de tijd draagt. Doel zestien per tijd. Elf nachten later, gemeten in de app:
#
#     indefinido 0 · imperfecto 0 · perfecto 0 · subjuntivo 0
#
# En de planner besluit ze elke nacht wél te maken. Uit --analyse van vandaag:
#
#     besluit: 4 kale zinnen in de indefinido (er liggen er 0 van de 16)
#     hartslag: beloofd {gaten:2, toetsje:1, kaal:1, nieuweLes:1}
#
# In --stub levert diezelfde stap gewoon vier zinnen af. De code klopt dus; het loopt mis met het
# echte model, en elf nachten lang heeft niets dat gezien.
#
# WAAROM NIETS HET ZAG, EN WAAROM DAT DE EIGENLIJKE FOUT IS
#
# De afsluitregel van v23.178 telt alles bij elkaar op:
#
#     const beloofd  = b.gaten + b.toetsje + (b.kaal || 0) + b.nieuweLes;
#     const geleverd = reparatie.sentences.length + reparatie.quizzes.length + (nieuweLes ? 1 : 0);
#     if (beloofd > 0 && geleverd === 0) → rood
#
# Vier beloftes gaan één getal in. De nacht belooft vier stukken werk, levert vijf drillzinnen en
# een toetsje, en is groen, terwijl het kale deel precies nul opleverde. Elke nacht opnieuw.
#
# Dat is dezelfde vorm als de bugs van deze week, en het is de regel die ik zelf de hele week heb
# toegepast: een controle waarin de goede en de foute uitkomst dezelfde waarde krijgen, controleert
# niets. HART.staat.geleverd noteerde `kaal: 0` gewoon apart. De informatie lag er; niemand keek.
#
# WAT ERAAN VERANDERT
#
# 1. DE CONTROLE GAAT PER SOORT. Elke belofte wordt tegen zijn eigen levering gelegd. Een soort die
#    nul oplevert terwijl er wat beloofd was, maakt de nacht rood, ook als de rest goed ging.
#
# 2. DE KALE STAP PROBEERT HET NOG EEN KEER. Als de zeef alles opeet, is nog een keer vragen wat een
#    mens zou doen. Twee pogingen, niet meer: blijft het dan leeg, dan is er iets anders aan de hand
#    en hoort de nacht dat te melden in plaats van te blijven proberen.
#
# 3. DE HARTSLAG ZEGT WIE HET OPAT. Nu gaan de afkeuringen van zeefKaal naar stderr en verder
#    nergens heen, dus morgen weet ik nog steeds niet of het de zeef was of de tegenlezer. Vanaf nu
#    staat per stap in de hartslag hoeveel er gemaakt, gezeefd en gekeurd zijn. Zonder dat getal is
#    de volgende ronde weer gokken, en gokken is precies wat elf nachten heeft gekost.
#
# WAT IK BEWUST NIET DOE
#
# De zeef losser zetten. Ik heb gemeten hoeveel van de bestaande, met de hand geschreven zinnen erdoor
# zouden komen:
#
#     indefinido  15 zinnen → 9 zonder tijdsaanduiding (60%)
#     imperfecto  18 zinnen → 2 zonder tijdsaanduiding (11%)
#     perfecto     9 zinnen → 1 zonder tijdsaanduiding (11%)
#
# Voor het indefinido is de zeef dus niet de flessenhals en zou losser zetten het probleem verplaatsen
# in plaats van oplossen. Voor het imperfecto ligt er iets anders: dat 11% is geen toeval maar de aard
# van de tijd. Een natuurlijke imperfecto-zin dráágt "antes", "siempre", "de pequeño" of "cuando era".
# Zestien kale imperfecto-zinnen eisen is misschien om onnatuurlijk Spaans vragen. Dat is een
# ontwerpvraag en geen bug, en die hoort bij Stefan te liggen voordat ik er iets aan verbouw.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
CUR = W / "tools" / "curriculum.js"
VER = W / "versie.txt"
APP = W / "index.html"
NIEUW = "v23.204"

src = CUR.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE = "function beloftesNagerekend(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:100])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de controle per soort
# =============================================================================================
CONTROLE = r'''/* ---------- de beloftes, per stuk nagerekend (v23.199) ----------

   Hier stond een optelling: alle beloftes bij elkaar tegen alle leveringen bij elkaar, en rood
   alleen als er in totaal niets uit kwam. Vier beloftes in één getal, en dan kan een nacht die het
   ene deel volledig laat vallen groen zijn omdat het andere deel wel iets opleverde. Dat is precies
   wat er elf nachten is gebeurd met de kale zinnen: elke nacht beloofd, elke nacht nul geleverd,
   elke nacht groen.

   Een controle waarin de goede en de foute uitkomst dezelfde waarde krijgen, controleert niets.
   Dus per soort, en de soorten staan hier één keer opgeschreven in plaats van twee keer verspreid
   over een optelling. */
const BELOFTE_SOORTEN = [
  { sleutel: "gaten",     naam: "de gaten uit het foutenlog", geleverd: g => g.zinnen },
  { sleutel: "toetsje",   naam: "het nieuwe toetsje",         geleverd: g => g.toetsjes },
  { sleutel: "kaal",      naam: "de kale zinnen",             geleverd: g => g.kaal },
  { sleutel: "nieuweLes", naam: "de nieuwe les",              geleverd: g => g.nieuweLes }
];
function beloftesNagerekend(beloofd, geleverd) {
  const b = beloofd || {}, g = geleverd || {};
  const mis = [];
  BELOFTE_SOORTEN.forEach(s => {
    if (!(b[s.sleutel] > 0)) return;                  // niets beloofd, dus niets te missen
    const n = s.geleverd(g) || 0;
    if (n === 0) mis.push(s.naam);
  });
  return mis;
}

'''

if DOE:
    rep("/* ---------- kale zinnen per tijd (v23.175) ----------", CONTROLE + "/* ---------- kale zinnen per tijd (v23.175) ----------")

    rep("""  const b = HART.staat.beloofd || { gaten: 0, toetsje: 0, kaal: 0, nieuweLes: 0 };
  const beloofd = b.gaten + b.toetsje + (b.kaal || 0) + b.nieuweLes;
  const geleverd = reparatie.sentences.length + reparatie.quizzes.length + (nieuweLes ? 1 : 0);
  if (beloofd > 0 && geleverd === 0) {
    HART.staat.reden = "het besluit vroeg om " + beloofd + " stuk(ken) werk en er is niets van weggeschreven";
    console.error("MISLUKT: " + HART.staat.reden + ". Kijk hierboven welk onderdeel afhaakte.");
    return 1;
  }
  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, kale zinnen compleet, voorraad ruim genoeg";""",
        """  /* v23.199: per soort, niet op de som. Zie de kop van beloftesNagerekend(). */
  const b = HART.staat.beloofd || { gaten: 0, toetsje: 0, kaal: 0, nieuweLes: 0 };
  const beloofd = b.gaten + b.toetsje + (b.kaal || 0) + b.nieuweLes;
  const mis = beloftesNagerekend(b, HART.staat.geleverd);
  if (mis.length) {
    HART.staat.mis = mis;
    HART.staat.reden = "beloofd en niet geleverd: " + mis.join(", ");
    console.error("MISLUKT: " + HART.staat.reden + ". Kijk hierboven welk onderdeel afhaakte.");
    return 1;
  }
  if (beloofd === 0) HART.staat.reden = "niets te doen: geen gaten, geen toetsgaten, kale zinnen compleet, voorraad ruim genoeg";""")

# =============================================================================================
# 2. de kale stap probeert het nog een keer, en meldt wie wat opat
# =============================================================================================
if DOE:
    rep("""  if (kaal.length) try {
    const gat = kaal[0];
    const n = Math.min(KAAL_PER_NACHT, gat.tekort);
    console.log(`  ${gat.tag}: ${n} kale zinnen maken…`);
    const ruw = zeefKaal(await maakZinnen(gat, n, inv, reparatie.sentences, motor));
    const goed = await keurZinnen(ruw, motor);
    if (!goed.length) console.error(`    ${gat.tag}: niets overgebleven`);
    else {""",
        """  if (kaal.length) try {
    const gat = kaal[0];
    const n = Math.min(KAAL_PER_NACHT, gat.tekort);
    /* v23.199: twee pogingen. De zeef is met opzet ruim ("fout naar de veilige kant is afkeuren",
       zie TIJDSWOORDEN in content-lib), en een model dat een natuurlijke verledentijdszin schrijft
       grijpt naar ayer, una vez, el otro día. Eén keer opnieuw vragen is wat een mens zou doen en
       het kost een halve minuut. Blijft het dán leeg, dan is er iets anders aan de hand en hoort de
       nacht dat te melden in plaats van te blijven proberen.

       En het telwerk per stap gaat de hartslag in. Tot nu toe verdwenen de afkeuringen van zeefKaal
       in stderr, en dus wist niemand 's ochtends of het de zeef was of de tegenlezer. Elf nachten
       lang was dat het verschil tussen "ik weet het" en "ik gok". */
    let goed = [], telling = [];
    for (let poging = 1; poging <= KAAL_POGINGEN && !goed.length; poging++) {
      console.log(`  ${gat.tag}: ${n} kale zinnen maken…` + (poging > 1 ? ` (poging ${poging})` : ""));
      const gemaakt = await maakZinnen(gat, n, inv, reparatie.sentences, motor);
      const gezeefd = zeefKaal(gemaakt);
      goed = await keurZinnen(gezeefd, motor);
      telling.push({ poging, gemaakt: gemaakt.length, naZeef: gezeefd.length, naKeuring: goed.length });
    }
    HART.staat.kaalVerloop = telling;
    telling.forEach(t => console.log(
      `    poging ${t.poging}: ${t.gemaakt} gemaakt → ${t.naZeef} door de zeef → ${t.naKeuring} door de tegenlezer`));
    if (!goed.length) console.error(`    ${gat.tag}: niets overgebleven na ${telling.length} poging(en)`);
    else {""")

    rep("""const KAAL_PER_NACHT = 4;""",
        """const KAAL_PER_NACHT = 4;
const KAAL_POGINGEN = 2;           // v23.199: zie de kop bij de kale stap in main()""")

# =============================================================================================
# 3. de hartslag draagt de nieuwe velden
# =============================================================================================
if DOE:
    rep("""const HART = { staat: { wanneer: null, gelukt: false, ladder: null, voorraadDagen: null,
                        beloofd: null, geleverd: null, versie: null, klachten: [],
                        reden: "de run is niet afgemaakt" } };""",
        """/* v23.199: mis en kaalVerloop erbij. Ze staan hier expliciet en niet alleen daar waar ze gezet
   worden, zodat de vorm van de hartslag op één plek te lezen is: dat bestand is 's ochtends het
   enige wat je opent als er iets niet klopt. */
const HART = { staat: { wanneer: null, gelukt: false, ladder: null, voorraadDagen: null,
                        beloofd: null, geleverd: null, versie: null, klachten: [],
                        mis: null, kaalVerloop: null,
                        reden: "de run is niet afgemaakt" } };""")

# =============================================================================================
# 4. een zelftest die de nieuwe controle vastlegt
# =============================================================================================
if DOE:
    rep("""/* ---------- zelftest van de zeef (v23.177) ----------""",
        """/* ---------- zelftest van de beloftecontrole (v23.199) ----------
   Het geval dat elf nachten groen bleef, en het controlegeval ernaast. */
function zelftestBelofte() {
  let mis = 0;
  const proef = (goed, wat) => { console.log((goed ? "  ok   " : "  FOUT ") + wat); if (!goed) mis++; };

  const beloofd = { gaten: 2, toetsje: 1, kaal: 1, nieuweLes: 1 };

  /* precies de nacht van 26 augustus: vijf drillzinnen en een toetsje geleverd, nul kale zinnen.
     De oude optelling gaf hier groen, want vijf plus een is niet nul. */
  const echteNacht = beloftesNagerekend(beloofd, { zinnen: 5, toetsjes: 1, kaal: 0, nieuweLes: 1 });
  proef(echteNacht.length === 1 && /kale zinnen/.test(echteNacht[0]),
    "de nacht van 26 aug wordt gezien: " + JSON.stringify(echteNacht));

  /* het controlegeval: een nacht waarin alles geleverd is, mag niet rood worden. Zonder deze proef
     haalt "altijd rood" de proef hierboven ook. */
  proef(beloftesNagerekend(beloofd, { zinnen: 5, toetsjes: 1, kaal: 4, nieuweLes: 1 }).length === 0,
    "een volledige nacht blijft groen");

  /* en wat niet beloofd is, kan niet missen */
  proef(beloftesNagerekend({ gaten: 2, toetsje: 0, kaal: 0, nieuweLes: 0 },
                           { zinnen: 5, toetsjes: 0, kaal: 0, nieuweLes: 0 }).length === 0,
    "een soort die niet beloofd was telt niet mee");

  /* alles beloofd en niets geleverd blijft rood, en noemt alle vier de soorten */
  proef(beloftesNagerekend(beloofd, { zinnen: 0, toetsjes: 0, kaal: 0, nieuweLes: 0 }).length === 4,
    "een lege nacht noemt alle vier de soorten");

  return mis;
}

/* ---------- zelftest van de zeef (v23.177) ----------""")

    # aanhaken in de zelftest-ingang
    ank = "function zelftestZeef() {"
    assert src.count(ank) == 1
    # zoek waar zelftestZeef wordt aangeroepen
    assert "zelftestZeef()" in src

if DOE:
    # de aanroep krijgt de nieuwe zelftest ernaast; de definitie blijft ongemoeid
    rep("""  if (OPT.zelftest) return zelftestZeef();   // v23.177""",
        """  if (OPT.zelftest) return zelftestZeef() + zelftestBelofte();   // v23.177, v23.199""")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE:
    CUR.write_text(src, encoding="utf-8")
    print("tools/curriculum.js: de beloftes worden per soort nagerekend, de kale stap krijgt een tweede poging")
else:
    print("tools/curriculum.js: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
