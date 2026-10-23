# Final push: blocked at Priority 2 live QA gate

Completed locally:
- Secret scanner checks working files and tracked files plus all commits reachable from all refs and reflogs; no secret values are printed.
- Priority 1 ground truth with all keyword matches and quoted lines is committed.
- Retrieval-only calibration: all 7 verified positive pages retrieved; 13/18 negatives bypass generation at threshold 0.596218667. No generation used for calibration.
- QA implementation includes hybrid retrieval, JSON schema, exact quote/page verification, disk response caching, call preflight, --max-calls, pacing, retries and daily-quota handling.
- Offline tests: 20 passed in 1.33 seconds.

## Live failure (unmodified provider body, contains no credential)

```json
{
  "error": {
    "code": 404,
    "message": "This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.8-flash for the latest features and improvements. We recommend you to use the Interactions API (https://ai.google.dev/gemini-api/docs/get-started).",
    "status": "NOT_FOUND"
  }
}
```

The 25-case evaluation printed a plan of 12 uncached generation calls with a
40-call guard. Its first generation request failed with HTTP 404. No successful
generation responses were received; no answer-accuracy or negative-set QA pass
is claimed. Model listing had accepted the configured name, but the generation
endpoint rejected it. The provider named gemini-3.8-flash as a replacement.

Stopped here under the user's gate-failure instruction. No automatic model
switch, extra provider probe, UI work or fabricated screenshot was performed.
The next action is to validate an available generation replacement, change only
GEMINI_MODEL, and rerun the same evaluation. The embedding model and 750 stored
vectors must be preserved.

Priority 3 Streamlit, Priority 4 browser proof/screenshots, final submission
answers/README completion and final verification remain unfinished. Nothing has
been pushed. This WIP is not ready for submission.
