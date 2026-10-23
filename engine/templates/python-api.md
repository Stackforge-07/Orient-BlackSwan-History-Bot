# Template: python-api (FastAPI)

**Use for:** Python required, data/ML/automation backends, quick JSON APIs. Flask/Django only if the brief names them.

## Create (starter includes a passing test)
```bash
engine/scripts/create-project.sh python-api ~/Desktop/<name>
cd ~/Desktop/<name>
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m pytest -q
./.venv/bin/uvicorn app.main:app --reload --port 8000     # docs at /docs
```

## Structure
```
app/
  main.py          FastAPI(), include_router(...)
  routers/<x>.py   APIRouter(prefix="/api/x")
  schemas.py       Pydantic models (request/response)
  db.py            SQLite via sqlite3 or SQLModel; get_db dependency
  services/        logic without HTTP
tests/test_<x>.py  TestClient
```

## Conventions
- Pydantic validates input; raise `HTTPException(404, "not found")`.
- CORS: `CORSMiddleware(allow_origins=[os.getenv("CLIENT_ORIGIN","http://localhost:5173")])`.
- Files: `UploadFile` + check `content_type` and size. Auth: `python-jose`/`pyjwt` + `passlib[bcrypt]` only if required.
- AI: `google-genai` package (Gemini) with `GEMINI_API_KEY`; Qdrant: `qdrant-client`.

## Done when
`pytest -q` passes · `/docs` shows all endpoints · main flow works via curl or the UI.
