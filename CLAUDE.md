# CLAUDE.md

This repo contains `engine/`, a reuse-first build toolkit. Load only what the task needs.

## For any new project or feature
1. `engine/scripts/route-task.sh "<request>"` → template + skills to load.
2. Read that ONE template (`engine/templates/<t>.md`) and only the listed skills (`engine/skills/<s>/SKILL.md`; also discoverable as `/` skills in `.claude/skills/`).
3. Search before writing code: `grep -n -i "<feature>" engine/registry/modules.md`, then open only the matching source files.
4. Plan in ≤10 lines, implement with focused edits, run `engine/scripts/verify-project.sh`.
5. Report: files changed, checks run (real results), start commands, what is incomplete.

## Rules
- Never read, print or commit `.env` files or keys; document variable names only.
- Never delete/reset Qdrant data, `uploads/`, backups or user data. No destructive commands.
- Don't change working app behavior unless the task requires it. Don't add dependencies without need.
- Skip `node_modules`, `.git`, `dist`, `build`, storage dirs in scans. Use `engine/scripts/inspect-project.sh` instead of exploring by hand.
- Never claim a feature works because it appears in the UI — verify it.

Details: `engine/ENGINE.md` (only when needed).
