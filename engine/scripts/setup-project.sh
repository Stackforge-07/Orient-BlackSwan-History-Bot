#!/usr/bin/env bash
# setup-project.sh — detect package managers and print (or run) safe install steps.
#
# Usage:
#   engine/scripts/setup-project.sh [DIR]            # dry run: print the plan only (default)
#   engine/scripts/setup-project.sh [DIR] --install  # run installs from existing manifests/lockfiles
#   engine/scripts/setup-project.sh [DIR] --env      # create missing .env from .env.example (never overwrites)
#
# Guarantees:
#   - Installs ONLY what the manifests/lockfiles already declare (npm ci / pnpm i --frozen-lockfile /
#     yarn --frozen-lockfile / pip install -r). Never adds packages.
#   - Never overwrites or reads an existing .env. --env copies .env.example only where .env is absent.
#   - Never deletes anything.
# Scans DIR and its subfolders up to depth 3 (e.g. ./, client/, server/, apps/web/).
set -u
DIR="."; INSTALL=0; ENV=0
for a in "$@"; do
  case "$a" in
    --install) INSTALL=1 ;; --env) ENV=1 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) DIR="$a" ;;
  esac
done
[ -d "$DIR" ] || { echo "error: not a directory: $DIR" >&2; exit 1; }
cd "$DIR" || exit 1
ROOT=$(pwd)
FAIL=0

run() { # print, and execute only when --install
  echo "  \$ $*"
  if [ $INSTALL -eq 1 ]; then ( eval "$@" ) || { echo "  !! failed: $*"; FAIL=1; }; fi
}
have() { command -v "$1" >/dev/null 2>&1; }

PRUNE='-name node_modules -o -name .git -o -name .venv -o -name venv -o -name dist -o -name build -o -name engine'
MANIFESTS=$(eval "find . -maxdepth 3 \( $PRUNE \) -prune -o -type f \( -name package.json -o -name 'requirements*.txt' -o -name pyproject.toml \) -print" | sort)

[ -z "$MANIFESTS" ] && { echo "No package.json / requirements.txt / pyproject.toml found (depth ≤3)."; exit 0; }
[ $INSTALL -eq 0 ] && echo "DRY RUN — re-run with --install to execute. Plan:"

for m in $MANIFESTS; do
  d=$(dirname "$m"); echo; echo "[$d] $(basename "$m")"
  case "$m" in
    */package.json)
      have node || { echo "  !! node not installed — install Node LTS (e.g. 'brew install node')"; FAIL=1; continue; }
      if   [ -f "$d/pnpm-lock.yaml" ]; then have pnpm || echo "  note: 'corepack enable' provides pnpm"; run "cd '$d' && pnpm install --frozen-lockfile"
      elif [ -f "$d/yarn.lock" ];      then have yarn || echo "  note: 'corepack enable' provides yarn"; run "cd '$d' && yarn install --frozen-lockfile"
      elif [ -f "$d/bun.lockb" ] || [ -f "$d/bun.lock" ]; then run "cd '$d' && bun install --frozen-lockfile"
      elif [ -f "$d/package-lock.json" ]; then run "cd '$d' && npm ci"
      else echo "  no lockfile → npm install will resolve versions from package.json ranges"; run "cd '$d' && npm install"; fi
      [ -d "$d/node_modules" ] && echo "  (node_modules already present)" ;;
    *requirements*.txt)
      have python3 || { echo "  !! python3 not found"; FAIL=1; continue; }
      if [ -d "$d/.venv" ] || [ -d "$d/venv" ]; then echo "  venv exists"; VENV=$( [ -d "$d/.venv" ] && echo .venv || echo venv)
      else VENV=.venv; run "cd '$d' && python3 -m venv .venv"; fi
      run "cd '$d' && ./$VENV/bin/pip install -r '$(basename "$m")'" ;;
    */pyproject.toml)
      if grep -q '^\[tool\.poetry' "$m"; then run "cd '$d' && poetry install"
      elif have uv; then run "cd '$d' && uv sync"
      else run "cd '$d' && python3 -m venv .venv && ./.venv/bin/pip install -e ."; fi ;;
  esac
done

echo; echo "[env files]"
for ex in $(eval "find . -maxdepth 3 \( $PRUNE \) -prune -o -type f \( -name '.env.example' -o -name '.env.sample' \) -print"); do
  d=$(dirname "$ex")
  if [ -f "$d/.env" ]; then echo "  $d/.env exists — left untouched"
  elif [ $ENV -eq 1 ]; then cp -n "$ex" "$d/.env" && echo "  created $d/.env from $(basename "$ex") — fill in real values"
  else echo "  $d/.env missing → run with --env (or: cp -n '$ex' '$d/.env') then fill values"; fi
done

echo; echo "[services]"
if grep -rqsl --include='*.js' --include='*.ts' --include='*.py' --include='*.yml' --include='*.yaml' -i 'qdrant' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=engine 2>/dev/null; then
  echo "  Qdrant referenced. Start it WITHOUT wiping data, e.g.:"
  echo "    docker run -d -p 6333:6333 -v \"\$(pwd)/qdrant_storage:/qdrant/storage\" qdrant/qdrant"
  echo "  (or 'docker compose up -d' if a compose file defines it)"
fi
grep -rqsl --include='*.js' --include='*.ts' --include='*.py' -iE 'mongoose|MongoClient|pymongo' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=engine 2>/dev/null \
  && echo "  MongoDB referenced — needs a running instance or Atlas URI in .env"
exit $FAIL
