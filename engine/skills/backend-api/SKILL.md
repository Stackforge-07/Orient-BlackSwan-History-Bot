---
name: backend-api
description: Design and implement REST APIs (Express or FastAPI) with validation, consistent errors, file uploads and testable app structure. Use when adding or changing server endpoints.
---
# Backend API

## Structure
- App factory (`createApp()` / `app = FastAPI()`) separate from `listen` → testable.
- Routes thin; logic in `services/`; DB access in `db.js`/models.
- Config from env in one place (`config.js`/`settings.py`), validated at startup: missing required var → clear error and exit.

## Contract rules
- REST nouns, plural: `/api/items/:id`. JSON in/out.
- Status: 200 get/update · 201 create · 204 delete · 400 invalid · 401 no/bad token · 403 wrong role · 404 missing · 409 conflict · 413 file too large · 500 unexpected.
- Error body always `{ "error": "<human message>" }`. Never leak stack traces or secrets.
- Validate every input server-side (zod/joi/express-validator if present; else small manual checks; Pydantic in FastAPI).
- Pagination `?page=&limit=` (cap limit ≤100). Search `?q=`.

## Express checklist
`express.json({limit})` · CORS restricted to `CLIENT_ORIGIN` · async errors reach the error handler (Express 5 does it natively; Express 4 needs try/catch or a wrapper) · `helmet` if allowed · rate-limit expensive routes (LLM, upload).

## Uploads
`multer` (memory or disk with size `limits`, `fileFilter` by mimetype+extension). Store under `uploads/` with generated names; never trust original filename for paths.

## Test
`node:test` + `fetch` against `app.listen(0)` (see create-project starter) or supertest if installed; FastAPI `TestClient`. Minimum: happy path, validation 400, not-found 404, auth 401 per protected route.

Document new endpoints in the project README (method, path, body, response).
