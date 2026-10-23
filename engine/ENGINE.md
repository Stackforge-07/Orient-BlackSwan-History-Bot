# ENGINE

Reuse-first, token-lean toolkit for building projects from existing code. Deterministic scripts do mechanical work; on-demand skills hold the judgment.

## Layout
| Path | Load when |
|---|---|
| `CLAUDE.md` (repo root) | always (kept short) |
| `engine/PROJECT_TYPES.md` | choosing a stack when `route-task.sh` says `(decide)` |
| `engine/templates/<t>.md` | after routing — exactly one |
| `engine/skills/<s>/SKILL.md` | only the skills routing lists |
| `engine/registry/modules.md` | grep it; never read whole when large |
| `engine/registry/dependencies.md` | adding a package |
| `engine/registry/commands.md` | need a run/build/test command |
| `engine/checklists/*.md` | requirements intake, security pass, before handing in |
| `engine/scripts/*.sh` | see below |

## Scripts (all `--help`)
| Script | Does | Writes? |
|---|---|---|
| `inspect-project.sh [dir] [--registry] [--tree N]` | stack/manifests/scripts/env names/infra summary; `--registry` drafts module list | no |
| `route-task.sh "<text>"` | template + skills for a request | no |
| `setup-project.sh [dir] [--install] [--env]` | install plan from lockfiles; `--install` runs it; `--env` creates missing `.env` from example | only with flags; never overwrites |
| `verify-project.sh [dir] [--only X] [--dry-run]` | runs defined typecheck/lint/test/build; exit 0 pass · 1 fail · 3 nothing ran | logs in `$TMPDIR` |
| `create-project.sh <tpl> <dest> [--from src --include a,b]` | new project + engine + starter; reuses chosen files only | new dir only |

## Workflow (every project)
1. **Intake** — requirements, deliverables, constraints → `checklists/requirements.md`.
2. **Route** — `route-task.sh`; override if requirements say otherwise.
3. **Inspect** — `inspect-project.sh`; grep registry; open only relevant files.
4. **Template** — smallest that fits; don't force React/Node/RAG.
5. **Skills** — load only routed ones.
6. **Plan** — ≤10 lines: files to add/change, reused modules, checks.
7. **Implement** — core first, focused patches, no rewrites of working files.
8. **Verify** — `verify-project.sh` + manual smoke of the main flow.
9. **Run commands** — exact, copy-pasteable.
10. **Report** — works / unverified / missing. Update registry with new reusable modules.

## Token rules
- Paths + contracts, not pasted code. Don't reread unchanged files. Don't re-explain documented architecture.
- One scan via script > many exploratory tool calls. Subagents only for isolated, parallel analysis returning short findings.
- No large generated docs. Summaries: files changed, checks run, blockers.
- These reduce wasted context; no specific saving is guaranteed.

## Safety (non-negotiable)
Never read/print secrets · only `.env.example` with names · never delete/reset Qdrant, uploads, backups · no silent overwrites · no paid services unless required.
