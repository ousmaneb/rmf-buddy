"""LLM client. Uses OpenRouter (OpenAI-compatible) for chat completions."""
from __future__ import annotations
import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI

# Load backend/.env if present. Idempotent.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o")


@lru_cache(maxsize=1)
def client() -> OpenAI:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise HTTPException(500, "OPENROUTER_API_KEY is not set on the server (backend/.env).")
    return OpenAI(
        api_key=key,
        base_url=OPENROUTER_BASE_URL,
        # OpenRouter recommends these headers for routing/attribution
        default_headers={
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "RMF Buddy",
        },
    )


def model() -> str:
    return DEFAULT_MODEL
