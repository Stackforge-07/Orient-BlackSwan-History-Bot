---
name: code-reuse
description: Find, verify and reuse existing modules via engine/registry/modules.md instead of rewriting; also maintains the registry. Use before implementing any feature and after creating a reusable module.
---
# Code reuse

## Before writing code
1. `grep -n -i "<keyword>" engine/registry/modules.md` (try 2–3 synonyms: upload|multer|file).
2. No registry hit → `grep -rln --exclude-dir={node_modules,.git,dist,build,engine} -i "<keyword>" .`
3. Open only the hit files. Check: exports, imports (deps present in target `package.json`?), env vars, side effects (DB connection on import?), tests.
4. Decide:
   - **reuse** as-is (same stack, compatible deps) → import it / copy that file only.
   - **adapt** → copy the smallest unit, change interface minimally, note the origin in a 1-line comment.
   - **write new** → only if incompatible or simpler to write than to adapt.
5. Copy between projects with `engine/scripts/create-project.sh … --from SRC --include "a,b"` (filters secrets/storage). Never copy a whole app.

## Avoid
Two implementations of the same thing · mixing ESM/CJS without converting · pulling a heavy dep for one helper · trusting a module whose test status is `unknown` without a smoke test.

## Registry entry format (`engine/registry/modules.md`)
```
### <Name> — `path/to/file.js` · status: implemented|partial|missing · tests: none|unit|manual-verified
- exports: fnA(args) → result; ComponentB({props})
- deps: express, @qdrant/js-client-rest · env: QDRANT_URL
- reuse: import as-is in Express apps; needs initClient() first
- limits: no retry; assumes 768-dim vectors
```
Regenerate a draft after big changes: `engine/scripts/inspect-project.sh . --registry > engine/registry/modules.draft.md`, then merge verified facts by hand. Status `implemented` only after you ran or tested it.
