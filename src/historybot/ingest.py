"""Resumable, document-scoped ingestion. Live validation is still required."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from historybot.config import ROOT, ConfigError, load_config, validate_models
from historybot.embedding_runtime import GeminiEmbeddings, redact
from historybot.extraction import chunk_pages, extract_pages


def store_chunks(store: Chroma, chunks: list[Document], *, limit: int | None = None,
                 batch_size: int = 8, token_budget: float = 20000) -> tuple[int, int]:
    """Skip durable IDs from prior batches, including a previously interrupted run."""
    existing = set(store.get(include=[])["ids"])
    missing = [c for c in chunks if c.metadata["chunk_id"] not in existing]
    selected = missing[:limit] if limit is not None else missing
    done = 0
    while done < len(selected):
        batch = []
        tokens = 0.0
        for chunk in selected[done:done + batch_size]:
            estimate = len(chunk.page_content) / 4
            if estimate > token_budget:
                raise ConfigError("A chunk exceeds EMBED_TOKENS_PER_MIN; increase the budget before retrying.")
            if tokens + estimate > token_budget:
                break
            tokens += estimate
            batch.append(chunk)
        store.add_documents(batch, ids=[c.metadata["chunk_id"] for c in batch])
        done += len(batch)
        print(f"Stored {done}/{len(selected)} new chunks; collection total {len(existing) + done}/{len(chunks)}; batch {len(batch)}; estimated tokens {tokens:.2f}", flush=True)
    expected = {c.metadata["chunk_id"] for c in selected}
    if not expected.issubset(set(store.get(include=[])["ids"])):
        raise ConfigError("Ingestion incomplete; rerun to resume missing batches.")
    return done, len(chunks) - len(missing)


def validate_collection_metadata(metadata: dict | None, model: str) -> None:
    metadata = metadata or {}
    if metadata.get("embedding_model") != model or metadata.get("embedding_dimension") != 3072:
        raise ConfigError("Collection embedding model/dimension metadata is missing or incompatible. Refusing to mix models; preserve the collection and verify it first.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-new-chunks", type=int, help="Embed only this many missing chunks for a probe")
    args = parser.parse_args()
    if args.max_new_chunks is not None and args.max_new_chunks <= 0:
        parser.error("--max-new-chunks must be positive")
    started = time.monotonic()
    embeddings = None
    config = None
    try:
        config = load_config()
        if not config.pdf_path.is_file():
            raise ConfigError(f"PDF missing: {config.pdf_path}")
        validate_models(config)
        pages = extract_pages(config.pdf_path)
        empty = [p.metadata["pdf_page"] for p in pages if not p.page_content.strip()]
        if empty:
            print(f"Warning: pages without extractable text: {empty}; OCR has not run.", file=sys.stderr)
        chunks = chunk_pages(pages)
        if not chunks:
            raise ConfigError("No extractable text; OCR is required before ingestion.")
        # Include extraction/chunk IDs and embedding model, preventing incompatible reuse.
        fingerprint = hashlib.sha256((config.embedding_model + "|" + "|".join(
            c.metadata["chunk_id"] for c in chunks)).encode()).hexdigest()
        collection = f"history-{fingerprint[:40]}"
        client = chromadb.PersistentClient(path=str(ROOT / "chroma_db"), settings=Settings(anonymized_telemetry=False))
        names = [c.name for c in client.list_collections()]
        if collection not in names:
            if any(client.get_collection(name).count() for name in names):
                raise ConfigError("The requested document/model does not match the existing collection. Refusing to replace or re-embed it without approval.")
            native = client.create_collection(collection, metadata={"embedding_model": config.embedding_model,
                                                                 "embedding_dimension": 3072})
        else:
            native = client.get_collection(collection)
        validate_collection_metadata(native.metadata, config.embedding_model)
        expected_ids = {c.metadata["chunk_id"] for c in chunks}
        previous_ids = set(native.get(include=[])["ids"])
        if not previous_ids.issubset(expected_ids):
            raise ConfigError("Collection contains chunk IDs outside the current splitter output; stopping without changes.")
        print(f"Before: {len(previous_ids)} existing chunks; {len(chunks)-len(previous_ids)} missing. Model: {config.embedding_model}; dimension: 3072", flush=True)
        embeddings = GeminiEmbeddings(config)
        store = Chroma(collection_name=collection, client=client, embedding_function=embeddings)
        new, skipped = store_chunks(store, chunks, limit=args.max_new_chunks,
                                   batch_size=max(1, min(8, math.floor(config.embed_chunks_per_min))),
                                   token_budget=config.embed_tokens_per_min)
        stored = native.get(include=["metadatas"])
        actual_ids = set(stored["ids"])
        complete = actual_ids == expected_ids and len(stored["ids"]) == len(chunks)
        pages_expected = {p.metadata["pdf_page"] for p in pages if p.page_content.strip()}
        pages_stored = {m["pdf_page"] for m in stored["metadatas"]}
        print(f"After: {len(actual_ids)}/{len(chunks)} chunks; pages represented {len(pages_stored)}/{len(pages_expected)}", flush=True)
        if args.max_new_chunks is not None and not complete:
            print(f"PROBE PASS: stored {new} new chunks; reused {skipped}; no completion manifest written.", flush=True)
            return 0
        if not complete or pages_stored != pages_expected:
            raise ConfigError("PHASE 1 GATE FAIL: exact chunk count/IDs or text-page coverage mismatch.")
        manifest = {"collection": collection, "document_hash": pages[0].metadata["document_hash"],
                    "embedding_model": config.embedding_model, "chunks": len(chunks)}
        target = ROOT / "chroma_db/manifest.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(manifest, indent=2))
        temporary.replace(target)
        print(f"Pages: {len(pages)}; chunks: {len(chunks)}; embedded: {new}; skipped: {skipped}")
        print("PHASE 1 GATE PASS: exact chunk IDs/count and all text-page coverage match.", flush=True)
        return 0
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        # Never echo provider exceptions: they may include credential-bearing requests.
        secret = config.api_key if config else ""
        print(f"Error: ingestion failed ({type(exc).__name__}): {redact(str(exc), secret)}", file=sys.stderr)
        return 1
    finally:
        if embeddings is not None:
            summary = embeddings.summary()
            summary["elapsed_seconds"] = round(time.monotonic() - started, 3)
            embeddings.log.write(status="run_summary", **summary)
            print("RUN SUMMARY: " + json.dumps(summary), flush=True)
            embeddings.close()


if __name__ == "__main__":
    raise SystemExit(main())
