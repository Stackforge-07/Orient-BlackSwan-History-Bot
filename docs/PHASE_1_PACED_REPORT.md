# Phase 1 paced ingestion: PASS

## Model consistency gate (before modifying ingestion)

One stored chunk was re-embedded with `gemini-embedding-001` using `RETRIEVAL_DOCUMENT`.
Stored and new vectors both had 3,072 dimensions; cosine similarity was
1.000000000000; maximum absolute coordinate difference was
6.1603546153143895e-09. All 96 original stored vectors were checked for dimension:
all were 3,072-dimensional. The single re-embedding is a sample consistency check,
not independent historical model provenance for every vector. The existing
collection now records `embedding_model` and `embedding_dimension`; conflicting
or missing metadata is rejected instead of mixed or silently replaced.

## Real ingestion results

| Stage | New chunks | Existing chunks reused | Requests | 429s | Retries | Estimated tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| Probe | 20 | 96 | 3 | 0 | 0 | 4,672.50 | 39.102 |
| Remaining | 634 | 116 | 80 | 0 | 0 | 147,661.00 | 699.648 |

Combined measured ingestion-run time: **738.750 seconds
(12 minutes 18.750 seconds)**, including each run's model validation/extraction.
This excludes implementation/testing time and the separate one-chunk model check.
The 83 logged embedding requests exclude that separate consistency-check request.
Estimated tokens are characters divided by four, not provider-reported usage.
The 96 original chunks were reused and not re-embedded by the resumed ingestion.
The model consistency check intentionally re-embedded one stored chunk without
writing its replacement vector to the database.

## Independent offline final gate

- Stored count: **750**; splitter count: **750**; exact chunk ID sets match.
- Text-bearing pages represented: **90/90**. The image-only cover is explicitly
  reported and is excluded from the text-page coverage denominator.
- Every stored vector is **3,072-dimensional** and collection model metadata
  matches `gemini-embedding-001`.
- Repeating storage against the complete collection with an embedding function
  that raises on any call returned **0 new, 750 skipped**: no embedding calls.
- A completion manifest exists only after the full count/ID/page gate passed.

## Pacing and logging

The local settings are `EMBED_CHUNKS_PER_MIN=60` and
`EMBED_TOKENS_PER_MIN=20000`. The maximum observed rolling 60-second request-start
window contained **56 chunks** and
**13,565.50 estimated tokens**. SDK automatic
retries are disabled. Requests, errors, quota metadata and waits are logged to
`logs/embed.log` as JSON lines; `logs/` is Git-ignored.

A 429 honors the returned delay, falling back to 65 seconds, with jitter and
bounded exponential backoff. Maximum retries: five per batch. An explicitly daily
quota stops the run before another embedding attempt, reports the next midnight
Pacific in IST using the appropriate daylight-saving offset, and leaves existing
vectors intact. A provider change requires the user's decision; no local model
was substituted.

No 429 occurred in either paced run, so there is no new live 429 body, quota ID or
retry delay to report. The hypothesis of a 100-chunk-per-minute server limit
remains **unproven**: the historical failure body and HTTP timings were not saved.
Successful pacing supports using these conservative settings; it does not prove
the provider's exact cap or whether its accounting unit is an HTTP request or
an input chunk. No daily quota limit was observed.

## Offline tests and secret handling

`python -m pytest -q tests/test_embedding_runtime.py`: **11 passed** in both
project and clean environments. The clean environment's `pip check` also passed.
Tests cover daily stopping without a second request, Pacific/IST reset conversion
in summer and winter, full-body redaction, RetryInfo/Retry-After handling, 65-second
fallback, five-retry limit, rolling budgets, metadata mismatch, and bad dimensions.
These daily/429 tests use mocked responses, not live quota errors.

A credential found in `.env.example` was removed. The configured-key exact-match
scan passed for source, template and logs; the template key is empty. A credential
had appeared in inspection output, so that exposed value should be rotated.
No secret value is included in this report.

Phase 1 is complete. Phase 2 and Gemini generation/calibration were not started
by this embedding repair. Before later calibration/negative tests, the planned
Gemini call count must be shown and approved as requested.
