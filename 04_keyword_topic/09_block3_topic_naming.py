"""
Day 5 Block 3: Topic naming via c-TF-IDF + KeyBERTInspired re-ranking.

Pipeline:
  1. For each cluster, build a "super-document" by concatenating
     (title + abstract) of all cluster members.
  2. c-TF-IDF: TF within cluster × IDF across clusters → top-30 candidate
     keywords per cluster (1-grams + 2-grams).
  3. KeyBERTInspired re-ranking: encode each candidate using SPECTER2,
     compute cosine similarity to cluster centroid (mean doc embedding),
     re-rank → top-15 final keywords per cluster.
  4. Also output top-N author_keywords per cluster as cross-source sanity
     check (does Day 5 abstract-topic align with author-stated keywords?).

Citations:
  - Grootendorst 2022. BERTopic. arXiv:2203.05794
  - Sharma & Li 2019. KeyBERT: keyword extraction with BERT embeddings.
  - Cohan et al. 2020 / Singh et al. 2023 (SPECTER2 reuse for word encoding).

Inputs:
  data/processed/cluster_assignments.parquet
  data/processed/integrated_corpus.parquet
  data/processed/specter2_embeddings.npy

Outputs:
  results/tables/topic_labels.csv      # cluster_id, top_ctfidf, top_keybert,
                                       # top_author_kw, n_docs, exemplar_titles
  data/processed/topic_labels.json     # programmatic re-use

Run:
  python 04_keyword_topic/09_block3_topic_naming.py
"""

from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.feature_extraction.text import CountVectorizer
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
TABLES = REPO / "results" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

CORPUS_PATH = DATA / "integrated_corpus.parquet"
CLUSTERS_PATH = DATA / "cluster_assignments.parquet"
EMB_PATH = DATA / "specter2_embeddings.npy"

OUT_CSV = TABLES / "topic_labels.csv"
OUT_JSON = DATA / "topic_labels.json"

MODEL_NAME = "allenai/specter2_base"
ADAPTER_NAME = "allenai/specter2"

N_CANDIDATES = 30   # c-TF-IDF top-N
N_FINAL = 15        # after KeyBERTInspired re-rank
N_AUTHOR_KW = 10    # author keyword sanity check
N_EXEMPLARS = 3     # representative titles per cluster

# Bibliometric-specific stopwords (besides English defaults)
EXTRA_STOPWORDS = {
    "study", "studies", "research", "result", "results", "method", "methods",
    "analysis", "analyses", "used", "using", "use", "based", "showed", "shown",
    "found", "conclusion", "conclusions", "objective", "background", "purpose",
    "aim", "aims", "introduction", "discussion", "review", "reviews", "article",
    "paper", "report", "abstract", "data", "datum", "patient", "patients",
    "subject", "subjects", "group", "groups", "model", "models", "approach",
    "approaches", "study group", "control group", "preliminary",
}


# ----------------------------------------------------------------------
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = re.sub(r"<[^>]+>", " ", s)               # strip HTML/XML tags
    s = re.sub(r"\b\d+\b", " ", s)               # remove standalone numbers
    s = re.sub(r"[^a-zA-Z\u00C0-\u024F\s\-]", " ", s)  # keep latin letters
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def encode_phrases(phrases, tokenizer, model, batch_size=32):
    """Encode candidate phrases using SPECTER2 (same model as document encoder
    for consistency with cluster centroids). Returns (n_phrases, 768)."""
    embeddings = np.zeros((len(phrases), 768), dtype=np.float32)
    model.eval()
    with torch.inference_mode():
        for i in range(0, len(phrases), batch_size):
            batch = phrases[i : i + batch_size]
            enc = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=64,
                return_tensors="pt",
                return_token_type_ids=False,
            )
            out = model(**enc)
            embeddings[i : i + len(batch)] = (
                out.last_hidden_state[:, 0, :].cpu().numpy()
            )
    return embeddings


def main():
    t0 = time.time()

    # --- Load -------------------------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Loading inputs...")
    df = pd.read_parquet(CORPUS_PATH)
    clusters = pd.read_parquet(CLUSTERS_PATH)
    embeddings = np.load(EMB_PATH)

    df = df.merge(clusters, on="record_id", how="left")
    assert df["cluster_id"].notna().all(), "missing cluster_id after merge"

    # Build text per record (title + abstract concatenation, cleaned)
    df["_text"] = (
        df["title"].fillna("") + " " + df["abstract"].fillna("")
    ).apply(clean_text)

    cluster_ids = sorted(c for c in df["cluster_id"].unique() if c >= 0)
    print(f"  Records: {len(df):,}, real clusters: {len(cluster_ids)}, "
          f"noise: {(df['cluster_id'] == -1).sum():,}")

    # Map record_id → embedding row index (defensive)
    with open(DATA / "specter2_embeddings_meta.json", encoding="utf-8") as f:
        meta = json.load(f)
    rid_to_idx = {rid: i for i, rid in enumerate(meta["record_ids"])}

    # --- c-TF-IDF candidate keywords --------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Computing c-TF-IDF...")
    # One "document" per cluster = concatenated cluster text
    cluster_docs = []
    cluster_doc_ids = []
    for cid in cluster_ids:
        cluster_text = " ".join(df.loc[df["cluster_id"] == cid, "_text"])
        cluster_docs.append(cluster_text)
        cluster_doc_ids.append(cid)

    vectorizer = CountVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        min_df=2,
        max_df=0.9,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b",
    )
    X = vectorizer.fit_transform(cluster_docs)
    vocab = np.array(vectorizer.get_feature_names_out())

    # Manual c-TF-IDF: classes are clusters
    # tf_c,t = count of term t in cluster c
    # idf_t  = log(1 + n_clusters / df_t)  where df_t = number of clusters containing t
    tf = X.toarray().astype(np.float64)
    # L1 normalize per cluster (account for cluster size differences)
    tf_norm = tf / (tf.sum(axis=1, keepdims=True) + 1e-12)
    df_term = (tf > 0).sum(axis=0)
    idf = np.log(1.0 + len(cluster_ids) / (df_term + 1e-12))
    ctfidf = tf_norm * idf  # shape (n_clusters, vocab_size)

    # Filter extra stopwords + single-character tokens
    keep_mask = np.array([
        (w not in EXTRA_STOPWORDS) and len(w) > 2 for w in vocab
    ])
    ctfidf = ctfidf * keep_mask[None, :]

    # Top-N candidates per cluster
    candidates_per_cluster: dict[int, list[str]] = {}
    for ci, cid in enumerate(cluster_doc_ids):
        top_idx = np.argsort(-ctfidf[ci])[:N_CANDIDATES]
        candidates_per_cluster[cid] = [vocab[i] for i in top_idx if ctfidf[ci, i] > 0]
    print(f"  c-TF-IDF done. Candidate keywords per cluster: ~{N_CANDIDATES}")

    # --- Load SPECTER2 for KeyBERTInspired re-ranking ---------------------
    print(f"[{time.strftime('%H:%M:%S')}] Loading SPECTER2 (for word encoding)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoAdapterModel.from_pretrained(MODEL_NAME)
    model.load_adapter(ADAPTER_NAME, source="hf", load_as="proximity", set_active=True)
    model.set_active_adapters("proximity")
    model.eval()

    # --- KeyBERTInspired re-ranking ---------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] KeyBERTInspired re-ranking...")
    topic_labels: dict[int, dict] = {}

    # Collect all unique candidates once to amortize encoding
    all_phrases = sorted({p for ps in candidates_per_cluster.values() for p in ps})
    print(f"  Encoding {len(all_phrases)} unique candidate phrases...")
    phrase_emb = encode_phrases(all_phrases, tokenizer, model, batch_size=32)
    phrase_emb_idx = {p: i for i, p in enumerate(all_phrases)}

    for cid in cluster_ids:
        # Cluster centroid in embedding space
        member_ids = df.loc[df["cluster_id"] == cid, "record_id"].tolist()
        member_idx = [rid_to_idx[r] for r in member_ids]
        centroid = embeddings[member_idx].mean(axis=0)
        centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-12)

        # Score candidates by cosine sim to centroid
        cands = candidates_per_cluster[cid]
        cand_vecs = np.array([phrase_emb[phrase_emb_idx[c]] for c in cands])
        cand_vecs_n = cand_vecs / (
            np.linalg.norm(cand_vecs, axis=1, keepdims=True) + 1e-12
        )
        sims = cand_vecs_n @ centroid_norm
        order = np.argsort(-sims)
        top_keybert = [cands[i] for i in order[:N_FINAL]]
        top_ctfidf = cands[:N_FINAL]  # original c-TF-IDF order for comparison

        # Author keywords sanity check
        sub = df[df["cluster_id"] == cid]
        author_kw_lists = sub["author_keywords"].dropna().tolist()
        kw_counter: Counter = Counter()
        for kws in author_kw_lists:
            if isinstance(kws, (list, np.ndarray)):
                for k in kws:
                    if isinstance(k, str) and k.strip():
                        kw_counter[k.lower().strip()] += 1
            elif isinstance(kws, str):
                for k in re.split(r"[;,]", kws):
                    k = k.strip().lower()
                    if k:
                        kw_counter[k] += 1
        top_author_kw = [k for k, _ in kw_counter.most_common(N_AUTHOR_KW)]

        # Exemplar titles: highest-prob members
        probs = sub.set_index("record_id")["probability"]
        top_prob_ids = probs.sort_values(ascending=False).head(N_EXEMPLARS).index
        exemplar_titles = (
            df.loc[df["record_id"].isin(top_prob_ids), "title"]
            .astype(str)
            .str.slice(0, 110)
            .tolist()
        )

        topic_labels[cid] = {
            "cluster_id": int(cid),
            "n_docs": int(len(sub)),
            "top_ctfidf": top_ctfidf,
            "top_keybert": top_keybert,
            "top_author_kw": top_author_kw,
            "exemplar_titles": exemplar_titles,
        }

    # --- Save -------------------------------------------------------------
    rows = []
    for cid in cluster_ids:
        lab = topic_labels[cid]
        rows.append({
            "cluster_id": cid,
            "n_docs": lab["n_docs"],
            "top_keybert_15": " | ".join(lab["top_keybert"]),
            "top_ctfidf_15": " | ".join(lab["top_ctfidf"]),
            "top_author_kw_10": " | ".join(lab["top_author_kw"]),
            "exemplar_title_1": lab["exemplar_titles"][0] if lab["exemplar_titles"] else "",
            "exemplar_title_2": lab["exemplar_titles"][1] if len(lab["exemplar_titles"]) > 1 else "",
            "exemplar_title_3": lab["exemplar_titles"][2] if len(lab["exemplar_titles"]) > 2 else "",
        })
    out_df = pd.DataFrame(rows).sort_values("n_docs", ascending=False)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"  → {OUT_CSV.name}")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(topic_labels, f, ensure_ascii=False, indent=2)
    print(f"  → {OUT_JSON.name}")

    # Console preview
    print(f"\nTop 10 topics by size:")
    for _, row in out_df.head(10).iterrows():
        print(f"\n  Topic {row['cluster_id']} ({row['n_docs']} docs):")
        print(f"    KeyBERT: {row['top_keybert_15'][:120]}")
        print(f"    Author : {row['top_author_kw_10'][:120]}")

    print(f"\n[{time.strftime('%H:%M:%S')}] Block 3 complete. "
          f"Total: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
