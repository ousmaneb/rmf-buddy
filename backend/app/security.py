"""Security middleware and helpers for the RMF Buddy backend.

Threat model: this server is intended to run on localhost only. It binds
127.0.0.1 (see hook script) and trusts the local user. The hardening here
defends against:
    - Browser-based exploits if the backend is ever exposed (CORS, headers).
    - Prompt injection from web content fetched by the agent (text sanitizer).
    - Cost / DoS via oversized chat payloads (request size + length caps).
    - Information leakage via verbose errors / `Server` header.

It does NOT add user authentication: that is out of scope for a single-user
local dev tool. If you decide to deploy this server publicly, add auth and
revisit allowed origins.
"""
from __future__ import annotations
import hmac
import os
import re
from typing import Iterable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ---------- CORS / origins ----------

# Strict allow-list of origins. The frontend dev server is on 5173.
ALLOWED_ORIGINS: tuple[str, ...] = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",  # vite preview
    "http://127.0.0.1:4173",
)


# ---------- Request limits (DoS / cost protection) ----------

MAX_CHAT_MESSAGE_CHARS = 8_000        # per-message cap
MAX_CHAT_TOTAL_CHARS = 80_000         # full-conversation cap sent to LLM
MAX_CHAT_TURNS = 40                   # number of turns per request
MAX_TEMPLATE_CTX_VALUE_CHARS = 1_000  # template fill-in field cap


# ---------- Security headers middleware ----------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply baseline security headers to every response.

    Notes:
      - CSP is only relevant for HTML responses, but we set it anyway as
        defense in depth. The API serves JSON exclusively.
      - HSTS is omitted because this is HTTP-only on localhost. Add it if
        you front this with TLS.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        h = response.headers
        h["X-Content-Type-Options"] = "nosniff"
        h["X-Frame-Options"] = "DENY"
        h["Referrer-Policy"] = "no-referrer"
        h["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        # Restrictive CSP: only same-origin, no inline scripts, no eval.
        # Allows connect to the same origin (the API itself).
        h["Content-Security-Policy"] = (
            "default-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'; "
            "form-action 'none'"
        )
        # Hide framework version surface.
        if "server" in h:
            del h["server"]
        return response


# ---------- Cross-site request guard + optional local token ----------

# Every request the frontend makes carries this header. Browsers cannot add a
# custom header to a cross-site request without a CORS preflight, and the
# preflight only succeeds for ALLOWED_ORIGINS. So requiring it on
# state-changing / paid requests blocks CSRF-style abuse from other websites
# (e.g. a hidden form or `fetch(..., {mode: "no-cors"})` that would otherwise
# spend LLM credits).
CSRF_HEADER = "x-rmf-buddy"
# Optional shared secret. Off unless RMF_BUDDY_TOKEN is set. When set, every
# /api request (except /api/health and CORS preflights) must send it in
# X-RMF-Buddy-Token. The Vite dev/preview proxy injects it server-side from
# the same variable, so the token never ships in the browser bundle.
TOKEN_HEADER = "x-rmf-buddy-token"
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
_TOKEN_EXEMPT_PATHS = frozenset({"/api/health"})


def _local_token() -> str:
    # Read lazily so backend/.env (loaded by app.llm) and test overrides apply.
    return os.environ.get("RMF_BUDDY_TOKEN", "").strip()


class LocalRequestGuardMiddleware:
    """Pure-ASGI middleware (safe with streaming responses)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope.get("path", "").startswith("/api/"):
            return await self.app(scope, receive, send)
        method = scope.get("method", "GET").upper()
        if method == "OPTIONS":
            return await self.app(scope, receive, send)
        headers = {k.decode("latin-1").lower(): v.decode("latin-1")
                   for k, v in scope.get("headers", [])}

        token = _local_token()
        if token and scope["path"] not in _TOKEN_EXEMPT_PATHS:
            supplied = headers.get(TOKEN_HEADER, "")
            if not hmac.compare_digest(supplied.encode(), token.encode()):
                return await _deny(scope, receive, send, 401, "missing or invalid token")

        if method not in _SAFE_METHODS and headers.get(CSRF_HEADER) != "1":
            return await _deny(scope, receive, send, 403, "missing X-RMF-Buddy header")

        return await self.app(scope, receive, send)


async def _deny(scope, receive, send, status: int, detail: str) -> None:
    resp = JSONResponse(status_code=status, content={"detail": detail})
    await resp(scope, receive, send)


# ---------- Prompt injection sanitizer for tool results ----------

# Strip ASCII control chars except for whitespace, and the Unicode tag /
# variation selectors / bidi controls that have been used in prompt-injection
# tricks.
_CONTROL_CHARS_RE = re.compile(
    r"[\x00-\x08\x0b-\x0c\x0e-\x1f"     # ASCII control chars (keep \t \n \r)
    r"\x7f"                              # DEL
    r"-"                     # C1 control chars
    r"​-‏"                     # zero-width / bidi marks
    r"‪-‮"                     # bidi override
    r"⁦-⁩"                     # bidi isolate
    r"⁪-⁯"                     # deprecated formatting
    r"￹-￻"                     # interlinear annotation
    r"\U000e0000-\U000e007f"             # Unicode Tags block (TaggedString attack)
    r"]"
)


def sanitize_untrusted_text(text: str, max_chars: int = 30_000) -> str:
    """Sanitize text from an untrusted source (web fetch, scraped page) before
    passing it to the LLM as a tool result.

    Removes hidden / formatting / tag Unicode characters that have been used
    to smuggle prompt-injection payloads invisibly, and caps length.
    """
    if not isinstance(text, str):
        return ""
    cleaned = _CONTROL_CHARS_RE.sub("", text)
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n\n[...truncated for length]"
    return cleaned


# ---------- Tool argument validation ----------

# Per-tool argument allowlist with type + length caps. The LLM-provided
# arguments are validated against these BEFORE dispatch, so a hallucinated /
# adversarial argument can't trigger arbitrary behavior.

_ID_RE = re.compile(r"^[A-Za-z0-9._\-+()]{1,40}$")          # control / cci / slug ids
_TECH_RE = re.compile(r"^T[0-9.]{1,12}$")                    # ATT&CK technique
_BASELINE_RE = re.compile(r"^(LOW|MODERATE|HIGH)$")
_FAMILY_RE = re.compile(r"^[a-zA-Z]{1,4}$")                  # 'ac', 'au', 'cm'...

# (validator, max_len) per field name.
_FIELD_RULES: dict[str, tuple[re.Pattern[str] | None, int]] = {
    # ID-shaped fields
    "control_id": (_ID_RE, 40),
    "control_a": (_ID_RE, 40),
    "control_b": (_ID_RE, 40),
    "cci_id": (_ID_RE, 40),
    "slug": (_ID_RE, 60),
    "term": (None, 80),
    "family": (_FAMILY_RE, 4),
    "baseline": (_BASELINE_RE, 8),
    "technique_id": (_TECH_RE, 12),
    # Free-text fields (queries, URLs)
    "query": (None, 500),
    "url": (None, 2_000),
    # Bounded numerics handled separately
    "limit": (None, 0),
    "k": (None, 0),
}

_INT_FIELDS = {"limit", "k"}
_INT_MAX = {"limit": 50, "k": 25}


def validate_tool_args(name: str, args: dict) -> dict:
    """Validate and normalize tool arguments. Returns sanitized args, or raises
    ValueError on violation. Unknown keys are dropped silently."""
    if not isinstance(args, dict):
        raise ValueError("arguments must be an object")
    out: dict = {}
    for key, val in args.items():
        if key not in _FIELD_RULES:
            # Drop unknown keys rather than passing them to the function.
            continue
        if key in _INT_FIELDS:
            try:
                n = int(val)
            except (TypeError, ValueError):
                raise ValueError(f"{key} must be an integer")
            if n < 1 or n > _INT_MAX[key]:
                raise ValueError(f"{key} must be between 1 and {_INT_MAX[key]}")
            out[key] = n
            continue
        if not isinstance(val, str):
            raise ValueError(f"{key} must be a string")
        # Length cap per field
        rule = _FIELD_RULES[key]
        max_len = rule[1]
        if max_len and len(val) > max_len:
            raise ValueError(f"{key} too long (max {max_len})")
        # Pattern check (skip for free-text)
        pattern = rule[0]
        if pattern is not None and not pattern.match(val):
            raise ValueError(f"{key} has an unexpected format")
        out[key] = val
    return out


# ---------- Error sanitizer ----------

async def sanitized_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Generic 500 handler that never leaks stack traces or internal paths."""
    # Log internally; respond with a stable message externally.
    import traceback, sys
    print("[exception]", repr(exc), file=sys.stderr)
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "internal server error"},
    )


def install(app: FastAPI) -> None:
    """Install all security middleware and exception handlers on the app."""
    app.add_middleware(LocalRequestGuardMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_exception_handler(Exception, sanitized_exception_handler)
