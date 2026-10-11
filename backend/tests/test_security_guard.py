"""Tests for the cross-site request guard and optional local token.

Run from backend/:  python -m pytest -q
"""
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("RMF_BUDDY_TOKEN", raising=False)
    monkeypatch.setattr(
        main, "_json_only_chat",
        lambda **kw: '{"scenario": "s", "expected_controls": ["AC-7"], "rationale": "r"}',
    )
    return TestClient(main.app, base_url="http://127.0.0.1")


def test_scenario_get_no_longer_allowed(client):
    r = client.get("/api/study/scenario")
    assert r.status_code == 405


def test_scenario_post_requires_custom_header(client):
    r = client.post("/api/study/scenario", json={"family": "ac"})
    assert r.status_code == 403


def test_scenario_post_with_header_ok(client):
    r = client.post("/api/study/scenario", json={"family": "ac"},
                    headers={"X-RMF-Buddy": "1"})
    assert r.status_code == 200
    assert r.json()["expected_controls"] == ["AC-7"]


def test_scenario_post_without_body_ok(client):
    r = client.post("/api/study/scenario", headers={"X-RMF-Buddy": "1"})
    assert r.status_code == 200


def test_scenario_family_length_capped(client):
    r = client.post("/api/study/scenario", json={"family": "x" * 50},
                    headers={"X-RMF-Buddy": "1"})
    assert r.status_code == 422


def test_other_posts_require_header(client):
    for path in ("/api/study/grade", "/api/chat/stream"):
        assert client.post(path, content=b"{}").status_code == 403


def test_get_works_without_header_when_no_token(client):
    assert client.get("/api/health").status_code == 200


def test_foreign_host_rejected(client):
    r = client.get("/api/health", headers={"Host": "evil.example"})
    assert r.status_code == 400


def test_token_enforced_when_set(client, monkeypatch):
    monkeypatch.setenv("RMF_BUDDY_TOKEN", "s3cret-test-token")
    hdr = {"X-RMF-Buddy": "1"}
    assert client.post("/api/study/scenario", headers=hdr).status_code == 401
    bad = {**hdr, "X-RMF-Buddy-Token": "wrong"}
    assert client.post("/api/study/scenario", headers=bad).status_code == 401
    good = {**hdr, "X-RMF-Buddy-Token": "s3cret-test-token"}
    assert client.post("/api/study/scenario", headers=good).status_code == 200
    # Health stays open for liveness checks.
    assert client.get("/api/health").status_code == 200


def test_cors_preflight_allows_custom_headers(client):
    r = client.options(
        "/api/study/scenario",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-rmf-buddy",
        },
    )
    assert r.status_code == 200


def test_cors_preflight_rejects_foreign_origin(client):
    r = client.options(
        "/api/study/scenario",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-rmf-buddy",
        },
    )
    assert "access-control-allow-origin" not in r.headers
