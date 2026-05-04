"""Embedding-backed semantic search over controls and CCIs."""
from __future__ import annotations
import sqlite3
import struct
from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = Path(__file__).resolve().parents[1] / "rmf.db"


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _index() -> tuple[np.ndarray, list[tuple[str, str, str]]]:
    """Load all embeddings into memory once. Returns (matrix, [(kind, ref_id, text), ...])."""
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT kind, ref_id, text, vec FROM embeddings").fetchall()
    con.close()
    meta = [(k, r, t) for k, r, t, _ in rows]
    dim = len(rows[0][3]) // 4
    mat = np.empty((len(rows), dim), dtype=np.float32)
    for i, (_, _, _, blob) in enumerate(rows):
        mat[i] = struct.unpack(f"{dim}f", blob)
    return mat, meta


def search(query: str, k_controls: int = 6, k_ccis: int = 6) -> dict:
    mat, meta = _index()
    qvec = _model().encode([query], normalize_embeddings=True)[0].astype(np.float32)
    sims = mat @ qvec  # cosine since both normalized

    ctrl_idx = [i for i, m in enumerate(meta) if m[0] == "control"]
    cci_idx = [i for i, m in enumerate(meta) if m[0] == "cci"]

    def topk(indices, k):
        local = np.array(indices)
        s = sims[local]
        order = np.argsort(-s)[:k]
        return [(meta[local[o]][1], float(s[o])) for o in order]

    return {
        "controls": topk(ctrl_idx, k_controls),
        "ccis": topk(cci_idx, k_ccis),
    }
