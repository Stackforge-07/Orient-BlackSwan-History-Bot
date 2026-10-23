# QUICKSTART

## 1. Install into a repo (once)
```bash
cd ~/Desktop
unzip ~/Downloads/engine-kit.zip -d engine-kit-tmp
cp -Rn engine-kit-tmp/engine engine-kit-tmp/.claude doc-rag-chatbot/   # -n: never overwrite
cp -n  engine-kit-tmp/CLAUDE.md doc-rag-chatbot/ || echo "CLAUDE.md exists — merge by hand"
chmod +x doc-rag-chatbot/engine/scripts/*.sh
```
If `doc-rag-chatbot/.claude/skills/` already existed, `-n` keeps your skills; the engine ones are added beside them.

## 2. Build the registry for this repo (once, then on big changes)
```bash
cd ~/Desktop/doc-rag-chatbot
engine/scripts/inspect-project.sh . --tree 2            # what's here
engine/scripts/inspect-project.sh . --registry > engine/registry/modules.draft.md
```
Then ask Claude Code: *"Verify engine/registry/modules.draft.md against the source, fill purpose/reuse/tests, mark implemented/partial/missing, and save as engine/registry/modules.md."*

## 3. Daily use
```bash
engine/scripts/route-task.sh "library management system with login, React + Express"
engine/scripts/setup-project.sh .            # plan; add --install to run
engine/scripts/verify-project.sh .           # real checks, honest exit codes
engine/scripts/create-project.sh fullstack-crud ~/Desktop/library-app \
  --from ~/Desktop/doc-rag-chatbot --include "server/src/middleware/auth.js"
```
(The `--include` path is an example — use paths listed in your registry.)

## 4. Prompt Claude Code
```
Use the engine. Exam mode. Build: <paste requirements>. Deadline 3 hours.
```
Claude routes, loads only the matching skills, reuses registry modules, verifies and reports.

In Claude Code you can also call skills directly: `/exam-fast-build`, `/rag-pipeline`, etc.
