# -*- coding: utf-8 -*-
# "Don Quijote", tien hoofdstukken. Het tweede boek van de literatuurlijn.
#
# Maat: die van Franco (tien hoofdstukken, gemiddeld 794 tekens). Stefan, 23 aug: "lengte zoals boek
# van chispa of franco is eigenlijk perfect."
#
# Tweede vak: literatuur, en binnen dit boek één doorlopende vraag. Is het beter de wereld te zien
# zoals hij is, of zoals je wilt dat hij is? Het boek kiest niet, en dit navertelsel ook niet. In
# hoofdstuk 10 keert de vraag zich om: als hij eindelijk gelijk krijgt van iedereen, wil niemand het.

H = []

def hs(num, titel, tekst, vragen, reflectie):
    H.append({"num": num, "titel": titel, "tekst": tekst, "vragen": vragen, "reflectie": reflectie})

hs(1, "El hombre que leía demasiado",
"En un pueblo de La Mancha vive un hombre de unos cincuenta años. Se llama Alonso Quijano. No está "
"casado, no tiene hijos y no es rico. Vive con su sobrina y un ama que cocina para él.\n\n"
"Tiene una casa normal y una sola pasión: los libros de caballeros. Son historias de hombres con "
"armadura que salvan a mujeres, matan gigantes y ganan batallas imposibles.\n\n"
"Los lee de día y de noche. Vende tierras para comprar más. Duerme cada vez menos. Y un día pasa "
"algo que nadie esperaba: deja de ver la diferencia entre esos libros y la calle donde vive.\n\n"
"Piensa que el mundo necesita caballeros y que ya no quedan. Piensa que él puede ser uno.\n\n"
"Busca en el desván una armadura vieja de su bisabuelo. Le falta media pieza; la arregla con "
"cartón. Elige un nombre nuevo para su caballo flaco: Rocinante. Y otro para sí mismo: don Quijote "
"de la Mancha.\n\n"
"Una mañana de julio, muy temprano, sale de casa sin decir nada a nadie.",
[{"q": "¿Cómo se llama el hombre al principio?", "opts": ["Don Quijote", "Alonso Quijano", "Rocinante"], "c": 1},
 {"q": "¿Qué lee todo el día?", "opts": ["Libros de caballeros", "Periódicos", "Cartas"], "c": 0},
 {"q": "¿Qué hace para comprar más libros?", "opts": ["Trabaja más", "Vende tierras", "Pide dinero al rey"], "c": 1},
 {"q": "¿Con qué arregla la armadura?", "opts": ["Con hierro nuevo", "Con cartón", "No la arregla"], "c": 1}],
"¿Hay algo que lees o miras tanto que empieza a cambiar cómo ves el día?")

hs(2, "El castillo que era una venta",
"Don Quijote lleva todo el día en el campo. Tiene calor, tiene sed y no ha encontrado ni una "
"aventura.\n\n"
"Al final de la tarde ve un edificio grande al lado del camino. Es una venta: una casa donde "
"comen y duermen los viajeros. Pero él ve otra cosa. Ve un castillo con cuatro torres y un puente.\n\n"
"En la puerta hay dos mujeres. Él las saluda como si fueran señoras nobles y les habla en un "
"español antiguo que ellas no entienden. Las mujeres se ríen. Él cree que se ríen de alegría.\n\n"
"El ventero es un hombre práctico. Ve enseguida que este cliente está loco, pero también ve que no "
"es peligroso y que da risa. Así que le sigue el juego.\n\n"
"Don Quijote le pide algo muy serio: quiere ser armado caballero. Sin eso, dice, no puede empezar. "
"El ventero acepta. Le da unos golpes con una espada, dice unas palabras que se inventa, y todos "
"aguantan la risa.\n\n"
"Don Quijote se va feliz. Ya es caballero. Se lo ha dicho un rey.",
[{"q": "¿Qué es en realidad el edificio?", "opts": ["Un castillo", "Una venta para viajeros", "Una iglesia"], "c": 1},
 {"q": "¿Por qué se ríen las mujeres?", "opts": ["Porque están contentas", "Porque no entienden cómo habla", "Porque tienen miedo"], "c": 1},
 {"q": "¿Qué hace el ventero?", "opts": ["Le sigue el juego", "Llama a la policía", "Lo echa fuera"], "c": 0},
 {"q": "¿Qué le pide don Quijote?", "opts": ["Comida", "Ser armado caballero", "Un caballo nuevo"], "c": 1}],
"El ventero le sigue el juego. ¿Es amable o cruel? ¿Depende de algo?")

hs(3, "Sancho Panza",
"Después de una primera salida corta, don Quijote vuelve a casa herido. Su sobrina y el cura queman "
"casi todos sus libros mientras él duerme. Cuando despierta le dicen que un mago se los llevó. Él "
"lo cree sin problema: los magos salen en todos sus libros.\n\n"
"Pero esta vez no quiere salir solo. Todo caballero tiene un escudero, y él busca el suyo.\n\n"
"Encuentra a un vecino: Sancho Panza, un labrador pobre, bajo y gordo, con mujer e hijos. Sancho no "
"ha leído un libro en su vida. Habla con refranes y piensa en la comida.\n\n"
"Don Quijote le hace una promesa enorme. Ven conmigo, dice, y cuando gane una isla te haré "
"gobernador. Sancho no sabe muy bien qué es una isla, pero le gusta la palabra gobernador. Va.\n\n"
"Y así empieza lo mejor del libro: dos hombres que no ven el mismo mundo, andando juntos durante "
"años. Uno mira arriba, el otro mira el suelo. Ninguno de los dos convence al otro, y ninguno de "
"los dos se va.",
[{"q": "¿Qué pasa con los libros de don Quijote?", "opts": ["Los venden", "Los queman su sobrina y el cura", "Los regala"], "c": 1},
 {"q": "¿Qué le dicen cuando despierta?", "opts": ["Que un mago se los llevó", "Que se perdieron", "La verdad"], "c": 0},
 {"q": "¿Quién es Sancho Panza?", "opts": ["Un caballero", "Un labrador vecino, pobre y práctico", "El cura del pueblo"], "c": 1},
 {"q": "¿Qué le promete don Quijote?", "opts": ["Una isla para gobernar", "Un caballo", "Dinero cada mes"], "c": 0}],
"¿Conoces a dos personas muy distintas que se aguantan bien? ¿Qué las une?")

hs(4, "Los molinos de viento",
"Van por un campo abierto de La Mancha. A lo lejos aparecen treinta o cuarenta molinos de viento, "
"grandes, blancos, con aspas que se mueven despacio.\n\n"
"Don Quijote se para. Mira. Y dice a Sancho que la suerte les ayuda: allí hay gigantes, y va a "
"luchar contra ellos.\n\n"
"Sancho contesta lo que contestaría cualquiera. Que no son gigantes, que son molinos, que esas "
"cosas largas son aspas y las mueve el viento.\n\n"
"Don Quijote no cambia de opinión. Le dice que se nota que Sancho no sabe nada de aventuras. Baja "
"la lanza, corre con Rocinante y ataca el primer molino.\n\n"
"El viento mueve el aspa. La lanza se rompe. El caballo y el hombre vuelan por el aire y caen al "
"suelo.\n\n"
"Sancho llega corriendo. Don Quijote no puede levantarse. Y entonces, en el suelo, explica lo que "
"ha pasado: eran gigantes, dice, pero un mago enemigo los ha convertido en molinos para quitarle la "
"victoria.\n\n"
"Es la escena más famosa del libro. Y fíjate: don Quijote no admite el error, pero tampoco miente. "
"Se inventa una explicación que salva lo que ve.",
[{"q": "¿Cuántos molinos hay más o menos?", "opts": ["Tres o cuatro", "Treinta o cuarenta", "Cien"], "c": 1},
 {"q": "¿Qué le dice Sancho?", "opts": ["Que son gigantes", "Que son molinos y los mueve el viento", "Que hay que volver"], "c": 1},
 {"q": "¿Qué pasa cuando ataca?", "opts": ["Gana", "El aspa lo tira al suelo", "El molino se para"], "c": 1},
 {"q": "¿Cómo explica don Quijote su derrota?", "opts": ["Dice que se equivocó", "Dice que un mago cambió los gigantes por molinos", "No dice nada"], "c": 1}],
"Cuando algo te sale mal, ¿buscas una explicación que salve lo que creías?")

hs(5, "El yelmo de Mambrino",
"Llueve. Por el camino viene un hombre a caballo con algo brillante en la cabeza.\n\n"
"Es un barbero. Va a trabajar a otro pueblo y, para no mojarse, se ha puesto encima la bacía: el "
"plato de metal que se usa para afeitar. Es redondo, tiene un hueco para el cuello y brilla mucho.\n\n"
"Don Quijote lo ve y se emociona. Eso, dice, es el yelmo de Mambrino, un casco de oro famoso en sus "
"libros. Ataca. El barbero, que no entiende nada, se baja del caballo y sale corriendo. La bacía "
"queda en el barro.\n\n"
"Don Quijote la recoge y se la pone en la cabeza. Le queda rara, porque es un plato.\n\n"
"Sancho le dice que parece una bacía de barbero. Don Quijote responde con calma que a los ojos de "
"la gente común parece una bacía, pero que él ve lo que es.\n\n"
"Más adelante, en una venta, discuten todos sobre el objeto. Unos dicen bacía, otros dicen yelmo, y "
"al final alguien propone una palabra nueva para no pelear: baciyelmo.\n\n"
"El libro se ríe, y a la vez pregunta en serio: ¿cuántas cosas llamamos por su nombre sólo porque "
"todos estamos de acuerdo?",
[{"q": "¿Qué lleva el barbero en la cabeza?", "opts": ["Un casco de oro", "Una bacía, para no mojarse", "Un sombrero"], "c": 1},
 {"q": "¿Qué cree don Quijote que es?", "opts": ["El yelmo de Mambrino", "Un plato", "Un regalo"], "c": 0},
 {"q": "¿Qué hace el barbero?", "opts": ["Pelea", "Sale corriendo", "Se lo vende"], "c": 1},
 {"q": "¿Qué palabra nueva se inventan?", "opts": ["Baciyelmo", "Molinete", "Quijotada"], "c": 0}],
"¿Hay palabras que usamos sólo porque todos estamos de acuerdo? ¿Cuáles?")

hs(6, "Los presos que quedaron libres",
"Por el camino real viene un grupo de hombres atados con una cadena larga. Van a galeras: a remar "
"en los barcos del rey durante años. Los llevan unos guardias.\n\n"
"Don Quijote pregunta a cada uno por qué va preso. Uno robó, otro engañó, otro hizo cosas peores. "
"Los escucha a todos con atención.\n\n"
"Y decide que van forzados, contra su voluntad, y que un caballero debe ayudar a quien va forzado. "
"Los guardias se ríen. Él ataca. Hay golpes, los guardias huyen y los presos quedan libres.\n\n"
"Entonces don Quijote les pide una sola cosa: que vayan a El Toboso a contarle esta aventura a "
"Dulcinea, su señora.\n\n"
"Los presos se miran. Uno de ellos, Ginés, le dice que eso es imposible y que deje de decir "
"tonterías. Don Quijote se enfada. Y los hombres a los que acaba de liberar le tiran piedras, le "
"quitan cosas y se van corriendo por el monte.\n\n"
"Se queda solo, en el suelo, otra vez.\n\n"
"Ha hecho algo generoso y ha salido mal. El libro no dice que estuviera equivocado. Sólo enseña "
"cómo acabó.",
[{"q": "¿Adónde llevan a los hombres de la cadena?", "opts": ["A casa", "A galeras, a remar", "A juicio"], "c": 1},
 {"q": "¿Por qué los libera don Quijote?", "opts": ["Porque son inocentes", "Porque van forzados", "Porque le pagan"], "c": 1},
 {"q": "¿Qué les pide a cambio?", "opts": ["Dinero", "Que vayan a contárselo a Dulcinea", "Que le sigan"], "c": 1},
 {"q": "¿Qué hacen los presos al final?", "opts": ["Le dan las gracias", "Le tiran piedras y se van", "Van a El Toboso"], "c": 1}],
"¿Es buena una acción generosa que acaba mal? ¿Cambia algo si sabías que podía pasar?")

hs(7, "Dulcinea del Toboso",
"Todo caballero de los libros tiene una señora. Don Quijote también necesita una, así que la elige.\n\n"
"En un pueblo cerca, El Toboso, vive una chica llamada Aldonza Lorenzo. Es fuerte, trabaja en el "
"campo y tiene buena voz. Él la vio alguna vez, hace años. Nunca han hablado.\n\n"
"Le pone un nombre nuevo, más bonito: Dulcinea del Toboso. Y a partir de ahí, cada golpe que da y "
"cada camino que anda es por ella.\n\n"
"Le manda mensajes que nunca llegan. Habla de su belleza a todo el que encuentra. Cuando alguien "
"duda, se enfada de verdad.\n\n"
"Aldonza no sabe nada de esto. No sabe que existe Dulcinea. Sigue trabajando en su pueblo.\n\n"
"Sancho, que es práctico, se lo dice una vez con cuidado: que él la conoce, que es una chica normal "
"y bastante ruidosa. Don Quijote contesta que eso no importa, porque él la imagina como quiere "
"imaginarla, y con eso basta.\n\n"
"Es una idea incómoda y muy moderna. ¿Amas a la persona, o a la persona que has construido en tu "
"cabeza?",
[{"q": "¿Quién es Dulcinea en realidad?", "opts": ["Una princesa", "Aldonza Lorenzo, una chica del campo", "Un personaje inventado del todo"], "c": 1},
 {"q": "¿Han hablado alguna vez?", "opts": ["Sí, mucho", "Nunca", "Sólo por carta"], "c": 1},
 {"q": "¿Qué sabe ella de todo esto?", "opts": ["Nada", "Todo", "Sólo lo que le cuenta Sancho"], "c": 0},
 {"q": "¿Qué contesta don Quijote cuando Sancho le dice la verdad?", "opts": ["Que la imagina como quiere y con eso basta", "Que se ha equivocado", "Que buscará a otra"], "c": 0}],
"¿Amamos a la persona o a la idea que nos hacemos de ella? ¿Se puede separar?")

hs(8, "El caballero de los espejos",
"En el pueblo hay gente preocupada. El cura, el barbero y un estudiante joven llamado Sansón "
"Carrasco quieren que don Quijote vuelva a casa y se cure.\n\n"
"Sansón tiene una idea. Si la locura viene de los libros de caballeros, hay que usar sus propias "
"reglas. En esos libros, el caballero que pierde un combate tiene que obedecer al vencedor.\n\n"
"Así que Sansón se pone una armadura, se hace llamar el Caballero de los Espejos y sale a buscarlo. "
"El plan es sencillo: ganarle y mandarlo a casa un año.\n\n"
"Se encuentran en el campo. Hablan como caballeros. Se preparan. Corren el uno contra el otro.\n\n"
"Y pasa lo que nadie había calculado: gana don Quijote. Sansón cae del caballo y se queda en el "
"suelo sin moverse. Cuando le quitan el casco, Sancho ve la cara de su vecino y no entiende nada.\n\n"
"Don Quijote tampoco. Dice que un mago ha puesto la cara de Sansón en la cabeza de su enemigo, para "
"confundirlo.\n\n"
"Sansón vuelve al pueblo dolorido y humillado. Y ya no lo hace sólo para curarlo.",
[{"q": "¿Qué quieren el cura y Sansón?", "opts": ["Que don Quijote vuelva a casa", "Que siga viajando", "Que escriba un libro"], "c": 0},
 {"q": "¿Por qué se disfraza Sansón de caballero?", "opts": ["Para divertirse", "Para ganarle y poder mandarlo a casa", "Para acompañarlo"], "c": 1},
 {"q": "¿Quién gana el combate?", "opts": ["Sansón", "Don Quijote", "Nadie"], "c": 1},
 {"q": "¿Cómo explica don Quijote la cara de Sansón?", "opts": ["Dice que es un mago", "Lo reconoce", "Se va corriendo"], "c": 0}],
"Sansón quería curarlo y acaba queriendo ganarle. ¿Por qué crees que cambia?")

hs(9, "La playa de Barcelona",
"Don Quijote y Sancho llegan a Barcelona. Es la primera vez que ven el mar. Se quedan mirando los "
"barcos, la gente, el ruido del puerto.\n\n"
"Un día, en la playa, aparece otro caballero con armadura blanca y brillante. Se hace llamar el "
"Caballero de la Blanca Luna. Es Sansón otra vez, mejor preparado.\n\n"
"El reto es duro y claro: si pierde don Quijote, tendrá que volver a su pueblo y dejar las armas "
"durante un año.\n\n"
"Corren. Esta vez el otro va más rápido y golpea mejor. Don Quijote cae en la arena y no puede "
"levantarse.\n\n"
"Con el hombre encima y la espada cerca, tiene una salida fácil: sólo tiene que negar a Dulcinea. "
"No lo hace. Dice, casi sin voz, que Dulcinea es la mujer más hermosa del mundo y que él es el "
"caballero más desgraciado de la tierra.\n\n"
"El vencedor lo deja marchar.\n\n"
"Vuelve a casa a pie, despacio, con Sancho al lado. Ha perdido, ha cumplido su palabra, y no ha "
"cambiado de opinión ni tumbado en la arena.",
[{"q": "¿Qué ven por primera vez en Barcelona?", "opts": ["El mar", "La nieve", "Un tren"], "c": 0},
 {"q": "¿Quién es el Caballero de la Blanca Luna?", "opts": ["Un desconocido", "Sansón Carrasco otra vez", "El barbero"], "c": 1},
 {"q": "¿Qué pasa si pierde don Quijote?", "opts": ["Debe volver a casa un año", "Pierde a Rocinante", "Debe pagar"], "c": 0},
 {"q": "¿Qué hace cuando está en el suelo?", "opts": ["Niega a Dulcinea", "Dice que Dulcinea es la más hermosa", "Pide perdón"], "c": 1}],
"Pierde y no cede en lo único que le piden. ¿Es valentía o cabezonería?")

hs(10, "Alonso Quijano, otra vez",
"Vuelve al pueblo cansado. Se acuesta y tiene fiebre unos días. Duerme mucho.\n\n"
"Y una mañana despierta tranquilo, mira a su sobrina y dice una frase que nadie esperaba: que ya "
"tiene la cabeza clara, que los libros de caballeros son mentiras, y que él no es don Quijote sino "
"Alonso Quijano, un hombre normal de un pueblo de La Mancha.\n\n"
"Pide un notario para hacer testamento y un cura para confesarse.\n\n"
"Entonces ocurre lo más raro del libro. Sancho, el hombre práctico, el que durante mil páginas dijo "
"que eran molinos, se pone a llorar y le pide que no se cure. Levántese, dice, vámonos al campo, "
"quizá encontramos a Dulcinea detrás de algún árbol.\n\n"
"Don Quijote le contesta con cariño que se acabó, que en los nidos de antaño no hay pájaros "
"hoy.\n\n"
"Muere unos días después, en su cama, cuerdo.\n\n"
"Todos tenían razón desde el principio: eran molinos. Y cuando por fin él lo admite, nadie se "
"alegra. Ni siquiera nosotros.",
[{"q": "¿Cómo despierta después de la fiebre?", "opts": ["Todavía loco", "Con la cabeza clara", "Sin memoria"], "c": 1},
 {"q": "¿Cómo se llama a sí mismo?", "opts": ["Don Quijote", "Alonso Quijano", "El Caballero de la Blanca Luna"], "c": 1},
 {"q": "¿Qué hace Sancho?", "opts": ["Se alegra", "Llora y le pide que no se cure", "Se va a casa"], "c": 1},
 {"q": "¿Cómo muere?", "opts": ["Luchando", "En su cama, cuerdo", "En Barcelona"], "c": 1}],
"Al final todos tenían razón y nadie se alegra. ¿Por qué crees que es así?")
