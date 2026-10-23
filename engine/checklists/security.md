# Security pass

## Secrets
- [ ] No keys in code, prompts, logs, README, tests or frontend bundle (`grep -rnE "AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9]{20,}|-----BEGIN" --exclude-dir={node_modules,.git,dist} .` → no hits).
- [ ] `.env` in `.gitignore`; `git ls-files | grep -E '(^|/)\.env$'` → empty.
- [ ] `.env.example` has names + placeholders only.
- [ ] Only `VITE_*` public values in the client.

## Input & data
- [ ] Server-side validation on every write route.
- [ ] SQL via prepared statements; Mongo ids validated; no `eval`/dynamic `require` of user input.
- [ ] Uploads: size limit, type allow-list, generated filenames, stored outside web root.
- [ ] LLM output rendered as text/sanitized markdown (no raw HTML injection).
- [ ] Prompt injection: retrieved documents are treated as data in the prompt, never as instructions that can trigger tools/actions.

## Auth
- [ ] Passwords hashed (bcrypt); never returned.
- [ ] Protected routes enforce auth server-side; role checks server-side; ownership checks on user data.
- [ ] `JWT_SECRET` from env, required at startup.

## Transport & abuse
- [ ] CORS restricted to known origin(s).
- [ ] Rate limit on login, upload and LLM routes.
- [ ] Errors return `{error}` without stack traces in production.

## Data safety
- [ ] No code path deletes a Qdrant collection, uploads dir or backups as a side effect.
- [ ] `npm audit --omit=dev` reviewed (don't run `audit fix --force` blindly).
