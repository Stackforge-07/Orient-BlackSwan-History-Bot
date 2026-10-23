# Orient BlackSwan History Bot

**Phase 1 complete: 750/750 chunks and 90/90 text pages verified.**
This repository currently contains the original engine toolkit and the start of
the Python project. It is not ready for submission. No final QA answers are claimed; live embedding results are documented below.

See [the audit](docs/PHASE_0_AUDIT.md) for the actual engine inspection,
PDF page count, extraction comparison, and limitations.

## Intended flow

```mermaid
flowchart LR
    A[PDF] --> B[Pages and metadata]
    B --> C[Overlapping chunks]
    C --> D[Gemini embeddings]
    D --> E[ChromaDB]
    E --> F[Vector and lexical retrieval]
    F --> G[Grounded Gemini answer]
    G --> H[Quote and page verification]
    H --> I[Answer with source or Not found]
```

The verification gate will require quoted evidence on the cited retrieved page.
The QA pipeline and its negative-set evaluation have not been implemented yet.

## Local setup status

The project virtual environment is `.venv`, created using Python 3.12.14.
Dependencies are installed and pinned in `requirements.txt`; `pip check` passes.
A second fresh-environment installation succeeded; its `pip check` and project/library imports pass.

The catalogue is in `data/History_2024-25.pdf`; it is deliberately excluded from
Git. For a future clone, obtain the same catalogue and place it at that path.

A local `.env` contains the variable names from `.env.example`. Fill in
`GOOGLE_API_KEY` locally; never commit or share its value. Generation and embedding
model IDs must be verified against the account's live model list; no defaults
have been guessed.

Install from a clone with `python -m pip install -r requirements.txt`.
Then run:

```bash
source .venv/bin/activate
python scripts/audit_pdf.py
python scripts/check_env.py
python -m historybot.ingest
```

The audit command writes raw page/chunk JSON into the Git-ignored
`data/extracted/` directory. The environment checker reports whether the key is
set, without printing it, and lists accessible model IDs if configured IDs are
missing or invalid.

## Remaining deliverables

Phase 2 keyword evidence and ground truth, QA,
live evaluation, unit tests, 
submission answers, screenshot commands and user-captured images, secret scans,
and the GitHub repository are still pending. No screenshot placeholders are
presented as real captures.

## Current limitations

The image-only cover has no extracted text and no OCR fallback has run. The
other 90 pages contain extractable text. Page labels and visibly printed page
numbers differ; metadata stores them separately. Column ordering was sampled
on three pages, not exhaustively verified for every entry. Some rupee signs
extract as backticks. Unknown section headings remain blank rather than guessed.

## Paced ingestion and quota handling

The original run stored 96 of 750 chunks before a quota/rate-limit error.
Before resuming, one stored chunk was re-embedded: both vectors have 3,072
dimensions and their cosine similarity was 1.000000000000. All 96 existing
vectors have 3,072 dimensions. This is a sample consistency check, not independent
proof of the original model provenance for each vector. The collection now records
the verified model name and dimension and refuses incompatible settings.

Configure the local `.env`:

```dotenv
EMBED_CHUNKS_PER_MIN=60
EMBED_TOKENS_PER_MIN=20000
```

Estimated tokens are characters divided by four, not provider-reported usage.
Requests are smoothly spaced and checked against rolling minute budgets for
both chunks and estimated tokens. These are conservative client budgets; they
do not assert that the server counts each chunk as a separate request. Only one
ingestion process should run at a time. Recent logged attempts carry the pacing
budget between invocations. Failed attempts consume the conservative local budget.

Every actual embedding attempt is recorded in Git-ignored `logs/embed.log` with
UTC time, run/request identifiers, batch size, estimated tokens and status.
Provider retries are disabled so no HTTP attempts bypass this log. Error records
include the full redacted body, returned quota identifiers, window classification,
and server retry delay. The log does not contain prompts, chunks or the API key.

A 429 waits for the server's retry delay, or 65 seconds if none is returned,
plus jitter and bounded exponential backoff. There are at most five retries per
batch. A quota explicitly identified as daily stops immediately, reports the next
midnight in `America/Los_Angeles` converted to IST (including daylight saving),
and makes no further embedding calls in that run. An unclassified 429 is reported
as unknown rather than guessed to be daily. A daily exhaustion requires the user's
choice before changing to local embeddings. No collection is wiped automatically.

```bash
python -m historybot.ingest --max-new-chunks 20  # probe missing chunks only
python -m historybot.ingest                    # resume remaining chunks
```

The probe reused all 96 stored IDs, added 20 chunks, and finished with 116 total:
three successful requests, zero 429s/retries, 4,672.5 estimated tokens, 39.102
seconds including extraction. The remaining 634 chunks completed under the same limits: 80 successful requests,
zero 429s/retries, 147,661 estimated tokens, and 699.648 seconds. A completion manifest is written only if the stored chunk count
and exact ID set equal the splitter output and every text page is represented.
That check passed: 750/750 exact chunk IDs and 90/90 text pages. An independent
offline repeat skipped all 750 chunks without an embedding call. Phase 2 has not
started during this embedding repair.

Verified before stopping: clean install from the pinned requirements, imports
in the clean environment, and `pip check` in both environments. A source-file
key-pattern scan found no matches outside the excluded local `.env` and generated
data. No Git repository or Git history exists yet.

Full pacing results and limitations: [Phase 1 report](docs/PHASE_1_PACED_REPORT.md).
The probe and remaining run together embedded 654 new chunks in 83 requests,
with zero 429s/retries, 152,333.5 estimated tokens and 738.750 measured seconds.
