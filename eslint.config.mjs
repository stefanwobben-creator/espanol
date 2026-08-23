// De controle die de nachten van 21 en 22 augustus had voorkomen (v23.178).
//
// In maakToets() stond `if (oud && ...)` terwijl `oud` bij een andere functie hoorde. Dat is geldige
// JavaScript, dus `node --check` liet het door; pas als de corrector iets afkeurde klapte de run met
// "oud is not defined", en omdat alles in één ketting zat ging de hele nacht mee.
//
// Eén regel is hier het doel: no-undef. Geen stijlregels, geen opmaak, niets waarover te twisteren
// valt. Een controle die over komma's begint wordt uitgezet, en dan vangt hij ook dit niet meer.
export default [
  {
    files: ["tools/**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "commonjs",
      globals: {
        require: "readonly", module: "writable", exports: "writable", process: "readonly",
        console: "readonly", __dirname: "readonly", __filename: "readonly", Buffer: "readonly",
        fetch: "readonly", setTimeout: "readonly", clearTimeout: "readonly",
        URL: "readonly", TextDecoder: "readonly", TextEncoder: "readonly", AbortController: "readonly"
      }
    },
    linterOptions: { reportUnusedDisableDirectives: false },
    rules: { "no-undef": "error" }
  }
];
