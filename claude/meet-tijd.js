// De nameting bij punt 6 uit claude/rapport.md (v23.38). Geen suite en dus geen onderdeel van de
// poort: een meetprogramma dat zegt hoeveel van de kloktijd de app opschrijft en waar de rest blijft.
// Draaien met de testserver van de poort ernaast:
//
//   node test/poort.js pw-schema.js     (of een eigen servertje op 8321)
//   CHROMIUM=<pad> node claude/meet-tijd.js
//
const { chromium } = require('playwright');
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  page.on('pageerror', e => console.log('PAGEERROR ' + e));
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({overgeslagen:true})); } catch(e){} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Meet' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => { S.lang='nl'; S.tour=true; try{persist();}catch(e){} const w=document.getElementById('tourWrap'); if(w&&w.remove) w.remove(); });

  // 1. Wat meet trackTijd van een reeks antwoorden met bekende gaten?
  const m1 = await page.evaluate(async () => {
    const wacht = ms => new Promise(r => setTimeout(r, ms));
    const d = today();
    S.dagStats = {}; tijdLaatst = 0;
    const gaten = [3000, 3000, 3000, 3000, 3000];   // vijf gaten van 3 s tussen zes antwoorden
    trackPoging(false);                              // eerste antwoord van de sessie
    for (const g of gaten) { await wacht(g); trackPoging(false); }
    const klok = gaten.reduce((a,b)=>a+b,0);
    return { klokSec: klok/1000, gemeten: (S.dagStats[d]||{}).sec || 0, pog: (S.dagStats[d]||{}).pogingen || 0 };
  });
  console.log('A. zes antwoorden, vijf gaten van 3 s:');
  console.log('   klok tussen eerste en laatste antwoord: ' + m1.klokSec + ' s, opgeschreven: ' + m1.gemeten + ' s, pogingen: ' + m1.pog);

  // 2. Wat gebeurt er met een gat langer dan twee minuten?
  const m2 = await page.evaluate(() => {
    const d = today();
    S.dagStats = {}; tijdLaatst = 0;
    // handmatig de klok terugzetten in plaats van echt wachten
    trackPoging(false);                       // tijdLaatst = nu
    tijdLaatst = Date.now() - 130000;         // alsof het vorige antwoord 130 s geleden was
    trackPoging(false);
    const na1 = (S.dagStats[d]||{}).sec || 0;
    tijdLaatst = Date.now() - 110000;         // en nu een gat van 110 s
    trackPoging(false);
    return { na130: na1, na110: ((S.dagStats[d]||{}).sec || 0) - na1 };
  });
  console.log('B. een gat van 130 s levert ' + m2.na130 + ' s op, een gat van 110 s levert ' + m2.na110 + ' s op.');

  // 3. Hoeveel sessies per dag kosten hoeveel? tijdLaatst begint bij elke paginalading op 0.
  const m3 = await page.evaluate(() => {
    const d = today();
    S.dagStats = {}; tijdLaatst = 0;
    let n = 0;
    for (let s = 0; s < 3; s++) {           // drie sessies van vier antwoorden, gaten van 10 s
      tijdLaatst = 0;                        // nieuwe paginalading
      for (let i = 0; i < 4; i++) {
        if (i > 0) tijdLaatst = Date.now() - 10000;
        trackPoging(false); n++;
      }
    }
    return { pog: n, gemeten: (S.dagStats[d]||{}).sec || 0 };
  });
  console.log('C. drie sessies van vier antwoorden met gaten van 10 s: klok tussen eerste en laatste per sessie 30 s, dus 90 s totaal; opgeschreven: ' + m3.gemeten + ' s.');

  // 4. Welke schermen tellen mee? Tel de knoppen die wel/niet op een nagekeken antwoord uitkomen.
  await page.evaluate(() => { S.dagStats = {}; tijdLaatst = 0; });
  console.log('D. zie de codetelling hieronder (grep), niet in de browser te meten.');

  await browser.close();
})();
