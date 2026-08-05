// De poort praat met niets buiten zichzelf.
//
// Waarom dit bestaat. De app doet bij het opstarten een fetch naar de familieserver op Render
// (`var API` in index.html). In de sandbox waarin al deze suites geschreven zijn, kwam dat verzoek
// nooit aan: geen route naar buiten, dus ERR_TUNNEL_CONNECTION_FAILED, en dat staat in elke suite in
// de lijst met ruis die niet meetelt. Op een GitHub-runner is er wél internet. Daar komt het verzoek
// echt aan bij Render, die het weigert omdat http://localhost:8321 niet in zijn CORS-lijst staat, en
// dat schrijft Chromium in de console als "has been blocked by CORS policy". Die tekst staat in geen
// enkele ruislijst, dus telde hij mee als appfout. Acht suites rood, in alle vier de shards, terwijl
// er niets mis was met de app.
//
// Dat is niet op te lossen door die ene zin ook te negeren. Het echte probleem is dat de kleur van de
// poort afhing van iets buiten de repo: of de runner internet heeft, of Render wakker is (gratis plan,
// hij valt in slaap), en wat er in zijn CORS-lijst staat. Een poort die daarvan afhangt, wordt vroeg
// of laat rood op een moment dat er niets aan de hand is, en dan is hij binnen een week een advies.
//
// Dus: alles wat niet naar de eigen testserver gaat, wordt afgebroken. Precies de toestand waarin de
// hele kern groen is geworden, nu overal hetzelfde, met of zonder internet. Wil je ooit tegen de
// echte server testen, dan is dat een eigen suite die dat expliciet aanzet, niet iets wat per ongeluk
// aanstaat omdat de machine toevallig online is.
//
// Dit bestand wordt door poort.js via NODE_OPTIONS voor elke suite ingeladen, zodat geen van de 35
// suites hoeft te weten dat het bestaat.
const pw = require('playwright');

const EIGEN = 'http://localhost:8321';

function magDoor(url) {
  var s = String(url);
  return s.indexOf(EIGEN) === 0 || s.indexOf('data:') === 0 || s.indexOf('blob:') === 0 ||
    s.indexOf('about:') === 0 || s.indexOf('chrome-extension:') === 0;
}

// Een predicaat in plaats van '**/*': dan onderschept Playwright alleen wat naar buiten wil, en
// blijven de duizenden verzoeken naar de eigen server ongemoeid en dus net zo snel als eerst.
async function afschermen(doel) {
  await doel.route((url) => !magDoor(url), (route) => route.abort());
}

['chromium', 'firefox', 'webkit'].forEach(function (naam) {
  var type = pw[naam];
  if (!type || typeof type.launch !== 'function') return;
  var launch = type.launch.bind(type);
  type.launch = async function () {
    var browser = await launch.apply(null, arguments);
    var newPage = browser.newPage.bind(browser);
    var newContext = browser.newContext.bind(browser);
    browser.newPage = async function () {
      var p = await newPage.apply(null, arguments);
      await afschermen(p);
      return p;
    };
    browser.newContext = async function () {
      var c = await newContext.apply(null, arguments);
      await afschermen(c);
      return c;
    };
    return browser;
  };
});
