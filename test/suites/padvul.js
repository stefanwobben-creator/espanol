// padvul.js (16 aug, v23.120) — GEEN suite. De poort pakt alleen pw-*.js, dit is een hulpbestand.
//
// WAAROM DIT ER IS
//
// Vier keer in twee dagen viel een suite om omdat er een stap bij het pad of bij de les kwam en de
// fixture die stappen met de hand opsomde:
//
//   v23.107   pw-conjfase had "11 fasen" staan
//   v23.117   pw-pad had "vijf stappen" staan
//   v23.118   pw-pad en pw-gestold hadden stapMax: 4 staan
//   v23.120   pw-pad en pw-gestold somden de brok-sleutels van het pad op
//
// Vier keer in testcode en nooit in de app, dus Stefan heeft er niets van gemerkt. Maar het is een
// patroon, en de vijfde keer komt vanzelf zolang elke suite zijn eigen lijstje bijhoudt.
//
// Deze functie vult een pad op grond van de PADDATA: hij loopt de stappen langs en zet elke stap in
// de pot die bij zijn soort hoort. Komt er morgen een stapsoort bij, dan is dit de enige plek die
// het hoeft te weten.
//
// Gebruik:
//   const { VUL } = require('./padvul.js');
//   await page.evaluate(new Function(VUL + `... vulPad(GRAM_PADEN[0]); ...`));
//
// vulPad(p)          alles af
// vulPad(p, n)       alleen de eerste n stappen af

const VUL = `
  function vulPad(p, totIdx) {
    S.brok = {}; S.gramwiz = {};
    p.stappen.forEach(function (s, i) {
      if (typeof totIdx === 'number' && i >= totIdx) return;
      if (s.soort === 'bestaandeles') {
        var id = gramLesId(s);
        if (id) S.gramwiz[id] = {stap: 9, klaar: true, rondes: 1};
      } else if (s.soort === 'les') {
        S.brok[s.brok] = {stapMax: LES_STAPPEN.length - 1, laatst: today()};
      } else if (s.soort === 'hertoets') {
        S.brok[s.brok] = {gehaald: addDays(today(), -HERTOETS_WACHT), gestold: today(), pogingen: 1, beste: 10};
      } else {
        S.brok[s.brok] = {beste: 12, rondes: 1, laatst: today()};
      }
    });
  }
`;

module.exports = { VUL };
