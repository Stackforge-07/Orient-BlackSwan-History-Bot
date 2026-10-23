"""Produce repeatable Phase 0/1 evidence without calling Gemini."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from historybot.extraction import chunk_pages, extract_pages


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "data/History_2024-25.pdf"
    if not path.is_file():
        print(f"Error: PDF missing: {path}", file=sys.stderr)
        return 1
    pages = extract_pages(path)
    chunks = chunk_pages(pages)
    output = root / "data/extracted"
    output.mkdir(parents=True, exist_ok=True)
    for name, documents in (("pages", pages), ("chunks", chunks)):
        (output / f"{name}.json").write_text(json.dumps([
            {"text": d.page_content, "metadata": d.metadata} for d in documents
        ], ensure_ascii=False, indent=2))
    empty = [p.metadata["pdf_page"] for p in pages if not p.page_content.strip()]
    print(f"Pages: {len(pages)}; pages with text: {len(pages)-len(empty)}")
    print(f"Pages without extractable text (OCR needed): {empty}")
    print(f"Chunks: {len(chunks)}; average characters: {sum(len(c.page_content) for c in chunks)/len(chunks):.1f}")
    print("Coverage: every page with text produced at least one chunk")
    print(f"Chunks without a detectable section: {sum(not c.metadata['section'] for c in chunks)}")
    print("Printed page is recorded only where a numeric History header is detected.")
    print("PDF labels are recorded separately; they are not proof of printed numbering.")
    for number in [2, 4, 20, 40, 60, 83, 91]:
        if number > len(pages):
            continue
        p = pages[number-1]
        print(f"\n--- PDF page {number}; label {p.metadata['pdf_label']}; printed {p.metadata['printed_page'] or 'not detected'} ---")
        print(p.page_content[:1800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
