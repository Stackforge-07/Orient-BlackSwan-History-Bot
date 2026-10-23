---
name: rag-pipeline
description: Build or reuse a retrieval-augmented generation pipeline — document parsing, chunking, embeddings, Qdrant vector storage, retrieval and cited LLM answers (Gemini by default). Use for chat-with-documents, semantic search, summaries or study tools over uploaded files.
---
# RAG pipeline

## Reuse first
`grep -n -i -E "qdrant|embed|gemini|chunk|pdf|parse|citation" engine/registry/modules.md`. In `doc-rag-chatbot`, reuse its verified client/embedding/parsing modules rather than re-creating them. Mark anything untested as such.

## Stages & contracts
| Stage | Contract | Notes |
|---|---|---|
| parse | `parse(buffer, mime) → [{page, text}]` | PDF: `pdf-parse`/`pdfjs-dist` (Node), `pypdf` (Py); DOCX: `mammoth`. Scanned PDFs need OCR — say so, don't fake it. |
| chunk | `chunk(pages) → [{text, page, idx}]` | ~800–1200 chars, ~15% overlap, split on paragraph/sentence; keep page. |
| embed | `embed(texts[]) → number[][]` | Batch; one model for docs AND queries. Gemini: `gemini-embedding-001` via `@google/genai` / `google-genai`; dimension must equal the collection's. |
| store | upsert `{id: uuid, vector, payload:{docId, filename, page, idx, text}}` | Create collection if missing (Cosine). Payload index on `docId`. **Never recreate/delete an existing collection** — a dimension mismatch means a new collection name. |
| retrieve | `search(qVec, k=6, filter docId?) → hits` | Drop hits below a score threshold; dedupe neighbours. |
| generate | prompt with numbered context `[1] (file p.3) text…` | Instruct: answer only from context, cite `[n]`, say "not found in the documents" otherwise. |
| respond | `{answer, sources:[{n, filename, page, snippet}]}` | Map only cited `[n]` to sources. |

## Config (env names)
`GEMINI_API_KEY`, `GEMINI_MODEL` (chat model — check Google's current model list; don't hardcode across files), `EMBEDDING_MODEL`, `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION`.

## Study features (built on the same retrieval)
Summary (map-reduce over chunks) · quiz/flashcards (ask the model for JSON, validate with a schema, retry once on parse failure) · voice (browser Web Speech API for STT/TTS — no server cost; check support, Safari differs).

## Safety & cost
Key server-side only · upload size/type limits · rate-limit `/chat` · truncate context to model limits · log token usage if available · delete a document = delete points by `docId` filter, not the collection.

## Verify
Ingest a real 2–5 page PDF → `count` points > 0 → ask a question answerable from page N → citation shows page N → ask an off-topic question → "not found". Record results in the registry entry.
