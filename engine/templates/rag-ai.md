# Template: rag-ai (LLM + optional retrieval)

**Use for:** chat with documents, Q&A with citations, summaries, quiz/flashcard generation, any LLM feature. **First:** grep the registry for existing Gemini/Qdrant/parsing modules — `doc-rag-chatbot` likely has them; reuse instead of rewriting.

## Create
```bash
engine/scripts/create-project.sh rag-ai ~/Desktop/<name> \
  --from ~/Desktop/doc-rag-chatbot --include "<paths from registry>"
cd ~/Desktop/<name>/server && npm install
docker run -d -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant   # only if retrieval needed
```

## Pipeline (each stage = one module; details in `rag-pipeline` skill)
```
upload → parse(text, pages) → chunk(~800–1200 chars, ~15% overlap, keep {docId, page})
       → embed(batch) → upsert Qdrant {id, vector, payload:{docId, page, text, filename}}
query  → embed(question) → search top-k(4–8) [filter docId] → prompt(context + numbered sources)
       → LLM → answer + citations [n] → client renders sources
```

## Env (names only — `server/.env.example`)
`GEMINI_API_KEY` · `QDRANT_URL` · `QDRANT_API_KEY` (cloud only) · `QDRANT_COLLECTION` · `PORT` · `CLIENT_ORIGIN`
Model names live in env or one config file, never scattered.

## API contract
`POST /api/documents` (multipart `file`) → `{docId, chunks}` ·
`GET /api/documents` · `DELETE /api/documents/:id` (deletes its points only, by payload filter) ·
`POST /api/chat {question, docIds?}` → `{answer, sources:[{n, filename, page, snippet}]}` (stream optional).

## No-retrieval variant
Skip Qdrant and embeddings: `llm.js` + route + UI. Don't run a vector DB you don't need.

## Done when
Upload → ask → cited answer works on a real PDF · no answer when context is empty ("not found in documents") · API key only on server · uploads have type/size limits.
