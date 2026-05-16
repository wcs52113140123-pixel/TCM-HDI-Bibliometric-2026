"""
Day 5 Block 3 recovery: rebuild topic_labels.json from topic_labels.csv.

Bug context: Block 3's json.dump() failed with
  TypeError: keys must be str, int, float, bool or None, not int32
because cluster_id values from pandas are numpy.int32, which json.dump
does not accept as dict keys. The CSV was saved successfully before the
exception, so we reconstruct JSON from CSV here without rerunning the
~5-minute c-TF-IDF + KeyBERTInspired pipeline.

Run:
  python 04_keyword_topic/09b_rebuild_topic_labels_json.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CSV_PATH = REPO / "results" / "tables" / "topic_labels.csv"
OUT_JSON = REPO / "data" / "processed" / "topic_labels.json"


def split_pipe(s: str) -> list[str]:
    if not isinstance(s, str):
        return []
    return [t.strip() for t in s.split("|") if t.strip()]


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Read {len(df)} rows from {CSV_PATH.name}")
    print(f"Columns: {list(df.columns)}")

    out: dict[str, dict] = {}
    for _, r in df.iterrows():
        cid = int(r["cluster_id"])  # critical: python int, not numpy.int32
        exemplars = []
        for col in ("exemplar_title_1", "exemplar_title_2", "exemplar_title_3"):
            v = r.get(col, "")
            if isinstance(v, str) and v.strip():
                exemplars.append(v.strip())
        out[str(cid)] = {  # json keys are always strings, use str() to be explicit
            "cluster_id": cid,
            "n_docs": int(r["n_docs"]),
            "top_keybert": split_pipe(r.get("top_keybert_15", "")),
            "top_ctfidf": split_pipe(r.get("top_ctfidf_15", "")),
            "top_author_kw": split_pipe(r.get("top_author_kw_10", "")),
            "exemplar_titles": exemplars,
        }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Wrote {OUT_JSON} with {len(out)} topics")

    # Quick sanity print
    sample_cid = next(iter(out))
    print(f"\nSample (cluster_id={sample_cid}):")
    print(json.dumps(out[sample_cid], ensure_ascii=False, indent=2)[:500])


if __name__ == "__main__":
    main()
