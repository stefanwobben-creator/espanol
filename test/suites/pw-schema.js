// v22.11: het schemanummer en de migratielijst.
// Stefan: "nu gebruiken nog niet veel mensen het, dus nu het fundament heel goed neerzetten."
//
// Dit is geen test op één migratie maar op het gereedschap eromheen, want dat is wat straks tien
// migraties moet dragen. Wat hier vastligt:
//  - een nieuw profiel begint op het huidige nummer en migreert dus nooit
//  - een profiel zonder nummer is er een van vóór vandaag: schema 1, dus alles draait nog
//  - de defaults mogen het nummer niet invullen voordat het gelezen is (dan zou niets ooit migreren)
//  - een migratie die klapt stopt de ketting en laat het nummer staan, zodat het opnieuw geprobeerd wordt
//  - migraties draaien op volgorde en slaan over wat al gebeurd is
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => {
    const t = msg.text();
    if (msg.type() === 'error' && !/Failed to load resource|migratie naar schema/.test(t)) errors.push('console.error: ' + t);
  });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwSc' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  const basis = await page.evaluate(() => ({
    schema: typeof SCHEMA,
    nummer: SCHEMA,
    lijst: Array.isArray(MIGRATIES),
    nieuw: defaultState().schema,
    oplopend: MIGRATIES.every((m, i) => m.naar === i + 2),
    hoogste: MIGRATIES.length ? MIGRATIES[MIGRATIES.length - 1].naar : 1
  }));
  ok(basis.schema === 'number', 'er is een SCHEMA-nummer');
  ok(basis.lijst, 'en een lijst MIGRATIES');
  ok(basis.nieuw === basis.nummer, 'een nieuw profiel begint op het huidige nummer');
  ok(basis.oplopend, 'de migraties lopen op zonder gaten, vanaf 2');
  ok(basis.hoogste === basis.nummer, 'SCHEMA is gelijk aan de laatste migratie: ' + basis.hoogste + ' vs ' + basis.nummer);

  // Een profiel van vóór vandaag: geen nummer, dus schema 1, dus alles draait nog.
  const oud = await page.evaluate(() => {
    const vuil = { txp: 500, comp: { luisteren: {}, schrijven: {} } };
    for (let i = 1; i <= 12; i++) vuil.comp.luisteren['s' + i] = true;
    vuil.comp.luisteren[AUDICIONES[0].id] = true;
    const na = normaliseerState(vuil);
    return { schema: na.schema, over: Object.keys(na.comp.luisteren).length, txp: na.txp };
  });
  ok(oud.schema === basis.nummer, 'een state zonder nummer wordt bijgewerkt tot het huidige: ' + oud.schema);
  ok(oud.over === 1, 'en de migratie heeft echt gedraaid: ' + oud.over + ' sleutel over');
  ok(oud.txp === 500, 'zonder iets anders aan te raken');

  // De valkuil: de defaults mogen het nummer niet invullen voordat het gelezen is.
  const valkuil = await page.evaluate(() => {
    const vuil = { txp: 1, comp: { luisteren: { s1: true, s2: true }, schrijven: {} } };
    return Object.keys(normaliseerState(vuil).comp.luisteren).length;
  });
  ok(valkuil === 0, 'defaultState() verklaart een oude state niet stiekem bij: ' + valkuil + ' sleutels over');

  // Al bij: niets meer doen.
  const bij = await page.evaluate(() => {
    const al = { schema: SCHEMA, comp: { luisteren: { rommel: true }, schrijven: {} } };
    const gedaan = migreer(al);
    return { gedaan: gedaan.length, over: Object.keys(al.comp.luisteren).length };
  });
  ok(bij.gedaan === 0, 'een profiel dat al bij is draait geen enkele migratie');
  ok(bij.over === 1, 'en er wordt dus ook niets aangeraakt');

  // Een migratie die klapt: de ketting stopt en het nummer blijft staan.
  const stuk = await page.evaluate(() => {
    const bewaard = MIGRATIES.slice();
    MIGRATIES.push({ naar: SCHEMA + 1, wat: 'proef die klapt', doe: function () { throw new Error('boem'); } });
    MIGRATIES.push({ naar: SCHEMA + 2, wat: 'proef die daarna niet mag draaien', doe: function (s) { s.stiekem = 1; return 1; } });
    const st = { schema: SCHEMA };
    const gedaan = migreer(st);
    MIGRATIES.length = 0;
    bewaard.forEach((m) => MIGRATIES.push(m));
    return { schema: st.schema, gedaan: gedaan.length, stiekem: !!st.stiekem };
  });
  ok(stuk.schema === basis.nummer, 'na een klapper blijft het nummer staan, dus het wordt opnieuw geprobeerd');
  ok(stuk.gedaan === 0, 'de geklapte migratie telt niet als gedaan');
  ok(stuk.stiekem === false, 'en de migratie erna draait niet op een halfverbouwde state');

  // Idempotent: twee keer draaien mag niets kapotmaken (profielen staan op meerdere apparaten).
  const twee = await page.evaluate(() => {
    const vuil = { comp: { luisteren: { s1: true }, schrijven: {} } };
    vuil.comp.luisteren[AUDICIONES[0].id] = true;
    const een = normaliseerState(vuil);
    const eersteAantal = Object.keys(een.comp.luisteren).length;
    een.schema = 1;                       // alsof een ander apparaat een oudere kopie terugstuurt
    const twee = normaliseerState(een);
    return { eersteAantal, tweedeAantal: Object.keys(twee.comp.luisteren).length };
  });
  ok(twee.eersteAantal === 1 && twee.tweedeAantal === 1, 'twee keer draaien geeft hetzelfde resultaat');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
