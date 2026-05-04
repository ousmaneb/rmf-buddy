"""Tool definitions for the agentic Claude loop.

Each tool maps to a deterministic lookup over the local NIST/CCI database.
The schemas are sent to Claude; `dispatch()` runs the actual call.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any

from .emass_kb import get_topic, list_topics, lookup_term
from .grc_kb import (
    get_topic as grc_get_topic,
    list_topics as grc_list_topics,
    lookup_term as grc_lookup_term,
)
from .nist_kb import get_publication, list_publications
from .retrieval import search
from .web import ALLOWED_DOMAIN_SUFFIXES, web_fetch as _web_fetch, web_search as _web_search

DB_PATH = Path(__file__).resolve().parents[1] / "rmf.db"


def _con() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# ---------- tool implementations ----------

def search_controls(query: str, limit: int = 6) -> dict:
    """Semantic search over controls + CCIs (does not include eMASS knowledge)."""
    hits = search(query, k_controls=limit, k_ccis=limit)
    con = _con()
    controls = []
    for cid, score in hits["controls"]:
        r = con.execute(
            "SELECT id, label, family_name, title FROM controls WHERE id=?", (cid,)
        ).fetchone()
        if r:
            controls.append({"id": r["id"], "label": r["label"], "title": r["title"],
                             "family": r["family_name"], "score": round(score, 3)})
    ccis = []
    for cid, score in hits["ccis"]:
        r = con.execute(
            "SELECT id, definition, control_id, control_index FROM ccis WHERE id=?", (cid,)
        ).fetchone()
        if r:
            ccis.append({"id": r["id"], "definition": r["definition"][:240],
                         "control": r["control_id"], "score": round(score, 3)})
    return {"controls": controls, "ccis": ccis}


def get_control(control_id: str) -> dict:
    con = _con()
    cid = control_id.lower()
    r = con.execute("SELECT * FROM controls WHERE id=?", (cid,)).fetchone()
    if not r:
        return {"error": f"control {control_id} not found"}
    baselines = [b[0] for b in con.execute(
        "SELECT baseline FROM baselines WHERE control_id=?", (cid,)).fetchall()]
    ccis = [dict(r2) for r2 in con.execute(
        "SELECT id, definition, control_index FROM ccis WHERE control_id=? ORDER BY id", (cid,)
    ).fetchall()]
    enhancements = [{"id": x[0], "label": x[1], "title": x[2]} for x in con.execute(
        "SELECT id, label, title FROM controls WHERE parent_id=? ORDER BY id", (cid,)
    ).fetchall()]
    return {
        "id": r["id"], "label": r["label"], "title": r["title"],
        "family": r["family_name"], "is_enhancement": bool(r["is_enhancement"]),
        "parent_id": r["parent_id"],
        "statement": r["statement"], "discussion": r["guidance"],
        "assessment_objectives": r["assessment"],
        "baselines": baselines, "ccis": ccis, "enhancements": enhancements,
    }


def get_cci(cci_id: str) -> dict:
    r = _con().execute("SELECT * FROM ccis WHERE id=?", (cci_id.upper(),)).fetchone()
    if not r:
        return {"error": f"CCI {cci_id} not found"}
    return dict(r)


def list_controls_in_family(family: str, baseline: str | None = None) -> dict:
    con = _con()
    sql = ("SELECT c.id, c.label, c.title FROM controls c "
           "JOIN baselines b ON b.control_id=c.id "
           "WHERE c.family=? AND b.baseline=? ORDER BY c.is_enhancement, c.id"
           if baseline else
           "SELECT id, label, title FROM controls WHERE family=? ORDER BY is_enhancement, id")
    params = (family.lower(), baseline.upper()) if baseline else (family.lower(),)
    rows = con.execute(sql, params).fetchall()
    return {"family": family.lower(), "baseline": baseline,
            "controls": [{"id": r["id"], "label": r["label"], "title": r["title"]} for r in rows]}


def find_related_controls(control_id: str, k: int = 5) -> dict:
    """Use the control's full text as a query to find semantically nearby controls."""
    con = _con()
    r = con.execute("SELECT full_text, label FROM controls WHERE id=?",
                    (control_id.lower(),)).fetchone()
    if not r:
        return {"error": f"control {control_id} not found"}
    hits = search(r["full_text"][:600], k_controls=k + 1, k_ccis=0)
    related = []
    for cid, score in hits["controls"]:
        if cid == control_id.lower():
            continue
        rc = con.execute("SELECT id, label, title FROM controls WHERE id=?", (cid,)).fetchone()
        if rc:
            related.append({"id": rc["id"], "label": rc["label"], "title": rc["title"],
                            "score": round(score, 3)})
        if len(related) >= k:
            break
    return {"control": r["label"], "related": related}


def get_assessment_procedures(control_id: str) -> dict:
    r = _con().execute("SELECT label, title, assessment FROM controls WHERE id=?",
                       (control_id.lower(),)).fetchone()
    if not r:
        return {"error": f"control {control_id} not found"}
    return {"control": r["label"], "title": r["title"],
            "assessment_objectives": r["assessment"] or "(none in catalog)"}


# ---------- eMASS knowledge tools ----------

def search_emass(query: str, limit: int = 5) -> dict:
    """Semantic search over the eMASS knowledge base (topics + glossary)."""
    from .retrieval import _model, _index  # type: ignore
    import numpy as np
    mat, meta = _index()
    qvec = _model().encode([query], normalize_embeddings=True)[0].astype(np.float32)
    sims = mat @ qvec
    out_topics: list[dict] = []
    out_terms: list[dict] = []
    # Collect best hits per kind
    topic_hits = sorted(
        ((sims[i], meta[i]) for i in range(len(meta)) if meta[i][0] == "emass_topic"),
        key=lambda x: -x[0],
    )[:limit]
    term_hits = sorted(
        ((sims[i], meta[i]) for i in range(len(meta)) if meta[i][0] == "emass_term"),
        key=lambda x: -x[0],
    )[:limit]
    for score, m in topic_hits:
        t = get_topic(m[1]) or {}
        out_topics.append({"slug": m[1], "title": t.get("title", ""),
                           "category": t.get("category", ""), "score": round(float(score), 3)})
    for score, m in term_hits:
        d = lookup_term(m[1])
        if d:
            out_terms.append({"term": d["term"], "definition": d["definition"],
                              "score": round(float(score), 3)})
    return {"topics": out_topics, "terms": out_terms}


def get_emass_topic(slug: str) -> dict:
    t = get_topic(slug)
    if not t:
        return {"error": f"unknown eMASS topic: {slug}"}
    return t


def lookup_emass_term(term: str) -> dict:
    d = lookup_term(term)
    if not d:
        return {"error": f"term {term!r} not in glossary"}
    return d


def list_emass_topics() -> dict:
    return {"topics": list_topics()}


# ---------- GRC knowledge tools ----------

def search_grc(query: str, limit: int = 5) -> dict:
    """Semantic search over the GRC knowledge base (topics + glossary)."""
    from .retrieval import _model, _index  # type: ignore
    import numpy as np
    mat, meta = _index()
    qvec = _model().encode([query], normalize_embeddings=True)[0].astype(np.float32)
    sims = mat @ qvec
    out_topics: list[dict] = []
    out_terms: list[dict] = []
    topic_hits = sorted(
        ((sims[i], meta[i]) for i in range(len(meta)) if meta[i][0] == "grc_topic"),
        key=lambda x: -x[0],
    )[:limit]
    term_hits = sorted(
        ((sims[i], meta[i]) for i in range(len(meta)) if meta[i][0] == "grc_term"),
        key=lambda x: -x[0],
    )[:limit]
    for score, m in topic_hits:
        t = grc_get_topic(m[1]) or {}
        out_topics.append({"slug": m[1], "title": t.get("title", ""),
                           "category": t.get("category", ""), "score": round(float(score), 3)})
    for score, m in term_hits:
        d = grc_lookup_term(m[1])
        if d:
            out_terms.append({"term": d["term"], "definition": d["definition"],
                              "score": round(float(score), 3)})
    return {"topics": out_topics, "terms": out_terms}


def get_grc_topic(slug: str) -> dict:
    t = grc_get_topic(slug)
    if not t:
        return {"error": f"unknown GRC topic: {slug}"}
    return t


def lookup_grc_term(term: str) -> dict:
    d = grc_lookup_term(term)
    if not d:
        return {"error": f"term {term!r} not in GRC glossary"}
    return d


def list_grc_topics() -> dict:
    return {"topics": grc_list_topics()}


# ---------- NIST publication library tools ----------

def get_nist_publication(slug: str) -> dict:
    p = get_publication(slug)
    if not p:
        return {"error": f"unknown publication: {slug}"}
    return p


def list_nist_publications() -> dict:
    return {"publications": list_publications()}


# ---------- MITRE ATT&CK tools ----------

def get_attack_techniques_for_control(control_id: str) -> dict:
    """List all ATT&CK techniques that the given 800-53 control mitigates (CTID mapping)."""
    cid = control_id.lower()
    rows = _con().execute(
        "SELECT technique_id, technique_name, comment FROM attack_mappings WHERE control_id=? ORDER BY technique_id",
        (cid,),
    ).fetchall()
    return {
        "control": cid,
        "techniques": [
            {"id": r["technique_id"], "name": r["technique_name"], "rationale": r["comment"]}
            for r in rows
        ],
    }


def get_controls_for_technique(technique_id: str) -> dict:
    """List all 800-53 controls that mitigate the given ATT&CK technique (e.g. 'T1078' or 'T1556.009')."""
    tid = technique_id.upper()
    con = _con()
    rows = con.execute(
        "SELECT m.control_id, m.technique_name, m.comment, c.label, c.title "
        "FROM attack_mappings m LEFT JOIN controls c ON c.id = m.control_id "
        "WHERE m.technique_id = ? ORDER BY m.control_id",
        (tid,),
    ).fetchall()
    if not rows:
        return {"error": f"no mappings for technique {tid}"}
    return {
        "technique": {"id": tid, "name": rows[0]["technique_name"]},
        "controls": [
            {"id": r["control_id"], "label": r["label"] or r["control_id"].upper(),
             "title": r["title"] or "(unknown)", "rationale": r["comment"]}
            for r in rows
        ],
    }


def search_attack_techniques(query: str, limit: int = 10) -> dict:
    """Search ATT&CK techniques by name (substring match across the mapped technique catalog)."""
    rows = _con().execute(
        "SELECT DISTINCT technique_id, technique_name FROM attack_mappings "
        "WHERE LOWER(technique_name) LIKE ? OR technique_id LIKE ? "
        "ORDER BY technique_id LIMIT ?",
        (f"%{query.lower()}%", f"{query.upper()}%", limit),
    ).fetchall()
    return {"techniques": [{"id": r["technique_id"], "name": r["technique_name"]} for r in rows]}


def compare_controls(control_a: str, control_b: str) -> dict:
    a = get_control(control_a)
    b = get_control(control_b)
    if "error" in a:
        return a
    if "error" in b:
        return b
    return {"a": a, "b": b}


# ---------- registry ----------

TOOLS_SCHEMA = [
    {
        "name": "search_controls",
        "description": ("Semantic search over the NIST 800-53 Rev. 5 catalog + DoD CCI list. "
                        "Use when the user asks a natural-language question and you don't yet "
                        "know which controls or CCIs are relevant. Returns labels + titles only - "
                        "follow up with get_control for full text."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural-language search query"},
                "limit": {"type": "integer", "description": "Max results per kind (default 6)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_control",
        "description": ("Fetch the full record for one control or enhancement: statement (with "
                        "parameters resolved), discussion, baselines, linked CCIs, enhancements, "
                        "and assessment objectives."),
        "input_schema": {
            "type": "object",
            "properties": {
                "control_id": {"type": "string",
                               "description": "Control id like 'ac-2' or 'ac-2.1' (lowercase)"},
            },
            "required": ["control_id"],
        },
    },
    {
        "name": "get_cci",
        "description": "Fetch a single CCI by ID (e.g. 'CCI-000001').",
        "input_schema": {
            "type": "object",
            "properties": {"cci_id": {"type": "string"}},
            "required": ["cci_id"],
        },
    },
    {
        "name": "list_controls_in_family",
        "description": ("List all controls in a family (e.g. 'AC', 'AU'), optionally filtered to a "
                        "baseline (LOW/MODERATE/HIGH). Use for scoping questions."),
        "input_schema": {
            "type": "object",
            "properties": {
                "family": {"type": "string", "description": "Two-letter family code (e.g. 'ac')"},
                "baseline": {"type": "string", "enum": ["LOW", "MODERATE", "HIGH"]},
            },
            "required": ["family"],
        },
    },
    {
        "name": "find_related_controls",
        "description": "Find controls semantically similar to a given control. Useful for cross-references.",
        "input_schema": {
            "type": "object",
            "properties": {
                "control_id": {"type": "string"},
                "k": {"type": "integer", "description": "Number of related controls (default 5)"},
            },
            "required": ["control_id"],
        },
    },
    {
        "name": "get_assessment_procedures",
        "description": ("Get the NIST 800-53A-style assessment objectives for a control, used by "
                        "Security Control Assessors to plan testing."),
        "input_schema": {
            "type": "object",
            "properties": {"control_id": {"type": "string"}},
            "required": ["control_id"],
        },
    },
    {
        "name": "search_emass",
        "description": ("Search the eMASS knowledge base - curated topics covering the RMF lifecycle "
                        "in eMASS, roles, package types (ATO/IATT/ATC/cATO), POA&M, inheritance, type "
                        "authorization, reciprocity, ConMon, common documents, workflows, and common "
                        "findings - plus a ~60-term glossary. Use whenever the user asks about eMASS "
                        "concepts, workflows, roles, or terminology that is NOT a 800-53 control."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "description": "Max hits per kind (default 5)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_emass_topic",
        "description": "Fetch the full body of one eMASS knowledge topic by slug (use search_emass to discover slugs).",
        "input_schema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "lookup_emass_term",
        "description": "Look up an eMASS / RMF acronym or term in the glossary (e.g. 'ATO', 'POA&M', 'CCP').",
        "input_schema": {
            "type": "object",
            "properties": {"term": {"type": "string"}},
            "required": ["term"],
        },
    },
    {
        "name": "list_emass_topics",
        "description": "List every eMASS knowledge topic with its title and category. Useful for orientation.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_grc",
        "description": ("Search the GRC (Governance, Risk & Compliance) knowledge base - "
                        "topics on frameworks (NIST CSF, ISO 27001, SOC 2, PCI-DSS, HIPAA, GDPR, "
                        "SOX, FedRAMP, CMMC, HITRUST), risk concepts (inherent/residual/appetite), "
                        "Three Lines of Defense, audit types, third-party risk, data classification, "
                        "incident management, GRC tooling - plus a 70+ term glossary. Use whenever "
                        "the user asks about non-RMF compliance frameworks, governance, or risk theory."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_grc_topic",
        "description": "Fetch the full body of one GRC topic by slug.",
        "input_schema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "lookup_grc_term",
        "description": "Look up a GRC / compliance acronym or term (e.g. 'SOC 2', 'GDPR', 'ITGC', 'inherent risk').",
        "input_schema": {
            "type": "object",
            "properties": {"term": {"type": "string"}},
            "required": ["term"],
        },
    },
    {
        "name": "list_grc_topics",
        "description": "List every GRC knowledge topic (frameworks, risk, audit, governance, tooling).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_nist_publications",
        "description": "List the NIST publication library entries (800-37, 800-53, 800-53A, 800-53B, 800-60, FIPS 199/200, CNSSI 1253, etc.).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_nist_publication",
        "description": "Fetch a NIST publication summary by slug (use list_nist_publications to discover slugs).",
        "input_schema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "get_attack_techniques_for_control",
        "description": ("List the MITRE ATT&CK techniques that a given 800-53 control mitigates, "
                        "per the MITRE Center for Threat-Informed Defense mapping. Use when the "
                        "user asks about threat coverage of a specific control."),
        "input_schema": {
            "type": "object",
            "properties": {"control_id": {"type": "string"}},
            "required": ["control_id"],
        },
    },
    {
        "name": "get_controls_for_technique",
        "description": ("List the 800-53 controls that mitigate a given ATT&CK technique "
                        "(e.g. 'T1078', 'T1110', 'T1556.009'). Use when the user asks 'which controls "
                        "defend against X' where X is an attack tactic."),
        "input_schema": {
            "type": "object",
            "properties": {"technique_id": {"type": "string"}},
            "required": ["technique_id"],
        },
    },
    {
        "name": "search_attack_techniques",
        "description": "Search ATT&CK techniques by name (e.g. 'phishing', 'credential dumping').",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "compare_controls",
        "description": "Fetch two controls together for side-by-side comparison.",
        "input_schema": {
            "type": "object",
            "properties": {
                "control_a": {"type": "string"},
                "control_b": {"type": "string"},
            },
            "required": ["control_a", "control_b"],
        },
    },
]

# ---------- Firecrawl-backed live web tools ----------

TOOLS_SCHEMA.extend([
    {
        "name": "web_fetch",
        "description": (
            "Fetch the live content of a single URL via Firecrawl, returned as clean markdown. "
            "Use this when our local snapshot might be stale or when the user needs the very "
            "latest version of a NIST publication, a STIG, or an ATT&CK page. "
            f"URL must be on the allow-list (suffixes: {', '.join(ALLOWED_DOMAIN_SUFFIXES)})."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "web_search",
        "description": (
            "Web search via Firecrawl, results filtered to authoritative allow-listed domains "
            f"({', '.join(ALLOWED_DOMAIN_SUFFIXES)}). Use to discover URLs to then web_fetch."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "description": "Default 5"},
            },
            "required": ["query"],
        },
    },
])


DISPATCH = {
    "search_controls": search_controls,
    "get_control": get_control,
    "get_cci": get_cci,
    "list_controls_in_family": list_controls_in_family,
    "find_related_controls": find_related_controls,
    "get_assessment_procedures": get_assessment_procedures,
    "compare_controls": compare_controls,
    "search_emass": search_emass,
    "get_emass_topic": get_emass_topic,
    "lookup_emass_term": lookup_emass_term,
    "list_emass_topics": list_emass_topics,
    "search_grc": search_grc,
    "get_grc_topic": get_grc_topic,
    "lookup_grc_term": lookup_grc_term,
    "list_grc_topics": list_grc_topics,
    "list_nist_publications": list_nist_publications,
    "get_nist_publication": get_nist_publication,
    "get_attack_techniques_for_control": get_attack_techniques_for_control,
    "get_controls_for_technique": get_controls_for_technique,
    "search_attack_techniques": search_attack_techniques,
    "web_fetch": _web_fetch,
    "web_search": _web_search,
}


def dispatch(name: str, args: dict[str, Any]) -> Any:
    fn = DISPATCH.get(name)
    if not fn:
        return {"error": f"unknown tool {name}"}
    try:
        return fn(**args)
    except TypeError as e:
        return {"error": f"bad arguments for {name}: {e}"}


# ---------- OpenAI function-calling schema adapter ----------

def _to_openai_tool(t: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }


OPENAI_TOOLS_SCHEMA = [_to_openai_tool(t) for t in TOOLS_SCHEMA]
