---
name: testing-debugging
description: Verify work with the project's real checks and debug failures systematically from evidence. Use before reporting any task done, and whenever a build, test or runtime error appears.
---
# Testing & debugging

## Verify (always, before "done")
1. `engine/scripts/verify-project.sh <dir>` — runs defined typecheck/lint/test/build. Exit 0 pass · 1 fail · 3 **nothing ran** (= unverified; say so).
2. Smoke the main flow: start server(s), hit the key endpoint (`curl -s localhost:5000/api/health`), click the core UI path.
3. Report exactly what ran and its result. Never write "tests pass" for checks that didn't run.

## Minimum tests to add (if the project has none)
API: one happy path per resource, one 400, one 404, one 401/403 per protected route. Pure logic (chunker, validators, calculators): table-driven unit tests. Use what's installed (`node:test` needs nothing; vitest if Vite; pytest for Python).

## Debug loop
1. **Reproduce** with the smallest command; copy the first real error line (not the last).
2. **Locate**: stack trace → file:line; `grep` the symbol; read ≤2 files.
3. **Hypothesis** in one sentence → one change → rerun the same command.
4. After 2 failed hypotheses, gather more evidence (log inputs, check versions/env names, inspect network tab) instead of guessing.

## Common causes
| Symptom | Check |
|---|---|
| `Cannot use import statement` / `require is not defined` | ESM vs CJS (`"type":"module"`) |
| CORS error | server `CLIENT_ORIGIN`, Vite proxy, port |
| 401 everywhere | header format `Bearer <t>`, same `JWT_SECRET`, expiry |
| `undefined` env var | `.env` location vs cwd, `dotenv` loaded first, Vite needs `VITE_` prefix |
| Qdrant `Wrong input: Vector dimension` | embedding dim ≠ collection dim → new collection name, don't delete |
| LLM 429/403 | quota/key/model name; add backoff; don't loop retries |
| native module build fails (bcrypt, better-sqlite3) | use bcryptjs / node:sqlite, or install Xcode CLT |
| port in use | `lsof -i :5000` (then stop the process you own) |

Fix root causes; don't silence errors or skip tests to go green.
