// pw-gramvariatie.js (13 aug, v23.89) — hoeveel verschillende oefenzinnen kan een onderwerp maken?
//
// WAAROM DIT ER IS
//
// Vier grammatica-onderwerpen (negacion, tuusted, pronombre, pedirpreguntar) hadden vijf patronen
// die alle vijf een vaste zin waren, zonder één gcKies(). Wie zo'n onderwerp één keer deed had het
// uitgeput: elke herhaling daarna was letterlijk dezelfde zin. Dat is een halve maand onopgemerkt
// gebleven, want geen enkele suite keek ernaar. v23.88 heeft ze gerepareerd; deze suite zorgt dat
// het niet stil terug kan komen.
//
// EN HOE JE HET NIET MOET METEN
//
// Mijn eerste meting hiervan was fout, en de fout is leerzaam genoeg om hier te staan. Ik riep
// gcMaakVragen(c, 1) zestig keer aan op een verse pagina en concludeerde dat zes onderwerpen maar
// één zin konden maken. Maar gcMaakVragen roteert over de patronen én begint bij patroon nul voor
// wie het onderwerp nog nooit deed (zie de opmerking daar, v23.59). Zestig keer n=1 op een vers
// profiel is dus zestig keer patroon nul.
//
// Op die verkeerde meting is toen GC_ORDE aangepast, en dat moest in v23.88 weer terug. Vandaar
// twee dingen in deze suite:
//
//   1. Er wordt gemeten zoals een terugkerende gebruiker het krijgt: met geschiedenis in S.gram, en
//      met n=5, want dat is een echte ronde.
//   2. Er zit een controlegeval in. serestar hoort ver boven de drempel te zitten. Zakt die ook,
//      dan is niet de content stuk maar de meting, en dan wil je dat weten vóórdat je iets gaat
//      repareren dat niet kapot is.
//
// DE GETALLEN
//
// Dertig rondes van vijf verzadigt: bij zestig rondes komen er geen nieuwe zinnen meer bij, en twee
// metingen achter elkaar geven hetzelfde. Gemeten op v23.88, de vijf laagste:
//
//     futuroir 10 · saberpoder 12 · gerundio 15 · quecual 16 · saberconocer 17   (serestar 98)
//
// De drempel staat op 8. Dat is ruim onder de laagste die er nu staat en ruim boven de vijf van een
// onderwerp met alleen vaste zinnen. Een onderwerp dat terugvalt naar vaste zinnen valt er dus door,
// en een onderwerp dat toevallig een paar zinnen minder maakt niet.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
const DREMPEL = Number(process.env.GRAM_DREMPEL || 8);
const RONDES = 30;
const CONTROLE = 'serestar';
const CONTROLE_MIN = 40;

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await page.goto(U);
  await page.waitForTimeout(1500);

  const r = await page.evaluate(({ rondes }) => {
    const uit = { terug: {}, eerste: {}, leeg: [] };
    S.gram = S.gram || {};
    GC_CONCEPTEN.forEach((c) => {
      // eerst als iemand die het onderwerp nog nooit deed: dan hoort hij patroon 0 t/m 4 te krijgen
      delete S.gram[c.id];
      let eerste = [];
      try { eerste = gcMaakVragen(c, 5); } catch (e) { eerste = []; }
      uit.eerste[c.id] = new Set(eerste.map((x) => x.v)).size;

      // en dan als terugkerende gebruiker, want daar gaat variatie over
      S.gram[c.id] = { goed: 3, fout: 1, box: 1 };
      const zn = new Set();
      for (let i = 0; i < rondes; i++) {
        let v = [];
        try { v = gcMaakVragen(c, 5); } catch (e) { v = []; }
        v.forEach((x) => { if (x && x.v) zn.add(x.v); else uit.leeg.push(c.id); });
      }
      uit.terug[c.id] = zn.size;
    });
    return uit;
  }, { rondes: RONDES });

  console.log('\n-- een verse gebruiker krijgt vijf verschillende vragen --');
  // Dit is de andere kant van dezelfde zaak: de eerste ronde mag geen dubbele bevatten. Dat kan
  // gebeuren als twee patronen toevallig dezelfde zin maken, en dan zie je op je eerste dag twee
  // keer hetzelfde.
  const teWeinig = Object.entries(r.eerste).filter(([, n]) => n < 5);
  ok(teWeinig.length === 0,
    'elk onderwerp geeft vijf verschillende vragen in de eerste ronde' +
      (teWeinig.length ? ' (' + teWeinig.map(([k, n]) => k + '=' + n).join(' ') + ')' : ''));

  console.log('\n-- en hoeveel kan hij er in totaal maken? --');
  const rij = Object.entries(r.terug).sort((a, b) => a[1] - b[1]);
  rij.slice(0, 6).forEach(([k, n]) => console.log('  ' + k.padEnd(18) + n));
  console.log('  ' + ('… ' + (rij.length - 7) + ' onderwerpen ertussen').padEnd(18));
  console.log('  ' + rij[rij.length - 1][0].padEnd(18) + rij[rij.length - 1][1]);

  const arm = rij.filter(([, n]) => n < DREMPEL);
  ok(arm.length === 0,
    'geen onderwerp onder de ' + DREMPEL + ' verschillende vragen' +
      (arm.length ? ' (' + arm.map(([k, n]) => k + '=' + n).join(' ') + ')' : ', laagste is ' + rij[0][0] + '=' + rij[0][1]));

  console.log('\n-- het controlegeval --');
  // Zakt deze mee, dan is de meting stuk en niet de content. Precies die verwarring kostte in
  // v23.83 een verandering die niet had gemoeten.
  ok((r.terug[CONTROLE] || 0) >= CONTROLE_MIN,
    CONTROLE + ' zit ruim boven de drempel (' + r.terug[CONTROLE] + ', minstens ' + CONTROLE_MIN +
      '); zakt deze mee, dan is niet de content stuk maar deze meting');

  ok(r.leeg.length === 0, 'geen enkel patroon gaf een lege vraag terug' +
    (r.leeg.length ? ' (' + [...new Set(r.leeg)].slice(0, 4).join(' ') + ')' : ''));
  ok(errs.length === 0, 'geen paginafouten tijdens het genereren' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
