"""Offline tests: no provider calls, no real waits, no existing database writes."""

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google.genai.errors import APIError

import historybot.embedding_runtime as runtime
from historybot.config import Config, ConfigError
from historybot.ingest import validate_collection_metadata


def quota(window="Minute", delay=None, secret=""):
    details = [{"violations": [{"quotaMetric": "embed_content_requests",
                                "quotaId": f"EmbedRequestsPer{window}PerProject", "quotaValue": "100"}]}]
    if delay is not None:
        details.append({"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": f"{delay}s"})
    return {"error": {"code": 429, "message": "Quota exceeded " + secret, "details": details}}


def instance(monkeypatch, tmp_path, outcomes):
    client = Mock()
    client.models.embed_content.side_effect = outcomes
    monkeypatch.setattr(runtime.genai, "Client", Mock(return_value=client))
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    embeddings = runtime.GeminiEmbeddings(Config("test-secret", "chat", "embed", tmp_path / "catalogue.pdf"))
    embeddings.pacer = SimpleNamespace(acquire=lambda *_: 0)
    waits = []
    monkeypatch.setattr(runtime.time, "sleep", waits.append)
    monkeypatch.setattr(runtime.random, "uniform", lambda *_: 0.5)
    return embeddings, client, waits


def success():
    return SimpleNamespace(embeddings=[SimpleNamespace(values=[0.1] * 3072)])


def test_quota_windows_and_retry_delay():
    assert runtime.quota_details(quota("Day", 12))["window"] == "day"
    assert runtime.quota_details(quota(delay=12))["retry_delay_seconds"] == 12
    assert runtime.quota_details({"error": {"message": "429"}})["window"] == "unknown"
    assert runtime.quota_details(quota(), {"retry-after": "30"})["retry_delay_seconds"] == 30


@pytest.mark.parametrize("instant,expected", [
    ("2026-10-23T10:00:00+00:00", "2026-10-24 12:30 IST"),
    ("2026-12-23T10:00:00+00:00", "2026-12-24 13:30 IST"),
])
def test_daily_reset_honors_pacific_dst(instant, expected):
    assert expected in runtime.daily_reset_message(datetime.fromisoformat(instant))


def test_daily_exhaustion_stops_without_retry_and_redacts(monkeypatch, tmp_path):
    embed, client, waits = instance(monkeypatch, tmp_path, [APIError(429, quota("Day", secret="test-secret"))])
    with pytest.raises(ConfigError, match="Daily Gemini quota exhausted"):
        embed.embed_documents(["text"])
    assert client.models.embed_content.call_count == 1
    assert waits == []
    text = (tmp_path / "logs/embed.log").read_text()
    assert "test-secret" not in text and "[REDACTED]" in text
    errors = [json.loads(line) for line in text.splitlines() if json.loads(line)["status"] == "error"]
    assert errors[0]["window"] == "day"
    assert errors[0]["violations"][0]["quotaValue"] == "100"


@pytest.mark.parametrize("server_delay,expected_wait", [(12, 12.5), (None, 65.5)])
def test_minute_retry_wait_and_success(monkeypatch, tmp_path, server_delay, expected_wait):
    embed, client, waits = instance(monkeypatch, tmp_path, [APIError(429, quota(delay=server_delay)), success()])
    assert len(embed.embed_documents(["12345678"])[0]) == 3072
    assert waits == [expected_wait]
    assert client.models.embed_content.call_count == 2
    assert embed.retries == embed.errors_429 == 1
    assert embed.estimated_tokens == 4


def test_retry_budget_is_five_retries(monkeypatch, tmp_path):
    embed, client, waits = instance(monkeypatch, tmp_path, [APIError(429, quota()) for _ in range(6)])
    with pytest.raises(ConfigError, match="exhausted 5 retries"):
        embed.embed_documents(["text"])
    assert client.models.embed_content.call_count == 6
    assert len(waits) == 5


def test_pacer_respects_budgets_and_recovers_from_log(tmp_path):
    now = [datetime.now(timezone.utc).timestamp()]
    waits = []
    def sleep(seconds):
        waits.append(seconds)
        now[0] += seconds
    log = runtime.RequestLog(tmp_path / "embed.log", "secret")
    pacer = runtime.Pacer(60, 20000, log, clock=lambda: now[0], sleep=sleep)
    pacer.acquire(8, 2000)
    pacer.acquire(8, 2000)
    assert waits == [8.0]
    with pytest.raises(ConfigError, match="exceeds"):
        pacer.acquire(61, 1)
    log.write(status="request_started", batch_size=8, estimated_tokens=2000)
    restored = runtime.Pacer(60, 20000, log, clock=lambda: now[0]-8, sleep=sleep)
    assert len(restored.events) == 1


def test_token_budget_can_be_stricter_than_chunk_budget(tmp_path):
    now = [100.0]
    waits = []
    def sleep(seconds):
        now[0] += seconds
        waits.append(seconds)
    pacer = runtime.Pacer(60, 1000, runtime.RequestLog(tmp_path / "log", ""),
                          clock=lambda: now[0], sleep=sleep)
    pacer.acquire(1, 750)
    pacer.acquire(1, 750)
    assert waits[0] >= 60


def test_model_metadata_refuses_mixing():
    validate_collection_metadata({"embedding_model": "embed", "embedding_dimension": 3072}, "embed")
    with pytest.raises(ConfigError, match="Refusing to mix"):
        validate_collection_metadata({"embedding_model": "different", "embedding_dimension": 3072}, "embed")
    with pytest.raises(ConfigError):
        validate_collection_metadata({}, "embed")


def test_wrong_dimension_never_returns_vectors(monkeypatch, tmp_path):
    embed, client, waits = instance(monkeypatch, tmp_path, [SimpleNamespace(embeddings=[SimpleNamespace(values=[1.0])])])
    with pytest.raises(ConfigError, match="dimension mismatch"):
        embed.embed_documents(["text"])
    assert client.models.embed_content.call_count == 1
