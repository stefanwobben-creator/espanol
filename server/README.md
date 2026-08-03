# ¡Vamos! API

Backend voor de Spaans-leerapp: profielsync (Neon/Postgres), foutenlogs en AI-feedback via de Anthropic API.

Deploy op Render: New Web Service → deze repo → Root Directory `server` → Build `npm install` → Start `npm start`.
Env vars: DATABASE_URL (Neon), ANTHROPIC_API_KEY, ADMIN_KEY (zelf verzinnen), ALLOWED_ORIGIN (https://vamos.stefanwobben.nl).

De LLM-ladder (llm.js) staat hier omdat de sleutels hier staan. `POST /api/admin/llm?key=ADMIN_KEY`
is de ingang die de nachtelijke curriculum-taak gebruikt: die draait op GitHub Actions en heeft dus
zelf geen sleutels. Zo ligt elke sleutel op één plek.
