"""Parse NIST 800-53 Rev 5 OSCAL catalog + DoD CCI List into SQLite, then embed."""
from __future__ import annotations
import json
import re
import sqlite3
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DB_PATH = ROOT / "backend" / "rmf.db"

CCI_NS = {"c": "http://iase.disa.mil/cci"}

FAMILY_NAMES = {}  # filled from groups


def init_db(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS controls;
        DROP TABLE IF EXISTS ccis;
        DROP TABLE IF EXISTS baselines;
        DROP TABLE IF EXISTS embeddings;

        CREATE TABLE controls (
            id          TEXT PRIMARY KEY,        -- e.g. 'ac-2' or 'ac-2.1'
            label       TEXT NOT NULL,           -- 'AC-2' or 'AC-2(1)'
            family      TEXT NOT NULL,           -- 'ac'
            family_name TEXT NOT NULL,           -- 'Access Control'
            title       TEXT NOT NULL,
            is_enhancement INTEGER NOT NULL,
            parent_id   TEXT,
            statement   TEXT,                    -- flattened control statement (params resolved)
            guidance    TEXT,
            assessment  TEXT,                    -- flattened assessment objectives (800-53A style)
            full_text   TEXT NOT NULL            -- everything for retrieval
        );
        CREATE INDEX idx_controls_family ON controls(family);

        CREATE TABLE ccis (
            id          TEXT PRIMARY KEY,        -- 'CCI-000001'
            definition  TEXT NOT NULL,
            type        TEXT,
            control_id  TEXT,                    -- mapped 800-53r5 control id (lowercase, e.g. 'ac-1')
            control_index TEXT                   -- raw index like 'AC-1 a'
        );
        CREATE INDEX idx_ccis_ctrl ON ccis(control_id);

        CREATE TABLE baselines (
            control_id  TEXT NOT NULL,
            baseline    TEXT NOT NULL,           -- LOW / MODERATE / HIGH
            PRIMARY KEY (control_id, baseline)
        );

        CREATE TABLE attack_mappings (
            control_id   TEXT NOT NULL,           -- normalized 800-53r5 id (e.g. 'cm-3')
            technique_id TEXT NOT NULL,           -- e.g. 'T1666' or 'T1556.009'
            technique_name TEXT NOT NULL,
            comment      TEXT,
            PRIMARY KEY (control_id, technique_id)
        );
        CREATE INDEX idx_attack_ctrl ON attack_mappings(control_id);
        CREATE INDEX idx_attack_tech ON attack_mappings(technique_id);

        CREATE TABLE embeddings (
            kind     TEXT NOT NULL,              -- 'control' | 'cci'
            ref_id   TEXT NOT NULL,
            text     TEXT NOT NULL,
            vec      BLOB NOT NULL,
            PRIMARY KEY (kind, ref_id)
        );
        """
    )
    con.commit()


# ---------- OSCAL parsing ----------

PARAM_RE = re.compile(r"\{\{\s*insert:\s*param,\s*([a-z0-9_.\-]+)\s*\}\}", re.I)


def resolve_params(text: str, params: dict[str, str]) -> str:
    """Replace OSCAL `{{ insert: param, X }}` with `[Assignment: <label>]`."""
    if not text:
        return text
    return PARAM_RE.sub(lambda m: f"[Assignment: {params.get(m.group(1), m.group(1))}]", text)


def build_param_map(ctrl: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in ctrl.get("params", []):
        pid = p.get("id", "")
        # Prefer .label, fall back to first guideline prose, fall back to id
        label = p.get("label") or ""
        if not label:
            gls = p.get("guidelines") or []
            if gls and gls[0].get("prose"):
                label = gls[0]["prose"]
        out[pid] = label or pid
        # Also map alt-identifier -> same value (some statements reference alt id)
        for prop in p.get("props", []):
            if prop.get("name") == "alt-identifier":
                out[prop["value"]] = label or pid
    return out


def collect_prose(part: dict, params: dict[str, str] | None = None) -> str:
    """Recursively flatten an OSCAL part into a readable string."""
    params = params or {}
    chunks = []
    label = ""
    for p in part.get("props", []):
        if p.get("name") == "label":
            label = p["value"]
            break
    prose = resolve_params(part.get("prose", ""), params)
    if label or prose:
        chunks.append(f"{label} {prose}".strip())
    for sp in part.get("parts", []):
        chunks.append(collect_prose(sp, params))
    return "\n".join(c for c in chunks if c)


def get_part(parts: list[dict], name: str) -> dict | None:
    for p in parts or []:
        if p.get("name") == name:
            return p
    return None


def get_label(props: list[dict]) -> str:
    if not props:
        return ""
    for p in props:
        if p.get("name") == "label" and p.get("class") != "zero-padded" and p.get("class") != "sp800-53a":
            return p["value"]
    for p in props:
        if p.get("name") == "label":
            return p["value"]
    return ""


def ingest_catalog(con: sqlite3.Connection) -> None:
    catalog = json.loads((DATA / "catalog.json").read_text())["catalog"]
    cur = con.cursor()
    rows = []
    for group in catalog.get("groups", []):
        family = group["id"]
        family_name = group["title"]
        FAMILY_NAMES[family] = family_name
        for ctrl in group.get("controls", []):
            rows.extend(_flatten_control(ctrl, family, family_name, parent=None))
    cur.executemany(
        "INSERT INTO controls(id,label,family,family_name,title,is_enhancement,parent_id,statement,guidance,assessment,full_text) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    con.commit()
    print(f"  inserted {len(rows)} controls/enhancements")


def _flatten_control(ctrl: dict, family: str, family_name: str, parent: str | None) -> list[tuple]:
    cid = ctrl["id"]
    title = ctrl["title"]
    label = get_label(ctrl.get("props", []))
    is_enh = 1 if parent else 0
    params = build_param_map(ctrl)
    parts = ctrl.get("parts", [])
    stmt_part = get_part(parts, "statement")
    gdn_part = get_part(parts, "guidance")
    obj_part = get_part(parts, "assessment-objective")
    statement = collect_prose(stmt_part, params) if stmt_part else ""
    guidance = resolve_params(gdn_part.get("prose", ""), params) if gdn_part else ""
    if gdn_part:
        for sp in gdn_part.get("parts", []):
            guidance += "\n" + collect_prose(sp, params)
    assessment = collect_prose(obj_part, params) if obj_part else ""
    full = (
        f"{label} {title}\n\nStatement:\n{statement}\n\nDiscussion/Guidance:\n{guidance}\n\n"
        f"Assessment Objectives:\n{assessment}"
    ).strip()
    out = [(cid, label, family, family_name, title, is_enh, parent, statement, guidance, assessment, full)]
    for child in ctrl.get("controls", []):
        out.extend(_flatten_control(child, family, family_name, parent=cid))
    return out


# ---------- Baselines ----------

def ingest_baselines(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    files = {"LOW": "low.json", "MODERATE": "mod.json", "HIGH": "high.json"}
    rows = []
    for name, fname in files.items():
        cat = json.loads((DATA / fname).read_text())["catalog"]
        ids = []

        def walk(node):
            for g in node.get("groups", []):
                for c in g.get("controls", []):
                    ids.append(c["id"])
                    for e in c.get("controls", []):
                        ids.append(e["id"])
                walk(g)

        walk(cat)
        for cid in ids:
            rows.append((cid, name))
    cur.executemany("INSERT OR IGNORE INTO baselines(control_id,baseline) VALUES (?,?)", rows)
    con.commit()
    print(f"  inserted {len(rows)} baseline rows")


# ---------- CCI ----------

CONTROL_INDEX_RE = re.compile(r"^([A-Z]{2})-(\d+)(?:\s*\((\d+)\))?", re.I)


def parse_control_id(index: str) -> str | None:
    """'AC-2 a 1' or 'AC-2 (1)' → 'ac-2' or 'ac-2.1' (lowercased)."""
    if not index:
        return None
    m = CONTROL_INDEX_RE.match(index.strip())
    if not m:
        return None
    fam, num, enh = m.group(1).lower(), m.group(2), m.group(3)
    return f"{fam}-{num}.{enh}" if enh else f"{fam}-{num}"


def ingest_ccis(con: sqlite3.Connection) -> None:
    tree = ET.parse(DATA / "U_CCI_List.xml")
    root = tree.getroot()
    items = root.findall(".//c:cci_item", CCI_NS)
    rows = []
    for item in items:
        cid = item.attrib["id"]
        defn = item.findtext("c:definition", default="", namespaces=CCI_NS) or ""
        ctype = item.findtext("c:type", default="", namespaces=CCI_NS) or ""
        # Pick the latest 800-53 reference (Rev 5 preferred, else max version)
        refs = item.findall(".//c:reference", CCI_NS)
        chosen = None
        for r in refs:
            title = r.attrib.get("title", "")
            ver = r.attrib.get("version", "")
            if title == "NIST SP 800-53" and ver == "5":
                chosen = r
                break
        if chosen is None:
            for r in refs:
                if r.attrib.get("title", "").startswith("NIST SP 800-53"):
                    if chosen is None or r.attrib.get("version", "0") > chosen.attrib.get("version", "0"):
                        chosen = r
        index = chosen.attrib.get("index", "") if chosen is not None else ""
        ctrl_id = parse_control_id(index)
        rows.append((cid, defn.strip(), ctype.strip(), ctrl_id, index))
    con.executemany(
        "INSERT INTO ccis(id,definition,type,control_id,control_index) VALUES (?,?,?,?,?)",
        rows,
    )
    con.commit()
    print(f"  inserted {len(rows)} CCIs")


# ---------- ATT&CK mappings ----------

def _normalize_capability_id(cap: str) -> str:
    """'CM-03' -> 'cm-3'; 'CM-3(2)' -> 'cm-3.2'."""
    cap = cap.strip().lower()
    m = re.match(r"^([a-z]{2})-0*(\d+)(?:\((\d+)\))?", cap)
    if not m:
        return cap
    fam, num, enh = m.group(1), m.group(2), m.group(3)
    return f"{fam}-{num}.{enh}" if enh else f"{fam}-{num}"


def ingest_attack(con: sqlite3.Connection) -> None:
    path = DATA / "attack_map.json"
    if not path.exists():
        print("  attack_map.json missing, skipping")
        return
    data = json.loads(path.read_text())
    rows = []
    for m in data.get("mapping_objects", []):
        if m.get("status") != "complete":
            continue
        cap = m.get("capability_id")
        tech = m.get("attack_object_id")
        if not cap or not tech:
            continue
        rows.append((
            _normalize_capability_id(cap),
            tech,
            m.get("attack_object_name", ""),
            (m.get("comments") or "").strip(),
        ))
    con.executemany(
        "INSERT OR REPLACE INTO attack_mappings(control_id, technique_id, technique_name, comment) "
        "VALUES (?,?,?,?)",
        rows,
    )
    con.commit()
    print(f"  inserted {len(rows)} ATT&CK mappings")


# ---------- Embeddings ----------

def embed_all(con: sqlite3.Connection) -> None:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    cur = con.cursor()

    items: list[tuple[str, str, str]] = []
    for row in cur.execute("SELECT id, full_text FROM controls"):
        items.append(("control", row[0], row[1]))
    for row in cur.execute("SELECT id, definition FROM ccis"):
        items.append(("cci", row[0], row[1]))

    # eMASS knowledge base (topics + glossary terms)
    from .emass_kb import TOPICS, GLOSSARY
    for t in TOPICS:
        items.append(("emass_topic", t["slug"], f"{t['title']}\n\n{t['body']}"))
    for term, defn in GLOSSARY.items():
        items.append(("emass_term", term, f"{term}: {defn}"))

    # NIST publication library
    from .nist_kb import PUBLICATIONS
    for p in PUBLICATIONS:
        items.append(("nist_pub", p["slug"], f"{p['title']}\n{p['summary']}\n\n{p['body']}"))

    # GRC knowledge base
    from .grc_kb import TOPICS as GRC_TOPICS, GLOSSARY as GRC_GLOSSARY
    for t in GRC_TOPICS:
        items.append(("grc_topic", t["slug"], f"{t['title']}\n\n{t['body']}"))
    for term, defn in GRC_GLOSSARY.items():
        items.append(("grc_term", term, f"{term}: {defn}"))

    print(f"  embedding {len(items)} items...")
    texts = [t for _, _, t in items]
    vecs = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)

    rows = []
    for (kind, ref_id, text), vec in zip(items, vecs):
        rows.append((kind, ref_id, text, struct.pack(f"{len(vec)}f", *vec.tolist())))
    cur.executemany(
        "INSERT OR REPLACE INTO embeddings(kind,ref_id,text,vec) VALUES (?,?,?,?)", rows
    )
    con.commit()
    print(f"  stored {len(rows)} embeddings (dim={len(vecs[0])})")


def main() -> None:
    DB_PATH.unlink(missing_ok=True)
    con = sqlite3.connect(DB_PATH)
    print("init db...")
    init_db(con)
    print("ingest 800-53 catalog...")
    ingest_catalog(con)
    print("ingest baselines...")
    ingest_baselines(con)
    print("ingest CCI list...")
    ingest_ccis(con)
    print("ingest ATT&CK mappings...")
    ingest_attack(con)
    print("embed...")
    embed_all(con)
    con.close()
    print(f"done. wrote {DB_PATH}")


if __name__ == "__main__":
    sys.exit(main())
