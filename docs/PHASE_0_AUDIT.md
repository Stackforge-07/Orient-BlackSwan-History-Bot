# Phase 0 audit

Status: source catalogue inspected; Phase 1 is in progress. This is not a completed submission.

## Existing engine

Ran `bash engine/scripts/inspect-project.sh . --tree 4` before creating files.
The scan reported 37 files: 32 Markdown and 5 shell scripts, no dependency
manifests, no application entry points, and zero tests. The module registry
states that it was created without access to the referenced `doc-rag-chatbot`.
There is no executable RAG implementation in the supplied kit to reuse.

Reused guidance: page metadata, overlapping chunks, batched embeddings,
document-scoped storage, grounded answers, and checking real command results.
The kit's Node/Qdrant defaults and fallback wording do not meet this assignment;
the new application uses the requested Python/LangChain/ChromaDB stack.
No Gemini model ID will be taken from the kit's examples.

## Catalogue

Source: `data/History_2024-25.pdf` (local, excluded from Git at the user's request).
The actual file has **91 pages**. Its embedded labels are `i`, `ii`, `iii`, then
`1` through `88`. These are PDF labels, not necessarily visible printed numbers.
For example, PDF page 40 visibly says `HISTORY 37`, while PDF page 2 has no
visible printed page number. Both fields must be stored separately.

All pages except PDF page 1 have extractable text. The first page is an image-only
cover. It was rendered and visually inspected; no OCR executable was found.
The pipeline reports that page explicitly and does not invent extracted text.
OCR coverage is therefore incomplete, limited to that cover.

Rendered and inspected PDF pages 1, 2, 4, 83, and 91. Page 4 uses separate book
panels; the index uses three columns. Page 91 is mostly blank but contains the
price-update footer. Listings combine publication year, ISBN, price, extent,
and binding on a line. The rupee glyph often extracts as a backtick: raw evidence
must not silently be rewritten to a different quote.

Compared pypdf with pdfplumber on PDF pages 4, 40, and 83. Native pypdf extraction
keeps the sampled entries/columns in reading order. Default pdfplumber geometric
ordering interleaves three columns on page 40, mixing unrelated text and prices.
Selected pypdf. The comparison is a sample check, not proof that every book
entry in the catalogue is perfectly reconstructed. Some extracted text contains
layout/file-production artifacts and repeated headers or footers.

## Environment and remaining gates

Bundled Python 3.12.14 was available; shell-default Python was 3.14. A local
`.venv` was created with Python 3.12. No Git repository existed at audit time.
A local `.env` was created only if absent, with empty key/model fields, and
excluded from Git. The user's secret must be configured locally.

Initial sandbox package access failed DNS resolution. An authorized network
retry reached the package index but timed out downloading optional PyMuPDF.
A retry omitting that unnecessary package was started. Installation, exact
version pinning, import checks, and `pip check` must be verified before claiming
the environment works.

Phase 1 cannot pass until real Gemini model listing, embedding, persistent
Chroma ingestion, and resumability are verified. Ground truth (Phase 2), QA,
live evaluation, final tests, screenshots, and GitHub publication are not done.

## Phase 1 progress

Installed and pinned dependencies; `pip check` reports no broken requirements.
Verified installed embedding interfaces and model metadata fields. Added fonttools
to decode the catalogue Type1 fonts and reran extraction without the missing-font
warnings. Result: 91 pages, 90 with text, 750 chunks, average 927.9 characters,
full text-page coverage; 11 chunks have no detectable section.

Live model listing succeeded after granting network access. Selected
`gemini-2.5-flash` and `gemini-embedding-001` from the returned available models.
The environment checker then passed without displaying the secret.

A real local Chroma smoke check using fake embeddings passed: insert one chunk,
resume two more, repeat the completed set; exactly three embeddings in total.
This verifies local resume/skip behavior, not live Gemini embedding correctness.
Live catalogue ingestion and a second clean install are in progress.

## Gate result

Live ingestion stored 96/750 chunks and then exhausted retries on a Gemini
quota/rate-limit failure. Phase 1 failed; work on later phases is stopped.
Persisted chunks are retained for resuming. No completed manifest was written.

## Final checks before stopping

The second fresh virtual environment installed `requirements.txt` successfully.
Its `pip check` reported no broken requirements; imports of the project, Chroma,
Gemini embeddings, and text splitter passed. Confirmed persisted collection count:
96; completion manifest absent. Source-file key-pattern scan: no matches outside
excluded local secrets/generated data. Git history scan is not applicable because
no repository exists. No Phase 2 ground truth or later-phase results are claimed.

## Paced resumption completed

The subsequent paced resumption passed Phase 1: 750/750 chunk IDs, all vectors
3,072-dimensional, 90/90 text pages. The original 96 chunks were preserved.
See [the paced-run report](PHASE_1_PACED_REPORT.md) for measured timing, request
counts, tests and quota limitations. Prior blocked-status entries above describe
the earlier run, not the current state.
