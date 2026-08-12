# ¡Vamos! API

Backend voor de Spaans-leerapp: profielsync (Neon/Postgres), foutenlogs en AI-feedback via de Anthropic API.

Deploy op Render: New Web Service → deze repo → Root Directory `server` → Build `npm install` → Start `npm start`.
Env vars: DATABASE_URL (Neon), ANTHROPIC_API_KEY, ADMIN_KEY (zelf verzinnen), ALLOWED_ORIGIN (https://vamos.stefanwobben.nl).

De LLM-ladder (llm.js) staat hier omdat de sleutels hier staan. `POST /api/admin/llm?key=ADMIN_KEY`
is de ingang die de nachtelijke curriculum-taak gebruikt: die draait op GitHub Actions en heeft dus
zelf geen sleutels. Zo ligt elke sleutel op één plek.

## De sloten op de ingangen

`/api/ai/*` zit sinds 11 aug achter een slot, `/api/sync` en `/api/log` sinds 13 aug. Drie sloten,
gedeeld in plaats van gekopieerd: herkomstcontrole, een teller per IP, en bij de AI ook een
dagplafond over alle bezoekers heen.

`GET /api/state/:code` blijft met opzet open. Die is beveiligd met de sync-code zelf, en een browser
stuurt bij een GET niet altijd een Origin mee; een herkomstcontrole zou daar echte gebruikers kunnen
buitensluiten om iets te beschermen dat al beschermd is.

Twee noodremmen, allebei een omgevingsvariabele, allebei zonder opnieuw uitrollen:

    AI_UIT=1       de AI-knoppen gaan uit
    POORT_UIT=1    de sloten op /api/sync en /api/log gaan open

`/health` laat zien of ze aanstaan, zodat je niet over een maand ontdekt dat er ooit één is
aangezet en nooit meer uit.

De grenzen staan ruim en zijn te verzetten zonder de code aan te raken:

    SYNC_PER_UUR (120)  SYNC_PER_DAG (600)
    LOG_PER_UUR   (60)  LOG_PER_DAG  (300)
    AI_PER_UUR    (20)  AI_PER_DAG    (60)  AI_DAGPLAFOND (800)

Vóór uitrollen: `sh server/rooktest-slot.sh`. Die start de server twee keer met een onbereikbare
database en controleert de vier manieren waarop dit mis kan gaan. Geen database nodig; een verzoek
dat "database-fout" oplevert is langs het slot gekomen, en dat is precies wat er bewezen moet worden.
