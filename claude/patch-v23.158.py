#!/usr/bin/env python3
# v23.158 - de ezelsbrug, en de fout die terugkomt
#
# Stefan, 21 aug: "ik mis nog vaak uitleg of als ik een foutmaak, waarom ik het fout maak en dan een
# ezelsbrug of andere hulp. (...) alsof de toetsjes te moeilijk zijn of niet stap voor stap
# aansluiten bij wat je leerde."
#
# Wat er stond, gemeten op de 23 concepten:
#
#   1. Bij een fout kreeg je het veld w. Dat legt uit waarom het JUISTE antwoord goed is. Nergens
#      staat wat JOUW antwoord betekende, en dat is precies de vraag die hij stelt.
#   2. Een ezelsbrug bestond niet. Nul, in 23 concepten en 122 patronen.
#   3. Stap 1 van elk concept begon met twee vragen en als enige begeleiding de zin "Eerst een
#      voorbeeld, en gok gerust". Er stond geen woord Spaans voordat de eerste vraag kwam: de regel
#      zelf zat achteraan, in stap 3, dichtgeklapt onder "De hele regel". Dat is letterlijk "niet
#      stap voor stap aansluiten bij wat je leerde", want je leerde nog niets.
#   4. Een fout antwoord kwam binnen de stap nooit terug. Je las een regel en klikte door. Geen
#      tweede poging, dus de correctie werd nooit opgehaald, alleen gelezen.
#
# Wat hier bij komt: per concept drie korte teksten (de kern, de ezelsbrug, waar het meestal
# misgaat), en een correctieronde aan het eind van de stap voor wat je fout had.
#
# Waarom per concept en niet per vraag: elk van deze 23 concepten IS één binaire beslissing. Kies je
# de andere kant, dan is dat vrijwel altijd dezelfde verwarring. 23 diagnoses dekken dus 122
# patronen, en ze zijn waar. 122 losse foutuitleggen zouden preciezer lijken en dat niet zijn.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.158"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# ---------------------------------------------------------------------------
# 1. de inhoud: per concept de kern, de ezelsbrug en de misvatting
# ---------------------------------------------------------------------------

HULP_BLOK = r'''/* v23.158: de drie dingen die ontbraken.
   Stefan: "ik mis nog vaak uitleg of als ik een foutmaak, waarom ik het fout maak en dan een
   ezelsbrug of andere hulp."

   kern  - de regel in twee zinnen, en die staat nu VOOR de eerste vraag in plaats van dichtgeklapt
           achter stap 3. Zonder dit begon elk onderwerp met raden.
   brug  - het ezelsbruggetje. Niet de regel nog eens, maar de haak waarmee je hem terugvindt op het
           moment dat het telt.
   mis   - wat jouw fout waarschijnlijk was. Dit kan per concept omdat elk concept precies één
           tweedeling is: kies je de andere kant, dan is dat bijna altijd dezelfde verwarring, en
           bij deze 23 is die verwarring bekend en benoembaar.

   Los van GC_CONCEPTEN, want dat is een lijst van vraaggeneratoren en dit is lesmateriaal. */
var GC_HULP = {
 muymucho:{
  kern:"Muy staat bij een woord dat iets beschrijft: muy alto, muy bien. Mucho staat bij een hoeveelheid (mucho dinero, muchas cosas) of bij het werkwoord zelf (trabajo mucho).",
  kernEn:"Muy goes with a word that describes: muy alto, muy bien. Mucho goes with an amount (mucho dinero, muchas cosas) or with the verb itself (trabajo mucho).",
  brug:"Mucho telt, en telt past zich aan: mucho, mucha, muchos, muchas. Muy verandert nooit van vorm. Verandert het woord mee met wat erachter staat, dan is het mucho.",
  brugEn:"Mucho counts, and counting means changing shape: mucho, mucha, muchos, muchas. Muy never changes. If the word has to agree with what follows, it is mucho.",
  mis:"Bijna iedereen kiest hier op de vertaling: “heel veel” voelt als mucho. Kijk niet naar het Nederlands maar naar het woord dat erachter staat.",
  misEn:"Almost everyone goes by the translation here: “very much” feels like mucho. Don't look at the English, look at the word that comes after."},
 serestar:{
  kern:"Ser is wie of wat iets is: identiteit, beroep, herkomst, karakter. Estar is hoe of waar iets nu is: toestand en plaats.",
  kernEn:"Ser is who or what something is: identity, job, origin, character. Estar is how or where something is right now: state and place.",
  brug:"EstAr heeft de A van Adres en van Anders-dan-anders. Ser is de essentie: wat overblijft als je alles van vandaag weghaalt.",
  brugEn:"EstAr has the A of Address and of Alterable. Ser is the essence: what is left when you take today away.",
  mis:"De regel die je waarschijnlijk gebruikt is blijvend tegenover tijdelijk. Die klopt vaak toevallig en laat je zakken waar het telt: está muerto is nogal permanent, es joven is nogal tijdelijk.",
  misEn:"The rule you are probably using is permanent versus temporary. It happens to work often and fails where it matters: está muerto is quite permanent, es joven is quite temporary."},
 porpara:{
  kern:"Para kijkt vooruit: doel, bestemming, deadline, voor wie het is. Por kijkt terug of gaat ergens doorheen: oorzaak, ruil, route, tijdsduur.",
  kernEn:"Para looks forward: purpose, destination, deadline, who it is for. Por looks back or passes through: cause, exchange, route, duration.",
  brug:"PARA is een pijl vooruit, met de A van Aankomst. POR is de weg zelf, met de O van Oorzaak en Omweg.",
  brugEn:"PARA is an arrow forward, with the A of Arrival. POR is the road itself, with the O of Origin and Of-going-through.",
  mis:"Allebei worden het in het Nederlands “voor”, en daar gaat het mis. Vraag niet welk woord er hoort maar welke kant de zin op kijkt: naar het doel, of naar de reden.",
  misEn:"Both come out as “for”, and that is where it breaks. Don't ask which word fits, ask which way the sentence is looking: at the goal, or at the reason."},
 hayestar:{
  kern:"Hay meldt dat iets bestaat, en is altijd hay. Está zegt waar iets bekends staat, en past zich aan: está, están.",
  kernEn:"Hay reports that something exists, and is always hay. Está says where something known is, and it agrees: está, están.",
  brug:"Kijk naar het woordje ervoor. Un, una, dos, muchos, nada: hay. El, la, mi, een naam: está. Het lidwoord beslist, niet de zin.",
  brugEn:"Look at the little word in front. Un, una, dos, muchos, nada: hay. El, la, mi, a name: está. The article decides, not the sentence.",
  mis:"Je koos waarschijnlijk wat natuurlijk klinkt in het Nederlands, waar “er is” en “staat” door elkaar lopen. Iets nieuws krijgt hay, iets bekends krijgt está.",
  misEn:"You probably went by what sounds natural, where “there is” and “is” blur together. Something new takes hay, something known takes está."},
 perfindef:{
  kern:"Loopt het tijdvak nog (hoy, esta semana, este año, nunca, ya)? Dan he hablado. Is het vak dicht (ayer, anoche, en 2019, hace tres años)? Dan hablé.",
  kernEn:"Is the time frame still running (hoy, esta semana, este año, nunca, ya)? Then he hablado. Is it closed (ayer, anoche, en 2019, hace tres años)? Then hablé.",
  brug:"Zoek het tijdwoord, niet het gevoel. Zit er este, esta of hoy in, dan loopt het vak nog: perfecto. Staat er ayer, anoche of een jaartal, dan is het dicht: indefinido.",
  brugEn:"Look for the time word, not the feeling. Este, esta or hoy in it means the frame is open: perfecto. Ayer, anoche or a year means it is closed: indefinido.",
  mis:"Je gebruikt vermoedelijk “kort geleden tegenover lang geleden”. Dat is niet de regel: esta mañana is om elf uur perfecto en om acht uur ’s avonds indefinido, terwijl het over hetzelfde moment gaat.",
  misEn:"You are probably using “recent versus long ago”. That is not the rule: esta mañana is perfecto at eleven and indefinido at eight in the evening, for the very same moment."},
 indefimperf:{
  kern:"Indefinido is wat er gebeurde en duwt het verhaal vooruit. Imperfecto is het decor eromheen: hoe het was, wat er aan de gang was, wat je altijd deed.",
  kernEn:"Indefinido is what happened and pushes the story forward. Imperfecto is the scenery around it: how things were, what was going on, what you always used to do.",
  brug:"Imperfecto is de film die al draaide, indefinido is de knal die erin gebeurt. Llovía cuando salí: het regende al, en toen ging ik naar buiten.",
  brugEn:"Imperfecto is the film already rolling, indefinido is the bang that happens in it. Llovía cuando salí: it was already raining, and then I went out.",
  mis:"De verleiding is om per werkwoord te kiezen, alsof sommige werkwoorden nou eenmaal imperfecto zijn. Het hangt niet van het werkwoord af maar van de rol in het verhaal, en hetzelfde werkwoord kan beide kanten op.",
  misEn:"The temptation is to choose per verb, as if some verbs are simply imperfecto. It does not depend on the verb but on its role in the story, and the same verb can go either way."},
 saberconocer:{
  kern:"Saber is een feit weten of iets kunnen: sé dónde está, sé nadar. Conocer is bekend zijn met een persoon, plaats of ding: conozco a Marta, conozco Madrid.",
  kernEn:"Saber is knowing a fact or knowing how: sé dónde está, sé nadar. Conocer is being familiar with a person, place or thing: conozco a Marta, conozco Madrid.",
  brug:"Conocer vraagt een persoonlijke a, saber nooit. Staat er een a voor een naam, dan is conocer de enige die past. Sé a Marta bestaat niet.",
  brugEn:"Conocer needs a personal a, saber never does. If there is an a before a name, only conocer fits. Sé a Marta does not exist.",
  mis:"In het Nederlands is beide “kennen”, en daar valt het verschil weg. Vraag: gaat het om informatie in je hoofd (saber) of om ergens geweest zijn en iemand ontmoet hebben (conocer)?",
  misEn:"English says “know” for both, so the split disappears. Ask: is it information in your head (saber) or having been somewhere and met someone (conocer)?"},
 gustar:{
  kern:"Het ding dat je leuk vindt is het onderwerp, niet jij. Me gusta el libro, me gustan los libros: het werkwoord telt de boeken, niet de mensen.",
  kernEn:"The thing you like is the subject, not you. Me gusta el libro, me gustan los libros: the verb counts the books, not the people.",
  brug:"Vertaal in je hoofd naar “het bevalt me”. Dan zie je meteen dat het boek het werkwoord stuurt en jij alleen het me bent.",
  brugEn:"Translate it as “it pleases me” in your head. Then you see at once that the book drives the verb and you are only the me.",
  mis:"Je hebt waarschijnlijk jezelf als onderwerp genomen, zoals in het Nederlands. Me gusto bestaat wel, maar betekent dat je jezelf leuk vindt.",
  misEn:"You probably took yourself as the subject, the way English does. Me gusto exists, but it means you like yourself."},
 concordancia:{
  kern:"Lidwoord en bijvoeglijk naamwoord nemen geslacht en aantal over van het zelfstandig naamwoord. Las casas blancas: drie keer vrouwelijk, drie keer meervoud.",
  kernEn:"The article and the adjective take gender and number from the noun. Las casas blancas: feminine three times, plural three times.",
  brug:"Het zelfstandig naamwoord is de baas, de rest is personeel. Zet eerst dat woord vast, dan volgt de rij vanzelf.",
  brugEn:"The noun is the boss, the rest is staff. Settle the noun first and the row follows by itself.",
  mis:"Het gaat meestal mis omdat je één woord wél aanpast en het andere vergeet. Loop de rij expliciet na: lidwoord, naamwoord, bijvoeglijk naamwoord, alle drie hetzelfde.",
  misEn:"It usually goes wrong because you adjust one word and forget the other. Walk the row on purpose: article, noun, adjective, all three the same."},
 genero:{
  kern:"-ción, -sión, -dad, -tad en -umbre zijn altijd la. -o en -or zijn el. De rest leer je per woord, samen met het lidwoord.",
  kernEn:"-ción, -sión, -dad, -tad and -umbre are always la. -o and -or are el. The rest you learn word by word, together with its article.",
  brug:"De vier vrouwelijke uitgangen passen in één zin: la canCIÓN de la ciuDAD, la liberTAD y la costUMBRE. Ken je dat zinnetje, dan ken je de regel.",
  brugEn:"The four feminine endings fit in one line: la canCIÓN de la ciuDAD, la liberTAD y la costUMBRE. Know the line and you know the rule.",
  mis:"De val is het Griekse groepje op -ma: el problema, el tema, el sistema, el idioma. Die zien er vrouwelijk uit en zijn mannelijk, en juist die kwam je waarschijnlijk tegen.",
  misEn:"The trap is the Greek group ending in -ma: el problema, el tema, el sistema, el idioma. They look feminine and are masculine, and that is probably the one you hit."},
 reflexivo:{
  kern:"Het voornaamwoord hoort bij de persoon van het werkwoord: me levanto, te levantas, se levanta, nos levantamos, os levantáis, se levantan.",
  kernEn:"The pronoun matches the person of the verb: me levanto, te levantas, se levanta, nos levantamos, os levantáis, se levantan.",
  brug:"De uitgang verklapt het voornaamwoord. Eindigt het werkwoord op -o, dan me. Op -s, dan te. Anders se of nos.",
  brugEn:"The ending gives away the pronoun. Verb ending in -o means me. In -s means te. Otherwise se or nos.",
  mis:"Se blijft vaak staan omdat je het werkwoord zo geleerd hebt: levantarse. Maar se hoort alleen bij hij, zij, u en zij-meervoud, nooit bij een ik-vorm.",
  misEn:"Se often sticks because that is how you learned the verb: levantarse. But se only belongs with he, she, you formal and they, never with an I-form."},
 demostrativo:{
  kern:"Este is bij mij, ese is bij jou, aquel is ver van ons allebei. Pas daarna kies je de vorm: este, esta, estos, estas.",
  kernEn:"Este is near me, ese is near you, aquel is far from both of us. Only after that do you pick the form: este, esta, estos, estas.",
  brug:"Drie stappen weg: este is hier in mijn hand, ese is daar bij jou, aquel is daarginds. En este heeft de T van “tegen mij aan”.",
  brugEn:"Three steps away: este is here in my hand, ese is there by you, aquel is over yonder.",
  mis:"Je had waarschijnlijk de goede afstand en de verkeerde vorm, of andersom. Het zijn twee beslissingen na elkaar: eerst de afstand, dan geslacht en aantal.",
  misEn:"You probably had the right distance and the wrong form, or the other way round. There are two decisions in a row: distance first, then gender and number."},
 quecual:{
  kern:"Qué vraagt wat voor iets: een soort, een omschrijving. Cuál vraagt welke van deze: een keuze uit een groep die er al is.",
  kernEn:"Qué asks what kind: a type, a description. Cuál asks which one of these: a choice from a group that already exists.",
  brug:"Staat er direct een zelfstandig naamwoord achter, dan qué: ¿Qué libro? Staat er es of son achter, dan cuál: ¿Cuál es tu nombre?",
  brugEn:"A noun straight after it means qué: ¿Qué libro? Es or son after it means cuál: ¿Cuál es tu nombre?",
  mis:"¿Cuál es tu nombre? is de zin waar bijna iedereen qué zegt, omdat “wat is je naam” nou eenmaal zo klinkt. Vóór es en son staat cuál, ook al voelt het verkeerd.",
  misEn:"¿Cuál es tu nombre? is the sentence where almost everyone says qué, because “what is your name” simply sounds that way. Before es and son it is cuál, however wrong it feels."},
 saberpoder:{
  kern:"Saber is iets geleerd hebben: sé nadar, ik kan zwemmen omdat ik het ooit leerde. Poder is nu mogelijk of toegestaan: no puedo nadar, het water is te koud.",
  kernEn:"Saber is having learned something: sé nadar, I can swim because I once learned. Poder is possible or allowed right now: no puedo nadar, the water is too cold.",
  brug:"Zeg de zin eens met “ik heb geleerd om” erin. Past dat, dan saber. Past “het lukt nu” of “het mag” beter, dan poder.",
  brugEn:"Try the sentence with “I know how to” in it. If it fits, saber. If “it is possible right now” or “I am allowed” fits better, poder.",
  mis:"In het Nederlands is allebei “kunnen”, dus je kiest op gevoel. Het verschil is de vaardigheid in je hoofd tegenover de omstandigheid om je heen.",
  misEn:"English says “can” for both, so you choose by feel. The difference is the skill in your head versus the circumstances around you."},
 apersonal:{
  kern:"Een bepaald persoon als lijdend voorwerp krijgt a: veo a Ana, busco a mi hermano. Een ding krijgt hem niet: veo la película.",
  kernEn:"A specific person as the object takes a: veo a Ana, busco a mi hermano. A thing does not: veo la película.",
  brug:"Kan het lijdend voorwerp je gedag zeggen? Dan zet je er a voor. Huisdieren met een naam horen erbij, een onbekende “een dokter, welke dan ook” niet.",
  brugEn:"Could the object say hello back? Then put a in front. Named pets count, an unspecific “a doctor, any doctor” does not.",
  mis:"De a heeft in het Nederlands geen tegenhanger, dus je vergeet hem gewoon. Hij verdwijnt alleen als de persoon onbepaald is: busco un médico.",
  misEn:"The a has no English counterpart, so you simply drop it. It only disappears when the person is unspecific: busco un médico."},
 pronombre:{
  kern:"Le staat voor aan wie iets gaat: le doy el libro. Lo en la staan voor wie of wat je ziet, koopt of doet: lo veo, la compro.",
  kernEn:"Le stands for who something goes to: le doy el libro. Lo and la stand for who or what you see, buy or do: lo veo, la compro.",
  brug:"Past het woordje “aan” ervoor? Dan le. Anders lo of la, en dan kijk je naar het geslacht van het ding.",
  brugEn:"Does the word “to” fit in front? Then le. Otherwise lo or la, and then check the gender of the thing.",
  mis:"Le en lo lijken op elkaar en het Nederlands zegt bij allebei “hem”. De vraag die het beslist is niet wie het is maar of er “aan” voor kan.",
  misEn:"Le and lo look alike and English says “him” for both. The deciding question is not who it is but whether “to” can go in front."},
 comparar:{
  kern:"Ongelijk: más of menos, dan que. Gelijk: tan plus een eigenschap plus como, maar tanto, tanta, tantos of tantas plus een zelfstandig naamwoord plus como.",
  kernEn:"Unequal: más or menos, then que. Equal: tan plus a quality plus como, but tanto, tanta, tantos or tantas plus a noun plus como.",
  brug:"Tan blijft altijd tan. Tanto telt, en telt past zich aan. Staat er een ding achter, dan wordt er geteld, dus tanto.",
  brugEn:"Tan always stays tan. Tanto counts, and counting means agreeing. A thing after it means counting, so tanto.",
  mis:"Het gaat vrijwel altijd mis tussen tan en tanto. Kijk niet naar de vertaling maar naar wat erachter staat: een eigenschap (tan alto) of een hoeveelheid (tantos libros).",
  misEn:"It nearly always goes wrong between tan and tanto. Don't look at the translation, look at what follows: a quality (tan alto) or an amount (tantos libros)."},
 zapato:{
  kern:"De klinker in de stam wisselt alleen als de klemtoon erop valt. Bij nosotros en vosotros springt de klemtoon naar de uitgang, dus daar wisselt er niets.",
  kernEn:"The stem vowel only changes when the stress lands on it. With nosotros and vosotros the stress jumps to the ending, so nothing changes there.",
  brug:"De schoen: de wissel raakt de vier hoeken (yo, tú, él, ellos) en laat het midden (nosotros, vosotros) staan. Teken die vorm in gedachten en je ziet een schoen.",
  brugEn:"The shoe: the change hits the four corners (yo, tú, él, ellos) and leaves the middle (nosotros, vosotros) alone. Sketch that shape and you see a shoe.",
  mis:"De fout is bijna altijd nosotros of vosotros mee laten wisselen. Podemos, niet puedemos. Queremos, niet quieremos. Precies daar zit het gat in de schoen.",
  misEn:"The mistake is nearly always letting nosotros or vosotros change too. Podemos, not puedemos. Queremos, not quieremos. That is exactly the hole in the shoe."},
 tuusted:{
  kern:"Usted is beleefd u, maar neemt de werkwoordsvorm van hij en zij: usted habla, usted tiene. En de kleine woordjes schuiven mee: te wordt se, tu wordt su.",
  kernEn:"Usted is polite you, but takes the he and she verb form: usted habla, usted tiene. And the little words shift along: te becomes se, tu becomes su.",
  brug:"Usted is de derde persoon met een pak aan. Praat over de ander alsof hij er niet bij zit, en de vorm klopt vanzelf.",
  brugEn:"Usted is the third person in a suit. Talk about the other person as if they were not there, and the form comes out right.",
  mis:"Je denkt “u” en pakt daarom de jij-vorm met een beleefd randje eraan. Usted hablas bestaat niet: usted heeft helemaal geen eigen vorm.",
  misEn:"You think “you” and reach for the tú form with a polite edge. Usted hablas does not exist: usted has no form of its own at all."},
 negacion:{
  kern:"Staat het ontkennende woord achter het werkwoord, dan hoort er no voor: no tengo nada. Zet je het vooraan, dan valt de no juist weg: nunca como carne.",
  kernEn:"If the negative word comes after the verb, no goes in front: no tengo nada. Put it at the front and the no drops out: nunca como carne.",
  brug:"Er staat altijd precies één ontkenning vóór het werkwoord. Is dat nada of nunca zelf al, dan is no overbodig. Is die plek leeg, dan hoort no daar.",
  brugEn:"There is always exactly one negative before the verb. If nada or nunca is already there, no is redundant. If that spot is empty, no belongs there.",
  mis:"In het Nederlands is een dubbele ontkenning fout, dus je haalt de no weg. In het Spaans is dit geen dubbele ontkenning maar één ontkenning die over twee woorden verdeeld staat.",
  misEn:"In English a double negative is wrong, so you delete the no. In Spanish this is not a double negative but one negation spread over two words."},
 pedirpreguntar:{
  kern:"Pedir is vragen om iets dat je wilt krijgen: pido un café. Preguntar is een vraag stellen omdat je iets wilt weten: pregunto dónde está.",
  kernEn:"Pedir is asking for something you want to receive: pido un café. Preguntar is asking a question because you want to know: pregunto dónde está.",
  brug:"Komt er een ding achter, dan pedir. Komt er een vraagwoord achter (dónde, cuándo, cuánto, si), dan preguntar.",
  brugEn:"A thing after it means pedir. A question word after it (dónde, cuándo, cuánto, si) means preguntar.",
  mis:"Het Nederlands heeft één woord voor allebei, dus je hoort het verschil niet. In een restaurant is het altijd pedir: je bestelt, je vraagt geen informatie.",
  misEn:"English has one word for both, so you don't hear the split. In a restaurant it is always pedir: you are ordering, not asking for information."},
 gerundio:{
  kern:"Presente is een gewoonte of iets algemeens: como a las dos. Estar plus gerundio is wat op dit moment bezig is: estoy comiendo.",
  kernEn:"Presente is a habit or something general: como a las dos. Estar plus gerundio is what is going on right now: estoy comiendo.",
  brug:"Het signaalwoord verklapt het. Ahora, ahora mismo en en este momento trekken gerundio. Normalmente, siempre en todos los días trekken presente.",
  brugEn:"The signal word gives it away. Ahora, ahora mismo and en este momento pull gerundio. Normalmente, siempre and todos los días pull presente.",
  mis:"Het Nederlands heeft geen aparte vorm, dus je pakt standaard de presente. Andersom komt ook voor: estoy comiendo todos los días klopt niet, want een gewoonte blijft presente.",
  misEn:"English overuses the -ing form, so it slips in where a habit belongs. Estoy comiendo todos los días is wrong: a habit stays presente."},
 futuroir:{
  kern:"Ir a plus het hele werkwoord is je plan: voy a comer. Ir draagt de persoon (voy, vas, va, vamos, vais, van), het tweede werkwoord verandert niet.",
  kernEn:"Ir a plus the infinitive is your plan: voy a comer. Ir carries the person (voy, vas, va, vamos, vais, van), the second verb does not change.",
  brug:"Alleen de eerste helft vervoegt. Na de a staat altijd het woordenboekwoord, met -ar, -er of -ir er nog aan.",
  brugEn:"Only the first half conjugates. After the a you always get the dictionary form, still ending in -ar, -er or -ir.",
  mis:"De verleiding is om het tweede werkwoord ook te vervoegen: voy a como. Er is er maar één die de persoon draagt, en dat is ir.",
  misEn:"The temptation is to conjugate the second verb as well: voy a como. Only one verb carries the person, and that is ir."}
};
function gcHulp(id){ return GC_HULP[(id || "").replace(/^concept-/, "")] || null; }
function gcHulpTekst(h, veld){ return h ? ct(h[veld], h[veld + "En"] || h[veld]) : ""; }
'''

# ---------------------------------------------------------------------------
# 2. de kern staat nu voor de eerste vraag, en de hulp reist mee met elke stap
# ---------------------------------------------------------------------------

if DOE_APP:
    rep("var GC_STAP_TXT = {", HULP_BLOK + "var GC_STAP_TXT = {")

    # stap 1: de regel erbij, en de gok-zin eruit. Je gokt niet meer.
    rep(
        '''    stappen.push({kop:GC_STAP_TXT.nl.k1, kopEn:GC_STAP_TXT.en.k1, procedureel:true,
      uitleg:"<p>" + GC_STAP_TXT.nl.u1 + "</p>", uitlegEn:"<p>" + GC_STAP_TXT.en.u1 + "</p>",
      vragen:vb.slice(0, 2)});''',
        '''    /* v23.158: hier stond alleen de zin "gok gerust". Stefan: "de toetsjes ... sluiten niet stap
       voor stap aan bij wat je leerde." Klopte letterlijk: op dit scherm stond geen woord Spaans
       voordat de eerste vraag kwam, en de regel zelf zat achteraan in stap 3, dichtgeklapt. Nu
       staat de kern erboven, met de ezelsbrug. Nog steeds geen eigen scherm (procedureel blijft),
       want je leest hem terwijl je hem gebruikt. */
    stappen.push({kop:GC_STAP_TXT.nl.k1, kopEn:GC_STAP_TXT.en.k1, procedureel:true, kern:true,
      hulp:gcHulp(c.id),
      uitleg:"<p>" + GC_STAP_TXT.nl.u1 + "</p>", uitlegEn:"<p>" + GC_STAP_TXT.en.u1 + "</p>",
      vragen:vb.slice(0, 2)});''')

    rep(
        '''    stappen.push({kop:GC_STAP_TXT.nl.k2, kopEn:GC_STAP_TXT.en.k2,
      uitleg:"", uitlegEn:"", vragen:vb.slice(2)});''',
        '''    stappen.push({kop:GC_STAP_TXT.nl.k2, kopEn:GC_STAP_TXT.en.k2, hulp:gcHulp(c.id),
      uitleg:"", uitlegEn:"", vragen:vb.slice(2)});''')

    rep(
        '''  stappen.push({kop:GC_STAP_TXT.nl.k3, kopEn:GC_STAP_TXT.en.k3,
    uitleg:"", uitlegEn:"",''',
        '''  stappen.push({kop:GC_STAP_TXT.nl.k3, kopEn:GC_STAP_TXT.en.k3, hulp:gcHulp(c.id),
    uitleg:"", uitlegEn:"",''')

    # ---------------------------------------------------------------------------
    # 3. de fout komt terug: een correctieronde aan het eind van de stap
    # ---------------------------------------------------------------------------

    rep(
        '''function gwVraagTekst(q){ return ct(q.v, q.vEn || q.v); }''',
        '''/* v23.158: de vragen van deze stap, plus wat je fout had en dus nog een keer krijgt.
   Wat er stond: je antwoordde fout, las één regel uitleg en klikte door. De correctie werd gelezen
   en nooit opgehaald, en ophalen is het hele punt van oefenen. Nu komt een fout antwoord aan het
   eind van de stap terug, met de opties in een andere volgorde zodat je de plek niet onthoudt.
   Eén keer per vraag: een tweede fout laat hem niet nog eens terugkomen, want dan zit je vast. */
function gwVragen(){
  var o = gwOnderwerp(gwSess.id);
  var stap = o && o.stappen[gwSess.stap];
  if(!stap) return [];
  return stap.vragen.concat(gwSess.extra || []);
}
function gwBasisAantal(){
  var o = gwOnderwerp(gwSess.id);
  var stap = o && o.stappen[gwSess.stap];
  return stap ? stap.vragen.length : 0;
}
function gwInCorrectie(){ return gwSess.vraag >= gwBasisAantal(); }
function gwVraagTekst(q){ return ct(q.v, q.vEn || q.v); }''')

    # gwSess krijgt de lijst mee
    rep('''  gwSess = {id:id, stap:s, fase:gwStapHeeftTekst(o, s) ? "uitleg" : "toets",
            vraag:0, goed:0, fout:0, gekozen:null};''',
        '''  gwSess = {id:id, stap:s, fase:gwStapHeeftTekst(o, s) ? "uitleg" : "toets",
            vraag:0, goed:0, fout:0, gekozen:null, extra:[]};''')

    rep('''          gwSess = {id:st.id, stap:Math.min(gwv.stap, gwo.stappen.length - 1), fase:"uitleg", vraag:0, goed:0, fout:0, gekozen:null};''',
        '''          gwSess = {id:st.id, stap:Math.min(gwv.stap, gwo.stappen.length - 1), fase:"uitleg", vraag:0, goed:0, fout:0, gekozen:null, extra:[]};''')

    rep('''function gwNaarToets(){
  gwSess.fase = "toets"; gwSess.vraag = 0; gwSess.gekozen = null;
  renderCheat();
}''',
        '''function gwNaarToets(){
  gwSess.fase = "toets"; gwSess.vraag = 0; gwSess.gekozen = null; gwSess.extra = [];
  renderCheat();
}''')

    rep('''    gwSess.fase = gwStapHeeftTekst(o, gwSess.stap) ? "uitleg" : "toets";
    gwSess.vraag = 0; gwSess.goed = 0; gwSess.fout = 0; gwSess.gekozen = null;''',
        '''    gwSess.fase = gwStapHeeftTekst(o, gwSess.stap) ? "uitleg" : "toets";
    gwSess.vraag = 0; gwSess.goed = 0; gwSess.fout = 0; gwSess.gekozen = null; gwSess.extra = [];''')

    rep('''function gwKies(i){
  var o = gwOnderwerp(gwSess.id);
  var stap = o.stappen[gwSess.stap];
  var q = stap.vragen[gwSess.vraag];
  if(gwSess.gekozen !== null) return; // al beantwoord
  gwSess.gekozen = i;
  if(i === q.g){
    gwSess.goed++;
    addXP(2);
    trackPoging(false);
  } else {''',
        '''function gwKies(i){
  var o = gwOnderwerp(gwSess.id);
  var stap = o.stappen[gwSess.stap];
  var q = gwVragen()[gwSess.vraag];
  if(gwSess.gekozen !== null) return; // al beantwoord
  gwSess.gekozen = i;
  /* v23.158: een correctievraag is geen toetsvraag. Hij telt niet mee voor je score, levert geen
     taco's op en raakt je doosje niet aan: anders zou fout antwoorden een manier zijn om extra
     punten te halen, en zou "2 van de 2 goed" opeens over vier vragen kunnen gaan. Het is een
     tweede poging op iets dat je net fout had, en dat is het. */
  if(gwInCorrectie()){
    gwSess.correctieGoed = (gwSess.correctieGoed || 0) + (i === q.g ? 1 : 0);
    persist();
    renderCheat();
    return;
  }
  if(i === q.g){
    gwSess.goed++;
    addXP(2);
    trackPoging(false);
  } else {
    // deze komt aan het eind van de stap nog één keer terug, met geschudde opties
    try {
      gwSess.extra = gwSess.extra || [];
      gwSess.extra.push(gcSchud({v:q.v, vEn:q.vEn, o:q.o.slice(), oEn:q.oEn ? q.oEn.slice() : null,
                                 g:q.g, w:q.w, wEn:q.wEn}));
    } catch(e){}''')

    rep('''function gwVolgende(){
  var o = gwOnderwerp(gwSess.id);
  var stap = o.stappen[gwSess.stap];
  if(gwSess.vraag < stap.vragen.length - 1){''',
        '''function gwVolgende(){
  var o = gwOnderwerp(gwSess.id);
  var stap = o.stappen[gwSess.stap];
  if(gwSess.vraag < gwVragen().length - 1){''')

    # ---------------------------------------------------------------------------
    # 4. het scherm: de kern erboven, en bij een fout de diagnose en de brug
    # ---------------------------------------------------------------------------

    rep('''  if(gwSess.fase === "toets"){
    var q = stap.vragen[gwSess.vraag];
    var opties = gwOpties(q);
    var beantwoord = gwSess.gekozen !== null;
    var html = kop +
      "<span class='kicker'>"+ct("Vraag ","Question ")+(gwSess.vraag+1)+"/"+stap.vragen.length+"</span>"+
      /* v23.154: de zin die eerst een heel scherm vulde staat nu hier, bij de eerste vraag, waar hij
         hoort: het is een gebruiksaanwijzing en die lees je terwijl je het doet. */
      (stap.procedureel && gwSess.vraag === 0
        ? "<p class='muted' style='margin:4px 0 0; font-size:.85rem'>"+
            String(ct(stap.uitleg, stap.uitlegEn) || "").replace(/<[^>]*>/g, "")+"</p>"
        : "")+''',
        '''  if(gwSess.fase === "toets"){
    var alleV = gwVragen(), basisN = gwBasisAantal(), inCorr = gwSess.vraag >= basisN;
    var q = alleV[gwSess.vraag];
    var opties = gwOpties(q);
    var beantwoord = gwSess.gekozen !== null;
    var html = kop +
      "<span class='kicker'>"+(inCorr
        ? ct("Nog een keer ","Once more ")+(gwSess.vraag - basisN + 1)+"/"+(alleV.length - basisN)
        : ct("Vraag ","Question ")+(gwSess.vraag+1)+"/"+basisN)+"</span>"+
      /* v23.158: hier stond alleen de gebruiksaanwijzing ("gok gerust"). Nu staat de regel zelf er,
         met de ezelsbrug eronder, vóór de eerste vraag. Zie gcBouw. */
      (stap.procedureel && gwSess.vraag === 0
        ? (stap.kern && stap.hulp
            /* de regel zelf, met de ezelsbrug eronder */
            ? "<div class='gwkern'><p>"+gcHulpTekst(stap.hulp, "kern")+"</p>"+
                "<p class='brug'><b>"+ct("Ezelsbruggetje","Memory hook")+":</b> "+gcHulpTekst(stap.hulp, "brug")+"</p></div>"
            /* v23.154 als terugval: een procedurele stap zonder hulp houdt zijn gebruiksaanwijzing.
               Twee grijze alinea's boven elkaar zetten is precies het schermvullen waar Stefan over
               schreef, dus het is het een of het ander. */
            : "<p class='muted' style='margin:4px 0 0; font-size:.85rem'>"+
                String(ct(stap.uitleg, stap.uitlegEn) || "").replace(/<[^>]*>/g, "")+"</p>")
        : "")+
      (inCorr && gwSess.vraag === basisN
        ? "<p class='muted' style='margin:4px 0 0; font-size:.85rem'>"+
            ct("Dit had je net fout. Dezelfde vraag, andere volgorde.","You got this wrong just now. Same question, different order.")+"</p>"
        : "")+''')

    rep('''    if(beantwoord){
      var goed = gwSess.gekozen === q.g;
      html += "<div class='feedback "+(goed?"ok":"fout")+"' style='margin-top:10px'>"+
        (goed ? "\\u00a1Correcto! \\u2713 (+2 "+xpw()+")" : ct("Nog niet. Het juiste antwoord staat gemarkeerd.","Not yet. The right answer is highlighted."))+
        "</div>"+
        "<p class='muted' style='margin-top:6px'>"+gwWaarom(q)+"</p>"+
        "<div class='row' style='margin-top:10px'><button class='primary' id='gwVolgende'>"+
          (gwSess.vraag < stap.vragen.length - 1 ? ct("Volgende vraag \\u2192","Next question \\u2192") : ct("Stap afronden \\u2192","Finish step \\u2192"))+
        "</button></div>";''',
        '''    if(beantwoord){
      var goed = gwSess.gekozen === q.g;
      html += "<div class='feedback "+(goed?"ok":"fout")+"' style='margin-top:10px'>"+
        (goed
          ? (inCorr ? ct("\\u00a1Correcto! \\u2713 Nu wel.","\\u00a1Correcto! \\u2713 Got it this time.") : "\\u00a1Correcto! \\u2713 (+2 "+xpw()+")")
          : ct("Nog niet. Het juiste antwoord staat gemarkeerd.","Not yet. The right answer is highlighted."))+
        "</div>"+
        "<p class='muted' style='margin-top:6px'>"+gwWaarom(q)+"</p>"+
        /* v23.158. Stefan: "als ik een fout maak, waarom ik het fout maak en dan een ezelsbrug of
           andere hulp." De regel hierboven zegt waarom het JUISTE antwoord goed is. Deze twee
           blokken gaan over jouw antwoord, en ze staan er alleen als je het fout had: bij een goed
           antwoord is dit ruis. */
        (!goed && stap.hulp
          ? "<div class='gwmis'><p><b>"+ct("Waar het meestal misgaat","Where this usually goes wrong")+":</b> "+
              gcHulpTekst(stap.hulp, "mis")+"</p>"+
              "<p class='brug'><b>"+ct("Ezelsbruggetje","Memory hook")+":</b> "+gcHulpTekst(stap.hulp, "brug")+"</p></div>"
          : "")+
        "<div class='row' style='margin-top:10px'><button class='primary' id='gwVolgende'>"+
          (gwSess.vraag < alleV.length - 1
            ? (gwSess.vraag + 1 >= basisN ? ct("Volgende \\u2192","Next \\u2192")
               : (gwSess.extra && gwSess.extra.length && gwSess.vraag === basisN - 1
                  ? ct("Nog even terug naar je fout \\u2192","Back to what you missed \\u2192")
                  : ct("Volgende vraag \\u2192","Next question \\u2192")))
            : ct("Stap afronden \\u2192","Finish step \\u2192"))+
        "</button></div>";''')

    # de stapklaar-teller blijft over de basisvragen gaan, en noemt de correctie apart
    rep('''  if(gwSess.fase === "stapklaar"){
    var totaal = stap.vragen.length;''',
        '''  if(gwSess.fase === "stapklaar"){
    var totaal = stap.vragen.length;
    var corrN = (gwSess.extra || []).length, corrG = gwSess.correctieGoed || 0;''')

    rep('''        ct(gwSess.goed+" van de "+totaal+" goed", gwSess.goed+" out of "+totaal+" correct")+''',
        '''        ct(gwSess.goed+" van de "+totaal+" goed", gwSess.goed+" out of "+totaal+" correct")+
        /* v23.158: de correctieronde telt niet mee in het cijfer, maar hem verzwijgen zou raar zijn:
           je hebt er net vragen voor beantwoord. */
        (corrN ? " \\u00b7 " + ct(corrG+" van de "+corrN+" verbeterd", corrG+" of "+corrN+" corrected") : "")+''')

    # ---------------------------------------------------------------------------
    # 5. de opmaak
    # ---------------------------------------------------------------------------

    rep('''  details.gwdiep{margin:4px 0 0; border-top:1px solid var(--border); padding-top:6px;}''',
        '''  /* v23.158: de regel vóór je eerste vraag, en de hulp na een fout. Twee kaders in plaats van
     nog een grijze alinea, want deze twee moeten er juist uitspringen. */
  .gwkern{margin:6px 0 0; padding:10px 12px; border-radius:10px; background:var(--bg);
    border:1.5px solid var(--border); font-size:.92rem; line-height:1.5;}
  .gwkern p{margin:0;}
  .gwkern p.brug{margin-top:7px; color:var(--muted);}
  .gwmis{margin-top:10px; padding:10px 12px; border-radius:10px; background:var(--amber-soft);
    color:var(--amber); font-size:.92rem; line-height:1.5;}
  .gwmis p{margin:0;}
  .gwmis p.brug{margin-top:7px;}
  details.gwdiep{margin:4px 0 0; border-top:1px solid var(--border); padding-top:6px;}''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
