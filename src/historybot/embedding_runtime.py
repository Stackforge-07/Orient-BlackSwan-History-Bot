"""Paced Gemini embeddings with one logged entry for each actual HTTP attempt."""

from __future__ import annotations

import json
import math
import random
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError
from langchain_core.embeddings import Embeddings

from historybot.config import ROOT, Config, ConfigError


def redact(text: str, secret: str) -> str:
    text = text.replace(secret, "[REDACTED]") if secret else text
    text = re.sub(r"AIza[\w-]{20,}", "[REDACTED]", text)
    return re.sub(r"(?i)([?&](?:key|api_key)=)[^&\s\"']+", r"\1[REDACTED]", text)


def quota_details(body: dict, headers: dict | None = None) -> dict:
    error = body.get("error", body)
    details = error.get("details", []) if isinstance(error, dict) else []
    violations = []
    delay = None
    for detail in details:
        violations.extend(detail.get("violations", []))
        raw_delay = detail.get("retryDelay")
        if isinstance(raw_delay, str) and re.fullmatch(r"\d+(?:\.\d+)?s", raw_delay):
            delay = float(raw_delay[:-1])
        elif isinstance(raw_delay, dict):
            delay = float(raw_delay.get("seconds", 0)) + float(raw_delay.get("nanos", 0)) / 1e9
    retry_after = (headers or {}).get("retry-after")
    if retry_after is not None:
        try:
            delay = max(delay or 0, float(retry_after))
        except ValueError:
            from email.utils import parsedate_to_datetime
            try:
                seconds = (parsedate_to_datetime(retry_after) - datetime.now(timezone.utc)).total_seconds()
                delay = max(delay or 0, seconds)
            except (ValueError, TypeError):
                pass
    # A numeric quotaValue alone does not tell us the quota window.
    labels = " ".join(str(v.get(k, "")) for v in violations
                      for k in ("quotaMetric", "quotaId", "description"))
    if not labels:
        labels = json.dumps(error)
    if re.search(r"per[ _-]*day|daily|\brpd\b", labels, re.I):
        window = "day"
    elif re.search(r"per[ _-]*minute|\brpm\b|\btpm\b", labels, re.I):
        window = "minute"
    else:
        window = "unknown"
    return {"window": window, "violations": violations, "retry_delay_seconds": delay}


def daily_reset_message(now: datetime | None = None) -> str:
    pacific = (now or datetime.now(timezone.utc)).astimezone(ZoneInfo("America/Los_Angeles"))
    tomorrow = pacific.date() + timedelta(days=1)
    reset = datetime.combine(tomorrow, datetime.min.time(), tzinfo=ZoneInfo("America/Los_Angeles"))
    local = reset.astimezone(ZoneInfo("Asia/Kolkata"))
    return f"Daily Gemini quota exhausted. Next midnight Pacific: {reset:%Y-%m-%d %H:%M %Z}; IST: {local:%Y-%m-%d %H:%M} IST. No further embedding calls."


class RequestLog:
    def __init__(self, path: Path, secret: str):
        self.path, self.secret = path, secret
        path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, **event) -> None:
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        line = redact(json.dumps(event, ensure_ascii=False, default=str), self.secret)
        with self.path.open("a") as stream:
            stream.write(line + "\n")
            stream.flush()


class Pacer:
    """Smooth spacing plus rolling-window budgets shared through the request log.

    A single ingestion process is supported. Concurrent writers are not supported.
    Attempts, including failed attempts, consume the local conservative budget.
    """

    def __init__(self, chunks_per_min: float, tokens_per_min: float, log: RequestLog,
                 clock: Callable[[], float] = time.time, sleep: Callable[[float], None] = time.sleep):
        if not all(math.isfinite(x) and x > 0 for x in (chunks_per_min, tokens_per_min)):
            raise ConfigError("EMBED_CHUNKS_PER_MIN and EMBED_TOKENS_PER_MIN must be positive finite numbers.")
        self.cpm, self.tpm, self.clock, self.sleep = chunks_per_min, tokens_per_min, clock, sleep
        self.events: list[tuple[float, int, float]] = []
        self.next_allowed = 0.0
        if log.path.exists():
            for line in log.path.read_text().splitlines():
                try:
                    e = json.loads(line)
                    if e.get("status") != "request_started":
                        continue
                    when = datetime.fromisoformat(e["timestamp"]).timestamp()
                    if when > clock() - 60:
                        self.events.append((when, e["batch_size"], e["estimated_tokens"]))
                        interval = 60 * max(e["batch_size"] / self.cpm, e["estimated_tokens"] / self.tpm)
                        self.next_allowed = max(self.next_allowed, when + interval)
                except (ValueError, KeyError, TypeError):
                    continue

    def acquire(self, chunks: int, tokens: float) -> float:
        if chunks > self.cpm or tokens > self.tpm:
            raise ConfigError("One embedding batch exceeds the configured minute budget; reduce batch size or increase the budget.")
        total_wait = 0.0
        while True:
            now = self.clock()
            self.events = [e for e in self.events if e[0] > now - 60]
            wait = max(0.0, self.next_allowed - now)
            if (sum(e[1] for e in self.events) + chunks > self.cpm or
                    sum(e[2] for e in self.events) + tokens > self.tpm):
                wait = max(wait, self.events[0][0] + 60.01 - now)
            if wait <= 0:
                self.events.append((now, chunks, tokens))
                self.next_allowed = now + 60 * max(chunks / self.cpm, tokens / self.tpm)
                return total_wait
            self.sleep(wait)
            total_wait += wait


class GeminiEmbeddings(Embeddings):
    def __init__(self, config: Config):
        self.config = config
        self.log = RequestLog(ROOT / "logs/embed.log", config.api_key)
        self.pacer = Pacer(config.embed_chunks_per_min, config.embed_tokens_per_min, self.log)
        self.run_id = uuid.uuid4().hex
        self.requests = self.successes = self.errors_429 = self.retries = 0
        self.estimated_tokens = self.successful_estimated_tokens = 0.0
        # Exactly one HTTP attempt per logged call; retry decisions live here.
        self.client = genai.Client(api_key=config.api_key, http_options=types.HttpOptions(
            timeout=30000, retry_options=types.HttpRetryOptions(attempts=1)))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]

    def _embed(self, texts: list[str], task: str) -> list[list[float]]:
        tokens = sum(len(t) for t in texts) / 4
        for attempt in range(6):
            paced = self.pacer.acquire(len(texts), tokens)
            self.requests += 1
            self.estimated_tokens += tokens
            common = {"run_id": self.run_id, "request": self.requests,
                      "model": self.config.embedding_model, "batch_size": len(texts),
                      "estimated_tokens": tokens, "attempt": attempt + 1}
            self.log.write(**common, status="request_started", pacing_seconds=paced)
            started = time.monotonic()
            try:
                result = self.client.models.embed_content(
                    model=self.config.embedding_model,
                    contents=[{"parts": [{"text": text}]} for text in texts],
                    config=types.EmbedContentConfig(task_type=task))
                vectors = [list(v.values) for v in result.embeddings or []]
                if len(vectors) != len(texts) or any(len(v) != 3072 for v in vectors):
                    raise ConfigError("Embedding response count/dimension mismatch; refusing to store vectors.")
                self.successes += 1
                self.successful_estimated_tokens += tokens
                self.log.write(**common, status="success", http_status=200, dimension=3072,
                               elapsed_seconds=time.monotonic() - started)
                return vectors
            except APIError as exc:
                response = exc.response
                raw = getattr(response, "text", None)
                if not isinstance(raw, str):
                    raw = json.dumps(exc.details, default=str)
                try:
                    body = json.loads(raw)
                except ValueError:
                    body = {"error": {"message": raw}}
                headers = dict(getattr(response, "headers", {}) or {})
                quota = quota_details(body, headers)
                self.log.write(**common, status="error", http_status=exc.code,
                               error_body=raw, **quota, elapsed_seconds=time.monotonic() - started)
                if exc.code == 429:
                    self.errors_429 += 1
                    if quota["window"] == "day":
                        message = daily_reset_message()
                        self.log.write(run_id=self.run_id, status="daily_exhaustion", message=message)
                        raise ConfigError(message) from None
                    delay = quota["retry_delay_seconds"]
                    delay = 65.0 if delay is None else delay
                elif exc.code in (408, 500, 502, 503, 504):
                    delay = 2 ** attempt
                else:
                    raise ConfigError(f"Gemini HTTP {exc.code}; see the redacted logs/embed.log error body.") from None
            except httpx.TransportError:
                self.log.write(**common, status="network_error", elapsed_seconds=time.monotonic() - started)
                delay = 2 ** attempt
            except ConfigError:
                self.log.write(**common, status="invalid_embedding_response")
                raise
            if attempt == 5:
                raise ConfigError("Embedding batch exhausted 5 retries; see logs/embed.log. Stored chunks are preserved.")
            delay = max(delay, 2 ** attempt) + random.uniform(0, 3)
            self.retries += 1
            self.log.write(**common, status="retry_wait", wait_seconds=delay)
            print(f"Retry {attempt + 1}/5: waiting {delay:.2f}s; details in logs/embed.log", flush=True)
            time.sleep(delay)
        raise AssertionError("Unreachable")

    def summary(self) -> dict:
        return {"run_id": self.run_id, "requests": self.requests, "successful_requests": self.successes,
                "http_429s": self.errors_429, "retries": self.retries,
                "estimated_tokens_attempted": self.estimated_tokens,
                "estimated_tokens_successful": self.successful_estimated_tokens}

    def close(self) -> None:
        self.client.close()
