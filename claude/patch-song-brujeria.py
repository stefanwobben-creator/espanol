#!/usr/bin/env python3
# Nachtrun 12 aug: liedverzoek van Stefan (11 aug 18:26, yt IufC8UoWHVk, titel "Brujeria")
# verwerken in SONGS. Idempotent; volgt DEPLOY.md (anker-check, versie.txt mee, per bestand een vlag).
import io, sys, os

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

NIEUWE_VERSIE = "v23.51"  # v23.50 bewust overgeslagen: de avondrun-hartslag van 12 aug claimt dat
                          # nummer al (push is nooit aangekomen); een dubbel versienummer met andere
                          # inhoud zou bij het terugzoeken verwarren.

SONG = '''  ]},
 {id:"song-brujeria", titel:"Brujer\\u00eda", artiest:"El Gran Combo de Puerto Rico", yt:"IufC8UoWHVk", lvl:"A2",
  intro:"Salsa van El Gran Combo de Puerto Rico, al zestig jaar \\u2018La Universidad de la Salsa\\u2019. De zanger zoekt een verklaring voor een liefde die sterker is dan hijzelf, en vindt er maar \\u00e9\\u00e9n: dit moet wel brujer\\u00eda zijn \\u2014 hekserij. De oogst hieronder is de betoverings-woordenschat die erbij hoort.",
  oogst:[
   {es:"la brujer\\u00eda", nl:"de hekserij", u:"De titel. Woorden op -er\\u00eda zijn vaak een vak of een winkel: la panader\\u00eda, la taquer\\u00eda \\u2014 hier dus het \\u2018vak\\u2019 van de bruja."},
   {es:"la bruja / el brujo", nl:"de heks / de tovenaar", u:"Vrouwelijk op -a, mannelijk op -o, net als chica/chico. In salsa is de bruja vaak de verklaring voor een liefde die je niet kunt uitleggen."},
   {es:"embrujado / embrujada", nl:"behekst", u:"Participio als toestand, dus met estar: estoy embrujado = ik ben behekst. Zelfde patroon als estar cansado uit je gezondheidsles (les 8): een toestand, geen eigenschap."},
   {es:"el hechizo", nl:"de betovering", u:"Familie van hecho (gemaakt, van hacer): iets wat je \\u2018aangedaan\\u2019 is. Het werkwoord is hechizar = beheksen."},
   {es:"enamorarse de", nl:"verliefd worden op", u:"Vaste prepositie DE, niet con: me enamor\\u00e9 de ella. Reflexief \\u00e9n indefinido tegelijk \\u2014 precies het patroon dat je kent uit La Bachata in je liedjeslijst."},
   {es:"la culpa", nl:"de schuld", u:"Tener la culpa = de schuld hebben: yo no tengo la culpa, \\u00a1fue la brujer\\u00eda! Vast met tener, net als tener suerte en tener sue\\u00f1o."},
   {es:"el coraz\\u00f3n", nl:"het hart", u:"Woorden op -\\u00f3n zijn mannelijk: el coraz\\u00f3n. In het meervoud verschuift de klemtoon vanzelf goed en verdwijnt het accent: corazones."}
  ],
  vragen:[
   {q:"'Estoy embrujado' betekent...", qe:"'Estoy embrujado' means...", optse:["I am bewitched","I am a wizard"], ue:"Participio as a state, so with estar: estoy embrujado = I am bewitched. The wizard himself is el brujo: soy brujo, with ser, because that is what you are.", opts:["ik ben behekst","ik ben een tovenaar"], c:0, u:"Participio als toestand, dus met estar: estoy embrujado = ik ben behekst. De tovenaar z\\u00e9lf is el brujo: soy brujo, met ser, want dat is wat je b\\u00e9nt."},
   {q:"Waarom is het 'el coraz\\u00f3n' en niet 'la coraz\\u00f3n'?", qe:"Why is it 'el coraz\\u00f3n' and not 'la coraz\\u00f3n'?", optse:["words ending in -\\u00f3n are masculine","hearts are romantic, so feminine"], ue:"Words in -\\u00f3n are masculine: el coraz\\u00f3n, el mont\\u00f3n. The plural loses the written accent: corazones.", opts:["woorden op -\\u00f3n zijn mannelijk","harten zijn romantisch, dus vrouwelijk"], c:0, u:"Woorden op -\\u00f3n zijn mannelijk: el coraz\\u00f3n, el mont\\u00f3n. Het meervoud verliest het geschreven accent: corazones."},
   {q:"'Yo no tengo la culpa' betekent...", qe:"'Yo no tengo la culpa' means...", optse:["it is not my fault","I have no luck"], ue:"Tener la culpa = to be to blame, a fixed tener-expression like tener suerte (to be lucky) and tener sue\\u00f1o (to be sleepy). No luck would be no tengo suerte.", opts:["het is niet mijn schuld","ik heb geen geluk"], c:0, u:"Tener la culpa = de schuld hebben, een vaste tener-uitdrukking net als tener suerte (geluk hebben) en tener sue\\u00f1o (slaap hebben). Geen geluk zou no tengo suerte zijn."}
  ]}
];'''

def rep(src, anker, nieuw, n=1):
    k = src.count(anker)
    if k != n:
        sys.exit("ANKER-FOUT: %r komt %d keer voor, verwacht %d" % (anker[:60], k, n))
    return src.replace(anker, nieuw)

# ---- index.html ----
h = io.open("index.html", encoding="utf-8").read()
if 'id:"song-brujeria"' in h:
    print("index.html: song-brujeria staat er al, niets te doen")
else:
    if 'var SONGS' not in h or 'id:"song-unsueno"' not in h:
        sys.exit("index.html is niet wat ik verwacht: SONGS of song-unsueno ontbreekt")
    i = h.index('id:"song-unsueno"')
    j = h.index("]}\n];", i)
    if j - i > 6000:
        sys.exit("sluiting van SONGS niet vlak na song-unsueno gevonden; structuur veranderd?")
    h = h[:j] + SONG + h[j + len("]}\n];"):]
    h = rep(h, 'batch:"batch-12"', 'batch:"batch-13"')
    h = rep(h, 'var APP_VERSIE = "v23.49";', 'var APP_VERSIE = "%s";' % NIEUWE_VERSIE)
    io.open("index.html", "w", encoding="utf-8").write(h)
    print("index.html: song-brujeria toegevoegd, batch-13, %s" % NIEUWE_VERSIE)

# ---- versie.txt (eigen vlag, per DEPLOY.md) ----
v = io.open("versie.txt", encoding="utf-8").read().strip()
if v == NIEUWE_VERSIE:
    print("versie.txt: staat al op %s, niets te doen" % NIEUWE_VERSIE)
elif v == "v23.49":
    io.open("versie.txt", "w", encoding="utf-8").write(NIEUWE_VERSIE + "\n")
    print("versie.txt: v23.49 -> %s" % NIEUWE_VERSIE)
else:
    sys.exit("versie.txt is %r, verwacht v23.49 of %s — eerst kijken wat er gebeurd is" % (v, NIEUWE_VERSIE))
