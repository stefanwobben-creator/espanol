#!/usr/bin/env node
// versiehoger.js (6 sep, v23.247) - het nummer dat ik lever is hoger dan het nummer dat al leeft
//
// WAAROM DIT ER IS
//
// tools/versiegelijk.js bewaakt dat versie.txt en APP_VERSIE hetzelfde zeggen: één boom, één
// nummer. Dit bestand bewaakt de andere kant: één nummer, één boom.
//
// Op 6 september ging dat mis. De avondrun ging voor het eerst zelfstandig live en publiceerde
// v23.245; mijn eigen ronde stond op dat moment open met datzelfde nummer. Twee verschillende
// bomen, allebei v23.245, en geen enkele melding. Dat nummer staat onderaan elk scherm van de app
// en het is het enige waaraan Stefan kan zien welke versie hij draait; wijst het er twee aan, dan
// wijst het er geen aan.
//
// claude/patchhulp.py voorkomt het bij het TOEPASSEN (het geplande nummer is daar een bodem, geen
// belofte). Dit bestand vangt het bij het AFLEVEREN, want de vorige keer keek ik precies langs de
// regel heen die het al zei.
//
//     Een regel die op één plek voorkómen wordt en op geen enkele plek gecontroleerd,
//     is een regel die je moet onthouden.
//
// WAT HIJ DOET
//
//   node tools/versiehoger.js                 # vergelijkt met origin/main
//   node tools/versiehoger.js --basis <ref>   # of met iets anders
//   node tools/versiehoger.js --zelftest
//
//   mijn nummer > dat van de basis              -> groen
//   gelijk, maar er valt niets te leveren       -> groen (er botst niets als er niets komt)
//   gelijk, en mijn boom is anders              -> ROOD, dit is de botsing
//   lager dan de basis                          -> ROOD
//   de basis is niet te lezen                   -> exitcode 3, en dat zegt hij ook
//
// Die laatste is met opzet geen groen. Een controle die zijn onderwerp niet kan vinden, hoort dat
// te melden en niet stilletjes te slagen: nul is geen bericht.
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function git(args, opties) {
  return execFileSync('git', args, Object.assign({ encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }, opties || '')).trim();
}

function num(v) {
  const d = String(v).match(/\d+/g);
  return d ? d.map(Number) : null;
}

// [23,9] < [23,10], wat een tekstvergelijking niet doet
function vergelijk(a, b) {
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const x = a[i] || 0, y = b[i] || 0;
    if (x !== y) return x < y ? -1 : 1;
  }
  return 0;
}

function meet(wortel, basis) {
  const mijnRuw = fs.readFileSync(path.join(wortel, 'versie.txt'), 'utf8').trim();
  const mijn = num(mijnRuw);
  if (!mijn) return { status: 'onleesbaar', mijnRuw };

  let basisRuw;
  try {
    basisRuw = git(['show', basis + ':versie.txt'], { cwd: wortel });
  } catch (e) {
    return { status: 'geenbasis', mijnRuw, basis, waarom: String(e.stderr || e.message).trim().split('\n')[0] };
  }
  const hun = num(basisRuw);
  if (!hun) return { status: 'onleesbaar', mijnRuw, basisRuw };

  // valt er eigenlijk iets te leveren? werkmap meegerekend, dus ook wat nog niet gecommit is
  let zelfde = false;
  try {
    git(['diff', '--quiet', basis, '--'], { cwd: wortel });
    zelfde = true;
  } catch (e) { zelfde = false; }

  const v = vergelijk(mijn, hun);
  if (v > 0) return { status: 'hoger', mijnRuw, basisRuw, basis };
  if (v < 0) return { status: 'lager', mijnRuw, basisRuw, basis, zelfde };
  return { status: zelfde ? 'gelijkleeg' : 'botsing', mijnRuw, basisRuw, basis };
}

function rapporteer(r) {
  if (r.status === 'onleesbaar') {
    console.log('CONTROLE MISLUKT: dit leest niet als een versie (' +
      JSON.stringify(r.basisRuw === undefined ? r.mijnRuw : r.basisRuw) + ').');
    return 1;
  }
  if (r.status === 'geenbasis') {
    console.log('KAN NIET METEN: ' + r.basis + ':versie.txt is niet te lezen.');
    console.log('  ' + r.waarom);
    console.log('Doe eerst `git fetch origin`, of noem een andere basis met --basis.');
    console.log('Dit is met opzet geen groen: een controle die zijn onderwerp niet vindt, heeft niets gecontroleerd.');
    return 3;
  }
  console.log('hier      : ' + r.mijnRuw);
  console.log(r.basis.padEnd(10) + ': ' + r.basisRuw);
  if (r.status === 'hoger') { console.log('\nhoger dan wat er leeft, dus dit nummer wijst één boom aan'); return 0; }
  if (r.status === 'gelijkleeg') { console.log('\ngelijk, maar er valt niets te leveren: geen botsing'); return 0; }
  if (r.status === 'lager') {
    console.log('\nDIT NUMMER LIGT ACHTER OP WAT ER AL LEEFT.');
    console.log('Rebase op ' + r.basis + ' en kies een nummer hoger dan ' + r.basisRuw + '.');
    return 1;
  }
  console.log('\nDIT NUMMER IS AL VERGEVEN, EN JOUW BOOM IS EEN ANDERE.');
  console.log('Twee verschillende bomen zouden dan allebei ' + r.mijnRuw + ' heten. Het nummer staat');
  console.log('onderaan elk scherm van de app; wijst het er twee aan, dan wijst het er geen aan.');
  console.log('\nWat je doet: hernummer deze ronde naar ' + hernummer(r.basisRuw) + ' (versie.txt, APP_VERSIE,');
  console.log('de naam van het patchscript en de titel van de commit) en lever opnieuw.');
  return 1;
}

function hernummer(v) {
  const m = /^(v?\d+(?:\.\d+)*\.)(\d+)$/.exec(String(v).trim());
  return m ? m[1] + (Number(m[2]) + 1) : '(volgende)';
}

// ---------------------------------------------------------------------------------------------
// de zelftest
//
// Bouwt een echt repository met een basis-tak en zet daar de vier gevallen op. Zonder deze proef is
// dit bestand een bewering; en zonder de twee CONTROLE-gevallen zou "alles groen" ook waar zijn als
// hij nooit rood kán worden.
// ---------------------------------------------------------------------------------------------
function zelftest() {
  const os = require('os');
  let fout = 0;
  const ok = (c, m) => { if (c) console.log('  ok   ' + m); else { fout++; console.log('  FOUT ' + m); } };

  const W = fs.mkdtempSync(path.join(os.tmpdir(), 'versiehoger-'));
  const g = (...a) => git(a, { cwd: W });
  g('init', '-q', '-b', 'main');
  g('config', 'user.email', 'proef@proef');
  g('config', 'user.name', 'proef');
  fs.writeFileSync(path.join(W, 'versie.txt'), 'v1.9\n');
  fs.writeFileSync(path.join(W, 'index.html'), 'start\n');
  g('add', '-A'); g('commit', '-qm', 'basis');
  g('branch', 'basis');

  const zet = (v, inhoud) => {
    fs.writeFileSync(path.join(W, 'versie.txt'), v + '\n');
    fs.writeFileSync(path.join(W, 'index.html'), inhoud);
  };

  console.log('-- het gewone geval --');
  zet('v1.10', 'mijn ronde\n');
  let r = meet(W, 'basis');
  ok(r.status === 'hoger', 'v1.10 boven v1.9 is hoger (' + r.status + ')');
  ok(rapporteer(r) === 0, '  en dat is groen');

  console.log('\n-- DE BOTSING VAN 6 SEPTEMBER --');
  zet('v1.9', 'mijn ronde, ander werk, zelfde nummer\n');
  r = meet(W, 'basis');
  ok(r.status === 'botsing', 'zelfde nummer, andere boom = botsing (' + r.status + ')');
  ok(rapporteer(r) === 1, '  CONTROLE: en die is ROOD, anders vangt dit bestand niets');

  console.log('\n-- gelijk nummer, maar niets te leveren --');
  zet('v1.9', 'start\n');
  r = meet(W, 'basis');
  ok(r.status === 'gelijkleeg', 'zelfde nummer, zelfde boom = geen botsing (' + r.status + ')');
  ok(rapporteer(r) === 0, '  en dat is groen');

  console.log('\n-- achterlopen --');
  zet('v1.8', 'mijn ronde\n');
  r = meet(W, 'basis');
  ok(r.status === 'lager', 'v1.8 onder v1.9 loopt achter (' + r.status + ')');
  ok(rapporteer(r) === 1, '  CONTROLE: en dat is ook rood');

  console.log('\n-- v1.9 en v1.10: als getal, niet als tekst --');
  ok(vergelijk(num('v1.9'), num('v1.10')) < 0, 'v1.9 komt voor v1.10');
  ok(vergelijk(num('v23.246'), num('v23.247')) < 0, 'v23.246 komt voor v23.247');

  console.log('\n-- een basis die er niet is --');
  zet('v1.10', 'mijn ronde\n');
  r = meet(W, 'bestaatniet');
  ok(r.status === 'geenbasis', 'een onbekende ref levert "geenbasis" (' + r.status + ')');
  const code = rapporteer(r);
  ok(code === 3, '  CONTROLE: en dat is exitcode 3, niet 0 (' + code + ')');

  console.log('\n-- de hernummer-tip klopt --');
  ok(hernummer('v23.245') === 'v23.246', 'na v23.245 komt v23.246 (' + hernummer('v23.245') + ')');
  ok(hernummer('v23.9') === 'v23.10', 'na v23.9 komt v23.10 (' + hernummer('v23.9') + ')');

  fs.rmSync(W, { recursive: true, force: true });
  console.log('');
  if (fout) { console.log(fout + ' fout'); return 1; }
  console.log('alles goed');
  return 0;
}

// ---------------------------------------------------------------------------------------------
if (process.argv.includes('--zelftest')) process.exit(zelftest());

const i = process.argv.indexOf('--basis');
const BASIS = i !== -1 ? process.argv[i + 1] : 'origin/main';
process.exit(rapporteer(meet(path.resolve(__dirname, '..'), BASIS)));
