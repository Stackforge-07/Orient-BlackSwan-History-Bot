#!/usr/bin/env bash
# create-project.sh — start a new project from an engine template, safely.
#
# Usage:
#   engine/scripts/create-project.sh TEMPLATE DEST [--from SRC --include "p1,p2,..."] [--scaffold] [--force]
#
#   TEMPLATE   react-vite | mern | rag-ai | python-api | fullstack-crud
#   DEST       new folder (must not exist or be empty; --force asks for interactive "yes")
#   --from     source repo to reuse code from (e.g. ~/Desktop/doc-rag-chatbot)
#   --include  comma-separated paths inside SRC to copy (smallest units only, e.g.
#              "server/src/services/rag.js,client/src/components/ChatBox.jsx")
#   --scaffold also run the official frontend generator (needs network: npm create vite)
#
# Always: copies engine/ + .claude/skills + CLAUDE.md into DEST, writes README, .gitignore,
# .env.example (names only) and a small runnable starter for the template.
# Never copies: .git node_modules .env* (except *.example) qdrant storage, uploads, backups,
# dist/build, keys. Never overwrites existing files (cp -n semantics).
set -eu
ENGINE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
KIT_ROOT="$(dirname "$ENGINE_DIR")"
usage() { sed -n '2,19p' "$0"; exit "${1:-0}"; }
[ $# -ge 2 ] || usage 1
TPL="$1"; DEST="$2"; shift 2
FROM=""; INCLUDE=""; SCAFFOLD=0; FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --from) FROM="$2"; shift ;; --include) INCLUDE="$2"; shift ;;
    --scaffold) SCAFFOLD=1 ;; --force) FORCE=1 ;; -h|--help) usage 0 ;;
    *) echo "unknown arg: $1" >&2; usage 1 ;;
  esac; shift
done
case "$TPL" in react-vite|mern|rag-ai|python-api|fullstack-crud) ;; *) echo "unknown template: $TPL" >&2; usage 1 ;; esac

if [ -n "$FROM" ]; then
  [ -d "$FROM" ] || { echo "error: --from not a dir: $FROM" >&2; exit 1; }
  [ -n "$INCLUDE" ] || { echo "error: --from needs --include (copy smallest units, not the whole app)" >&2; exit 1; }
fi
if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
  [ $FORCE -eq 1 ] || { echo "refusing: $DEST exists and is not empty (use --force to add files without overwriting)"; exit 1; }
  [ -t 0 ] || { echo "refusing: --force needs an interactive terminal to confirm"; exit 1; }
  printf 'DEST %s is not empty. Existing files are kept; only missing files are added. Type yes: ' "$DEST"
  read -r ans; [ "$ans" = "yes" ] || { echo aborted; exit 1; }
fi
mkdir -p "$DEST"; DEST="$(cd "$DEST" && pwd)"

EXCL='(^|/)(\.git|node_modules|\.venv|venv|dist|build|\.next|qdrant_storage|qdrant_data|storage|uploads|backups?[^/]*|__pycache__)(/|$)|(^|/)\.env($|\.[^/]*$)|\.(pem|key|p12)$'
safe_copy() { # src_file dest_file [rel_path_for_filter]  (no overwrite, no secrets)
  local rel="${3:-$(basename "$1")}"
  case "$rel" in *.example|*.sample) ;; *) if echo "$rel" | grep -Eq "$EXCL"; then echo "  skip (excluded): $rel"; return 0; fi ;; esac
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ]; then echo "  keep existing: ${2#$DEST/}"; else cp "$1" "$2"; [ -n "${4:-}" ] && echo "  + $rel"; fi
  return 0
}
copy_tree() { # src_dir dest_dir
  (cd "$1" && find . -type f -print) | sed 's|^\./||' | while IFS= read -r f; do safe_copy "$1/$f" "$2/$f" "$f"; done
}
put() { # dest_rel content(stdin) — write only if missing
  local p="$DEST/$1"; mkdir -p "$(dirname "$p")"
  if [ -e "$p" ]; then echo "  keep existing: $1"; cat >/dev/null; else cat > "$p"; echo "  + $1"; fi
}

echo "== engine → $DEST"
copy_tree "$ENGINE_DIR" "$DEST/engine"
[ -d "$KIT_ROOT/.claude/skills" ] && copy_tree "$KIT_ROOT/.claude/skills" "$DEST/.claude/skills"
[ -f "$KIT_ROOT/CLAUDE.md" ] && safe_copy "$KIT_ROOT/CLAUDE.md" "$DEST/CLAUDE.md"
# fresh registry for the new project: keep the format, drop source-repo entries
printf '# Module Registry\n\nNew project from template `%s`. Add modules as they are created (format: engine/skills/code-reuse/SKILL.md).\nSource-repo modules: see the registry in the repo you reused from.\n' "$TPL" > "$DEST/engine/registry/modules.md"

echo "== common files"
put .gitignore <<'EOF'
node_modules/
dist/
build/
.venv/
__pycache__/
.env
.env.*
!.env.example
qdrant_storage/
uploads/
*.log
.DS_Store
EOF

node_server() { # $1 = dir
put "$1/package.json" <<'EOF'
{
  "name": "server",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "node --watch src/index.js",
    "start": "node src/index.js",
    "test": "node --test"
  },
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.4.7",
    "express": "^5.1.0"
  }
}
EOF
put "$1/src/app.js" <<'EOF'
import express from 'express';
import cors from 'cors';

export function createApp() {
  const app = express();
  app.use(cors({ origin: process.env.CLIENT_ORIGIN || 'http://localhost:5173' }));
  app.use(express.json({ limit: '1mb' }));
  app.get('/api/health', (_req, res) => res.json({ ok: true }));
  // mount feature routers here: app.use('/api/items', itemsRouter);
  app.use((err, _req, res, _next) => {
    console.error(err);
    res.status(err.status || 500).json({ error: err.expose ? err.message : 'Internal error' });
  });
  return app;
}
EOF
put "$1/src/index.js" <<'EOF'
import 'dotenv/config';
import { createApp } from './app.js';

const port = Number(process.env.PORT) || 5000;
createApp().listen(port, () => console.log(`API on http://localhost:${port}`));
EOF
put "$1/test/health.test.js" <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createApp } from '../src/app.js';

test('GET /api/health', async () => {
  const server = createApp().listen(0);
  const { port } = server.address();
  const res = await fetch(`http://127.0.0.1:${port}/api/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
  server.close();
});
EOF
}

case "$TPL" in
  python-api)
    put requirements.txt <<'EOF'
fastapi>=0.115
uvicorn[standard]>=0.30
python-dotenv>=1.0
pytest>=8
httpx>=0.27
EOF
    put app/__init__.py </dev/null
    put app/main.py <<'EOF'
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="API")


@app.get("/api/health")
def health():
    return {"ok": True}
EOF
    put tests/test_health.py <<'EOF'
from fastapi.testclient import TestClient
from app.main import app


def test_health():
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200 and r.json() == {"ok": True}
EOF
    put .env.example <<'EOF'
PORT=8000
EOF
    RUN='python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m pytest -q
./.venv/bin/uvicorn app.main:app --reload --port 8000' ;;
  react-vite)
    put .env.example <<'EOF'
VITE_API_URL=http://localhost:5000
EOF
    RUN='npm create vite@latest client -- --template react   # (done for you with --scaffold)
cd client && npm install && npm run dev'
    [ $SCAFFOLD -eq 1 ] && (cd "$DEST" && npm create vite@latest client -- --template react) ;;
  mern|fullstack-crud|rag-ai)
    node_server server
    case "$TPL" in
      mern) put server/.env.example <<'EOF'
PORT=5000
CLIENT_ORIGIN=http://localhost:5173
MONGODB_URI=mongodb://127.0.0.1:27017/app
JWT_SECRET=change-me
EOF
      ;;
      fullstack-crud) put server/.env.example <<'EOF'
PORT=5000
CLIENT_ORIGIN=http://localhost:5173
DATABASE_URL=
JWT_SECRET=change-me
EOF
      ;;
      rag-ai) put server/.env.example <<'EOF'
PORT=5000
CLIENT_ORIGIN=http://localhost:5173
GEMINI_API_KEY=
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=documents
EOF
      ;;
    esac
    RUN='cd server && npm install && npm test && npm run dev
npm create vite@latest client -- --template react && cd client && npm install && npm run dev'
    [ $SCAFFOLD -eq 1 ] && (cd "$DEST" && npm create vite@latest client -- --template react) ;;
esac

if [ -n "$FROM" ]; then
  FROM="$(cd "$FROM" && pwd)"
  echo "== reuse from $FROM"
  OLDIFS=$IFS; IFS=','
  for p in $INCLUDE; do
    IFS=$OLDIFS; p=$(echo "$p" | sed 's/^ *//;s/ *$//')
    if [ -d "$FROM/$p" ]; then (cd "$FROM" && find "$p" -type f -print) | while IFS= read -r f; do safe_copy "$FROM/$f" "$DEST/$f" "$f" v; done
    elif [ -f "$FROM/$p" ]; then safe_copy "$FROM/$p" "$DEST/$p" "$p" v
    else echo "  !! not found: $p"; fi
    IFS=','
  done; IFS=$OLDIFS
  echo "  NOTE: check copied files' imports/deps and record them in engine/registry/modules.md"
fi

put README.md <<EOF
# New $TPL project

Template guide: \`engine/templates/$TPL.md\` · Engine: \`engine/ENGINE.md\`

## Run
\`\`\`bash
$RUN
\`\`\`

Copy every \`.env.example\` to \`.env\` and fill real values (never commit \`.env\`).
EOF

echo; echo "Done. Next:"; echo "  cd \"$DEST\""; echo "$RUN" | sed 's/^/  /'
