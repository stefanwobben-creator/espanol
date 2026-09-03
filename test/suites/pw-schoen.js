// pw-schoen.js (16 aug, v23.125) — zijn de 22 onregelmatige echt zes patronen, en kan de les ze aan?
//
// WAAROM DIT ER IS
//
// Stefan vroeg wat het beste is om Spaans te leren, bij de vraag waar de presente-route moet
// beginnen. Ik dacht "de -er/-ir-uitgangen" of "toegepaste zinnen". Doorrekenen gaf iets anders:
// 22 van de 33 werkwoorden zijn onregelmatig in het presente, en die 22 zijn zes patronen. Daar
// zit de massa, en het zijn de frequentste werkwoorden die er zijn.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE REKENSOM KLOPT. 11 regelmatig, 22 onregelmatig, en elk van die 22 zit in minstens één
//      rij. Valt er één buiten, dan belooft de app een systeem dat een gat heeft.
//   2. HET IS UITGEREKEND EN NIET OPGESCHREVEN. Een verzonnen werkwoord met een e→ie-schoen moet
//      zichzelf in de goede rij sorteren, zonder dat er ergens een lijst bijgewerkt wordt. Dit is
//      de controle die zegt of punt 1 iets waard is.
//   3. DE LES KAN ELKE RIJ AAN. Alle zes de stappen, met de goede antwoorden, voor elke rij die
//      lesRijIds() aanbiedt. Een rij die de les niet kan draaien is een dode knop.
//   4. DE VOORTGANG STAAT ONDER DE RIJ. les.schoen.ie en niet les.presente, anders zouden een tijd
//      en een patroon elkaars vinkje zetten.
//   5. DE OVERDRACHTSSTAP BLIJFT IN DE RIJ. Stap 6 toetst of je het patroon kent en niet of je
//      querer kent, dus moet hij werkwoorden uit dezelfde rij pakken en nooit het leswerkwoord.
//   6. DE MENGRIJ MENGT ECHT (v23.127). Stap 7 van de presente-route is "de zes door elkaar", en
//      dan moet élke vraagstap uit de pool van 22 trekken in plaats van uit één modelwerkwoord.
//      Een mengrij die stiekem hetzelfde werkwoord blijft vragen is geen interleaving.
//   7. HET SCHERM TOONT DE TABEL VAN DE OPGAVE. Stond fout sinds v23.115 en viel niet op omdat bij
//      een gewone rij het leswerkwoord én het opgavewerkwoord hetzelfde zijn.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwSch' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    S.lang = 'nl'; S.speelAlles = true;
    /* v23.234: deze suite gaat over de oefening en niet over de tijdpoort. Die poort houdt een
       ongelezen tijd tegen (zie pw-focus), en zonder dit zou elke proef hieronder de poort meten. */
    S.tijdGelezen = {}; (typeof TIJDEN !== 'undefined' ? TIJDEN : []).forEach(function (t) { S.tijdGelezen[t.id] = today(); });
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    try { persist(); } catch (e) {}
  });

  // ---- 1. de rekensom ----
  const som = await page.evaluate(() => {
    /* v23.227: alleen de rijen van het presente. Sinds die versie heeft het indefinido zijn eigen
       zes rijen, en deze rekensom gaat over de 22 onregelmatige VAN HET PRESENTE. Zonder deze
       grens telt hij leer mee als "regelmatig werkwoord in een rij", terwijl leer regelmatig is in
       het presente en onregelmatig in het indefinido. */
    const rijen = {};
    CONJ_PATRONEN.filter((p) => conjPatroonTijd(p) === 'presente')
      .forEach((p) => { rijen[p.id] = conjPatroonPool(p.id).map((v) => v.inf); });
    const reg = VERBOS.filter((v) => conjPatroon(v).regelmatig).map((v) => v.inf);
    const onreg = VERBOS.filter((v) => !conjPatroon(v).regelmatig).map((v) => v.inf);
    const gedekt = {};
    Object.keys(rijen).forEach((k) => rijen[k].forEach((i) => { gedekt[i] = (gedekt[i] || 0) + 1; }));
    return {
      rijen, n: VERBOS.length, reg: reg.length, onreg: onreg.length,
      ongedekt: onreg.filter((i) => !gedekt[i]),
      // een regelmatig werkwoord hoort in géén rij te staan
      teVeel: reg.filter((i) => gedekt[i]),
      dubbel: Object.keys(gedekt).filter((i) => gedekt[i] > 1)
    };
  });

  console.log('\n-- DE REKENSOM --');
  ok(som.reg + som.onreg === som.n,
    'alle ' + som.n + ' werkwoorden zijn ingedeeld (' + som.reg + ' regelmatig, ' + som.onreg + ' niet)');
  ok(som.onreg === 22, 'tweeëntwintig onregelmatige in het presente (nu: ' + som.onreg + ')');
  ok(Object.keys(som.rijen).length === 6, 'zes presente-rijen (nu: ' + Object.keys(som.rijen).length + ')');
  ok(som.ongedekt.length === 0,
    'DE REGEL: elke onregelmatige zit in minstens één rij (buiten de boot: ' + (som.ongedekt.join(', ') || 'geen') + ')');
  ok(som.teVeel.length === 0,
    'CONTROLE: en geen enkele regelmatige staat in een rij (' + (som.teVeel.join(', ') || 'geen') + ')');
  ok(som.dubbel.length === 3,
    'drie werkwoorden staan in twee rijen, want die hebben allebei (' + som.dubbel.join(', ') + ')');
  Object.keys(som.rijen).forEach((k) => {
    ok(som.rijen[k].length > 0, k + ': ' + som.rijen[k].length + ' (' + som.rijen[k].join(', ') + ')');
  });

  // ---- 2. uitgerekend, niet opgeschreven ----
  // Een verzonnen werkwoord met een e→ie-schoen hoort zichzelf in te sorteren. Staat het patroon
  // ergens als lijst, dan valt dit werkwoord er stilletjes buiten en gaat deze meting rood.
  const verzonnen = await page.evaluate(() => {
    const nep = {inf:'merlar', nl:'merlen', en:'to merl',
                 presente:['mierlo','mierlas','mierla','merlamos','merláis','mierlan']};
    const netjes = {inf:'zomper', nl:'zompen', en:'to zomp',
                    presente:['zompo','zompes','zompe','zompemos','zompéis','zompen']};
    VERBOS.push(nep, netjes);
    const uit = {
      nep: conjPatroonPool('schoen.ie').map((v) => v.inf).indexOf('merlar') !== -1,
      nepPatroon: conjPatroon(nep),
      netjes: conjPatroon(netjes).regelmatig,
      inRij: CONJ_PATRONEN.filter((p) => conjPatroonTijd(p) === 'presente')
               .filter((p) => conjPatroonPool(p.id).some((v) => v.inf === 'zomper')).length
    };
    VERBOS.splice(VERBOS.length - 2, 2);
    return uit;
  });

  console.log('\n-- CONTROLE: uitgerekend, niet opgeschreven --');
  ok(verzonnen.nep === true,
    'DE REGEL: een verzonnen werkwoord met een e→ie-schoen sorteert zichzelf in schoen.ie');
  ok(verzonnen.nepPatroon.wissel === 'ie' && verzonnen.nepPatroon.yo === null,
    'en het leest de wissel goed af (' + JSON.stringify(verzonnen.nepPatroon) + ')');
  ok(verzonnen.netjes === true && verzonnen.inRij === 0,
    'CONTROLE: een verzonnen regelmatig werkwoord komt in géén enkele rij');

  // ---- 3, 4, 5. de les draait elke rij ----
  const rijen = await page.evaluate(() => lesRijIds());
  console.log('\n-- de les, per rij (' + rijen.length + ') --');

  const uitslag = await page.evaluate(() => {
    const uit = [];
    lesRijIds().forEach((id) => {
      S.brok = {};
      const start = lesStart(id);
      if (!start) { uit.push({id, gestart:false}); return; }
      const r = lesRij(id);
      const overWw = {}, overP = {};
      let veilig = 0;
      /* 22 aug, v23.173: deze lus deed lesSpel.i++ zonder lesSpel.gekozen leeg te maken, en
         lesAntwoord() keert meteen terug zolang er al iets gekozen is. Elke stap werd dus één keer
         beantwoord en daarna vijf keer voor niets. Dat viel niet op zolang niemand naar de score
         keek; sinds v23.173 zet de laatste stap een terugkeerdatum op basis van goed en fout, en
         toen bleek de simulatie een stap uit te spelen die de app zo nooit uitspeelt. De knop in de
         app doet i++ én gekozen = null; hier nu ook. */
      while (lesSpel && lesSpel.stap < LES_STAPPEN.length && veilig++ < 400) {
        const stapId = lesStapId(lesSpel.stap);
        if (stapId === 'ontmoeten' || stapId === 'opbouwen') { lesStapAf(); lesSpel.stap++; lesSpel.i = 0; continue; }
        const q = lesOpgaveNu();
        if (!q) { lesStapAf(); lesSpel.stap++; lesSpel.i = 0; lesSpel.goed = 0; lesSpel.over = null; continue; }
        if (stapId === 'overdracht') { overWw[q.v.inf] = 1; overP[q.p] = 1; }
        lesAntwoord(conjVorm(q.v, q.p, lesSpel.t));
        lesSpel.i++; lesSpel.gekozen = null;   // zie de noot boven de eerste lus
        if (lesSpel.i >= lesOpgaven(lesSpel.stap)) {
          lesStapAf();
          lesSpel.stap++; lesSpel.i = 0; lesSpel.goed = 0; lesSpel.opties = null; lesSpel.over = null;
        }
      }
      const st = brokLees(lesId(id));
      uit.push({
        id, gestart: true, tijd: r.tijd, mix: !!r.mix, model: r.v.inf, t: r.t,
        klaar: lesKlaar(id), stapMax: st.stapMax,
        sleutels: Object.keys(S.brok),
        overWw: Object.keys(overWw), overP: Object.keys(overP).length,
        pool: r.tijd ? null : conjPatroonPool(id).map((v) => v.inf)
      });
      lesSpel = null;
    });
    return uit;
  });

  // v23.127: een mengrij is ook geen tijd, maar hij put uit alle zes en heeft dus zijn eigen
  // meting verderop. Deze blokken gaan over de zes patroonrijen.
  const patronen = uitslag.filter((u) => u.tijd === false && !u.mix && u.t === 'presente');
  ok(uitslag.every((u) => u.gestart), 'elke rij start (' + uitslag.filter((u) => !u.gestart).map((u) => u.id).join(', ') + ')');
  ok(uitslag.every((u) => u.klaar),
    'DE REGEL: elke rij loopt alle ' + (await page.evaluate(() => LES_STAPPEN.length)) + ' stappen uit (mis: ' +
    (uitslag.filter((u) => !u.klaar).map((u) => u.id).join(', ') || 'geen') + ')');
  ok(patronen.length === 6, 'zes daarvan zijn een presente-patroon (nu: ' + patronen.length + ')');
  /* v23.227: hier stond "een patroonles staat altijd in het presente". Dat was waar zolang er geen
     andere tijd rijen had, en het was precies de aanname die het bouwen ervan blokkeerde. Wat er nu
     staat is de regel die overblijft: een patroonrij staat in een tijd die ook echt open is, en
     nooit in "mix". */
  const indefRijen = uitslag.filter((u) => u.tijd === false && !u.mix && u.t !== 'presente');
  ok(indefRijen.length > 0, 'en er zijn ook patroonrijen in een andere tijd (' + indefRijen.length + ')');
  ok(indefRijen.every((u) => u.t === 'indefinido'),
    'die allemaal in het indefinido staan (' + indefRijen.map((u) => u.t).join(', ') + ')');

  console.log('\n-- de voortgang staat onder de rij --');
  uitslag.forEach((u) => {
    ok(u.sleutels.indexOf('les.' + u.id) !== -1,
      u.id + ' → ' + u.sleutels.join(', '));
  });
  ok(uitslag.every((u) => u.sleutels.length === 1),
    'DE REGEL: één rij zet precies één vinkje, dus een tijd en een patroon lopen elkaar niet in de weg');

  console.log('\n-- de overdrachtsstap blijft in de rij --');
  const buiten = patronen.filter((u) => u.overWw.some((w) => u.pool.indexOf(w) === -1));
  const eigen = patronen.filter((u) => u.overWw.indexOf(u.model) !== -1);
  ok(patronen.every((u) => u.overWw.length > 0),
    'elke patroonrij heeft werkwoorden voor stap ' + (await page.evaluate(() => LES_STAPPEN.length)));
  ok(buiten.length === 0,
    'DE REGEL: stap 6 pakt alleen werkwoorden uit dezelfde rij (buiten: ' +
    (buiten.map((u) => u.id + ': ' + u.overWw.join('/')).join(', ') || 'geen') + ')');
  ok(eigen.length === 0,
    'en nooit het leswerkwoord zelf, want dan meet hij niets nieuws (' +
    (eigen.map((u) => u.id).join(', ') || 'geen') + ')');

  // ---- de mengrij ----
  const mix = await page.evaluate(() => {
    const uit = [];
    LES_MIXRIJEN.forEach((m) => {
      const r = lesRij(m.id);
      if (!r) { uit.push({ id: m.id, bestaat: false }); return; }
      S.brok = {};
      lesStart(m.id);
      const perStap = {}, alle = {};
      let veilig = 0;
      while (lesSpel && lesSpel.stap < LES_STAPPEN.length && veilig++ < 400) {
        const id = lesStapId(lesSpel.stap);
        if (id === 'ontmoeten' || id === 'opbouwen') { lesStapAf(); lesSpel.stap++; lesSpel.i = 0; continue; }
        const q = lesOpgaveNu();
        if (!q) { lesStapAf(); lesSpel.stap++; lesSpel.i = 0; lesSpel.goed = 0; lesSpel.over = null; continue; }
        (perStap[id] = perStap[id] || {})[q.v.inf] = 1;
        alle[q.v.inf] = 1;
        // buiten de pool zou betekenen dat de mengrij ergens anders uit put
        if (!m.pool().some((w) => w.inf === q.v.inf)) alle['BUITEN:' + q.v.inf] = 1;
        lesAntwoord(conjVorm(q.v, q.p, lesSpel.t));
        lesSpel.i++; lesSpel.gekozen = null;   // zie de noot boven de eerste lus
        if (lesSpel.i >= lesOpgaven(lesSpel.stap)) {
          lesStapAf();
          lesSpel.stap++; lesSpel.i = 0; lesSpel.goed = 0; lesSpel.opties = null; lesSpel.over = null;
        }
      }
      uit.push({
        id: m.id, bestaat: true, mix: !!r.mix, pool: m.pool().length,
        klaar: lesKlaar(m.id), sleutels: Object.keys(S.brok),
        alle: Object.keys(alle).length,
        buiten: Object.keys(alle).filter((k) => k.indexOf('BUITEN:') === 0),
        perStap: Object.keys(perStap).map((k) => ({ stap: k, n: Object.keys(perStap[k]).length }))
      });
      lesSpel = null;
    });
    return uit;
  });

  console.log('\n-- de mengrij --');
  ok(mix.length > 0 && mix.every((m) => m.bestaat), 'er is ' + mix.length + ' mengrij');
  mix.forEach((m) => {
    ok(m.mix === true, m.id + ' draagt mix:true');
    ok(m.pool === som.onreg,
      m.id + ' put uit alle ' + som.onreg + ' onregelmatige (nu: ' + m.pool + ')');
    ok(m.klaar === true, m.id + ' loopt alle stappen uit');
    ok(m.sleutels.length === 1 && m.sleutels[0] === 'les.' + m.id,
      'en zet zijn eigen vinkje (' + m.sleutels.join(', ') + ')');
    ok(m.buiten.length === 0,
      'CONTROLE: geen werkwoord van buiten de pool (' + (m.buiten.join(', ') || 'geen') + ')');
    const eenVerb = m.perStap.filter((x) => x.n < 2);
    ok(eenVerb.length === 0,
      'DE REGEL: élke vraagstap mengt echt, ook de eerste (' +
      m.perStap.map((x) => x.stap + ':' + x.n).join(', ') + ')');
    ok(m.alle >= 8, 'over één doorloop zie je ' + m.alle + ' verschillende werkwoorden');
  });

  // ---- het scherm toont de tabel van de opgave, niet van het leswerkwoord ----
  const tabel = await page.evaluate(() => {
    S.brok = {};
    lesStart('presente.mix');
    lesSpel.stap = LES_STAPPEN.map((x) => x.id).indexOf('gat');
    lesSpel.i = 0; lesSpel.over = null;
    funView = 'les'; show('speeltuin', true);
    const q = lesOpgaveNu();
    const kaart = document.getElementById('funCard').innerText;
    const vormen = conjAlleVormen(q.v, lesSpel.t);
    const model = lesSpel.v;
    return {
      opgave: q.v.inf, model: model.inf,
      noemtOpgave: kaart.indexOf(q.v.inf) !== -1,
      // minstens één vorm van het opgavewerkwoord staat in de tabel
      tabelKlopt: vormen.some((f) => kaart.indexOf(f) !== -1)
    };
  });
  console.log('\n-- de tabel hoort bij de opgave --');
  ok(tabel.noemtOpgave === true,
    'het scherm noemt het werkwoord van de opgave (' + tabel.opgave + ')');
  ok(tabel.tabelKlopt === true,
    'DE REGEL: en de tabel is die van ' + tabel.opgave + ', niet van het leswerkwoord ' + tabel.model);

  // ---- het modelwerkwoord ----
  // tener stond vooraan in schoen.ie en heeft óók een yo op -go, dus deed een les over e → ie zijn
  // voorbeeld met "tengo". Dat is het tegenvoorbeeld. Het model mag in maar één rij staan.
  const model = await page.evaluate(() => CONJ_PATRONEN.map((p) => {
    const v = conjPatroonModel(p.id), t = conjPatroonTijd(p);
    // v23.227: per tijd geteld, want "in hoeveel rijen sta je" is een vraag binnen één tijd
    return { id: p.id, inf: v ? v.inf : null, rijen: v ? conjPatroonAantal(v, t) : 0,
             kanEnkel: conjPatroonPool(p.id).some((w) => conjPatroonAantal(w, t) === 1) };
  }));
  console.log('\n-- het modelwerkwoord --');
  model.forEach((m) => ok(m.rijen === 1 || !m.kanEnkel,
    m.id + ' doet het voor met ' + m.inf + ' (in ' + m.rijen + ' rij' + (m.rijen === 1 ? '' : 'en') + ')'));
  ok(model.every((m) => m.rijen === 1 || !m.kanEnkel),
    'DE REGEL: het voorbeeld van een patroon heeft dat patroon en geen tweede');

  // ---- het keuzescherm ----
  await page.evaluate(() => { lesSpel = null; funView = 'les'; show('speeltuin', true); });
  await page.waitForTimeout(300);
  const keuze = await page.evaluate(() => ({
    knoppen: document.querySelectorAll('.les-t').length,
    kop: document.querySelectorAll('#lesPatroonKop').length,
    tekst: document.getElementById('funCard').innerText
  }));

  console.log('\n-- het keuzescherm --');
  ok(keuze.knoppen === rijen.length,
    'één knop per rij (' + keuze.knoppen + ' van de ' + rijen.length + ')');
  ok(keuze.kop === 1, 'de patronen staan onder een eigen kopje, zodat ze niet als zesde tijd lezen');
  ok(/bota/.test(keuze.tekst), 'en de schoen staat er met zijn Spaanse naam bij');

  // ---- de terugknop belooft de goede plek ----
  const label = await page.evaluate(() => {
    lesSpel = null; funView = 'les'; show('speeltuin', true);
    const gram = (document.getElementById('btnFunTerug') || {}).innerText || '';
    funView = 'letras'; ltSpel = null; show('speeltuin', true);
    const spel = (document.getElementById('btnFunTerug') || {}).innerText || '';
    return { gram, spel };
  });
  console.log('\n-- de terugknop --');
  ok(/Grammatica|Grammar/.test(label.gram),
    'DE REGEL: op een grammatica-scherm belooft hij Grammatica ("' + label.gram.trim() + '")');
  ok(/Speeltuin|Playground/.test(label.spel),
    'CONTROLE: op een spel belooft hij nog steeds de Speeltuin ("' + label.spel.trim() + '")');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
