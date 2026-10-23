# Dependencies — default picks

Add a package only when a requirement needs it and nothing installed already does the job. Check the target `package.json`/`requirements.txt` first; match existing major versions. Versions below are not pinned on purpose — let the lockfile decide; verify current majors with `npm view <pkg> version` when starting fresh.

## Node
| Need | Default | Alt / note |
|---|---|---|
| HTTP server | `express` (v5: async errors handled) | `fastify` if already used |
| env | `dotenv` | Node ≥20.6: `node --env-file=.env` |
| CORS | `cors` | Vite proxy in dev |
| validation | `zod` | manual checks for 1–2 routes |
| uploads | `multer` | always set `limits` |
| SQLite | `better-sqlite3` (native build) | `node:sqlite` (Node ≥22.5) |
| MongoDB | `mongoose` | `mongodb` driver |
| Postgres | `pg` | ORM only if required |
| auth | `jsonwebtoken`, `bcryptjs` (pure JS, no build) | `bcrypt` native |
| Gemini | `@google/genai` (current SDK) | `@google/generative-ai` is the older SDK — keep only if repo uses it |
| Qdrant | `@qdrant/js-client-rest` | |
| PDF / DOCX | `pdf-parse` / `mammoth` | `pdfjs-dist` for page-accurate text |
| tests | `node:test` (built-in) | `vitest` (Vite apps), `supertest` |
| security | `helmet`, `express-rate-limit` | |

## Frontend
`react`, `vite`, `react-router-dom` (multi-page only), `recharts` (charts), `react-markdown` (+ sanitize) for model output. No UI kit unless the repo already has one.

## Python
`fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `httpx` + `pytest`, `sqlmodel` or stdlib `sqlite3`, `google-genai`, `qdrant-client`, `pypdf`, `python-docx`, `passlib[bcrypt]` + `pyjwt`.

## Services
| Service | Free/local option | Paid? |
|---|---|---|
| Vector DB | Qdrant in Docker (`qdrant/qdrant`) | Qdrant Cloud free tier |
| LLM | Gemini API (free tier with limits) | paid tiers; don't add OpenAI/Anthropic unless required |
| DB | SQLite / local MongoDB | Atlas free tier |
| Voice | browser Web Speech API | cloud STT/TTS are paid |
