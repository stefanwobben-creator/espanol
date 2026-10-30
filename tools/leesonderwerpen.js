/* tools/leesonderwerpen.js - de bronlijst waar leesverhalen vandaan komen
   =======================================================================

   WAAROM DIT BESTAND BESTAAT

   Stefan, 30 oktober: "ik weet wel dat de inhoud van de verhalen heel belangrijk is, chispa verhaal
   was echt leuk, franco regime was interessant, de verhalen geinspireerd op don quijote ook heel
   leuk."

   Hij noemt drie van de vier bestaande reeksen. De vierde, "España por dentro" (het etentje van
   tienen, de sobremesa), noemt hij niet. Leg dat naast de gemeten tokendekking:

       quij   68,1%   Don Quijote            noemt hij
       boek   69,9%   Chispa                 noemt hij
       hist   71,7%   Franco                 noemt hij
       vida   73,5%   España por dentro      noemt hij niet

   De drie die hij leuk vindt zijn de moeilijkste, en de makkelijkste noemt hij niet. Vier reeksen is
   geen bewijs, maar het waarschuwt wel ergens voor: een tekst optimaliseren op dekking levert een
   tekst op die over woorden gaat in plaats van over iets.

   Daarom deze volgorde, en die is de hele reden van dit bestand:

       HET ONDERWERP KOMT VAN BUITEN. DE WOORDENLIJST BEPAALT HOE JE HET VERTELT, NIET WAAROVER.

   Dat is hoe graded readers al honderd jaar gemaakt worden: een bestaand verhaal, naverteld binnen
   een afgebakende woordenschat. Niemand maakt er een door een woordenlijst te nemen en te kijken wat
   voor verhaal eruit valt. Een taalmodel is uitstekend in navertellen en slecht in bedenken wat
   iemand boeit, dus het krijgt het onderwerp aangereikt en doet alleen het navertellen.

   WAT DE DRIE GESLAAGDE REEKSEN GEMEEN HEBBEN

   Er staat iets op het spel en er is een wereld. Een ei dat zijn lied niet kent, een land dat in
   tweeën breekt, een man die te veel gelezen heeft. Geen enkele gaat over boodschappen doen.

   HET CONTRACT VOOR DE GENERATOR

   Per hoofdstuk:
     - ongeveer 180 lopende woorden, net als de bestaande hist- en vida-hoofdstukken
     - tokendekking minstens 98% gerekend op (leswoorden van de lezer) + (kernwoorden van dit
       onderwerp) + (de FREQ-top-1000)
     - hoogstens 2 woorden die daar buiten vallen, en die komen daarna in de woordenlijst
     - de kernwoorden hieronder tellen NIET mee als onbekend, op voorwaarde dat ze binnen het
       hoofdstuk minstens twee keer voorkomen. Zonder die uitzondering kun je Franco niet navertellen
       zonder dictatuur, ballingschap en censuur te verliezen, en dat zijn precies de woorden die het
       onderwerp maken. Het nieuwe woord is dan de opbrengst en niet de drempel.
     - de tekst is meteen de transcriptie: audio wordt eruit gegenereerd (zie tools/avondrun-audio.js
       en generate-boek-audio.js), dus geen opsommingen, geen haakjes, geen jaartallen in cijfers waar
       een verteller over struikelt. Schrijf "negentienhonderdzesendertig" waar dat natuurlijk klinkt.

   WELKE WOORDEN "KENT DE LEZER"

   Niet de hele woordenlijst van de app, maar de woorden die deze lezer heeft gehad. En bij voorkeur
   met voorrang voor wat die week toch al toe is voor herhaling: dan is het hoofdstuk niet alleen
   nieuwe content maar een tweede ontmoeting met precies die woorden, in een context in plaats van op
   een kaartje.

   WAT NIET GEKOZEN MAG WORDEN

   Onderwerpen die het leed van nog levende mensen als decor gebruiken. De gestolen kinderen uit de
   Franco-tijd staan daarom niet in deze lijst, hoe sterk het verhaal ook is: dat is geen lesstof voor
   tussen de woordjes door. De burgeroorlog zelf staat er wel in, want die is er al en die werkte.

   ACCURATESSE

   Dit zijn echte onderwerpen en een leerapp is geen plek om geschiedenis te verzinnen. Waar de
   overlevering en de bronnen uiteenlopen staat dat bij het onderwerp, en dan hoort de navertelling
   dat ook te zeggen ("volgens de overlevering") in plaats van het als feit te brengen.

   Twintig onderwerpen, ongeveer tweehonderd hoofdstukken, genoeg voor een paar jaar bij twee per
   week. Geschreven zonder dat Stefan hoefde te schrappen; hij mag er alsnog uit gooien wat hij niet
   wil. */

module.exports = [

  /* ---------- Historia ---------- */
  {
    id: "alandalus", reeks: "Historia", titel: "Al-Andalus", deel: "Ocho siglos", hoofdstukken: 10,
    pitch: "Bijna achthonderd jaar lang was een deel van Spanje Arabisch, en Córdoba was even de " +
           "grootste stad van West-Europa.",
    waarom: "Het ligt overal om hem heen in Spanje en bijna niemand kan het navertellen. En het " +
            "eindigt op een datum die hij al kent: 1492.",
    kernwoorden: ["el califa", "la mezquita", "el reino", "la frontera", "el ejército", "la conquista"]
  },
  {
    id: "mil492", reeks: "Historia", titel: "Mil cuatrocientos noventa y dos", deel: "Un solo año",
    hoofdstukken: 8,
    pitch: "In één jaar valt Granada, vertrekt Columbus en worden de joden het land uit gezet. " +
           "Drie dingen die alles veranderden, binnen twaalf maanden.",
    waarom: "Eén jaar als hoofdpersoon. Dat geeft vanzelf tempo, en de drie verhaallijnen raken " +
            "elkaar.",
    kernwoorden: ["la reina", "el rey", "el viaje", "expulsar", "la corona", "el puerto"]
  },
  {
    id: "numancia", reeks: "Historia", titel: "Numancia", deel: "La ciudad que ardió",
    hoofdstukken: 8,
    pitch: "Een stad in het noorden hield Rome twintig jaar tegen en koos volgens de overlevering " +
           "het vuur boven de overgave.",
    waarom: "Klein, afgebakend, en het einde weet je vanaf hoofdstuk één. Dat werkt hetzelfde als " +
            "bij Chispa: niet wat er gebeurt maar hoe.",
    kernwoorden: ["el muro", "el soldado", "el hambre", "rendirse", "el fuego", "el cerco"],
    letOp: "De brand en de zelfgekozen dood komen uit latere Romeinse bronnen. Vertel het als " +
           "overlevering, niet als vaststaand feit."
  },
  {
    id: "carlistas", reeks: "Historia", titel: "Las guerras carlistas", deel: "Tres veces lo mismo",
    hoofdstukken: 8,
    pitch: "Drie burgeroorlogen in de negentiende eeuw, allemaal over de vraag wie er op de troon " +
           "hoort. Het noorden tegen het zuiden, en het blijft terugkomen.",
    waarom: "Het legt uit waarom Spanje in 1936 al wist hoe een burgeroorlog ging. Het verbindt " +
            "zich met de reeks die hij al goed vond.",
    kernwoorden: ["el trono", "la herencia", "la montaña", "el bando", "la paz", "el heredero"]
  },
  {
    id: "gripe", reeks: "Historia", titel: "La gripe mal llamada", deel: "Mil novecientos dieciocho",
    hoofdstukken: 6,
    pitch: "De Spaanse griep kwam niet uit Spanje. Hij heet zo omdat Spanje als enige niet loog " +
           "over hoe erg het was.",
    waarom: "Een naam die een leugen is. Dat is precies het soort wending dat een hoofdstuk draagt.",
    kernwoorden: ["la enfermedad", "la guerra", "el periódico", "la censura", "el médico", "la ola"]
  },
  {
    id: "transicion", reeks: "Historia", titel: "La Transición", deel: "De la dictadura al voto",
    hoofdstukken: 10,
    pitch: "Hoe een dictatuur een democratie werd zonder nieuwe oorlog, en hoe dicht dat in " +
           "februari eenentachtig alsnog bij misging.",
    waarom: "De directe vervolgreeks op Franco, die hij interessant vond. En de afloop is de wereld " +
            "waar hij nu in woont.",
    kernwoorden: ["el voto", "la ley", "el golpe", "la libertad", "el partido", "la plaza"]
  },

  /* ---------- Literatura ---------- */
  {
    id: "lazarillo", reeks: "Literatura", titel: "Lazarillo de Tormes", deel: "El primer pícaro",
    hoofdstukken: 10,
    pitch: "Een arme jongen dient de ene na de andere meester en bedriegt ze allemaal, te beginnen " +
           "met een blinde man. Niemand weet wie het geschreven heeft.",
    waarom: "Dezelfde vorm die bij Don Quijote werkte: losse afleveringen, één hoofdpersoon, en een " +
            "toon die vierhonderd jaar oud is en nog steeds grappig.",
    kernwoorden: ["el amo", "el ciego", "el pan", "engañar", "el hambre", "la calle"]
  },
  {
    id: "lorca", reeks: "Literatura", titel: "Lorca y los del veintisiete", deel: "Amigos y versos",
    hoofdstukken: 10,
    pitch: "Een groep dichters en kunstenaars die elkaar vonden, beroemd werden, en in zesendertig " +
           "uit elkaar werd geslagen. Lorca werd vlak bij Granada doodgeschoten en nooit gevonden.",
    waarom: "Vriendschap met een afloop die je ziet aankomen. En het geeft hem gedichten die kort " +
            "genoeg zijn om echt te lezen.",
    kernwoorden: ["el poeta", "el verso", "el amigo", "la luna", "el olivo", "desaparecer"],
    letOp: "Over de precieze omstandigheden van Lorca's dood bestaat geen zekerheid. Niet invullen " +
           "wat niet vaststaat."
  },
  {
    id: "celestina", reeks: "Literatura", titel: "La Celestina", deel: "La vieja que sabía demasiado",
    hoofdstukken: 8,
    pitch: "Een oude koppelaarster brengt twee geliefden bij elkaar voor geld, en het loopt voor " +
           "iedereen slecht af. Uit veertienhonderdnegenennegentig.",
    waarom: "Eén sluwe hoofdpersoon die alles in gang zet. Dat leest als een misdaadverhaal.",
    kernwoorden: ["el amor", "el dinero", "la vieja", "el jardín", "la mentira", "el criado"]
  },
  {
    id: "macondo", reeks: "Literatura", titel: "Macondo", deel: "Cien años, en cien páginas no",
    hoofdstukken: 10,
    pitch: "Een dorp midden in het niets, zeven generaties van dezelfde familie, en regen die vier " +
           "jaar duurt.",
    waarom: "Niet Spaans maar Spaanstalig, en het is het beroemdste boek van de taal die hij leert. " +
            "Goed om te weten dat Spaans meer is dan Spanje.",
    kernwoorden: ["el pueblo", "la lluvia", "la familia", "el hielo", "la memoria", "el río"]
  },

  /* ---------- Arte ---------- */
  {
    id: "meninas", reeks: "Arte", titel: "Las Meninas", deel: "¿Quién mira a quién?",
    hoofdstukken: 6,
    pitch: "Velázquez schildert zichzelf terwijl hij iets schildert dat je niet ziet, en in de " +
           "spiegel achterin staan de koning en de koningin. Of toch niet.",
    waarom: "Eén schilderij, zes hoofdstukken, en elk hoofdstuk draait het om. Hij kan het in het " +
            "Prado gaan bekijken.",
    kernwoorden: ["el cuadro", "el espejo", "la infanta", "el pintor", "la mirada", "el pincel"]
  },
  {
    id: "goyanegro", reeks: "Arte", titel: "Las pinturas negras", deel: "La casa del sordo",
    hoofdstukken: 8,
    pitch: "Een dove oude man schildert veertien nachtmerries rechtstreeks op de muren van zijn " +
           "eigen huis, en laat ze aan niemand zien.",
    waarom: "Donker, kort, en volstrekt raar. Precies het register van het Chispa-boek, maar dan " +
            "voor volwassenen.",
    kernwoorden: ["la pared", "el sordo", "el miedo", "la pintura", "la noche", "el perro"]
  },
  {
    id: "sagrada", reeks: "Arte", titel: "La Sagrada Família", deel: "Una obra más larga que su autor",
    hoofdstukken: 8,
    pitch: "Gaudí begon aan een kerk waarvan hij wist dat hij hem nooit af zou zien, en werd " +
           "overreden door een tram terwijl hij eraan werkte.",
    waarom: "Nog steeds niet af, dus het verhaal loopt door terwijl hij het leest.",
    kernwoorden: ["la torre", "la piedra", "el arquitecto", "la obra", "la luz", "el tranvía"]
  },
  {
    id: "guernica", reeks: "Arte", titel: "Guernica", deel: "Un cuadro como noticia",
    hoofdstukken: 6,
    pitch: "Een dorp wordt op een marktdag gebombardeerd, en zes weken later hangt het als " +
           "schilderij op de wereldtentoonstelling in Parijs.",
    waarom: "Sluit aan op de Franco-reeks en laat zien wat kunst kan doen dat een krant niet kan.",
    kernwoorden: ["el toro", "el caballo", "la bomba", "el grito", "el mercado", "el blanco"]
  },

  /* ---------- Lugares ---------- */
  {
    id: "camino", reeks: "Lugares", titel: "El Camino", deel: "Mil años andando",
    hoofdstukken: 10,
    pitch: "Duizend jaar lang lopen mensen dezelfde weg naar het noordwesten, en niemand is het " +
           "erover eens waarom.",
    waarom: "Een reis met etappes is de makkelijkste vorm die er is voor hoofdstukken, en het is " +
            "iets wat hij zelf kan gaan doen.",
    kernwoorden: ["el peregrino", "la concha", "el albergue", "la flecha", "el camino", "la lluvia"]
  },
  {
    id: "alhambra", reeks: "Lugares", titel: "La Alhambra", deel: "Agua y matemáticas",
    hoofdstukken: 8,
    pitch: "Een paleis gebouwd rond water en herhaling, en de laatste sultan die het weggaf en " +
           "erom huilde.",
    waarom: "Hangt vast aan Al-Andalus en aan veertienhonderdtweeënnegentig, dus de reeksen praten " +
            "met elkaar.",
    kernwoorden: ["el agua", "el patio", "la fuente", "el sultán", "la nieve", "la llave"]
  },
  {
    id: "toledo", reeks: "Lugares", titel: "Toledo", deel: "Tres en una",
    hoofdstukken: 8,
    pitch: "Eén stad op een rots in een rivier, waar eeuwenlang christenen, moslims en joden naast " +
           "elkaar woonden. Hoe dat ging en hoe het ophield.",
    waarom: "Een plek in plaats van een periode, en je kunt er binnen een dag heen.",
    kernwoorden: ["el río", "la puerta", "la espada", "el puente", "la sinagoga", "la cuesta"],
    letOp: "Die drie gemeenschappen leefden niet altijd vreedzaam samen. Niet romantiseren."
  },
  {
    id: "mancha", reeks: "Lugares", titel: "La Mancha", deel: "Llano y molinos",
    hoofdstukken: 6,
    pitch: "Het vlakste en leegste stuk Spanje, en waarom precies daar iemand reuzen kon zien.",
    waarom: "De directe buurman van de Quijote-reeks die hij leuk vond, maar dan over de echte " +
            "plek in plaats van het boek.",
    kernwoorden: ["el molino", "el llano", "el viento", "el queso", "el camino", "la tierra"]
  },

  /* ---------- Hoy ---------- */
  {
    id: "movida", reeks: "Hoy", titel: "La Movida", deel: "Madrid no duerme",
    hoofdstukken: 8,
    pitch: "Nog geen vijf jaar na de dood van een dictator danst Madrid de hele nacht en mag " +
           "ineens alles.",
    waarom: "Het is de opluchting na de Franco-reeks, en de muziek is nog te vinden, dus het kan " +
            "aan Música gekoppeld worden.",
    kernwoorden: ["la noche", "la canción", "el barrio", "la libertad", "la ropa", "el grupo"]
  },
  {
    id: "bcn92", reeks: "Hoy", titel: "Barcelona noventa y dos", deel: "Una ciudad se da la vuelta",
    hoofdstukken: 8,
    pitch: "Een stad die met haar rug naar zee stond, brak zichzelf open voor twee weken sport en " +
           "is daarna nooit meer dezelfde geweest.",
    waarom: "Recent genoeg om foto's bij te hebben, en het gaat over iets wat hij in het echt kan " +
            "zien als hij er loopt.",
    kernwoorden: ["la playa", "el estadio", "la obra", "el puerto", "la antorcha", "el barrio"]
  },
  {
    id: "fuego", reeks: "Hoy", titel: "Pueblos que queman cosas", deel: "Fallas, Tomatina y más",
    hoofdstukken: 6,
    pitch: "Valencia bouwt een jaar lang reusachtige poppen om ze in één nacht te verbranden, en " +
           "Buñol gooit honderd ton tomaten door de straten.",
    waarom: "Licht, grappig en volstrekt onbegrijpelijk van buitenaf. Goede afwisseling tussen de " +
            "zware reeksen door.",
    kernwoorden: ["la fiesta", "el fuego", "la falla", "el tomate", "la calle", "la pólvora"]
  }
];
