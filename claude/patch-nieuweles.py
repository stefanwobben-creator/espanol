# patch-nieuweles.py - de nieuwe les strandt niet meer op een ontbrekend veld dat de machine zelf weet.
#
# WAT ER GEMETEN IS
#
# tools/avondrun-hart.json van 30 oktober, en het is elke nacht hetzelfde beeld:
#
#   "nieuwe les AFGEKEURD:
#      - woord 7 (w362): de vertaling verklapt het Spaanse woord ("het sociale netwerk")
#      - zin 1 (s380): veld "tag" ontbreekt
#      ... (zin 2 tot en met 8: idem)"
#   "MISLUKT: beloofd en niet geleverd: de nieuwe les"
#
# Acht zinnen, allemaal zonder tag. Dat is geen toeval en geen slechte nacht: in het gatenpad
# (maakZinnen) dwingt de code tag zelf af, want daar weet hij hem. Bij een nieuwe les stond hij
# alleen in het voorbeeld in de prompt, en een voorbeeld is geen garantie. Het model mag zich
# daar ook niet in hoeven vergissen.
#
# En daarnaast: veertien woorden, een ervan verklapt zijn eigen antwoord, en de hele les gaat de
# prullenbak in. Dertien goede woorden, acht zinnen, een toetsje en een spiekkaart kwijt om een
# kaartje. Voor zinnen en voor toetsvragen is dat al eerder per stuk gemaakt (v23.177, 14 aug);
# voor woorden niet.
#
# WAT DEZE PATCH DOET
#
#   1. tag afdwingen op de zinnen en woorden van een nieuwe les. Eerst wat het model zelf zette,
#      anders het themaslug dat het op zijn eigen woorden zet, anders een slug van de lestitel.
#   2. Woorden per stuk keuren in plaats van alles of niets, met dezelfde drempel als de zinnen:
#      blijven er te weinig over, dan is de les alsnog niets.
#
# Wat deze patch NIET doet: de batchcontrole in pasToe weghalen. Die vangt wat een los item niet
# kan zien. Valt hij na deze zeef alsnog om, dan is er echt iets mis en hoort de nacht rood te zijn.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/tools/curriculum.js")
s = io.open(P, encoding="utf-8").read()

if "function themaSlug(" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


HELPER = '''/* Het themaslug van een nieuwe les. De woorden krijgen van het model een tag mee ("<thema-slug>"
   staat zo in de prompt), de zinnen in de praktijk niet. Dus nemen we de tag die het vaakst op de
   woorden staat, en pas als die er ook niet is maken we er zelf een van de titel. Een lege tag is
   geen optie: de keuring eist het veld, en dan valt een hele les om op iets dat de machine weet. */
function themaSlug(les) {
  const tel = {};
  (les.words || []).forEach(w => {
    const t = String((w && w.tag) || "").trim();
    if (t) tel[t] = (tel[t] || 0) + 1;
  });
  const top = Object.keys(tel).sort((a, b) => tel[b] - tel[a])[0];
  if (top) return top;
  const uit = String(les.titel || "les").toLowerCase()
    .normalize("NFD").replace(/[\\u0300-\\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 24);
  return uit || "les";
}

'''

rep("async function maakNieuweLes(inv, motor) {", HELPER + "async function maakNieuweLes(inv, motor) {")

OUD = """    les.words = les.words.slice(0, 14).map((w, i) => Object.assign({}, w, { id: ids.words[i] }));
    les.sentences = les.sentences.slice(0, 8)
      .map((s, i) => Object.assign({}, s, { id: ids.sents[i] }))
      .map(lib.herstelAlt);   // zelfde reden als in maakZinnen: alt is machinewerk"""

NIEUW = """    les.words = les.words.slice(0, 14).map((w, i) => Object.assign({}, w, { id: ids.words[i] }));
    /* ids, tag en alt dwingen we zelf af, net als in maakZinnen. Acht nachten op rij strandde de
       nieuwe les op "veld tag ontbreekt" bij alle acht de zinnen. Het model krijgt een voorbeeld
       met een tag erin en zet hem er toch niet op; dat is dan ook niets om op te wachten. */
    const thema = themaSlug(les);
    les.words = les.words.map(w => Object.assign({}, w, { tag: String(w.tag || "").trim() || thema }));
    les.sentences = les.sentences.slice(0, 8)
      .map((s, i) => Object.assign({}, s, { id: ids.sents[i], tag: String(s.tag || "").trim() || thema }))
      .map(lib.herstelAlt);   // zelfde reden als in maakZinnen: alt is machinewerk
    /* Woorden per stuk keuren, net als de zinnen hieronder en de toetsvragen verderop. In de nacht
       van 30 oktober ging een hele les eraan omdat een van de veertien woorden zijn eigen antwoord
       verklapte ("het sociale netwerk"). Dertien goede kaartjes, acht zinnen, een toetsje en een
       spiekkaart kwijt om er een. Blijven er te weinig over, dan is de les alsnog niets. */
    const goedeWoorden = les.words.filter(w => lib.valideer({ words: [w] }, inv).length === 0);
    if (goedeWoorden.length < les.words.length) {
      les.words.filter(w => goedeWoorden.indexOf(w) === -1).forEach(w =>
        console.error(`    woord ${w.id} eruit: ${lib.valideer({ words: [w] }, inv).join(" | ")}`));
      console.error(`    ${les.words.length - goedeWoorden.length} van de ${les.words.length} woorden afgekeurd, de rest gaat door`);
    }
    if (goedeWoorden.length < 10) { console.error("    te weinig woorden over, les niet aangeboden"); return null; }
    les.words = goedeWoorden;"""

rep(OUD, NIEUW)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
