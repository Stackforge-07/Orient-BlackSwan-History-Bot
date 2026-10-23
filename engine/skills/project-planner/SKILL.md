---
name: project-planner
description: Turn a project brief or exam question into requirements, a chosen stack/template and a ≤10-line plan before any code. Use at the start of every new project or large feature.
---
# Project planner

1. **Extract** (use `engine/checklists/requirements.md`): required features (numbered, verbatim from brief), deliverables (repo, report, screenshots, demo), constraints (stack, time, offline, no paid APIs), and ambiguities. Ask ≤3 questions only if a wrong guess would be costly; else state assumptions.
2. **Route:** `engine/scripts/route-task.sh "<brief>"`. Check against `engine/PROJECT_TYPES.md`; override with reason if the brief names a stack.
3. **Inventory:** `engine/scripts/inspect-project.sh <dir>` once. `grep -n -i "<feature>" engine/registry/modules.md` per feature. Open only matching files.
4. **Map** each requirement → `reuse <path>` | `adapt <path>` | `new <file>`.
5. **Plan** (≤10 lines): files to create/change, order (data → API → UI → tests), checks to run, risks.
6. **Order of work:** smallest end-to-end slice first (one resource fully working), then breadth, then polish.

Output format:
```
Type: <template> · Skills: <list>
Req → impl: R1 reuse server/x.js · R2 new routes/items.js · …
Plan: 1… 2…
Assumptions: …
```
Don't write a long design doc. Don't start coding before the req→impl map exists.
