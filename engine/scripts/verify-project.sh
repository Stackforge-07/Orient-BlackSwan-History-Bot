#!/usr/bin/env bash
# verify-project.sh — run the checks a project actually defines, report honestly.
#
# Usage:
#   engine/scripts/verify-project.sh [DIR] [--only test|lint|build|typecheck] [--dry-run]
#
# For each package.json (depth ≤3) runs, if defined: typecheck, lint, test, build.
#   - npm's placeholder test ("no test specified") counts as NOT defined.
#   - Missing node_modules → SKIP (run setup-project.sh --install first). Never reported as PASS.
#   - Tests run with CI=true so watchers (vitest/jest) exit.
# Python: runs pytest if tests exist and pytest is installed; ruff if configured.
# Exit codes: 0 = every executed check passed and ≥1 ran · 1 = a check failed · 3 = nothing could run.
set -u
DIR="."; ONLY=""; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --only) ONLY="${2:-}"; shift ;; --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) DIR="$1" ;;
  esac; shift
done
cd "$DIR" || { echo "error: bad dir $DIR" >&2; exit 1; }
LOG_DIR="${TMPDIR:-/tmp}/verify-project.$$"; mkdir -p "$LOG_DIR"
PASS=0; FAILN=0; RAN=0; REPORT=""
add() { REPORT="$REPORT$1\n"; }

script_cmd() { # $1 pkg.json, $2 script name → prints command or nothing
  if command -v node >/dev/null 2>&1; then
    node -e 'try{const s=(require(require("path").resolve(process.argv[1])).scripts||{})[process.argv[2]]||"";if(!/no test specified/.test(s))process.stdout.write(s)}catch(e){}' "$1" "$2"
  else
    python3 -c 'import json,sys
s=json.load(open(sys.argv[1])).get("scripts",{}).get(sys.argv[2],"")
print("" if "no test specified" in s else s,end="")' "$1" "$2" 2>/dev/null
  fi
}
pm_run() {
  if [ -f "$1/pnpm-lock.yaml" ]; then echo "pnpm run"; elif [ -f "$1/yarn.lock" ]; then echo "yarn"
  elif [ -f "$1/bun.lockb" ] || [ -f "$1/bun.lock" ]; then echo "bun run"; else echo "npm run"; fi
}
check() { # label dir cmd
  local label="$1" d="$2" cmd="$3" log
  log="$LOG_DIR/$(echo "$d-$label" | tr '/.' '__').log"
  if [ $DRY -eq 1 ]; then add "  PLAN  [$d] $label: $cmd"; return; fi
  printf '  running [%s] %s ... ' "$d" "$label"
  if ( cd "$d" && CI=true eval "$cmd" ) >"$log" 2>&1; then
    echo ok; PASS=$((PASS+1)); add "  PASS  [$d] $label"
  else
    echo FAILED; FAILN=$((FAILN+1)); add "  FAIL  [$d] $label  (log: $log)"
    tail -n 15 "$log" | sed 's/^/        /'
  fi
  RAN=$((RAN+1))
}
want() { [ -z "$ONLY" ] || [ "$ONLY" = "$1" ]; }

PKGS=$(find . -maxdepth 3 \( -name node_modules -o -name .git -o -name engine -o -name dist -o -name build \) -prune -o -name package.json -type f -print | sort)
for p in $PKGS; do
  d=$(dirname "$p"); r=$(pm_run "$d"); any=0
  for s in typecheck lint test build; do
    want "$s" || continue
    c=$(script_cmd "$p" "$s"); [ -n "$c" ] || continue; any=1
    if [ ! -d "$d/node_modules" ] && [ ! -d "./node_modules" ]; then add "  SKIP  [$d] $s — node_modules missing (run setup-project.sh --install)"; continue; fi
    check "$s" "$d" "$r $s"
  done
  [ $any -eq 0 ] && add "  NONE  [$d] no typecheck/lint/test/build scripts defined"
done

# Python
PYT=$(find . -maxdepth 4 \( -name node_modules -o -name .git -o -name .venv -o -name venv -o -name engine \) -prune -o -type f \( -name 'test_*.py' -o -name '*_test.py' \) -print | head -1)
if [ -n "$PYT" ] && want test; then
  PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
  if $PY -c 'import pytest' 2>/dev/null; then check "pytest" "." "$PY -m pytest -q"
  else add "  SKIP  [.] pytest — tests exist but pytest not installed"; fi
fi
if want lint && { [ -f ruff.toml ] || grep -qs '\[tool.ruff' pyproject.toml; } && command -v ruff >/dev/null 2>&1; then check "ruff" "." "ruff check ."; fi

echo; echo "== VERIFY SUMMARY"; printf "%b" "$REPORT"
if [ $DRY -eq 1 ]; then exit 0; fi
echo "  ran=$RAN pass=$PASS fail=$FAILN"
[ $FAILN -gt 0 ] && exit 1
[ $RAN -eq 0 ] && { echo "  WARNING: no checks were executed — nothing is verified."; exit 3; }
exit 0
