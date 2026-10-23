#!/usr/bin/env bash
# route-task.sh — map a project/task description to the smallest template + skills to load.
#
# Usage: engine/scripts/route-task.sh "build a student management system with login and CRUD"
#        engine/scripts/route-task.sh --file requirements.txt
#
# Keyword-based and deterministic (a starting point, not a decision): the agent still reads the
# requirements and may override. Rules mirror engine/PROJECT_TYPES.md.
set -u
if [ "${1:-}" = "--file" ]; then TXT=$(cat "$2"); else TXT="$*"; fi
[ -n "$TXT" ] || { sed -n '2,8p' "$0"; exit 1; }
T=$(echo "$TXT" | tr '[:upper:]' '[:lower:]')
has() { echo "$T" | grep -Eq "$1"; }

RAG='rag|retriev|embedding|vector|qdrant|pinecone|chroma|chat with (your |the )?(doc|pdf|file)|document q&?a|semantic search|knowledge base|citation'
AI='gemini|openai|llm|chatbot|ai assistant|summar|generate (text|quiz)|gpt|claude api'
PY='python|fastapi|flask|django|pandas|pytest'
MERN='mern|mongo|mongoose|express'
CRUD='crud|management system|inventory|library|student|employee|hospital|booking|todo|records?|admin panel|add.{0,12}(edit|update).{0,12}delete'
AUTH='login|sign ?up|register|auth|jwt|role|admin|rbac|password'
UI='website|landing|dashboard|portfolio|frontend|react|vite|ui|page|chart'

TPL=""; SKILLS="project-planner code-reuse"
if   has "$RAG"; then TPL="rag-ai"; SKILLS="$SKILLS rag-pipeline backend-api"
elif has "$PY"; then TPL="python-api"; SKILLS="$SKILLS backend-api"
elif has "$MERN"; then TPL="mern"; SKILLS="$SKILLS backend-api database-auth frontend-ui"
elif has "$CRUD"; then TPL="fullstack-crud"; SKILLS="$SKILLS backend-api database-auth frontend-ui"
elif has "$AI"; then TPL="rag-ai"; SKILLS="$SKILLS backend-api"; NOTE="AI integration without retrieval: use rag-ai template's LLM layer only, skip vector DB"
elif has "$UI"; then TPL="react-vite"; SKILLS="$SKILLS frontend-ui"
else TPL="(decide)"; NOTE="no strong signal — read PROJECT_TYPES.md and choose from installed tools"; fi

has "$AUTH" && ! echo "$SKILLS" | grep -q database-auth && SKILLS="$SKILLS database-auth"
has "$UI|chat ?ui|interface" && ! echo "$SKILLS" | grep -q frontend-ui && [ "$TPL" != "python-api" ] && SKILLS="$SKILLS frontend-ui"
has 'exam|assignment|practical|deadline|hours?|lab test|viva' && SKILLS="$SKILLS exam-fast-build"
SKILLS="$SKILLS testing-debugging"

echo "template: $TPL"
[ "$TPL" != "(decide)" ] && echo "read:     engine/templates/$TPL.md"
echo "skills:   $SKILLS"
echo "registry: grep -n -i '<feature>' engine/registry/modules.md"
[ -n "${NOTE:-}" ] && echo "note:     $NOTE"
exit 0
