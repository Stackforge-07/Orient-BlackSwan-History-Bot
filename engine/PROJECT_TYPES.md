# PROJECT TYPES → template + skills

Pick by **requirements + installed tools**, not habit. `route-task.sh` implements the first matching row; override when the brief says otherwise (e.g. "must use Django").

| Signals in the brief | Template | Skills (plus project-planner, code-reuse, testing-debugging) |
|---|---|---|
| RAG, chat with PDFs/docs, embeddings, vector DB, citations, semantic search | `rag-ai` | rag-pipeline, backend-api, frontend-ui |
| Python, FastAPI, Flask, data/ML scripts, pytest | `python-api` | backend-api (+ database-auth if login/db) |
| MERN, MongoDB, Mongoose, Express named | `mern` | backend-api, database-auth, frontend-ui |
| CRUD / "management system" / records / admin panel (no stack named) | `fullstack-crud` | backend-api, database-auth, frontend-ui |
| LLM feature without retrieval (summarise, generate, classify) | `rag-ai` (LLM layer only) | backend-api |
| Website, landing page, dashboard, portfolio, UI-only | `react-vite` | frontend-ui |
| Login / roles / JWT anywhere | (any) | + database-auth |
| Exam / assignment / deadline | (any) | + exam-fast-build |

## Decision rules
- **Static or UI-only?** No backend. `react-vite` (or plain HTML if the brief allows and no build tool exists).
- **Needs persistence?** Small/offline → SQLite (`better-sqlite3` / `sqlite3` stdlib). Brief says Mongo → MongoDB. Relational + many joins → Postgres only if available.
- **Python vs Node backend?** Follow the brief; else follow what the reused code uses; else Node if the frontend is React (one language).
- **Auth?** Only if required. Sessions are fine for server-rendered; JWT for SPA + API.
- **AI provider?** Reuse the existing integration (Gemini in this repo, if confirmed in the registry). Never add a paid provider the brief doesn't need.
- **Other stacks** (Java/Spring, PHP, Go, Django…): no template — use `project-planner` + `backend-api` skills with the official generator, if that toolchain is installed (`inspect-project.sh` / `which <tool>`).

## Check routing
```bash
engine/scripts/route-task.sh "chatbot that answers questions from uploaded PDFs with citations"
# template: rag-ai
engine/scripts/route-task.sh "employee management system with add, edit, delete and admin login"
# template: fullstack-crud
```
