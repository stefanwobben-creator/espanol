// De poort. Draait de regressiekern tegen de index.html die in deze map staat en geeft exit 1
// zodra er iets rood is. Alles wat langs deze poort komt mag live; wat er niet langs komt, niet.
//
// Waarom een eigen runner en geen playwright test-runner: de suites zijn losse node-programma's die
// zelf hun browser starten en zelf hun uitkomst printen. Ze omschrijven naar @playwright/test zou
// 34 bestanden aanpassen en dus 34 kansen op een stille gedragsverandering geven. De poort behandelt
// ze daarom als wat ze zijn: programma's die exit 0 of exit 1 geven.
//
//   node test/poort.js                 alles
//   node test/poort.js --deel 2/4      alleen het tweede kwart (voor de matrix in CI)
//   node test/poort.js pw-taal.js      alleen deze suite
//
// De suites vragen om http://localhost:8321/espanol-stefan.html. In de repo heet dat bestand
// index.html. De server hieronder vertaalt dat ene pad; verder serveert hij gewoon de repo.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const WORTEL = path.resolve(__dirname, '..');
const SUITES = path.join(__dirname, 'suites');
// De suites maken screenshots met een pad zonder map ernaast. Die horen niet tussen de broncode,
// en bij een rode run wil je ze juist wel kunnen bekijken. Dus draaien ze in een eigen uitvoermap,
// die in CI als artefact wordt bewaard en lokaal in .gitignore staat.
const WERK = path.join(__dirname, 'uitvoer');
// Voor elke suite ingeladen: breekt elk verzoek af dat niet naar de eigen testserver gaat. Zie
// geenserver.js voor waarom de poort anders rood wordt zodra de machine toevallig internet heeft.
const AFSCHERMING = path.join(__dirname, 'geenserver.js');
const POORT = 8321;
const TIJD = 240000;
const TEGELIJK = Number(process.env.TEGELIJK || 4);

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.ogg': 'audio/ogg'
};

// De naam waaronder de app historisch in de tests staat. Eén alias, geen kopie op schijf: een kopie
// kan verouderen en dan test je stilletjes een ander bestand dan je publiceert.
const ALIAS = { '/espanol-stefan.html': 'index.html' };

function server() {
  return new Promise((klaar, mis) => {
    const s = http.createServer((req, res) => {
      const schoon = decodeURIComponent(req.url.split('?')[0]);
      const rel = ALIAS[schoon] || schoon.replace(/^\/+/, '') || 'index.html';
      const p = path.join(WORTEL, rel);
      if (!p.startsWith(WORTEL)) { res.writeHead(403); return res.end('nee'); }
      fs.readFile(p, (e, d) => {
        if (e) { res.writeHead(404); return res.end('niet gevonden: ' + rel); }
        res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
        res.end(d);
      });
    });
    s.on('error', mis);
    s.listen(POORT, '127.0.0.1', () => klaar(s));
  });
}

function kies() {
  const args = process.argv.slice(2);
  const los = args.filter((a) => /\.js$/.test(a));
  let alles = fs.readdirSync(SUITES).filter((f) => /^pw-.*\.js$/.test(f)).sort();
  if (los.length) return alles.filter((f) => los.indexOf(f) !== -1);
  const d = args.indexOf('--deel');
  if (d !== -1 && args[d + 1]) {
    const [n, van] = args[d + 1].split('/').map(Number);
    // om de beurt uitdelen in plaats van in blokken: de trage suites staan niet netjes verspreid
    // over het alfabet, en anders trekt één shard alle lange runs.
    alles = alles.filter((_, i) => i % van === n - 1);
  }
  return alles;
}

(async () => {
  fs.mkdirSync(WERK, { recursive: true });
  const s = await server();
  const suites = kies();
  console.log('poort :: ' + suites.length + ' suites, ' + TEGELIJK + ' tegelijk\n');

  const uit = [];
  let i = 0;
  function volgende() {
    if (i >= suites.length) return Promise.resolve();
    const f = suites[i++];
    const t0 = Date.now();
    return new Promise((res) => {
      execFile('node', [path.join(SUITES, f)],
        { cwd: WERK, timeout: TIJD, maxBuffer: 64 * 1024 * 1024,
          env: Object.assign({}, process.env, {
            NODE_OPTIONS: ((process.env.NODE_OPTIONS || '') + ' --require ' + AFSCHERMING).trim()
          }) },
        (err, so, se) => {
          const sec = Math.round((Date.now() - t0) / 1000);
          const groen = !err;
          uit.push({ f, groen, sec, so, se, timeout: !!(err && err.killed) });
          console.log((groen ? '  groen  ' : '  ROOD   ') + f.padEnd(26) + sec + 's');
          res();
        });
    }).then(volgende);
  }
  await Promise.all(Array.from({ length: TEGELIJK }, volgende));
  s.close();

  const rood = uit.filter((u) => !u.groen);
  if (rood.length) {
    console.log('\n================ wat er rood is ================');
    rood.forEach((r) => {
      console.log('\n--- ' + r.f + (r.timeout ? ' (liep vast, ' + r.sec + 's)' : '') + ' ---');
      const regels = (r.so || '').split('\n');
      const raak = regels.filter((l) => /✗|FAIL|GEFAALD|Error|error:/.test(l));
      console.log((raak.length ? raak : regels.slice(-25)).slice(-25).join('\n'));
      if (r.se) console.log((r.se || '').split('\n').slice(-8).join('\n'));
    });
  }
  const sec = uit.reduce((a, b) => a + b.sec, 0);
  console.log('\n' + (uit.length - rood.length) + '/' + uit.length + ' groen, ' + sec + 's rekentijd');
  console.log(rood.length ? 'POORT DICHT: ' + rood.map((r) => r.f).join(', ') : 'POORT OPEN');
  process.exit(rood.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
