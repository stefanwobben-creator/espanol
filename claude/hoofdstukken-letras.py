# -*- coding: utf-8 -*-
# De tien hoofdstukken van "El hilo de las palabras". Los bestand, want een patchscript met
# tienduizend tekens verhaal erin is niet meer na te lezen.

H = []

def hs(num, titel, tekst, vragen, reflectie):
    H.append({"num": num, "titel": titel, "tekst": tekst, "vragen": vragen, "reflectie": reflectie})

hs(1, "Los gigantes que eran molinos",
"Hay un hombre que lee demasiado.\n\n"
"Vive en un pueblo de La Mancha, en el centro de España. Es viejo, es pobre y está solo. Por las "
"noches no duerme: lee libros de caballeros, de castillos y de batallas. Lee tanto que un día ya no "
"sabe qué es verdad y qué es historia.\n\n"
"Entonces toma una decisión extraña. Coge una armadura vieja, un caballo flaco y sale de casa. «A "
"partir de hoy me llamo don Quijote de la Mancha», dice.\n\n"
"En el camino ve unos molinos de viento. Para él no son molinos: son gigantes con brazos largos. Su "
"amigo Sancho le dice que no, que son molinos, que todo el mundo lo ve. Don Quijote no escucha. "
"Ataca, y cae.\n\n"
"¿Quién tiene razón? Sancho ve lo que hay. Don Quijote ve lo que quiere que haya. El libro no dice "
"cuál de los dos vive mejor.\n\n"
"Cuatrocientos años después seguimos leyéndolo.",
[{"q": "¿Por qué don Quijote ya no sabe qué es verdad?", "opts": ["Porque está enfermo", "Porque lee demasiados libros de caballeros", "Porque nadie le habla"], "c": 1},
 {"q": "¿Qué ve don Quijote en el campo?", "opts": ["Gigantes con brazos largos", "Un castillo", "Un ejército"], "c": 0},
 {"q": "¿Qué hace Sancho?", "opts": ["Ataca con él", "Le dice que son molinos", "Se va a casa"], "c": 1},
 {"q": "¿Qué dice el libro sobre quién vive mejor?", "opts": ["Que Sancho vive mejor", "Que don Quijote vive mejor", "No lo dice"], "c": 2}],
"¿Conoces a alguien que ve el mundo como quiere que sea? ¿Vive peor por eso?")

hs(2, "El niño que tenía hambre",
"Lázaro es un niño pobre. Su madre no puede darle de comer, así que lo entrega a un hombre ciego. "
"«Él te enseñará la vida», dice.\n\n"
"El ciego le enseña, pero no con palabras. El primer día le pide a Lázaro que ponga la oreja en una "
"piedra con forma de toro. Cuando el niño obedece, el ciego le golpea la cabeza contra la piedra. "
"«Aprende: el criado del ciego tiene que saber más que el ciego.»\n\n"
"Lázaro aprende. Tiene hambre siempre, así que se vuelve listo. Hace un agujero pequeño en el jarro "
"de vino y bebe por debajo. Roba pan. Miente. No lo hace porque sea malo: lo hace porque come una "
"vez al día.\n\n"
"Este libro es de 1554 y nadie sabe quién lo escribió. Antes, en los libros, los héroes eran "
"caballeros y santos. Aquí el héroe es un niño con hambre que engaña a todo el mundo, y el lector "
"está de su parte.\n\n"
"España se ve distinta desde abajo.",
[{"q": "¿Por qué la madre entrega a Lázaro al ciego?", "opts": ["Porque no puede darle de comer", "Porque el niño se porta mal", "Porque el ciego es rico"], "c": 0},
 {"q": "¿Qué le hace el ciego el primer día?", "opts": ["Le da pan", "Le golpea la cabeza contra una piedra", "Le enseña a leer"], "c": 1},
 {"q": "¿Por qué Lázaro roba y miente?", "opts": ["Porque es malo", "Porque tiene hambre", "Porque quiere ser rico"], "c": 1},
 {"q": "¿Qué tiene de nuevo este libro?", "opts": ["El héroe es un niño pobre y no un caballero", "Está escrito en verso", "Sabemos quién lo escribió"], "c": 0}],
"¿Es Lázaro un ladrón o una víctima? ¿Se puede ser las dos cosas?")

hs(3, "Y si todo fuera un sueño",
"Un rey encierra a su hijo en una torre.\n\n"
"Antes de nacer el niño, los astrólogos dicen que será un hombre violento y que destruirá el reino. "
"El rey tiene miedo y decide que su hijo crecerá solo, en una torre, sin ver a nadie. El niño se "
"llama Segismundo y no sabe que es príncipe.\n\n"
"Muchos años después el rey duda. ¿Y si los astrólogos se equivocaron? Duerme a su hijo con una "
"bebida, lo lleva al palacio y espera.\n\n"
"Segismundo despierta en una cama de oro. Le dicen que es príncipe. Y se comporta fatal: grita, "
"amenaza, tira a un hombre por la ventana. El rey lo devuelve a la torre y le dice que todo fue un "
"sueño.\n\n"
"Entonces Segismundo piensa algo que cambia la obra. Si la vida puede ser un sueño, dice, hay que "
"hacer el bien igual, porque el bien no se pierde ni en los sueños.\n\n"
"Calderón escribió esto en 1635. La pregunta sigue abierta.",
[{"q": "¿Por qué el rey encierra a su hijo?", "opts": ["Porque los astrólogos dicen que será violento", "Porque el niño está enfermo", "Porque no es su hijo"], "c": 0},
 {"q": "¿Cómo se comporta Segismundo en el palacio?", "opts": ["Muy bien", "Fatal: grita y amenaza", "No dice nada"], "c": 1},
 {"q": "¿Qué le dicen cuando vuelve a la torre?", "opts": ["Que ahora es rey", "Que todo fue un sueño", "Que su padre ha muerto"], "c": 1},
 {"q": "¿A qué conclusión llega Segismundo?", "opts": ["Que hay que hacer el bien igual", "Que nada importa", "Que hay que volver al palacio"], "c": 0}],
"Si supieras que hoy es un sueño, ¿harías algo distinto?")

hs(4, "¿Quién mira a quién?",
"Entra en una sala del Museo del Prado, en Madrid. En la pared hay un cuadro grande de 1656. Se "
"llama Las Meninas.\n\n"
"En el centro hay una niña rubia: la infanta Margarita, hija del rey. A su lado, dos chicas jóvenes "
"le ofrecen agua. Hay un perro, una mujer pequeña y un hombre en una puerta al fondo.\n\n"
"Y a la izquierda hay un pintor con un pincel en la mano. Es Velázquez, el que pintó el cuadro. "
"Está dentro de su propio cuadro, mirándote.\n\n"
"¿Y qué está pintando? No lo vemos. El lienzo está de espaldas. Pero al fondo hay un espejo, y en "
"el espejo están el rey y la reina.\n\n"
"Entonces, ¿dónde están los reyes? Están donde estás tú, delante del cuadro. Sin saberlo, ocupas su "
"lugar.\n\n"
"Trescientos setenta años después la gente sigue discutiendo qué pasa exactamente en esa sala. Un "
"cuadro que hace una pregunta dura más que uno que da una respuesta.",
[{"q": "¿Quién está en el centro del cuadro?", "opts": ["La reina", "La infanta Margarita", "Velázquez"], "c": 1},
 {"q": "¿Qué hace Velázquez en el cuadro?", "opts": ["Está pintando y te mira", "Duerme", "No aparece"], "c": 0},
 {"q": "¿Quiénes aparecen en el espejo del fondo?", "opts": ["Los reyes", "Dos perros", "Nadie"], "c": 0},
 {"q": "¿Dónde estás tú cuando miras el cuadro?", "opts": ["Detrás del pintor", "En el lugar de los reyes", "Fuera de la sala"], "c": 1}],
"¿Qué cambia en un cuadro cuando el pintor se pinta a sí mismo dentro?")

hs(5, "Las golondrinas que no volverán",
"Gustavo Adolfo Bécquer vivió poco y mal.\n\n"
"Nació en Sevilla en 1836. Sus padres murieron pronto. Fue a Madrid a escribir y pasó frío y "
"hambre. Publicó poco. Murió a los treinta y cuatro años, casi desconocido. Sus amigos reunieron "
"sus poemas después de su muerte.\n\n"
"Hoy casi todos los españoles conocen sus primeras líneas: «Volverán las oscuras golondrinas en tu "
"balcón sus nidos a colgar...»\n\n"
"Las golondrinas volverán, dice. Volverán a tu balcón y otra vez habrá primavera. Pero aquellas, "
"las que aprendieron nuestros nombres, ésas no volverán.\n\n"
"Es una idea sencilla y todo el mundo la entiende: la vida sigue, pero no la misma vida.\n\n"
"Lo interesante es cómo lo dice. En prosa serían dos frases y las olvidarías. En verso lo lees una "
"vez y se queda. Un poema no informa: hace que algo te pase.",
[{"q": "¿Cómo vivió Bécquer?", "opts": ["Rico y famoso", "Pobre y casi desconocido", "Fuera de España"], "c": 1},
 {"q": "¿Cuándo se publicaron sus poemas?", "opts": ["De niño", "Después de su muerte", "Nunca"], "c": 1},
 {"q": "¿Qué dice el poema sobre las golondrinas?", "opts": ["Que volverán otras, pero no aquellas", "Que no volverá ninguna", "Que se quedan siempre"], "c": 0},
 {"q": "Según el capítulo, ¿qué hace un poema?", "opts": ["Explica algo nuevo", "Hace que algo te pase", "Cuenta una historia larga"], "c": 1}],
"¿Hay alguna frase, de una canción o de un libro, que se te quedó y no sabes por qué?")

hs(6, "Mirar despacio algo pequeño",
"«Platero es pequeño, peludo, suave; tan blando por fuera, que se diría todo de algodón.»\n\n"
"Así empieza uno de los libros más leídos de España. Platero es un burro. El que habla es un hombre "
"que pasea con él por Moguer, un pueblo blanco de Andalucía, hace más de cien años.\n\n"
"No pasa casi nada. Van al río. Ven una flor. Encuentran a unos niños. Llega la primavera, llega el "
"verano. El hombre le habla al burro y el burro no contesta.\n\n"
"Juan Ramón Jiménez escribió esto en 1914 y ganó el Premio Nobel muchos años después. Mucha gente "
"cree que es un libro para niños. No lo es del todo: hay muerte, hay pobreza y hay crueldad, "
"contadas en voz baja.\n\n"
"Lo que enseña es una manera de mirar. Casi todo lo que ves cada día te parece pequeño porque lo "
"miras deprisa. Este libro va despacio a propósito.\n\n"
"Un burro puede ser un tema si lo miras el tiempo suficiente.",
[{"q": "¿Quién es Platero?", "opts": ["Un niño", "Un burro", "Un pueblo"], "c": 1},
 {"q": "¿Dónde pasean?", "opts": ["Por Madrid", "Por Moguer, en Andalucía", "Por la costa de Galicia"], "c": 1},
 {"q": "¿Qué pasa en el libro?", "opts": ["Casi nada: cosas pequeñas de cada día", "Una guerra", "Un viaje a América"], "c": 0},
 {"q": "¿Es un libro sólo para niños?", "opts": ["Sí", "No: también hay muerte y pobreza", "Es un libro de historia"], "c": 1}],
"¿Qué cosa pequeña ves cada día sin mirarla nunca de verdad?")

hs(7, "Caminante, no hay camino",
"Antonio Machado fue profesor de francés en pueblos pequeños. Escribía poemas sobre campos, caminos "
"y álamos.\n\n"
"Sus versos más conocidos dicen así: «Caminante, no hay camino, se hace camino al andar.»\n\n"
"Es decir: el camino no existe antes de que alguien lo recorra. Lo haces tú, andando. Si miras "
"atrás ves una senda, pero delante no hay nada todavía.\n\n"
"En 1939 terminó la guerra civil. Machado salió de España a pie, con su madre anciana, por la "
"frontera de Francia. Llovía. Tenía sesenta y cuatro años y estaba enfermo. Murió tres semanas "
"después en un pueblo pequeño junto al mar.\n\n"
"En el bolsillo de su abrigo encontraron un papel con un solo verso escrito a mano: «Estos días "
"azules y este sol de la infancia.»\n\n"
"Fue lo último que escribió. Su tumba sigue en Francia y todavía recibe flores.",
[{"q": "¿De qué trabajaba Machado?", "opts": ["De profesor de francés", "De médico", "De periodista"], "c": 0},
 {"q": "¿Qué significa «se hace camino al andar»?", "opts": ["Que el camino ya existe", "Que el camino lo haces tú andando", "Que hay que volver atrás"], "c": 1},
 {"q": "¿Por qué salió de España en 1939?", "opts": ["Por trabajo", "Por el final de la guerra civil", "Para estudiar"], "c": 1},
 {"q": "¿Qué encontraron en su bolsillo?", "opts": ["Una carta a su madre", "Un verso escrito a mano", "Una foto"], "c": 1}],
"¿Hay un camino en tu vida que sólo existió después de que empezaste a andar?")

hs(8, "El duende",
"Federico García Lorca sabía cantar, tocar el piano y dibujar. Escribía teatro y poesía, y en sus "
"poemas hay gitanos, guardias civiles, luna, cuchillos y caballos.\n\n"
"Él hablaba de una cosa que llamaba el duende. No es un fantasma. Es lo que ocurre cuando alguien "
"canta o baila y de repente te toca por dentro, sin que sepas por qué. «El duende no llega si no ve "
"posibilidad de muerte», decía.\n\n"
"En 1929 fue a Nueva York y escribió un libro muy distinto, lleno de máquinas, de ciudad y de gente "
"sola.\n\n"
"En agosto de 1936, al principio de la guerra civil, unos hombres se lo llevaron de una casa en "
"Granada. Lo mataron esa misma noche, cerca de un olivo. Tenía treinta y ocho años. Nunca se "
"encontró su cuerpo.\n\n"
"Sus obras se siguen representando en todo el mundo. La gente todavía busca en aquel campo.",
[{"q": "¿Qué es el duende, según Lorca?", "opts": ["Un fantasma", "Lo que te toca por dentro cuando alguien canta o baila", "Un instrumento"], "c": 1},
 {"q": "¿Adónde fue Lorca en 1929?", "opts": ["A Nueva York", "A París", "A México"], "c": 0},
 {"q": "¿Qué le pasó en agosto de 1936?", "opts": ["Se fue de España", "Lo mataron cerca de Granada", "Dejó de escribir"], "c": 1},
 {"q": "¿Qué pasó con su cuerpo?", "opts": ["Está en Madrid", "Nunca se encontró", "Está en Nueva York"], "c": 1}],
"¿Has sentido alguna vez algo parecido al duende, escuchando música?")

hs(9, "El español del otro lado",
"«Muchos años después, frente al pelotón de fusilamiento, el coronel Aureliano Buendía había de "
"recordar aquella tarde remota en que su padre lo llevó a conocer el hielo.»\n\n"
"Es la primera frase de Cien años de soledad, de 1967. En un pueblo caliente llamado Macondo, el "
"hielo es una cosa mágica que llega con un circo.\n\n"
"En ese libro pasan cosas imposibles y nadie se sorprende. Una mujer sube al cielo mientras tiende "
"la ropa. Llueve durante cuatro años. Un hombre vive tanto que pierde la cuenta. Los personajes lo "
"cuentan como quien habla del tiempo que hace.\n\n"
"Gabriel García Márquez era colombiano. Y aquí hay algo importante: el español no es sólo de "
"España. Lo hablan más de cuatrocientos millones de personas, y la mayoría vive al otro lado del "
"océano.\n\n"
"Cuando aprendes español no entras en un país. Entras en veinte.",
[{"q": "¿Qué es el hielo en Macondo?", "opts": ["Algo normal", "Una cosa mágica que llega con un circo", "Una comida"], "c": 1},
 {"q": "¿Cómo reaccionan los personajes ante lo imposible?", "opts": ["Con miedo", "Como si fuera normal", "Se van del pueblo"], "c": 1},
 {"q": "¿De dónde era García Márquez?", "opts": ["De España", "De Colombia", "De México"], "c": 1},
 {"q": "¿Cuánta gente habla español?", "opts": ["Más de cuatrocientos millones", "Unos cincuenta millones", "Sólo en España"], "c": 0}],
"¿Qué español quieres hablar tú: el de España, el de América, o te da igual?")

hs(10, "Por qué seguimos leyendo",
"Han pasado nueve capítulos. Un hombre que ve gigantes. Un niño con hambre. Un príncipe en una "
"torre. Un pintor dentro de su cuadro. Unas golondrinas. Un burro. Un camino que no existe. Un "
"poeta cerca de un olivo. Un pueblo donde llueve cuatro años.\n\n"
"¿Por qué seguimos leyendo estos libros?\n\n"
"No es porque sean antiguos. Hay miles de libros antiguos que nadie abre. Éstos siguen aquí porque "
"hacen preguntas que todavía no tienen respuesta, y porque las hacen con una imagen que no se "
"olvida: los molinos, el espejo, el papel en el bolsillo.\n\n"
"Y hay otra razón, más práctica para ti. Ahora puedes leerlos. No traducidos: en español. Puede que "
"no entiendas todas las palabras todavía, pero entiendes de qué van.\n\n"
"Don Quijote salió de casa porque había leído demasiado. Tú acabas de leer diez capítulos. Ten "
"cuidado.",
[{"q": "Según el capítulo, ¿por qué seguimos leyendo estos libros?", "opts": ["Porque son antiguos", "Porque hacen preguntas sin respuesta", "Porque son cortos"], "c": 1},
 {"q": "¿Qué tienen en común los libros de esta serie?", "opts": ["Una imagen que no se olvida", "El mismo autor", "La misma época"], "c": 0},
 {"q": "¿Qué puedes hacer ahora, según el texto?", "opts": ["Leerlos traducidos", "Leerlos en español", "Escribir uno"], "c": 1},
 {"q": "¿Con qué broma termina el capítulo?", "opts": ["Que leer demasiado es peligroso", "Que hay que dejar de leer", "Que Don Quijote existió"], "c": 0}],
"De los nueve, ¿cuál quieres leer entero algún día?")
