# Example project requests

## A. Exam CRUD (copy, edit, paste into Claude Code)
```
Use the engine. Exam mode, 3 hours.
Build a Library Management System:
R1 Admin login. R2 Add/edit/delete/list books (title, author, ISBN unique, copies).
R3 Add members. R4 Issue and return books; copies decrease/increase; cannot issue when 0.
R5 Search books by title/author. Stack: React + Express, any DB.
Deliverables: source + README with run steps + screenshots.
Create it at ~/Desktop/library-app.
```
Expected routing (`engine/scripts/route-task.sh`): `fullstack-crud` + backend-api, database-auth, frontend-ui, exam-fast-build.

Expected agent output (short):
```
Type: fullstack-crud · Skills: …
Req → impl: R1 new middleware/auth.js (+ seed admin) · R2 new routes/books.js · R4 transaction in routes/loans.js …
Plan: 1 create-project … 2 schema.sql … 3 books API+UI … 4 members … 5 loans … 6 auth … 7 verify
```

## B. RAG feature on the existing repo
```
Use the engine. In doc-rag-chatbot add "Generate 10 flashcards from a selected document".
Reuse the existing Gemini + Qdrant modules. Show cards in a flip UI. Don't touch existing chat behaviour.
```
Expected routing: `rag-ai` + rag-pipeline, backend-api, frontend-ui.

## C. Python API
```
Use the engine. FastAPI service that accepts a CSV upload and returns column stats as JSON, with tests.
```
Expected routing: `python-api` + backend-api.
