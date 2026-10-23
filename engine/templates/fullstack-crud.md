# Template: fullstack-crud (React + Express + SQLite)

**Default for "management system" briefs** with no stack named: zero DB server, one file DB, fast to demo.

## Create
```bash
engine/scripts/create-project.sh fullstack-crud ~/Desktop/<name>
cd ~/Desktop/<name>/server && npm install && npm i better-sqlite3
npm create vite@latest ../client -- --template react && (cd ../client && npm install)
```
(`better-sqlite3` compiles natively; if install fails, use Node ≥22.5 built-in `node:sqlite` or switch to `python-api`.)

## Structure
```
server/src/db.js            open data.db, run schema.sql on start (CREATE TABLE IF NOT EXISTS)
server/src/schema.sql       tables + constraints (NOT NULL, UNIQUE, CHECK)
server/src/routes/<res>.js  CRUD with prepared statements ONLY (no string-built SQL)
server/src/middleware/      auth.js, validate.js
client/src/pages/           List (search + pagination), Form (create/edit), Detail
client/src/lib/api.js
```

## Resource contract
| Method | Path | 2xx | Errors |
|---|---|---|---|
| GET | /api/items?q=&page=&limit= | 200 `{items,total}` | — |
| GET | /api/items/:id | 200 | 404 |
| POST | /api/items | 201 item | 400 `{error}` |
| PUT | /api/items/:id | 200 item | 400/404 |
| DELETE | /api/items/:id | 204 | 404 |

Admin-only writes → `requireRole('admin')` (database-auth skill).

## UI minimum
Table with search · create/edit form with inline validation · delete with confirm · toast/message on success/error · empty state.

## Done when
All 5 operations work in UI · invalid input rejected server-side · tests cover create + validation + 404 · `npm run build` (client) passes.
