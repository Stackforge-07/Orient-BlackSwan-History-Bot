#!/usr/bin/env bash
# inspect-project.sh — compact, secret-safe summary of a project.
#
# Usage:
#   engine/scripts/inspect-project.sh [DIR]              # summary (default DIR = .)
#   engine/scripts/inspect-project.sh [DIR] --registry   # draft module registry (markdown)
#   engine/scripts/inspect-project.sh [DIR] --tree N     # also print dir tree to depth N (default off)
#
# Never prints file contents of .env / keys. Only env VARIABLE NAMES from *.example files.
# Skips: node_modules .git dist build .next .venv venv __pycache__ coverage
#        qdrant storage / uploads / backups / generated data.
# Portable: bash 3.2+ (macOS default), find, grep, sed, awk, wc. Node/python3 optional.
set -u

DIR="."; MODE="summary"; TREE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --registry) MODE="registry" ;;
    --tree) TREE="${2:-2}"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) DIR="$1" ;;
  esac
  shift
done
[ -d "$DIR" ] || { echo "error: not a directory: $DIR" >&2; exit 1; }
cd "$DIR" || exit 1

PRUNE_NAMES='node_modules .git dist build out .next .nuxt .turbo .cache .venv venv env __pycache__ .pytest_cache coverage .idea qdrant_storage qdrant_data storage uploads backup backups .parcel-cache target vendor'

# Build find prune expression
prune_expr() {
  local first=1
  printf '\\( '
  for n in $PRUNE_NAMES; do
    if [ $first -eq 1 ]; then first=0; else printf ' -o'; fi
    printf ' -name %s' "$n"
  done
  printf " -o -name 'backup*' \\) -prune -o"
}

# list files (relative), excluding pruned dirs, secrets and big/binary types
list_files() {
  # shellcheck disable=SC2046
  eval "find . $(prune_expr) -type f -print" 2>/dev/null \
    | sed 's|^\./||' \
    | grep -Ev '(^|/)\.env($|\.local$|\.production$|\.development$)|\.(pem|key|p12|pfx|crt)$|(^|/)\.DS_Store$' \
    | grep -Ev '\.(png|jpe?g|gif|webp|ico|pdf|zip|gz|tar|mp3|mp4|wav|woff2?|ttf|eot|lock|map|sqlite|db|bin|pt|onnx)$'
}

FILES="$(list_files)"

is_secret_name() { case "$1" in *.example|*.sample|*.template) return 1;; esac; case "$1" in .env|*/.env|.env.*|*/.env.*) return 0;; esac; return 1; }

pkg_scripts() { # $1 = package.json path → "name: cmd" lines
  if command -v node >/dev/null 2>&1; then
    node -e 'try{const p=require(require("path").resolve(process.argv[1]));const s=p.scripts||{};for(const k in s)console.log("    "+k+": "+s[k])}catch(e){}' "$1"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys
try:
  s=json.load(open(sys.argv[1])).get("scripts",{})
  [print("    %s: %s"%(k,v)) for k,v in s.items()]
except Exception: pass' "$1"
  else
    sed -n '/"scripts"/,/}/p' "$1" | sed '1d;$d;s/^ */    /'
  fi
}

pkg_deps() { # $1 = package.json → space-separated dep names
  if command -v node >/dev/null 2>&1; then
    node -e 'try{const p=require(require("path").resolve(process.argv[1]));console.log(Object.keys(Object.assign({},p.dependencies||{},p.devDependencies||{})).join(" "))}catch(e){}' "$1"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys
try:
  p=json.load(open(sys.argv[1])); d={}; d.update(p.get("dependencies",{})); d.update(p.get("devDependencies",{})); print(" ".join(d))
except Exception: pass' "$1"
  fi
}

pm_for_dir() { # detect package manager for a dir from lockfiles
  local d="$1"
  if   [ -f "$d/pnpm-lock.yaml" ]; then echo pnpm
  elif [ -f "$d/yarn.lock" ]; then echo yarn
  elif [ -f "$d/bun.lockb" ] || [ -f "$d/bun.lock" ]; then echo bun
  elif [ -f "$d/package-lock.json" ]; then echo npm
  else echo "npm (no lockfile)"; fi
}

# ---------------------------------------------------------------- registry mode
if [ "$MODE" = "registry" ]; then
  echo "# Module Registry (DRAFT — generated $(date '+%Y-%m-%d'))"
  echo
  echo "> Auto-extracted exports. **Unverified**: confirm purpose, deps and test status by reading each file before relying on it."
  echo
  echo "$FILES" | grep -E '\.(js|jsx|ts|tsx|mjs|cjs|py)$' \
    | grep -Ev '(\.test\.|\.spec\.|/tests?/|__tests__|\.config\.|\.d\.ts$|^engine/)' \
    | while IFS= read -r f; do
      [ -n "$f" ] || continue
      case "$f" in
        *.py) ex=$(grep -E '^(def|class|async def) [A-Za-z]' "$f" 2>/dev/null | sed -E 's/^(async )?(def|class) ([A-Za-z0-9_]+).*/\3/' | grep -v '^_' | head -12 | tr '\n' ' ') ;;
        *)    ex=$(grep -E '^export |module\.exports|^exports\.' "$f" 2>/dev/null \
                | sed -E 's/export (default )?(async )?(function|const|let|class|interface|type|enum)? ?\*? ?([A-Za-z0-9_$]+)?.*/\4/; s/module\.exports *= *\{?([^};]*).*/\1/; s/exports\.([A-Za-z0-9_$]+).*/\1/' \
                | tr ',' '\n' | sed 's/^ *//;s/ *$//;s/:.*//' | grep -v '^$' | head -12 | tr '\n' ' ') ;;
      esac
      imp=$(grep -Eo "(from ['\"][^'\"./][^'\"]*['\"]|require\(['\"][^'\"./][^'\"]*['\"]\)|^import [a-zA-Z_][a-zA-Z0-9_.]*|^from [a-zA-Z_][a-zA-Z0-9_.]* import)" "$f" 2>/dev/null \
            | sed -E "s/^from ['\"]//; s/^require\(['\"]//; s/['\"]\)?$//; s/^import //; s/^from //; s/ import$//" \
            | sed -E 's#^(@[^/]+/[^/]+).*#\1#; s#^([^@/][^/]*)/.*#\1#; s#\..*##' | sort -u | head -8 | tr '\n' ' ')
      [ -z "$ex" ] && continue
      lines=$(wc -l < "$f" | tr -d ' ')
      echo "### \`$f\` ($lines lines)"
      echo "- exports: $ex"
      [ -n "$imp" ] && echo "- external deps: $imp"
      echo "- purpose: TODO · reuse: TODO · tests: unknown"
      echo
    done
  exit 0
fi

# ----------------------------------------------------------------- summary mode
echo "== PROJECT: $(pwd)"
echo "files scanned (excluding deps/secrets/binaries): $(echo "$FILES" | grep -c . )"
echo
echo "== LANGUAGES (file count by extension, top 12)"
echo "$FILES" | grep -Eo '\.[A-Za-z0-9]+$' | sort | uniq -c | sort -rn | head -12 | awk '{printf "  %-8s %s\n",$2,$1}'
echo

echo "== MANIFESTS"
echo "$FILES" | grep -E '(^|/)(package\.json|requirements[^/]*\.txt|pyproject\.toml|Pipfile|go\.mod|Cargo\.toml|pom\.xml|build\.gradle|composer\.json|Gemfile)$' | head -30 | while IFS= read -r m; do
  [ -n "$m" ] || continue
  d=$(dirname "$m")
  case "$m" in
    *package.json)
      echo "  $m  [pm: $(pm_for_dir "$d")]"
      deps=$(pkg_deps "$m")
      [ -n "$deps" ] && echo "    deps: $(echo "$deps" | tr ' ' '\n' | head -40 | tr '\n' ' ')"
      echo "    scripts:"; pkg_scripts "$m" ;;
    *requirements*.txt) echo "  $m  ($(grep -Ecv '^\s*(#|$)' "$m") packages): $(grep -Ev '^\s*(#|$)' "$m" | sed -E 's/[<>=~!; ].*//' | head -25 | tr '\n' ' ')" ;;
    *) echo "  $m" ;;
  esac
done
echo

echo "== FRAMEWORK / FEATURE SIGNALS (from manifests + filenames; NOT proof a feature works)"
ALLDEPS=""
for m in $(echo "$FILES" | grep -E '(^|/)package\.json$'); do ALLDEPS="$ALLDEPS $(pkg_deps "$m")"; done
for m in $(echo "$FILES" | grep -E 'requirements[^/]*\.txt$|pyproject\.toml$'); do ALLDEPS="$ALLDEPS $(grep -Eo '^[A-Za-z0-9_.-]+' "$m" 2>/dev/null | tr '\n' ' ')"; done
sig() { # label, regex
  local hit; hit=$(echo "$ALLDEPS" | tr ' ' '\n' | grep -Ei "$2" | sort -u | tr '\n' ' ')
  [ -n "$hit" ] && printf '  %-14s %s\n' "$1" "$hit"
}
sig "frontend"   '^(react|react-dom|vue|svelte|next|vite|@vitejs/.*|tailwindcss|@angular/core)$'
sig "backend"    '^(express|fastify|koa|@nestjs/core|hono|fastapi|flask|django|uvicorn)$'
sig "database"   '^(mongoose|mongodb|pg|mysql2|sqlite3|better-sqlite3|prisma|@prisma/client|sequelize|typeorm|drizzle-orm|sqlalchemy|psycopg2.*|pymongo|redis|ioredis)$'
sig "auth"       '^(jsonwebtoken|bcrypt|bcryptjs|passport.*|next-auth|@auth/.*|express-session|python-jose|passlib|pyjwt)$'
sig "ai/llm"     '^(@google/genai|@google/generative-ai|google-genai|google-generativeai|openai|@anthropic-ai/sdk|anthropic|langchain.*|@langchain/.*|llamaindex|ai)$'
sig "vector-db"  '^(@qdrant/.*|qdrant-client|chromadb|pinecone.*|@pinecone-database/.*|faiss.*|pgvector)$'
sig "doc-parse"  '^(pdf-parse|pdfjs-dist|mammoth|multer|busboy|formidable|pypdf.*|pdfplumber|python-docx|unstructured|tesseract.*|xlsx)$'
sig "testing"    '^(jest|vitest|mocha|chai|supertest|@testing-library/.*|playwright|@playwright/test|cypress|pytest)$'
sig "lint/types" '^(eslint|prettier|typescript|ruff|black|mypy|flake8)$'
echo

echo "== ENTRY / ROUTE / KEY FILES (by name)"
echo "$FILES" | grep -Ei '(^|/)(server|app|index|main)\.(js|ts|mjs|py)$|/routes?/|/controllers?/|/middlewares?/|/models?/|/services?/|/hooks/|/components/[^/]+$|/(rag|embed|qdrant|gemini|vector|ingest|parse|chunk)[^/]*\.' \
  | grep -Ev '\.(test|spec)\.' | head -60 | sed 's/^/  /'
echo

echo "== ENV (variable NAMES only; real .env files are never read)"
for f in $(eval "find . $(prune_expr) -type f \( -name '.env' -o -name '.env.*' \) -print" 2>/dev/null | sed 's|^\./||'); do
  if is_secret_name "$f"; then echo "  $f  (present — contents not read)"
  else echo "  $f: $(grep -Eo '^[A-Z][A-Z0-9_]*' "$f" | tr '\n' ' ')"; fi
done
CODEVARS=$(echo "$FILES" | grep -E '\.(js|jsx|ts|tsx|mjs|py)$' | grep -v '^engine/' | while IFS= read -r f; do grep -Eho 'process\.env\.[A-Z][A-Z0-9_]*|import\.meta\.env\.[A-Z][A-Z0-9_]*|os\.(environ\.get|getenv)\(["'"'"'][A-Z][A-Z0-9_]*' "$f" 2>/dev/null; done | sed -E 's/.*[.(]["'"'"']?//' | sort -u | tr '\n' ' ')
[ -n "$CODEVARS" ] && echo "  referenced in code: $CODEVARS"
echo

echo "== INFRA / TESTS"
echo "$FILES" | grep -Ei '(^|/)(Dockerfile[^/]*|docker-compose[^/]*\.ya?ml|compose\.ya?ml|Makefile|\.github/workflows/.*|vercel\.json|netlify\.toml|render\.yaml|Procfile)$' | sed 's/^/  infra: /'
TESTS=$(echo "$FILES" | grep -Ec '(\.test\.|\.spec\.|(^|/)tests?/|__tests__|(^|/)test_[^/]+\.py$)')
echo "  test files: $TESTS"
[ "$TESTS" -gt 0 ] && echo "$FILES" | grep -E '(\.test\.|\.spec\.|(^|/)tests?/|__tests__|(^|/)test_[^/]+\.py$)' | head -10 | sed 's/^/    /'
[ -f CLAUDE.md ] && echo "  CLAUDE.md: present"
[ -d engine ] && echo "  engine/: present"
[ -d .git ] && command -v git >/dev/null 2>&1 && echo "  git: branch $(git rev-parse --abbrev-ref HEAD 2>/dev/null), $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') uncommitted changes"

if [ "$TREE" -gt 0 ]; then
  echo; echo "== TREE (depth $TREE)"
  echo "$FILES" | awk -F/ -v d="$TREE" '{p=""; for(i=1;i<=NF&&i<=d;i++){p=(p==""?$i:p"/"$i); if(i<NF) print p"/"; else print p}}' | sort -u | head -150 | sed 's/^/  /'
fi
exit 0
