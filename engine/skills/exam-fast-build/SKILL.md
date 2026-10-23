---
name: exam-fast-build
description: Exam/assignment mode — deliver every required feature as a minimal complete working app fast, reusing engine templates and registry modules, then polish, verify and disclose gaps honestly. Use when the user gives an exam question, practical, assignment or a deadline.
---
# Exam fast-build

## 0. Timebox (state it)
~10% plan · 60% core features · 15% verify/fix · 15% polish + README. If time is short, cut polish, never required features or verification.

## 1. Requirements lock (5 min)
Number every required feature **verbatim** from the brief (R1…Rn), plus deliverables (code, README, screenshots, report, viva notes) and constraints (stack, DB, no internet?). Ambiguity → pick the simplest reasonable reading and write it under "Assumptions".

## 2. Route & reuse
`engine/scripts/route-task.sh "<brief>"` → one template. Grep registry for each Rn. Required stack overrides defaults.

## 3. Build order
1. Starter: `engine/scripts/create-project.sh <tpl> <dest>`; get `/api/health` + blank page running.
2. Data model + one resource end-to-end (DB → API → UI) — prove the stack works.
3. Remaining required features, one at a time, each verified in the browser before the next.
4. Auth/roles if required (database-auth skill).
5. Only then: polish (consistent layout, nav, feedback messages, seed data for demo).

## 4. Quality floor (non-negotiable)
Server-side validation · no secrets in code/repo · parameterised queries · passwords hashed · errors shown to user, not swallowed · `verify-project.sh` run · main flow smoke-tested.

## 5. Hand-in
- `engine/checklists/final-submission.md`.
- README: what it is, features (R1…Rn ✓/✗), tech stack, setup + run commands, env var names, test command, assumptions.
- Seed/demo data and demo credentials (clearly marked demo-only).
- Final report to user:
```
Done: R1 ✓ R2 ✓ R3 ✓(manual) R4 ✗ (reason)
Run: <exact commands>
Checks: verify-project → <real result>
Not verified / limits: …
```
Never mark a requirement ✓ that wasn't exercised.
