"""Firecrawl wrapper - domain-allow-listed web fetch + search."""
from __future__ import annotations
import os
from urllib.parse import urlparse

import httpx

# Allow-list: hostname must end with one of these.
ALLOWED_DOMAIN_SUFFIXES = (
    "nist.gov",
    "cyber.mil",
    "mitre.org",
    "cnss.gov",
    "disa.mil",
)

FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"


def _key() -> str | None:
    return os.environ.get("FIRECRAWL_API_KEY") or None


def _domain_allowed(url: str) -> bool:
    """SSRF guard. Reject anything that isn't an https:// URL on a hostname
    that is exactly, or a subdomain of, an allow-listed authoritative domain.

    Defensive notes:
      - Force https only (Firecrawl can follow http -> https on its end, but we
        refuse outbound http to prevent passive-network MITM injection).
      - Reject URLs with userinfo (`https://attacker@victim.com/`) which can
        spoof allow-list checks if a parser splits them differently.
      - Lowercase + strip trailing dot before matching.
    """
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme != "https":
        return False
    if p.username or p.password:
        return False
    host = (p.hostname or "").lower().rstrip(".")
    if not host:
        return False
    # Reject IP literals (catches https://10.0.0.1/, https://[::1]/, etc.)
    if host.replace(".", "").isdigit() or host.startswith("[") or ":" in host:
        return False
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAIN_SUFFIXES)


def web_fetch(url: str) -> dict:
    """Fetch a single URL via Firecrawl. Returns markdown + metadata, or an error dict."""
    if not _key():
        return {"error": "FIRECRAWL_API_KEY not set on server"}
    if not isinstance(url, str) or len(url) > 2_000:
        return {"error": "invalid url"}
    if not url.startswith("https://"):
        return {"error": "url must start with https://"}
    if not _domain_allowed(url):
        return {
            "error": (
                f"domain not on allow-list. Allowed suffixes: "
                f"{', '.join(ALLOWED_DOMAIN_SUFFIXES)}"
            )
        }
    try:
        r = httpx.post(
            f"{FIRECRAWL_BASE}/scrape",
            headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
            timeout=45,
        )
        r.raise_for_status()
        data = r.json()
        # Firecrawl returns { success, data: { markdown, metadata: {...} } }
        payload = data.get("data") or {}
        md = payload.get("markdown", "")
        meta = payload.get("metadata") or {}
        return {
            "url": url,
            "title": meta.get("title") or meta.get("ogTitle") or "",
            "markdown": md[:30000],
            "truncated": len(md) > 30000,
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"Firecrawl HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": f"Firecrawl request failed: {e}"}


def web_search(query: str, limit: int = 5) -> dict:
    """Web search via Firecrawl. Results are filtered to the allow-list."""
    if not _key():
        return {"error": "FIRECRAWL_API_KEY not set on server"}
    try:
        r = httpx.post(
            f"{FIRECRAWL_BASE}/search",
            headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
            json={"query": query, "limit": max(limit * 3, 10)},
            timeout=45,
        )
        r.raise_for_status()
        data = r.json()
        raw = data.get("data") or []
        # Each item typically has { url, title, description }
        results = []
        for item in raw:
            url = item.get("url") or ""
            if not _domain_allowed(url):
                continue
            results.append({
                "url": url,
                "title": item.get("title", ""),
                "description": item.get("description", "")[:300],
            })
            if len(results) >= limit:
                break
        return {
            "query": query,
            "results": results,
            "note": (
                "Results filtered to allow-listed authoritative domains: "
                + ", ".join(ALLOWED_DOMAIN_SUFFIXES)
            ),
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"Firecrawl HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": f"Firecrawl search failed: {e}"}
