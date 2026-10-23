# Commands

## Engine
```bash
engine/scripts/inspect-project.sh [dir] [--tree 2]        # stack summary (no secrets)
engine/scripts/inspect-project.sh . --registry > engine/registry/modules.draft.md
engine/scripts/route-task.sh "<brief>"                    # template + skills
engine/scripts/setup-project.sh [dir] [--install] [--env] # deps from lockfiles; .env from example if missing
engine/scripts/verify-project.sh [dir] [--only test]      # real checks; exit 0/1/3
engine/scripts/create-project.sh <tpl> <dest> [--from SRC --include "a,b"] [--scaffold]
```

## doc-rag-chatbot
Fill from `inspect-project.sh` → "MANIFESTS / scripts" (not yet recorded — repo not inspected when this was written). Typical shape to confirm:
```bash
cd server && npm run dev        # API
cd client && npm run dev        # UI
docker run -d -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

## Generic
| Task | Node | Python |
|---|---|---|
| install (locked) | `npm ci` | `./.venv/bin/pip install -r requirements.txt` |
| dev | `npm run dev` | `uvicorn app.main:app --reload` |
| test | `npm test` | `python -m pytest -q` |
| build | `npm run build` | — |
| free a port | `lsof -i :5000` then stop your own process | same |
| health | `curl -s localhost:5000/api/health` | `curl -s localhost:8000/api/health` |
| Qdrant count | `curl -s localhost:6333/collections/<name>` (read-only) | same |

Never in routine work: `rm -rf`, `git reset --hard`, `docker volume rm`, Qdrant `DELETE /collections/*`.
