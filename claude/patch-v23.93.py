#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.93: Stefans viertalige verhaal, overgezet op de goede index.html.

Op 14 augustus om 11:10 landde commit 341d673 op main: "het verhaal achter Vamos geactualiseerd in
vier talen". Het werk klopte, de ondergrond niet. Die commit was geschreven op een index.html uit de
tijd van v23.14 (2,12 MB in plaats van 2,62 MB) en zette daarmee de hele app terug: geen plank, geen
Escuchar-scenes, geen recepten, geen grammatica-generatoren. versie.txt stond weer op v23.14 en
test/suites/pw-samen.js was meegedraaid. Live stond op dat moment nog op v23.88, dus de publicatie
was er nog net niet doorheen.

Die commit is teruggedraaid. Deze patch zet terug wat wél goed was: de Engelse, Franse en Duitse
tekst van het verhaal, letterlijk overgenomen uit 341d673.

Het Nederlands staat er al sinds v23.91 en is identiek; het enige verschil was `kán` tegenover
`k&aacute;n`, en dat rendert hetzelfde.

Frans en Duits gaan hierbij mee terwijl UI_LANGS alleen nl en en kent, dus niemand ziet ze. Dat is
een bewuste keuze: het werk verdwijnt niet in een revert, en punt 28 van de doorlichting (die twee
talen eruit) is een aparte beslissing die Stefan apart neemt.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.93"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.93" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


PAREN = [
  # ---- EN ----
  ('<div class="card">\n        <span class="kicker">The story behind ¡Vamos!</span>\n        <p style="margin-top:10px"><b>The Uber driver isn\'t going anywhere. So I practise my Spanish on him. At the barber: same story. At the market too.</b></p>\n        <p>Since moving from the Netherlands to Spain, I\'ve been trying to properly learn the language. I tested all the well-known apps, but they\'re built to make you come back every day, not to teach you anything. And most people don\'t quit because Spanish is too hard; they quit because it gets too boring. So I built my own.</p>\n        <p>¡Vamos! follows the books of my actual Spanish classes (twice a week at <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, highly recommended). You type your answers instead of tapping them, every word comes back exactly when you\'re about to forget it, and your mistakes are turned into new exercises overnight. Making mistakes doesn\'t cost points, it earns them. And missing a day? Totally fine. This app is a companion to spéaking, not a replacement. You learn a language in conversation; the app makes sure you have something to say.</p>\n        <p>Along the way, Chispa grows with you: an axolotl that lives off your effort. Think of it as a language tamagotchi, except this one teaches you Spanish.</p>\n        <p>I built this for myself, but by now my whole family is learning along, complete with a family leaderboard. Secretly that\'s my favourite part. Because a new language is the best workout you can give your brain.</p>\n      </div>\n      ',
   '<div class="card">\n        <span class="kicker">The story behind ¡Vamos!</span>\n        <p style="margin-top:10px"><b>The Uber driver isn\'t going anywhere. So I practise my Spanish on him. At the barber: same story. At the market too.</b></p>\n        <p>Since moving from the Netherlands to Spain, I\'ve been trying to properly learn the language. I tested all the well-known apps, and they\'re very good at what they\'re built for: getting you to come back tomorrow. It worked, too. I had a streak of months. I still couldn\'t put a sentence together at the market. Every app measures something, and what you measure is what you get. They measure whether you come back. I wanted something that measures whether I can actually do it.</p>\n        <p>And I never quit because Spanish was too hard. I quit because it got too boring. So I built my own.</p>\n        <p>¡Vamos! follows the books of my actual Spanish classes (twice a week at <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, highly recommended). You type your answers instead of tapping them, and every word comes back exactly when you\'re about to forget it.</p>\n        <p>The difference is in what "learned" means. In most apps you tap the right picture out of four, and it counts. Here a word only counts once you\'ve actually typed it correctly five times, spread across at least twenty-five days. That\'s slow. That\'s the point, because otherwise all you\'re measuring is how often you tapped.</p>\n        <p>And your mistakes are turned into new exercises overnight. Not on some random topic, but on exactly the thing you keep tripping over. Making mistakes doesn\'t cost points, it earns them. And missing a day? Totally fine. This app is a companion to spéaking, not a replacement. You learn a language in conversation; the app makes sure you have something to say.</p>\n        <p>Along the way, Chispa grows with you: an axolotl that lives off your effort. Think of it as a language tamagotchi, except this one teaches you Spanish.</p>\n        <p>I built this for myself, but by now my whole family is learning along. There was a family leaderboard, and I ripped it back out. You start playing to win instead of to learn. Now your home screen simply shows what the others learned that day, without points and without comparison, and you can shout something back. Secretly that\'s my favourite part. Because a new language is the best workout you can give your brain.</p>\n      </div>\n      '),
  # ---- FR ----
  ('<div class="card">\n        <span class="kicker">L\'histoire derrière ¡Vamos!</span>\n        <p style="margin-top:10px"><b>Le chauffeur Uber ne va nulle part de toute façon. Alors je pratique mon espagnol sur lui. Chez le coiffeur : même histoire. Au marché aussi.</b></p>\n        <p>Depuis que j\'ai quitté les Pays-Bas pour l\'Espagne, j\'essaie d\'apprendre la langue sérieusement. J\'ai testé toutes les applis connues, mais elles sont conçues pour vous faire revenir chaque jour, pas pour vous apprendre quelque chose. Et la plupart des gens n\'abandonnent pas parce que l\'espagnol est trop difficile, mais parce que ça devient trop ennuyeux. Alors j\'ai créé la mienne.</p>\n        <p>¡Vamos! suit les livres de mes vrais cours d\'espagnol (deux fois par semaine à l\'<a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, je recommande). Vous tapez vos réponses au lieu de les cliquer, chaque mot revient exactement au moment où vous alliez l\'oublier, et vos erreurs sont transformées en nouveaux exercices pendant la nuit. Se tromper ne coûte pas de points, ça en rapporte. Et manquer une journée ? Aucun problème. Cette appli est un complément à la parole, pas un remplacement. Une langue s\'apprend en conversation ; l\'appli fait en sorte que vous ayez quelque chose à dire.</p>\n        <p>En chemin, Chispa grandit avec vous : un axolotl qui vit de vos efforts. Un tamagotchi linguistique, sauf que celui-ci vous apprend l\'espagnol.</p>\n        <p>J\'ai créé ça pour moi, mais entre-temps toute ma famille apprend l\'espagnol, classement familial inclus. C\'est secrètement ma partie préférée. Parce qu\'une nouvelle langue est le meilleur entraînement que vous puissiez offrir à votre cerveau.</p>\n      </div>\n      ',
   '<div class="card">\n        <span class="kicker">L\'histoire derrière ¡Vamos!</span>\n        <p style="margin-top:10px"><b>Le chauffeur Uber ne va nulle part de toute façon. Alors je pratique mon espagnol sur lui. Chez le coiffeur : même histoire. Au marché aussi.</b></p>\n        <p>Depuis que j\'ai quitté les Pays-Bas pour l\'Espagne, j\'essaie d\'apprendre la langue sérieusement. J\'ai testé toutes les applis connues, et elles sont très bonnes dans ce pour quoi elles sont faites : vous faire revenir demain. Ça marchait, d\'ailleurs : j\'avais une série de plusieurs mois. Sauf que je n\'arrivais toujours pas à faire une phrase au marché. Chaque appli mesure quelque chose, et ce que vous mesurez est ce que vous obtenez. Elles mesurent si vous revenez. Je voulais quelque chose qui mesure si j\'y arrive.</p>\n        <p>Et je n\'ai jamais arrêté parce que l\'espagnol était trop difficile, mais parce que ça devenait trop ennuyeux. Alors j\'ai créé la mienne.</p>\n        <p>¡Vamos! suit les livres de mes vrais cours d\'espagnol (deux fois par semaine à l\'<a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, je recommande). Vous tapez vos réponses au lieu de les cliquer, et chaque mot revient exactement au moment où vous alliez l\'oublier.</p>\n        <p>La différence est dans le sens du mot "appris". Dans la plupart des applis, vous cliquez la bonne image parmi quatre, et ça compte. Ici, un mot ne compte que lorsque vous l\'avez vraiment tapé correctement cinq fois, réparties sur au moins vingt-cinq jours. C\'est lent. C\'est voulu, sinon vous ne mesurez que le nombre de clics.</p>\n        <p>Et vos erreurs sont transformées en nouveaux exercices pendant la nuit. Pas sur un thème au hasard, mais exactement sur ce qui vous fait trébucher à chaque fois. Se tromper ne coûte pas de points, ça en rapporte. Et manquer une journée ? Aucun problème. Cette appli est un complément à la parole, pas un remplacement. Une langue s\'apprend en conversation ; l\'appli fait en sorte que vous ayez quelque chose à dire.</p>\n        <p>En chemin, Chispa grandit avec vous : un axolotl qui vit de vos efforts. Un tamagotchi linguistique, sauf que celui-ci vous apprend l\'espagnol.</p>\n        <p>J\'ai créé ça pour moi, mais entre-temps toute ma famille apprend l\'espagnol. Il y avait un classement entre nous, et je l\'ai retiré. On se met à jouer pour gagner au lieu d\'apprendre. Maintenant, votre écran d\'accueil montre simplement ce que les autres ont appris ce jour-là, sans points et sans comparaison, et vous pouvez leur lancer un mot en retour. C\'est secrètement ma partie préférée. Parce qu\'une nouvelle langue est le meilleur entraînement que vous puissiez offrir à votre cerveau.</p>\n      </div>\n      '),
  # ---- DE ----
  ('<div class="card">\n        <span class="kicker">Die Geschichte hinter ¡Vamos!</span>\n        <p style="margin-top:10px"><b>Der Uber-Fahrer fährt sowieso nirgendwo hin. Also übe ich mein Spanisch an ihm. Beim Friseur: dieselbe Geschichte. Auf dem Markt auch.</b></p>\n        <p>Seit ich von den Niederlanden nach Spanien gezogen bin, versuche ich, die Sprache wirklich zu lernen. Ich habe alle bekannten Apps getestet, aber die sind dafür gebaut, dass du jeden Tag wiederkommst, nicht dafür, dir etwas beizubringen. Und die meisten Menschen hören nicht auf, weil Spanisch zu schwer ist, sondern weil es zu langweilig wird. Also habe ich meine eigene gebaut.</p>\n        <p>¡Vamos! folgt den Büchern meines echten Spanischunterrichts (zweimal pro Woche in der <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, sehr zu empfehlen). Du tippst deine Antworten, statt sie anzuklicken, jedes Wort kommt genau dann zurück, wenn du es fast vergessen hast, und deine Fehler werden nachts zu neuen Übungen verarbeitet. Fehler kosten keine Punkte, sie bringen welche. Und mal einen Tag auslassen? Völlig in Ordnung. Diese App ist eine Ergänzung zum Sprechen, kein Ersatz. Eine Sprache lernst du im Gespräch; die App sorgt dafür, dass du in dem Gespräch etwas zu sagen hast.</p>\n        <p>Unterwegs wächst Chispa mit dir mit: ein Axolotl, der von deinem Einsatz lebt. Ein Sprach-Tamagotchi, nur dass dieses dir Spanisch beibringt.</p>\n        <p>Ich habe das für mich selbst gebaut, aber inzwischen lernt meine ganze Familie mit, samt Familien-Rangliste. Das ist heimlich mein Lieblingsteil. Denn eine neue Sprache ist das beste Training, das du deinem Gehirn schenken kannst.</p>\n      </div>\n      ',
   '<div class="card">\n        <span class="kicker">Die Geschichte hinter ¡Vamos!</span>\n        <p style="margin-top:10px"><b>Der Uber-Fahrer fährt sowieso nirgendwo hin. Also übe ich mein Spanisch an ihm. Beim Friseur: dieselbe Geschichte. Auf dem Markt auch.</b></p>\n        <p>Seit ich von den Niederlanden nach Spanien gezogen bin, versuche ich, die Sprache wirklich zu lernen. Ich habe alle bekannten Apps getestet, und sie sind sehr gut in dem, wofür sie gebaut sind: dafür sorgen, dass du morgen wiederkommst. Das hat auch funktioniert, ich hatte eine Serie von Monaten. Nur konnte ich auf dem Markt immer noch keinen Satz bilden. Jede App misst etwas, und was du misst, bekommst du. Sie messen, ob du wiederkommst. Ich wollte etwas, das misst, ob ich es kann.</p>\n        <p>Und ich habe nie aufgehört, weil Spanisch zu schwer war, sondern weil es zu langweilig wurde. Also habe ich meine eigene gebaut.</p>\n        <p>¡Vamos! folgt den Büchern meines echten Spanischunterrichts (zweimal pro Woche in der <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, sehr zu empfehlen). Du tippst deine Antworten, statt sie anzuklicken, und jedes Wort kommt genau dann zurück, wenn du es fast vergessen hast.</p>\n        <p>Der Unterschied liegt darin, was "gelernt" bedeutet. In den meisten Apps tippst du das richtige Bild aus vieren an, und dann zählt es. Hier zählt ein Wort erst, wenn du es fünfmal wirklich richtig getippt hast, verteilt über mindestens fünfundzwanzig Tage. Das geht langsam. Das ist Absicht, denn sonst misst du nur, wie oft du getippt hast.</p>\n        <p>Und deine Fehler werden nachts zu neuen Übungen verarbeitet. Nicht zu irgendeinem Thema, sondern genau zu der einen Sache, über die du ständig stolperst. Fehler kosten keine Punkte, sie bringen welche. Und mal einen Tag auslassen? Völlig in Ordnung. Diese App ist eine Ergänzung zum Sprechen, kein Ersatz. Eine Sprache lernst du im Gespräch; die App sorgt dafür, dass du in dem Gespräch etwas zu sagen hast.</p>\n        <p>Unterwegs wächst Chispa mit dir mit: ein Axolotl, der von deinem Einsatz lebt. Ein Sprach-Tamagotchi, nur dass dieses dir Spanisch beibringt.</p>\n        <p>Ich habe das für mich selbst gebaut, aber inzwischen lernt meine ganze Familie mit. Es gab eine Familien-Rangliste, und die habe ich wieder herausgerissen. Man fängt an zu spielen, um zu gewinnen, statt um zu lernen. Jetzt zeigt dein Startbildschirm einfach, was die anderen an dem Tag gelernt haben, ohne Punkte und ohne Vergleich, und du kannst ihnen etwas zurufen. Das ist heimlich mein Lieblingsteil. Denn eine neue Sprache ist das beste Training, das du deinem Gehirn schenken kannst.</p>\n      </div>\n      '),
]

if DOE_APP:
    ontbreekt = [i + 1 for i, p in enumerate(PAREN) if p[0] not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; blok %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.92. Eerst bijtrekken:\n\n    git pull --rebase\n"
              % ", ".join(map(str, ontbreekt)))
        sys.exit(1)
    for a, b in PAREN:
        rep(a, b)

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
