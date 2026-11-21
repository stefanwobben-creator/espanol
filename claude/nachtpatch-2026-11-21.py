#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 21 nov 2026 - fouten verwerken.

Bron: tools/logs-latest.json (snapshot cb1023e, Stefans laatste stand 19 nov 22:52 UTC)
gediffd tegen de vorige snapshot met fouten (b690b29, stand 15 nov). Gegroeid, allemaal
woordkaarten op 19 nov:

  w125 prestar              8 -> 9   (a2-5)
  w150 el descubrimiento    8 -> 9   (a2-9)
  w147 ya no                6 -> 7   (a2-9)
  w62  los seres queridos   4 -> 6   (a2-1)
  w89  llevar gafas         3 -> 5   (a2-3, nog nooit goed)
  w61  descubrir            3 -> 4   (a2-1)
  w129 ¿te importaría...?   2 -> 3   (a2-5)
  w400 la afición           nieuw 2  (b1-18, nog nooit goed)

Ids: tools/ids.json en np.volgendeVrij bestaan (nog) niet in deze repo. Daarom kiest dit
script zelf het eerste vrije nummer BOVEN alles wat ergens geclaimd is: index.html,
audio/dictado/*.mp3, audio/stemmen.json en tools/*.json. Dat sluit s543-s557 uit (audio en
curriculum-laatste.json van de avondrun, zie logboek). Eerste vrije: s558.

Idempotent: tweede keer draaien zegt "stond er al".
"""
import io, json, os, re, sys, glob

WORTEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORTEL, "tools"))
import nachtpatch as np

PAD = os.path.join(WORTEL, "index.html")

# (les, tag, nl, en, es, alt, uitleg, ue)
ZINNEN = [
 ("a2-5", "les5",
  "Ik heb mijn boek aan Juan uitgeleend.",
  "I lent my book to Juan.",
  "Le he prestado mi libro a Juan.",
  ["le he prestado mi libro a juan", "le presté mi libro a juan", "le preste mi libro a juan"],
  "Prestar = uitlenen: jij geeft. Prestar algo a alguien, en de ontvanger krijgt er le bij (le he prestado), ook al staat a Juan er al.",
  "Prestar = to lend: you give. Prestar algo a alguien, and the receiver also gets le (le he prestado), even with a Juan in the sentence."),
 ("a2-5", "les5",
  "Mijn broer leent me nooit zijn auto uit.",
  "My brother never lends me his car.",
  "Mi hermano nunca me presta su coche.",
  ["mi hermano nunca me presta su coche", "mi hermano no me presta nunca su coche", "mi hermano nunca me deja su coche"],
  "Hier geeft je broer, dus prestar met hem als onderwerp: me presta (hij leent mij uit). Zelf lenen ván iemand is pedir prestado.",
  "Here your brother gives, so prestar with him as subject: me presta (he lends me). Borrowing from someone yourself is pedir prestado."),
 ("a2-5", "les5",
  "Zou je het erg vinden om de deur dicht te doen?",
  "Would you mind closing the door?",
  "¿Te importaría cerrar la puerta?",
  ["te importaria cerrar la puerta", "te importaría cerrar la puerta"],
  "¿Te importaría + infinitief? is een beleefd verzoek. Importar werkt als gustar (te importaría, letterlijk 'zou het jou uitmaken') en daarna komt meteen het hele werkwoord: cerrar.",
  "¿Te importaría + infinitive? is a polite request. Importar works like gustar (te importaría, literally 'would it matter to you') and the full verb follows directly: cerrar."),
 ("a2-5", "les5",
  "Zou u het erg vinden om wat langzamer te praten?",
  "Would you mind speaking a bit more slowly?",
  "¿Le importaría hablar un poco más despacio?",
  ["le importaria hablar un poco mas despacio", "le importaría hablar un poco más despacio"],
  "Bij usted wordt te importaría: le importaría. Zelfde constructie, alleen formeel: le + importaría + infinitief (hablar).",
  "With usted, te importaría becomes le importaría. Same construction, just formal: le + importaría + infinitive (hablar)."),
 ("a2-9", "les9",
  "Ik rook niet meer.",
  "I don't smoke anymore.",
  "Ya no fumo.",
  ["ya no fumo", "no fumo más", "no fumo mas", "yo ya no fumo"],
  "Ya no + werkwoord = niet meer. Ya no staat vóór het werkwoord (ya no fumo). No fumo más kan ook, maar ya no is de gewone vorm.",
  "Ya no + verb = not anymore. Ya no goes before the verb (ya no fumo). No fumo más is also possible, but ya no is the usual form."),
 ("a2-9", "les9",
  "Mijn opa werkt niet meer; vroeger werkte hij elke dag.",
  "My grandfather doesn't work anymore; he used to work every day.",
  "Mi abuelo ya no trabaja; antes trabajaba todos los días.",
  ["mi abuelo ya no trabaja antes trabajaba todos los dias", "mi abuelo ya no trabaja, antes trabajaba todos los días"],
  "Nu tegenover vroeger: ya no + presente (ya no trabaja) voor 'niet meer', en antes + imperfecto (trabajaba) voor wat hij vroeger gewoonlijk deed.",
  "Now versus then: ya no + present (ya no trabaja) for 'not anymore', and antes + imperfect (trabajaba) for what he used to do."),
 ("a2-9", "les9",
  "De ontdekking van penicilline veranderde de geneeskunde.",
  "The discovery of penicillin changed medicine.",
  "El descubrimiento de la penicilina cambió la medicina.",
  ["el descubrimiento de la penicilina cambio la medicina", "el descubrimiento de la penicilina cambió la medicina"],
  "El descubrimiento = de ontdekking, het naamwoord bij descubrir. Mannelijk, want op -miento (zoals el conocimiento), ook al is 'de ontdekking' in het Nederlands een de-woord.",
  "El descubrimiento = the discovery, the noun from descubrir. Masculine, because it ends in -miento (like el conocimiento)."),
 ("a2-1", "persoonlijk",
  "Ik heb een klein restaurant ontdekt; het was een echte ontdekking.",
  "I discovered a small restaurant; it was a real discovery.",
  "He descubierto un restaurante pequeño; fue un verdadero descubrimiento.",
  ["he descubierto un restaurante pequeno fue un verdadero descubrimiento", "descubrí un restaurante pequeño, fue un verdadero descubrimiento", "descubri un restaurante pequeno fue un verdadero descubrimiento"],
  "Werkwoord en naamwoord naast elkaar: descubrir (ontdekken, onregelmatig deelwoord descubierto) en el descubrimiento (de ontdekking).",
  "Verb and noun side by side: descubrir (to discover, irregular participle descubierto) and el descubrimiento (the discovery)."),
 ("a2-1", "persoonlijk",
  "Met Kerst ben ik graag bij mijn dierbaren.",
  "At Christmas I like to be with my loved ones.",
  "En Navidad me gusta estar con mis seres queridos.",
  ["en navidad me gusta estar con mis seres queridos"],
  "Los seres queridos = de dierbaren, letterlijk 'de geliefde wezens'. Bijna altijd meervoud: seres (van el ser) en queridos past zich daaraan aan.",
  "Los seres queridos = loved ones, literally 'the beloved beings'. Almost always plural: seres (from el ser) and queridos agrees with it."),
 ("a2-3", "les3",
  "Mijn zus draagt sinds dit jaar een bril.",
  "My sister has been wearing glasses since this year.",
  "Mi hermana lleva gafas desde este año.",
  ["mi hermana lleva gafas desde este ano", "mi hermana lleva gafas desde este año"],
  "Een bril dragen = llevar gafas: met llevar (niet tener of usar), en gafas is meervoud zonder lidwoord. Sinds + nu: presente met desde (lleva gafas desde).",
  "To wear glasses = llevar gafas: with llevar (not tener or usar), and gafas is plural without an article. Since + now: present with desde."),
 ("a2-3", "les3",
  "Draag jij een bril of lenzen?",
  "Do you wear glasses or contact lenses?",
  "¿Llevas gafas o lentillas?",
  ["llevas gafas o lentillas", "tu llevas gafas o lentillas", "¿llevas gafas o lentillas?"],
  "Llevas gafas: llevar voor wat je op of aan hebt, zonder lidwoord. Lentillas = contactlenzen (in Spanje).",
  "Llevas gafas: llevar for what you wear, no article. Lentillas = contact lenses (in Spain)."),
 ("b1-18", "ocio",
  "Mijn grootste hobby is fotografie.",
  "My biggest hobby is photography.",
  "Mi mayor afición es la fotografía.",
  ["mi mayor aficion es la fotografia", "mi mayor afición es la fotografía", "mi afición más grande es la fotografía"],
  "La afición = de hobby of liefhebberij, vrouwelijk (la afición, mis aficiones). Mayor = grootste; en la fotografía houdt het lidwoord, zoals bij elk vak of hobby in het algemeen.",
  "La afición = hobby or passion, feminine (la afición, mis aficiones). Mayor = biggest; la fotografía keeps its article, as with any field or hobby in general."),
]


def geclaimd(src):
    """Elk s-nummer dat ergens al geclaimd is, ook buiten index.html."""
    nrs = set()
    for lijst in np.alleIds(src).values():
        nrs |= {int(x[1:]) for x in lijst if re.match(r"^s\d+$", x)}
    for f in glob.glob(os.path.join(WORTEL, "audio", "dictado", "s*.mp3")):
        m = re.match(r"^s(\d+)\.mp3$", os.path.basename(f))
        if m:
            nrs.add(int(m.group(1)))
    for f in [os.path.join(WORTEL, "audio", "stemmen.json")] + glob.glob(os.path.join(WORTEL, "tools", "*.json")):
        if os.path.basename(f) == "logs-latest.json":
            continue
        tekst = io.open(f, encoding="utf-8").read()
        nrs |= {int(x) for x in re.findall(r'"s(\d+)"', tekst)}
        nrs |= {int(x) for x in re.findall(r'\(s(\d+)\)', tekst)}
    return nrs


def main():
    src = np.laad(PAD)
    marker = ZINNEN[0][4]
    if marker in np.arrayTekst(src, "SENTENCES"):
        print("stond er al; niets gedaan")
        return
    vrij = max(geclaimd(src)) + 1
    nieuwPerLes = {}
    for (les, tag, nl, en, es, alt, uitleg, ue) in ZINNEN:
        zid = "s%d" % vrij
        vrij += 1
        item = {"id": zid, "lvl": 2, "nl": nl, "en": en, "es": es, "alt": alt,
                "uitleg": uitleg, "ue": ue, "tag": tag}
        src = np.zinToevoegen(src, "SENTENCES", json.dumps(item, ensure_ascii=False, separators=(",", ":")))
        nieuwPerLes.setdefault(les, []).append(zid)
    for les, ids in nieuwPerLes.items():
        if les.startswith("b1-"):
            # B1-lessen staan als hele les in nieuweLessen, niet in de lessen-map
            d = np.extraLees(src)
            doel = [l for l in d["nieuweLessen"] if l.get("id") == les]
            assert len(doel) == 1, "les %s niet gevonden in nieuweLessen" % les
            for x in ids:
                if x not in doel[0]["sents"]:
                    doel[0]["sents"].append(x)
            src = np.extraSchrijf(src, d)
        else:
            src = np.lesKoppelen(src, les, ids)
    src = np.batchOphogen(src, "a2")
    np.keuring(src)
    np.bewaar(PAD, src)
    for les, ids in nieuwPerLes.items():
        print("%s: %s" % (les, ", ".join(ids)))
    print("batch a2 ->", np.batchNu(src, "a2"))


if __name__ == "__main__":
    main()
