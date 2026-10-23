"""Local configuration and live model discovery; secret values never displayed."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TypeVar

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
T = TypeVar("T")


class ConfigError(ValueError):
    """An actionable configuration error safe to show to the user."""


def retry(operation: Callable[[], T]) -> T:
    """Bounded exponential backoff; do not include server errors or keys in logs."""
    import httpx
    from google.genai.errors import APIError
    from langchain_google_genai._common import GoogleGenerativeAIError

    for attempt in range(4):
        try:
            return operation()
        except (httpx.TransportError, APIError, GoogleGenerativeAIError) as exc:
            cause = exc.__cause__ if isinstance(exc, GoogleGenerativeAIError) and exc.__cause__ else exc
            code = getattr(cause, "code", None)
            transient = isinstance(cause, httpx.TransportError) or code in (408, 429, 500, 502, 503, 504)
            if not transient or attempt == 3:
                reason = "quota/rate limit" if code == 429 else "network or API access"
                raise ConfigError(f"Gemini {reason} failed. Check connectivity, key access and quota; then retry.") from None
            time.sleep(2 ** attempt)
    raise AssertionError("Unreachable")


@dataclass(frozen=True)
class Config:
    api_key: str = field(repr=False)
    model: str
    embedding_model: str
    pdf_path: Path
    embed_chunks_per_min: float = 60
    embed_tokens_per_min: float = 20000


def load_config() -> Config:
    load_dotenv(ROOT / ".env", override=False)
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not key:
        raise ConfigError("GOOGLE_API_KEY is not set. Add it to the local .env; never paste it into chat.")
    pdf = Path(os.getenv("PDF_PATH", "data/History_2024-25.pdf"))
    if not pdf.is_absolute():
        pdf = ROOT / pdf
    try:
        cpm = float(os.getenv("EMBED_CHUNKS_PER_MIN", "60"))
        tpm = float(os.getenv("EMBED_TOKENS_PER_MIN", "20000"))
    except ValueError:
        raise ConfigError("Embedding minute budgets must be numbers.") from None
    return Config(key, os.getenv("GEMINI_MODEL", "").strip().removeprefix("models/"),
                  os.getenv("GEMINI_EMBED_MODEL", "").strip().removeprefix("models/"), pdf, cpm, tpm)


def validate_models(config: Config) -> None:
    from google import genai
    from google.genai import types

    with genai.Client(api_key=config.api_key, http_options=types.HttpOptions(timeout=30000)) as client:
        models = retry(lambda: list(client.models.list()))
    chat, embed = [], []
    for model in models:
        name = (model.name or "").removeprefix("models/")
        actions = model.supported_actions or []
        if "generateContent" in actions:
            chat.append(name)
        if "embedContent" in actions:
            embed.append(name)
    if config.model not in chat or config.embedding_model not in embed:
        raise ConfigError(
            "Set valid GEMINI_MODEL and GEMINI_EMBED_MODEL in .env. "
            f"Available generation models: {', '.join(sorted(chat)) or '(none)'}. "
            f"Available embedding models: {', '.join(sorted(embed)) or '(none)'}."
        )
