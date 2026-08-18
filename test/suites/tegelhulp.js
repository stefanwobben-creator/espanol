// tegelhulp.js (16 aug, v23.124) — GEEN suite. De poort pakt alleen pw-*.js, dit is een hulpbestand.
//
// WAAROM DIT ER IS
//
// Sinds v23.124 wonen de tegels niet meer allemaal op hetzelfde scherm: wie gram:true draagt staat
// op de Grammatica-tab, de rest in de Speeltuin. Vijf suites deden "klik op de Speeltuin-tab, klik
// dan op #ftLes", en die vielen alle vijf om.
//
// De verleiding is om in elke suite een regel te zetten die weet welke tegel waar staat. Dat is
// precies het patroon uit de kop van padvul.js: vier keer in twee dagen viel een suite om omdat
// testcode een feit napraatte dat al in de data stond. Daarom vraagt dit bestand het aan de app:
// spelInfo() weet waar de tegel woont, en de suite hoeft er niets van te weten.
//
//   const { naarTegel } = require('./tegelhulp.js');
//   const n = await naarTegel(page, 'ftLes');   // naar de goede tab, en klikken
//   const n = await naarTegelTab(page, 'ftBrok', false);  // alleen naar de goede tab
//
// Geeft terug hoe vaak de tegel op het scherm stond (0 of 1), zodat de suite dat kan blijven eisen.

async function naarTegelTab(page, id, klik) {
  const gram = await page.evaluate((i) => {
    const g = spelInfo().filter((x) => x.id === i)[0];
    return g ? !!g.gram : false;
  }, id);

  await page.evaluate(() => { funView = null; });
  if (gram) {
    await page.evaluate(() => { gwSess = null; gcLeesId = null; show('spiekbrief'); });
  } else {
    await page.click('#nav button[data-tab="speeltuin"]');
    await page.waitForTimeout(250);
    await page.evaluate(() => { funView = null; renderFun(); });
  }
  await page.waitForTimeout(250);

  const n = await page.locator('#' + id).count();
  if (n && klik !== false) {
    await page.click('#' + id);
    await page.waitForTimeout(300);
  }
  return n;
}

async function naarTegel(page, id) { return naarTegelTab(page, id, true); }

module.exports = { naarTegel, naarTegelTab };
