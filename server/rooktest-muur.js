// Rooktest voor v22.5: draait de ECHTE queries uit server/index.js tegen een echte Postgres.
// Wat hier bewezen moet worden: de groep levert de muurvelden, de krabbel van een groepslid mag,
// die van een buitenstaander niet, en de dag wordt geklemd op gisteren..vandaag.
const { Pool } = require('pg');
const pool = new Pool({ connectionString: 'postgres://postgres:p@localhost:5432/vamostest' });

function muurVelden(st) {
  return {
    woorden: Object.keys((st && st.srs) || {}).length,
    mijlpalen: (st && st.mijlpalen) || {},
    wear: (st && st.wear) || {},
    baile: (st && st.baile) || null,
    bailes: (st && st.bailes) || [],
    oogst: oogstKort((st && st.oogst) || {}),
  };
}
function oogstKort(o) {
  const vandaag = new Date().toISOString().slice(0, 10);
  const gisteren = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  const uit = {};
  if (o[vandaag]) uit[vandaag] = o[vandaag];
  if (o[gisteren]) uit[gisteren] = o[gisteren];
  return uit;
}
let fails = 0;
const ok = (c, n) => { console.log(c ? 'PASS' : 'FAIL', n); if (!c) fails++; };

(async () => {
  await pool.query(`
    DROP TABLE IF EXISTS krabbels, group_members, groups, profiles;
    CREATE TABLE profiles (code text PRIMARY KEY, name text NOT NULL, track text NOT NULL,
      state jsonb NOT NULL DEFAULT '{}'::jsonb, updated_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE groups (gcode text PRIMARY KEY, naam text NOT NULL);
    CREATE TABLE group_members (gcode text NOT NULL, pcode text NOT NULL, PRIMARY KEY (gcode, pcode));
    CREATE TABLE krabbels (van text NOT NULL, naar text NOT NULL, sleutel text NOT NULL,
      dag date NOT NULL DEFAULT current_date, created_at timestamptz NOT NULL DEFAULT now(),
      PRIMARY KEY (van, naar, dag));`);

  const vandaagStr = new Date().toISOString().slice(0,10);
  const oudStr = '2020-05-05';
  const stefan = { oogst: { [vandaagStr]: {w:5, z:18}, [oudStr]: {w:9, z:9} },
                   txp: 5200, srs: {a:1,b:1,c:1}, mijlpalen: {'woorden-500':'2026-08-08','les-a2-8':'oud'},
                   wear: { sombrero: true }, baile: 'salsa', bailes: ['salsa','tango'], lessons: {'a2-8':{done:true}} };
  const ilona  = { txp: 340, srs: {a:1}, mijlpalen: {'woorden-100':'2026-08-08'}, wear: {}, baile: 'salsa', bailes: ['salsa'] };
  await pool.query("INSERT INTO profiles (code,name,track,state) VALUES ('c1','Stefan','a2',$1),('c2','Ilona','beginner',$2),('c3','Buiten','a2','{}')",
    [stefan, ilona]);
  await pool.query("INSERT INTO groups VALUES ('fam','Familie')");
  await pool.query("INSERT INTO group_members VALUES ('fam','c1'),('fam','c2')");

  // --- 1. de groep levert de muurvelden ---
  const r = await pool.query(
    "SELECT p.name, p.track, p.state FROM group_members m JOIN profiles p ON p.code = m.pcode WHERE m.gcode=$1", ['fam']);
  const spelers = r.rows.map((row) => Object.assign({ naam: row.name }, muurVelden(row.state || {})));
  const st = spelers.find((x) => x.naam === 'Stefan');
  ok(spelers.length === 2, 'twee leden, de buitenstaander zit er niet bij');
  ok(st.woorden === 3, 'woorden geteld uit srs');
  ok(st.wear.sombrero === true, 'wear komt mee');
  ok(st.baile === 'salsa', 'baile komt mee');
  ok(st.mijlpalen['woorden-500'] === '2026-08-08', 'mijlpalen komen mee, met datum');
  ok(JSON.stringify(spelers).indexOf('c1') === -1, 'geen sync-code in het antwoord');
  ok(st.oogst[vandaagStr] && st.oogst[vandaagStr].w === 5, 'de oogst van vandaag komt mee');
  ok(st.oogst[oudStr] === undefined, 'oude dagen worden eruit gefilterd, dat is dode last');

  // --- 2. krabbel binnen de groep mag, van buiten niet ---
  const leden = (await pool.query(
    "SELECT lower(p.name) AS naam FROM group_members m JOIN profiles p ON p.code=m.pcode WHERE m.gcode=$1", ['fam']
  )).rows.map((x) => x.naam);
  ok(leden.indexOf('stefan') >= 0 && leden.indexOf('ilona') >= 0, 'beide leden herkend');
  ok(leden.indexOf('buiten') === -1, 'de buitenstaander is geen lid, dus die mag niet krabbelen');

  const zet = (van, naar, sleutel, dag) => pool.query(
    `INSERT INTO krabbels (van, naar, sleutel, dag)
     VALUES ($1,$2,$3, GREATEST(LEAST(COALESCE($4::date, current_date), current_date), current_date - 1))
     ON CONFLICT (van, naar, dag) DO UPDATE SET sleutel = EXCLUDED.sleutel, created_at = now()
     RETURNING dag::text`, [van, naar, sleutel, dag || null]);

  ok((await zet('stefan','ilona','baile')).rows[0].dag === new Date().toISOString().slice(0,10), 'zonder dag wordt het vandaag');
  const gisteren = new Date(Date.now()-86400000).toISOString().slice(0,10);
  ok((await zet('stefan','ilona','ole', gisteren)).rows[0].dag === gisteren, 'gisteren mag');
  ok((await zet('stefan','ilona','ole','2020-01-01')).rows[0].dag === gisteren, 'ouder dan gisteren wordt naar gisteren getrokken');
  ok((await zet('stefan','ilona','ole','2099-01-01')).rows[0].dag === new Date().toISOString().slice(0,10), 'de toekomst wordt naar vandaag getrokken');

  // --- 3. terugleveren aan de muur: twee dagen, alleen binnen de groep ---
  await pool.query("INSERT INTO krabbels (van,naar,sleutel,dag) VALUES ('buiten','ilona','ole',current_date)");
  const kr = (await pool.query(
    `SELECT van, naar, sleutel, dag::text FROM krabbels
      WHERE dag >= current_date - 1 AND van = ANY($1) AND naar = ANY($1) ORDER BY created_at`,
    [['stefan','ilona']])).rows;
  ok(kr.length === 2, 'vandaag en gisteren komen mee, twee regels: ' + kr.length);
  ok(!kr.some((x) => x.van === 'buiten'), 'de krabbel van buiten de groep komt niet mee');
  // Een tweede reactie op dezelfde dag naar dezelfde persoon vervangt de eerste. Dat is geen bug maar
  // de vorm van de tabel, en hij past op de muur: daar staat ook precies een regel per persoon per dag.
  ok(kr.filter((x) => x.van === 'stefan' && x.naar === 'ilona').length === 2,
     'een regel voor vandaag en een voor gisteren, niet meer');
  const vandaagRegel = kr.find((x) => x.dag === new Date().toISOString().slice(0,10));
  ok(vandaagRegel.sleutel === 'ole', 'de laatste reactie van die dag vervangt de vorige');
  const opnieuw = await zet('ilona','stefan','baile');
  ok(opnieuw.rows[0].dag === new Date().toISOString().slice(0,10), 'het dansje is een geldige sleutel');

  await pool.end();
  console.log(fails === 0 ? 'ROOKTEST GROEN' : fails + ' FOUT');
  process.exit(fails ? 1 : 0);
})();
