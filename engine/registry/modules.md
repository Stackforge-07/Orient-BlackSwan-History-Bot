# Module Registry

> **Status: NOT YET POPULATED for doc-rag-chatbot.** The engine was built without access to the repo, so no entries are listed — nothing here is guessed.
> Populate it (one time, ~2 min + review):
> ```bash
> engine/scripts/inspect-project.sh . --registry > engine/registry/modules.draft.md
> ```
> Then ask Claude Code: *"Load the code-reuse skill. Verify modules.draft.md against the source, fill purpose/reuse/limits, set status implemented|partial|missing only from evidence (running or tests), group by area below, and write the result here."*

Search: `grep -n -i "<keyword>" engine/registry/modules.md`

## Entry format
```
### <Name> — `path/to/file` · status: implemented|partial|missing · tests: none|unit|manual-verified
- exports: …        - deps: … · env: VAR_NAMES
- reuse: …          - limits: …
```

## Areas (fill under each)
### Backend: server, routes, middleware, auth
### AI: Gemini client, prompts, generation
### RAG: parsing, chunking, embeddings, Qdrant, retrieval, citations
### Documents: upload, storage, listing, deletion
### Study features: summaries, quizzes, flashcards
### Voice
### Frontend: components, hooks, pages, API client
### Utilities & config
### Missing / UI-only (named in UI but no working implementation found)
