#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.96: Frans en Duits eruit, en zeven stukken code die niets meer deden (punt 28 en 29).

## Punt 28: twee talen die niemand kon zien

In index.html stonden complete Franse en Duitse teksten: het proefscherm, het aanmeldscherm, de
landing voor wie via een uitnodigingslink binnenkomt, en het hele verhaal achter Vamos. Ze waren
onbereikbaar. `UI_LANGS` kent alleen nl en en, `taalWeHebben()` valt alles wat daarbuiten valt terug
op en, en de taalkeuze bij het aanmelden komt uit diezelfde tabel. Er was geen weg naar het Frans.

De kiezer van de steunpagina testte nog wel op fr en de, en dat is precies hoe zoiets blijft staan:
de code ziet er levend uit.

Dat kost ruim 20.000 tekens die iedereen op elke telefoon meedownloadt, in een bestand van 2,5 MB
waarvan de laadtijd al een keer eerder een onderwerp was.

Voor de duidelijkheid, want dit is verwarrend: het Franse en Duitse verhaal is vanmiddag nog met
v23.93 teruggezet. Dat was juist: dat werk zat in een commit die om een andere reden werd
teruggedraaid, en werk verdwijnt niet in een revert. Nu is het een schone beslissing van Stefan in
plaats van een ongeluk, en die beslissing is: eruit. Het staat in de geschiedenis als iemand ooit een
derde taal wil.

## Punt 29: zeven stukken die niets meer deden

Weg: `nogTeHalen()`, `spelZinSrs()`, `krabbelLokaal()`, `krabbelOntvangenHtml()`,
`basisHtml()` en de variabele `sModusOverride`.

Die laatste is de interessantste. Hij stond in een keten `(S.modusKeuze && S.modusKeuze.zin) ||
sModusOverride || sAdaptiefModus(s)`, en op de enige plek waar hij gezet werd, werd `S.modusKeuze.zin`
in dezelfde regel op dezelfde waarde gezet. Hij kon dus nooit winnen. Zo'n variabele is erger dan dode
code, want hij suggereert een mechanisme dat niet bestaat.

## Wat er NIET uit gaat, en waarom

`nivBalkHtml()` stond op mijn lijst als dood. Dat was fout: hij wordt gewoon gebruikt, twee keer, in
de niveaubalken op Voortgang. Nagekeken voordat ik hem weghaalde.

`dueCount()` blijft ook, en om dezelfde reden als updateBadge: hij wordt door niets in de app
aangeroepen, maar `pw-tellersweg.js` gebruikt hem als meetpunt om te bewijzen dat de SRS-boekhouding
onder water doorloopt nu de badge weg is. Dat is geen dode code, dat is een naad met een doel. De
poort ving dit toen ik hem toch weghaalde; precies waar die poort voor is.

`updateBadge()` blijft. Hij is leeg sinds de badge in v19.64 verdween, maar achttien plekken roepen
hem aan. Die achttien aanroepen weghalen kost achttien bewerkingen in code die nu werkt, vlak voor een
lancering, en levert niets op behalve netheid. Hij krijgt een kop die vertelt dat hij met opzet leeg
is; dat lost het echte probleem op, namelijk dat een lezer denkt dat er iets gebeurt.

Punt 30 (twee SRS-ladders voor hetzelfde) is van de lijst: zie het gespreksverslag. `GRAM_INTERVALS`
is de ladder van de toetsjes en `GRAM_BOX` die van de concepten. Twee ladders voor twee verschillende
dingen, geen dubbeling. Samenvoegen zou een ontwerpkeuze zijn en geen opruiming.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.96"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.96" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

PAREN = [
  # ---- PROEF_TXT fr+de ----
  (',\n fr:{kop:"Apprends ton premier mot d\'espagnol", sub:"Pas de compte, pas de tracas. Essaie :", vraag:"Qu\'est-ce que ça veut dire ?",\n     goed:"¡Muy bien! +2 tacos", fout:"C\'était : ", foutXp:". Les erreurs sont de l\'or : +1 taco !",\n     klaarKop:"Voilà tes 3 premiers mots d\'espagnol ! 🎉", klaarSub:"En trente secondes. Le reste est aussi léger. Je te les garde ?",\n     bewaar:"Garde mes mots →", heb:"J\'ai déjà un profil ou un code de synchro"},\n de:{kop:"Lern jetzt dein erstes spanisches Wort", sub:"Kein Konto, kein Aufwand. Einfach ausprobieren:", vraag:"Was bedeutet das?",\n     goed:"¡Muy bien! +2 Tacos", fout:"Es war: ", foutXp:". Fehler sind Gold: +1 Taco!",\n     klaarKop:"Das sind deine ersten 3 spanischen Wörter! 🎉", klaarSub:"In einer halben Minute. So leicht fühlt sich der Rest auch an. Soll ich sie dir aufheben?",\n     bewaar:"Meine Wörter speichern →", heb:"Ich habe schon ein Profil oder einen Sync-Code"}',
   ''),
  # ---- SIGNUP_TXT fr+de ----
  (',\n fr:{welkom:"Bienvenue ! Crée ton profil", nieuw:"Nouveau profil", kies:"Qui va pratiquer ?", naamPh:"Prénom",\n     niveau:"Niveau :", a0:"A0 · totalement débutant", a1:"A1 · quelques mots", a2:"A2 · je connais les bases", b1:"B1 · bientôt",\n     taal:"Langue maternelle :", mailUitleg:"Facultatif : e-mail, pour retrouver ta progression si tu perds ton code d\'accès.",\n     mailPh:"E-mail (facultatif)",\n     groepUitleg:"Tu as reçu un <b>lien d\'invitation</b> pour un groupe ? Ouvre simplement ce lien. Seulement un <b>code</b> ? Saisis-le ci-dessous. Ni l\'un ni l\'autre ? Laisse vide : tu peux toujours créer un groupe (par exemple comme prof, pour ta classe) depuis ton profil.",\n     groepPh:"Code de groupe (seulement si tu en as reçu un)", start:"Commencer", test:"Pas sûr ? Fais le test de niveau",\n     hint:"Choisis un niveau, ou fais le test de 10 questions (2 minutes).",\n     syncKop:"Tu pratiques déjà sur un autre appareil ?", syncUitleg:"Saisis ton code de synchronisation (sur ta page de profil de l\'autre appareil) et reprends où tu en étais.",\n     syncKnop:"Récupérer ma progression", herstel:"Code perdu ? Récupère via ton e-mail", herstelPh:"L\'adresse e-mail de ton profil",\n     herstelKnop:"Retrouver ma progression",\n     doel:"Combien de temps par jour ? Cela détermine la taille de ta portion quotidienne — modifiable à tout moment, par exemple en vacances.",\n     m5:"5 minutes", m10:"10 minutes", m20:"20 minutes", m30:"30 minutes"},\n de:{welkom:"Willkommen! Erstelle dein Profil", nieuw:"Neues Profil", kies:"Wer übt?", naamPh:"Name",\n     niveau:"Niveau:", a0:"A0 · ganz neu", a1:"A1 · ein paar Wörter", a2:"A2 · ich kenne die Basics", b1:"B1 · bald",\n     taal:"Muttersprache:", mailUitleg:"Optional: E-Mail, damit du deinen Fortschritt wiederfindest, falls du deinen Zugangscode verlierst.",\n     mailPh:"E-Mail (optional)",\n     groepUitleg:"Hast du einen <b>Einladungslink</b> für eine Gruppe bekommen? Öffne einfach den Link. Nur einen <b>Code</b>? Trage ihn unten ein. Weder noch? Leer lassen: eine Gruppe starten (z. B. als Lehrkraft für deine Klasse) geht jederzeit über dein Profil.",\n     groepPh:"Gruppencode (nur falls du einen bekommen hast)", start:"Los geht\'s", test:"Unsicher? Mach den Einstufungstest",\n     hint:"Wähle ein Niveau oder mach den Test mit 10 Fragen (2 Minuten).",\n     syncKop:"Übst du schon auf einem anderen Gerät?", syncUitleg:"Gib deinen Sync-Code ein (auf der Profilseite deines anderen Geräts) und mach weiter, wo du warst.",\n     syncKnop:"Fortschritt holen", herstel:"Code verloren? Über E-Mail wiederherstellen", herstelPh:"Die E-Mail-Adresse deines Profils",\n     herstelKnop:"Fortschritt suchen",\n     doel:"Wie viel Zeit pro Tag? Das bestimmt die Größe deiner Tagesportion — jederzeit änderbar, zum Beispiel im Urlaub.",\n     m5:"5 Minuten", m10:"10 Minuten", m20:"20 Minuten", m30:"30 Minuten"}',
   ''),
  # ---- LANDING_TXT fr+de ----
  (',\n fr:{kicker:"Tu es invité 👋", persoon:"{n} apprend l\'espagnol et t\'invite à le rejoindre.",\n     groep:"Tu es invité à rejoindre {n}.", anoniem:"Quelqu\'un apprend l\'espagnol et t\'invite.",\n     sub:"Cinq minutes par jour. Pas de compte, pas de paiement, pas de publicité. Chispa explique le reste.",\n     cadeau:"🫒 <b>Cadeau :</b> 10 tapas pour ton propre Chispa, prêtes dès que tu commences.",\n     start:"C\'est parti →", alleen:"Je préfère d\'abord regarder seul"},\n de:{kicker:"Du bist eingeladen 👋", persoon:"{n} lernt Spanisch und fragt, ob du mitmachst.",\n     groep:"Du bist eingeladen zu {n}.", anoniem:"Jemand lernt Spanisch und fragt, ob du mitmachst.",\n     sub:"Fünf Minuten am Tag. Kein Konto, keine Zahlung, keine Werbung. Chispa erklärt den Rest.",\n     cadeau:"🫒 <b>Geschenk:</b> 10 Tapas für dein eigenes Chispa, bereit sobald du anfängst.",\n     start:"Los geht\'s →", alleen:"Ich schaue mich lieber erst allein um"}',
   ''),
  # ---- losse regel SIGNUP_TXT.fr.uitnodigGroep = "🎉 T ----
  ('SIGNUP_TXT.fr.uitnodigGroep = "🎉 Tu es invité ! Crée ton profil ci-dessous et tu rejoins directement le groupe de ton ami. Vous voyez vos séries et objectifs, jamais vos erreurs.";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.de.uitnodigGroep = "🎉 D ----
  ('SIGNUP_TXT.de.uitnodigGroep = "🎉 Du bist eingeladen! Leg unten dein Profil an, dann bist du sofort in der Gruppe deines Freundes. Ihr seht Streak und Tagesziel, nie die Fehler des anderen.";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.fr.uitnodigDuel = "⚔️ T ----
  ('SIGNUP_TXT.fr.uitnodigDuel = "⚔️ Tu es défié pour un Palabra Duel ! Crée ton profil ci-dessous et le duel t\'attend.";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.de.uitnodigDuel = "⚔️ D ----
  ('SIGNUP_TXT.de.uitnodigDuel = "⚔️ Du wurdest zu einem Palabra Duel herausgefordert! Leg unten dein Profil an, dann steht das Duell bereit.";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.fr.meer = "⚙️ Plus d'op ----
  ('SIGNUP_TXT.fr.meer = "⚙️ Plus d\'options : objectif quotidien, e-mail, code de groupe (possible plus tard aussi)";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.de.meer = "⚙️ Mehr Opti ----
  ('SIGNUP_TXT.de.meer = "⚙️ Mehr Optionen: Tagesziel, E-Mail, Gruppencode (geht auch später)";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.fr.wijzig = "modifier"; ----
  ('SIGNUP_TXT.fr.wijzig = "modifier";\n',
   ''),
  # ---- losse regel SIGNUP_TXT.de.wijzig = "ändern"; ----
  ('SIGNUP_TXT.de.wijzig = "ändern";\n',
   ''),
  # ---- steunFR en steunDE ----
  ('    <div id="steunFR" class="hidden">\n      <div class="card">\n        <span class="kicker">L\'histoire derrière ¡Vamos!</span>\n        <p style="margin-top:10px"><b>Le chauffeur Uber ne va nulle part de toute façon. Alors je pratique mon espagnol sur lui. Chez le coiffeur : même histoire. Au marché aussi.</b></p>\n        <p>Depuis que j\'ai quitté les Pays-Bas pour l\'Espagne, j\'essaie d\'apprendre la langue sérieusement. J\'ai testé toutes les applis connues, et elles sont très bonnes dans ce pour quoi elles sont faites : vous faire revenir demain. Ça marchait, d\'ailleurs : j\'avais une série de plusieurs mois. Sauf que je n\'arrivais toujours pas à faire une phrase au marché. Chaque appli mesure quelque chose, et ce que vous mesurez est ce que vous obtenez. Elles mesurent si vous revenez. Je voulais quelque chose qui mesure si j\'y arrive.</p>\n        <p>Et je n\'ai jamais arrêté parce que l\'espagnol était trop difficile, mais parce que ça devenait trop ennuyeux. Alors j\'ai créé la mienne.</p>\n        <p>¡Vamos! suit les livres de mes vrais cours d\'espagnol (deux fois par semaine à l\'<a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, je recommande). Vous tapez vos réponses au lieu de les cliquer, et chaque mot revient exactement au moment où vous alliez l\'oublier.</p>\n        <p>La différence est dans le sens du mot "appris". Dans la plupart des applis, vous cliquez la bonne image parmi quatre, et ça compte. Ici, un mot ne compte que lorsque vous l\'avez vraiment tapé correctement cinq fois, réparties sur au moins vingt-cinq jours. C\'est lent. C\'est voulu, sinon vous ne mesurez que le nombre de clics.</p>\n        <p>Et vos erreurs sont transformées en nouveaux exercices pendant la nuit. Pas sur un thème au hasard, mais exactement sur ce qui vous fait trébucher à chaque fois. Se tromper ne coûte pas de points, ça en rapporte. Et manquer une journée ? Aucun problème. Cette appli est un complément à la parole, pas un remplacement. Une langue s\'apprend en conversation ; l\'appli fait en sorte que vous ayez quelque chose à dire.</p>\n        <p>En chemin, Chispa grandit avec vous : un axolotl qui vit de vos efforts. Un tamagotchi linguistique, sauf que celui-ci vous apprend l\'espagnol.</p>\n        <p>J\'ai créé ça pour moi, mais entre-temps toute ma famille apprend l\'espagnol. Il y avait un classement entre nous, et je l\'ai retiré. On se met à jouer pour gagner au lieu d\'apprendre. Maintenant, votre écran d\'accueil montre simplement ce que les autres ont appris ce jour-là, sans points et sans comparaison, et vous pouvez leur lancer un mot en retour. C\'est secrètement ma partie préférée. Parce qu\'une nouvelle langue est le meilleur entraînement que vous puissiez offrir à votre cerveau.</p>\n      </div>\n      <div class="card">\n        <h2>Faire un don 💛</h2>\n        <p class="muted">L\'appli est gratuite et le restera. Je paie moi-même les coûts du serveur et de l\'IA, parce que je pense que tout le monde doit pouvoir apprendre une langue, même sans argent. Vous voulez donner quelque chose en retour ? Votre don fait tourner l\'appli, pour les autres aussi. Vous hésitez sur le montant ? La plupart des gens donnent dix euros.</p>\n        <div class="row">\n          <a class="donatebtn" style="background:var(--card); color:var(--ink); border:2px solid var(--border)" href="https://paypal.me/stefanwobben/2EUR" target="_blank" rel="noopener">2 €</a>\n          <a class="donatebtn" href="https://paypal.me/stefanwobben/10EUR" target="_blank" rel="noopener">10 € ⭐ le plus choisi</a>\n          <a class="donatebtn" style="background:var(--card); color:var(--ink); border:2px solid var(--border)" href="https://paypal.me/stefanwobben/25EUR" target="_blank" rel="noopener">25 €</a>\n        </div>\n        <p class="muted" style="margin-top:8px"><a href="https://paypal.me/stefanwobben" target="_blank" rel="noopener">Ou choisissez votre montant →</a></p>\n        <p class="muted" style="margin-top:6px">¡Muchas gracias! — Stefan (et Chispa 🌮)</p>\n      </div>\n    </div>\n    <div id="steunDE" class="hidden">\n      <div class="card">\n        <span class="kicker">Die Geschichte hinter ¡Vamos!</span>\n        <p style="margin-top:10px"><b>Der Uber-Fahrer fährt sowieso nirgendwo hin. Also übe ich mein Spanisch an ihm. Beim Friseur: dieselbe Geschichte. Auf dem Markt auch.</b></p>\n        <p>Seit ich von den Niederlanden nach Spanien gezogen bin, versuche ich, die Sprache wirklich zu lernen. Ich habe alle bekannten Apps getestet, und sie sind sehr gut in dem, wofür sie gebaut sind: dafür sorgen, dass du morgen wiederkommst. Das hat auch funktioniert, ich hatte eine Serie von Monaten. Nur konnte ich auf dem Markt immer noch keinen Satz bilden. Jede App misst etwas, und was du misst, bekommst du. Sie messen, ob du wiederkommst. Ich wollte etwas, das misst, ob ich es kann.</p>\n        <p>Und ich habe nie aufgehört, weil Spanisch zu schwer war, sondern weil es zu langweilig wurde. Also habe ich meine eigene gebaut.</p>\n        <p>¡Vamos! folgt den Büchern meines echten Spanischunterrichts (zweimal pro Woche in der <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, sehr zu empfehlen). Du tippst deine Antworten, statt sie anzuklicken, und jedes Wort kommt genau dann zurück, wenn du es fast vergessen hast.</p>\n        <p>Der Unterschied liegt darin, was "gelernt" bedeutet. In den meisten Apps tippst du das richtige Bild aus vieren an, und dann zählt es. Hier zählt ein Wort erst, wenn du es fünfmal wirklich richtig getippt hast, verteilt über mindestens fünfundzwanzig Tage. Das geht langsam. Das ist Absicht, denn sonst misst du nur, wie oft du getippt hast.</p>\n        <p>Und deine Fehler werden nachts zu neuen Übungen verarbeitet. Nicht zu irgendeinem Thema, sondern genau zu der einen Sache, über die du ständig stolperst. Fehler kosten keine Punkte, sie bringen welche. Und mal einen Tag auslassen? Völlig in Ordnung. Diese App ist eine Ergänzung zum Sprechen, kein Ersatz. Eine Sprache lernst du im Gespräch; die App sorgt dafür, dass du in dem Gespräch etwas zu sagen hast.</p>\n        <p>Unterwegs wächst Chispa mit dir mit: ein Axolotl, der von deinem Einsatz lebt. Ein Sprach-Tamagotchi, nur dass dieses dir Spanisch beibringt.</p>\n        <p>Ich habe das für mich selbst gebaut, aber inzwischen lernt meine ganze Familie mit. Es gab eine Familien-Rangliste, und die habe ich wieder herausgerissen. Man fängt an zu spielen, um zu gewinnen, statt um zu lernen. Jetzt zeigt dein Startbildschirm einfach, was die anderen an dem Tag gelernt haben, ohne Punkte und ohne Vergleich, und du kannst ihnen etwas zurufen. Das ist heimlich mein Lieblingsteil. Denn eine neue Sprache ist das beste Training, das du deinem Gehirn schenken kannst.</p>\n      </div>\n      <div class="card">\n        <h2>Spenden 💛</h2>\n        <p class="muted">Die App ist kostenlos und bleibt es. Die Server- und KI-Kosten zahle ich selbst, weil ich finde, dass jeder eine Sprache lernen können sollte, auch wer kein Geld dafür hat. Willst du trotzdem etwas zurückgeben? Deine Spende hält die App am Laufen, auch für andere. Unsicher, wie viel? Die meisten geben einen Zehner.</p>\n        <div class="row">\n          <a class="donatebtn" style="background:var(--card); color:var(--ink); border:2px solid var(--border)" href="https://paypal.me/stefanwobben/2EUR" target="_blank" rel="noopener">2 €</a>\n          <a class="donatebtn" href="https://paypal.me/stefanwobben/10EUR" target="_blank" rel="noopener">10 € ⭐ am häufigsten</a>\n          <a class="donatebtn" style="background:var(--card); color:var(--ink); border:2px solid var(--border)" href="https://paypal.me/stefanwobben/25EUR" target="_blank" rel="noopener">25 €</a>\n        </div>\n        <p class="muted" style="margin-top:8px"><a href="https://paypal.me/stefanwobben" target="_blank" rel="noopener">Oder wähle selbst einen Betrag →</a></p>\n        <p class="muted" style="margin-top:6px">¡Muchas gracias! — Stefan (und Chispa 🌮)</p>\n      </div>\n    </div>\n',
   ''),
  # ---- de taalkiezer van de steunpagina ----
  ('    var sl = profLang();\n    if(sl !== "nl" && sl !== "fr" && sl !== "de") sl = "en";\n    ["NL","EN","FR","DE"].forEach(function(k){',
   '    /* v23.96: hier stond een lijst van vier talen en een test op fr en de. UI_LANGS kent alleen\n       nl en en, en profLang() kan dus nooit iets anders teruggeven; die takken waren onbereikbaar. */\n    var sl = profLang() === "nl" ? "nl" : "en";\n    ["NL","EN"].forEach(function(k){'),
  # ---- dode functie nogTeHalen ----
  ('function nogTeHalen(rang){\n  // ligt er op dit niveau nog een poolwoord dat niet stevig is?\n  var drempel = stevigDrempel(), i, w, st;\n  for(i = 0; i < WORDS.length; i++){\n    w = WORDS[i];\n    if(woordNiveau(w.id) !== rang) continue;\n    st = S.srs[w.id];\n    if(!st || (st.box || 0) < drempel) return true;\n  }\n  return false;\n}\n',
   ''),
  # ---- dode functie spelZinSrs ----
  ('function spelZinSrs(zin){\n  var map = spelWordIdx(), gezien = {}, n = 0;\n  String((zin && zin.es) || "").split(/[^A-Za-z\\u00c0-\\u024f]+/).forEach(function(tok){\n    if(!tok) return;\n    var id = map[stripAcc(norm(tok))];\n    if(!id || gezien[id]) return;\n    gezien[id] = 1;\n    if(spelSrsBij(id)) n++;\n  });\n  if(n){ persist(); updateBadge(); }\n  return n;\n}\n',
   ''),
  # ---- dode functie krabbelLokaal ----
  ('function krabbelLokaal(){\n  if(!S.krabbels) S.krabbels = {};\n  if(S.krabbelDag !== today()){ S.krabbels = {}; S.krabbelDag = today(); }\n  return S.krabbels;\n}\n',
   ''),
  # ---- dode functie krabbelOntvangenHtml ----
  ('function krabbelOntvangenHtml(naam, krabbels){\n  if(!krabbels || !krabbels.length) return "";\n  var mijn = krabbels.filter(function(x){ return String(x.naar||"").toLowerCase() === String(naam||"").toLowerCase(); });\n  if(!mijn.length) return "";\n  var chips = mijn.map(function(x){\n    var kr = krabbelVind(x.sleutel);\n    if(!kr) return "";\n    // titel = de hele Spaanse zin, chip zelf blijft kort: emoji + afzender\n    return "<span class=\'krabchip\' title=\'"+kr.es+"\'>"+kr.e+" <span class=\'es\'>"+kr.es+"</span>"+\n      "<span class=\'van\'>\\u00b7 "+x.van+"</span></span>";\n  }).filter(Boolean).join("");\n  return chips ? "<div class=\'krabchips\'>"+chips+"</div>" : "";\n}\n',
   ''),
  # ---- dode functie basisHtml ----
  ('function basisHtml(actief14){\n  var t = voortgangTellers();\n  var d1 = t.dek.A1 || 0;\n  var w1 = Math.max(d1, (t.dekw && t.dekw.A1) || 0);   // onderweg is nooit minder dan stevig\n  var pctW = Math.round(100 * (w1 - d1) / (PCIC_NOEMER.A1 || 390));\n  var poort = poortRang();\n  var k = leerKpi().recent;\n  var doelPct = Math.round(POORT_PCT * 100);\n  var poortTxt;\n  if(poort <= 0){\n    poortTxt = ct("A1 is nu aan de beurt. Zodra "+doelPct+"% stevig staat gaat A2 open; tot die tijd krijg je er elke dag één woord van hogerop bij.",\n                  "A1 is up now. Once "+doelPct+"% is solid, A2 opens; until then you get one word from higher up each day.");\n  } else if(poort >= 9){\n    poortTxt = ct("Je basis staat. Alles is open.","Your base is in place. Everything is open.");\n  } else {\n    poortTxt = ct("A1 staat. Je bouwt nu verder op "+NIV_NAAM[poort]+".",\n                  "A1 is in place. You\'re building on "+NIV_NAAM[poort]+" now.");\n  }\n  var dagen = (S.dagen && S.dagen.count) || 0;\n  var tk = terugkomKpi();\n  var pw = Math.round(10 * tk.actief * 7 / tk.venster) / 10;\n  var pwTxt = tk.rijp ? String(pw).replace(".", ",") + "×" : actief14 + "/14";\n  // v19.86: de zin die Stefan zelf heeft gedefinieerd. Onder zijn grens neemt de\n  // app de schuld, niet de gebruiker, en laat zien wat hij eraan doet.\n  var terugTxt = "";\n  if(tk.onder){\n    terugTxt = "<p class=\'muted\' style=\'margin:8px 0 0\'>"+\n      ct("Je komt nu minder dan "+tk.pw+" keer per week terug. Dat is de grens die je zelf hebt getrokken: "+\n         "daaronder ligt het aan het ontwerp, niet aan jou. Dus is je dagportie kleiner gemaakt "+\n         "("+portieMax()+" woorden, waarvan "+nieuwPerDag()+" nieuw) zodat een sessie in een paar minuten klaar is. "+\n         "Kom je weer vaker, dan groeit hij vanzelf terug.",\n         "You\'re coming back less than "+tk.pw+" times a week. That\'s the line you drew yourself: "+\n         "below it, the design is at fault, not you. So your daily portion has been made smaller "+\n         "("+portieMax()+" words, "+nieuwPerDag()+" of them new) so a session takes a couple of minutes. "+\n         "Come back more often and it grows back on its own.")+"</p>";\n  }\n  /* v23.1. Hier stonden twee balken (A1 en A2), allebei op 0%, met een alinea over wat donker en\n     licht betekenen. Op Vandaag stond intussen hetzelfde verhaal met een aantal als kop. Twee\n     schermen, twee sommen, geen manier om te zien dat ze over hetzelfde gingen.\n\n     Nu roept dit scherm dagBasisRegelHtml() aan: precies het blok van Vandaag, met dezelfde kop,\n     dezelfde balk en dezelfde legenda. Eén implementatie. De niveaubalken per niveau staan een\n     regel lager, onder een vouw, want daar horen ze: dat is verdieping en geen antwoord op "waar\n     sta ik". De uitleg over donker en licht is overbodig geworden; de legenda zegt het nu bij de\n     balk zelf, met getallen erbij. */\n  /* v23.14: zonder legenda. Die vier getallen staan een stuk lager op ditzelfde scherm in de\n     lange lijst, daar met een regel uitleg erbij. Hier zou het een tweede weergave van dezelfde\n     som zijn, en dat is precies wat dit scherm niet meer doet. */\n  return "<h2>"+ct("Waar je staat","Where you are")+"</h2>"+\n    dagBasisRegelHtml({legenda:false})+\n    "<details style=\'margin-top:10px\'><summary class=\'muted\' style=\'cursor:pointer; font-size:.86rem\'>"+\n      ct("Per niveau","Per level")+"</summary>"+\n      nivBalkHtml("A1", t)+nivBalkHtml("A2", t)+\n      "<p class=\'muted\' style=\'margin:6px 0 0; font-size:.82rem\'>"+poortTxt+"</p></details>"+\n    "<div class=\'statgrid\' style=\'margin-top:10px\'>"+\n      // v19.86b, Stefan: "ik vind de indicator belangrijker dan de doelstelling."\n      // Dus staat het terugkomcijfer vooraan, in zijn eenheid: keer per week.\n      // v19.90d: in de opbouwfase is het getal "9/14", en dan klopt "keer per week"\n      // niet met wat er staat. Het label volgt nu het getal in plaats van andersom.\n      "<div class=\'stat\'><b>"+pwTxt+"</b><span class=\'muted\'>"+(tk.rijp\n        ? ct("keer per week terug ("+dagen+" dagen totaal)","times a week you come back ("+dagen+" days total)")\n        : ct("van de laatste 14 dagen actief ("+dagen+" dagen totaal)","of the last 14 days active ("+dagen+" days total)"))+"</span></div>"+\n      // v19.90: hier stonden ook het foutpercentage en het grammaticacijfer. Die\n      // staan nu bij "Wat je kunt", een stukje verderop op ditzelfde scherm, en\n      // twee keer hetzelfde getal laten zien maakt allebei de keren ongeloofwaardig.\n      // Wat hier overblijft gaat over je ritme, en dat is precies wat deze plek\n      // hoort te zijn: de voorspeller, niet de opbrengst.\n      "<div class=\'stat\'><b>"+nieuwPerDag()+"</b><span class=\'muted\'>"+ct("nieuwe woorden per dag","new words a day")+"</span></div>"+\n      "</div>"+terugTxt+\n    (tk.rijp && !tk.onder\n      ? "<p class=\'muted\' style=\'margin:8px 0 0\'>"+\n        ct("Boven je eigen ondergrens van "+tk.pw+" keer per week. Dit is het cijfer dat het meest voorspelt, "+\n           "want die A1-balk vult alleen als je blijft komen.",\n           "Above your own floor of "+tk.pw+" times a week. This is the number that predicts the most, "+\n           "because that A1 bar only fills if you keep coming back.")+"</p>"\n      : "");\n}\n',
   ''),
  # ---- sModusOverride, de declaratie ----
  ('var sModusOverride = null; // (historisch) per-item override; sinds 29 juli wint S.modusKeuze.zin als die gezet is\n',
   ''),
  # ---- sModusOverride in sModus ----
  ('(S.modusKeuze && S.modusKeuze.zin) || sModusOverride || sAdaptiefModus(s)',
   '(S.modusKeuze && S.modusKeuze.zin) || sAdaptiefModus(s)'),
  # ---- updateBadge, eerlijk gemaakt ----
  ('function updateBadge(){\n}\n',
   '/* v23.96: deze functie is met opzet leeg en blijft bestaan.\n\n   Hij telde ooit het aantal openstaande herhalingen in een badge. Die badge is in v19.64 weggehaald\n   (een getal dat groeit terwijl je niets doet, straft wegblijven af), en sindsdien staat hier niets.\n   Achttien plekken roepen hem nog aan.\n\n   Waarom hij niet gewoon weg is: die achttien aanroepen weghalen kost achttien bewerkingen in code\n   die nu werkt, en levert niets op behalve netheid. Deze kop is goedkoper en lost het echte probleem\n   op, namelijk dat een lezer denkt dat hier iets gebeurt. */\nfunction updateBadge(){\n}\n'),
  # ---- sModusOverride nullen in renderSentence ----
  ('if(fresh || sIdx===null){ sIdx = pickSentence(); sModusOverride = null; }',
   'if(fresh || sIdx===null){ sIdx = pickSentence(); }'),
  # ---- sModusOverride zetten in de moeilijk-toggle ----
  ('S.modusKeuze.zin = m; sModusOverride = m; zTegel = null;',
   'S.modusKeuze.zin = m; zTegel = null;'),
  # ---- sModusOverride nullen bij het kiezen van een zin ----
  ('sIdx = z; sModusOverride = null; zTegel = null;',
   'sIdx = z; zTegel = null;'),
]

if DOE_APP:
    ontbreekt = [i + 1 for i, p in enumerate(PAREN) if p[0] not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; anker %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.95. Eerst bijtrekken:\n\n    git pull --rebase\n"
              % ", ".join(map(str, ontbreekt)))
        sys.exit(1)
    for a, b in PAREN:
        n = src.count(a)
        assert n == 1, "anker komt %d keer voor in plaats van 1:\n%s" % (n, a[:200])
        src = src.replace(a, b, 1)

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
