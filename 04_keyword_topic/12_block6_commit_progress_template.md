# Day 5 Block 6 — Commit Checklist & master_progress.md Update Template

> This is a checklist + template, not a script. Fill in numbers from your actual
> Block 1-5 outputs before commit.

---

## A. Pre-commit verification (engineering discipline)

Run from repo root **after** Block 1-5 all complete:

```powershell
cd D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026

# 1. Sanity check expected outputs exist
$expected = @(
  "data\processed\specter2_embeddings.npy",
  "data\processed\specter2_embeddings_meta.json",
  "data\processed\umap_5d.npy",
  "data\processed\umap_2d.npy",
  "data\processed\cluster_assignments.parquet",
  "data\processed\topic_labels.json",
  "results\tables\cluster_stats.csv",
  "results\tables\topic_labels.csv",
  "results\tables\topic_yearly_freq.csv",
  "results\tables\topic_yearly_pct.csv",
  "results\tables\topic_period_freq.csv",
  "results\tables\topic_rising_declining.csv",
  "results\tables\day4_vs_day5_metrics.csv",
  "results\tables\day4_vs_day5_confusion_matrix.csv",
  "results\figures\figure_12_topic_yearly_heatmap.png",
  "results\figures\figure_13_topic_evolution_3period.png",
  "results\figures\figure_14_topic_rising_declining.png",
  "results\figures\figure_15_day4_vs_day5_confusion.png",
  "results\audits\day5_block0_audit.md",
  "results\audits\day5_cross_dedup_fix_report.md",
  "results\audits\day5_cross_validation_report.md"
)
foreach ($f in $expected) {
  if (Test-Path $f) { Write-Host "✓ $f" -ForegroundColor Green }
  else { Write-Host "✗ MISSING: $f" -ForegroundColor Red }
}

# 2. Git status — must show only intended additions
git status

# 3. Diff master_progress.md before staging — make sure your edits look right
git diff docs/master_progress.md
```

If `git status` shows unintended changes (e.g., notebook scratch files,
.bak_pre_cross_dedup, .npy intermediate files), .gitignore them first:

```powershell
# .gitignore additions if needed
Add-Content .gitignore "`n# Day 5 backups"
Add-Content .gitignore "data/processed/*.bak_pre_cross_dedup"
```

---

## B. Suggested commit sequence

Split into logical commits — easier to review and revert later:

### Commit 1: data cleanup (cross-dedup fix)
```powershell
git add data\processed\integrated_corpus.parquet
git add data\processed\integrated_corpus_partial2026.parquet
git add results\audits\day5_cross_dedup_fix_report.md
git add 04_keyword_topic\06_day5_block0_audit.py
git add 04_keyword_topic\06b_anomaly_audit.py
git add 04_keyword_topic\06c_cross_dedup_fix.py
git commit -m "Day 5 cleanup: cross-file dedup fix (main+partial)

- Audit revealed 37 DOI overlaps between main and partial 2026 files
- 3 root cause groups: 24 main(2026)=partial(2026), 12 main(2025) vs
  partial(2026) in-press year discrepancies, 1 pure dup
- Strict year-based reclassification: year<=2025 -> main, year=2026 -> partial
- Result: main 9,438->9,413 (-25), partial 316->304 (-12), total
  unique 9,754->9,717 (-37). Backups in .bak_pre_cross_dedup.
- Day 4 keyword analysis kept at original 9,438 snapshot (0.27% perturbation,
  no rank/cluster changes); will document footnote in Methods."
```

### Commit 2: Day 5 topic modeling pipeline
```powershell
git add 04_keyword_topic\07_block1_specter2_embedding.py
git add 04_keyword_topic\08_block2_umap_hdbscan.py
git add 04_keyword_topic\09_block3_topic_naming.py
git add 04_keyword_topic\10_block4_topic_evolution.py
git add 04_keyword_topic\11_block5_cross_validation.py
git add data\processed\specter2_embeddings.npy
git add data\processed\specter2_embeddings_meta.json
git add data\processed\umap_5d.npy
git add data\processed\umap_2d.npy
git add data\processed\cluster_assignments.parquet
git add data\processed\topic_labels.json
git add results\tables\cluster_stats.csv
git add results\tables\topic_labels.csv
git add results\tables\topic_yearly_freq.csv
git add results\tables\topic_yearly_pct.csv
git add results\tables\topic_period_freq.csv
git add results\tables\topic_rising_declining.csv
git add results\tables\day4_vs_day5_metrics.csv
git add results\tables\day4_vs_day5_confusion_matrix.csv
git add results\figures\figure_12_topic_yearly_heatmap.png
git add results\figures\figure_13_topic_evolution_3period.png
git add results\figures\figure_14_topic_rising_declining.png
git add results\figures\figure_15_day4_vs_day5_confusion.png
git add results\audits\day5_block0_audit.md
git add results\audits\day5_cross_validation_report.md
git commit -m "Day 5: SPECTER2 + UMAP + HDBSCAN topic modeling

Pipeline (5 blocks on 9,413 main corpus abstracts):
- Block 1: SPECTER2-base + proximity adapter (Cohan 2020, Singh 2023);
  CPU batch embedding; 97% title+abstract, 3% title-only fallback;
  head+tail 75/25 truncation for 10.3% records exceeding 512 tokens.
- Block 2: UMAP cosine -> 5-dim (HDBSCAN) + 2-dim (viz);
  HDBSCAN min_cluster_size=50, min_samples=10 (Klarin 2024 heuristic).
- Block 3: c-TF-IDF candidates + KeyBERTInspired re-ranking
  (Grootendorst 2022; Sharma 2019); author keywords as sanity check.
- Block 4: Yearly (21-bin) + 3-period (Day-4 aligned) topic evolution.
- Block 5: ARI + NMI cross-validation vs Day 4 keyword co-occurrence
  clusters (Hubert & Arabie 1985; Strehl & Ghosh 2002)."
```

### Commit 3: master_progress update
```powershell
git add docs\master_progress.md
git add 04_keyword_topic\12_block6_commit_progress_template.md
git commit -m "Day 5 progress: master_progress.md updated through Day 5"
git push
```

---

## C. master_progress.md Day 5 section template

Insert this after the Day 4 section in `docs/master_progress.md`. Fill in
the `<<...>>` placeholders from actual Block outputs.

```markdown
---

## Day 5 (May 15, 2026): Topic Modeling ✅

**Status**: Complete
**Duration**: <<X hours hands-on work>>
**Deliverables**: 6 scripts + 8 data files + 9 tables + 4 figures + 1 audit

### Block 0: Pre-flight audit + cross-file dedup fix

**Critical methodological discovery**: Pre-embedding audit revealed
**37 cross-file DOI overlaps** between `integrated_corpus.parquet` (main)
and `integrated_corpus_partial2026.parquet`, decomposing into three
groups:
- A: 24 main(year=2026) ↔ partial(year=2026) — in-press articles
  appearing in both files
- B: 12 main(year=2025) ↔ partial(year=2026) — same DOI with year
  discrepancy across source databases (WoS issue year vs PubMed epub
  year)
- C: 1 pure duplicate (main and partial both labeled year=2025)

**Fix strategy (locked)**: strict year-based classification — year ≤ 2025
→ main, year = 2026 → partial; on conflict keep the main-corpus copy
(earliest documented year, source-precedence dedup convention).

**Result**: main 9,438 → **9,413** (−25); partial 316 → **304** (+1
unique main-only 2026 moved to partial, −13 cross-overlap pruned); total
unique publications 9,754 → **9,717** (−37). 24-hour backups of original
files retained at `.bak_pre_cross_dedup`.

**Day 4 impact**: 0.27% record perturbation; Top-50 keyword ranking,
5-cluster co-occurrence structure, and 3-period rising/declining analysis
unchanged. Day 4 outputs retained on original 9,438 snapshot; Methods §2
will include a one-sentence footnote.

### Block 1: SPECTER2 Embedding ✅

**Script**: `04_keyword_topic/07_block1_specter2_embedding.py`
**Outputs**: `data/processed/specter2_embeddings.npy` (9413×768 float32,
27.6 MB); `specter2_embeddings_meta.json` (record_id row alignment).

**Model**: `allenai/specter2_base` (Cohan et al. 2020 ACL) + **proximity
adapter** `allenai/specter2` (Singh et al. 2023 EMNLP SciRepEval). The
proximity adapter is fine-tuned for clustering/similarity tasks, directly
aligned with our downstream HDBSCAN objective.

**Input format**: `title [SEP] abstract` (SPECTER2 standard).
**Truncation**: head+tail 75/25 split of available budget after
preserving title, applied to 10.3% (966/9413) of records exceeding 512
tokens (Sun et al. 2019 long-document BERT practice).
**Fallback**: title-only for 3.0% (285/9413) records lacking abstract
(PubMed structural limitation for pre-2012 records).
**Pooling**: `[CLS]` token last_hidden_state.
**Device / batch**: CPU, batch_size=8.
**Elapsed**: <<X min>> on <<your CPU>>.

### Block 2: UMAP + HDBSCAN Clustering ✅

**Script**: `04_keyword_topic/08_block2_umap_hdbscan.py`
**Outputs**: `umap_5d.npy`, `umap_2d.npy`, `cluster_assignments.parquet`,
`cluster_stats.csv`.

**UMAP** (McInnes et al. 2018): two separate fits:
- 5-dim for HDBSCAN density estimation: `n_neighbors=15, min_dist=0.0,
  metric=cosine, random_state=42`
- 2-dim for scatter visualization: same except `min_dist=0.1`

**HDBSCAN** (Campello et al. 2013): `min_cluster_size=50, min_samples=10,
metric=euclidean, cluster_selection_method=eom, prediction_data=True`.
`min_cluster_size=50 ≈ √N/2` (Klarin 2024 bibliometric heuristic).

**Result**: **<<K>>** clusters discovered; **<<N_noise>>** noise points
(<<X>>% of corpus); cluster sizes <<min>>-<<max>>, median <<med>>.

### Block 3: Topic Naming (c-TF-IDF + KeyBERTInspired) ✅

**Script**: `04_keyword_topic/09_block3_topic_naming.py`
**Outputs**: `results/tables/topic_labels.csv`,
`data/processed/topic_labels.json`.

Following near-2026 顶刊 BERTopic-bibliometric review best practice
(Grootendorst 2022; Educational Psychology Review 2024):
1. **c-TF-IDF** (class-based TF-IDF): per-cluster super-document, 1- and
   2-gram CountVectorizer, English stopwords + 26 bibliometric-specific
   stopwords (study, results, method, ...). Top-30 candidate keywords per
   cluster.
2. **KeyBERTInspired re-ranking** (Sharma & Li 2019; Grootendorst doc):
   each candidate phrase encoded by **SPECTER2 (same model as document
   encoder)**, cosine similarity to cluster centroid → re-rank, output
   top-15.
3. **Author keywords sanity check**: top-10 author-stated keywords per
   cluster reported alongside for convergent validity inspection.
4. **Exemplar titles**: top-3 highest-probability member titles per
   cluster for human readability.

### Block 4: Topic Temporal Evolution ✅

**Script**: `04_keyword_topic/10_block4_topic_evolution.py`
**Outputs**: 4 CSV tables + 3 figures.

Two-level analysis (BERTopic dynamic topic modeling convention,
Blei & Lafferty 2006):
- **Fine**: 21 yearly bins (2005-2025) → topic frequency heatmap
  (figure_12), each topic's lifetime distribution over years.
- **Coarse**: 3 periods (Early 2005-2011 / Middle 2012-2018 / Recent
  2019-2025) aligned with Day-4 keyword evolution; supports
  paradigm-shift narrative + cross-validation.

**Top Rising Topics (Δ Recent% − Early%)**:
<<Fill from `topic_rising_declining.csv` top 5>>

**Top Declining Topics**:
<<Fill from `topic_rising_declining.csv` bottom 5>>

### Block 5: Cross-validation vs Day 4 Keyword Clusters ✅

**Script**: `04_keyword_topic/11_block5_cross_validation.py`
**Outputs**: `day4_vs_day5_metrics.csv`,
`day4_vs_day5_confusion_matrix.csv`, `figure_15_day4_vs_day5_confusion.png`,
`day5_cross_validation_report.md`.

**Method**: each record's Day-4 label = majority vote of its keywords'
VOSviewer cluster assignments; Day-5 label = HDBSCAN cluster_id from
SPECTER2 embeddings. Inner-joined on `record_id`, noise (-1) excluded.

**Metrics** (Hubert & Arabie 1985; Strehl & Ghosh 2002):
- **ARI = <<X>>** (<<interpretation>>)
- **NMI = <<X>>** (<<interpretation>>)
- n records compared: <<N>>

**Interpretation**: <<convergent validity narrative — does
SPECTER2-embeddings of abstracts independently recover the keyword
co-occurrence thematic structure?>>

### Day 5 Engineering Lessons

1. **Audit before production runs (yet again)**. Block 0 surfaced a
   data integrity bug — 37 cross-file DOI overlaps — that would have
   silently propagated through topic modeling and inflated corpus counts
   in Methods §2. Cost: 30 minutes audit + fix. Benefit:
   reviewer-resistant numbers.

2. **`adapters` 1.x `set_active=True` doesn't propagate to forward pass**.
   The `load_adapter(..., set_active=True)` call only sets loading-time
   state; an explicit `model.set_active_adapters(name)` is required
   afterwards. Without it, the proximity adapter is loaded but
   `forward()` runs on base SPECTER2, silently degrading clustering
   quality (~3 NDCG points on SciDocs). The warning
   `"There are adapters available but none are activated for the forward
   pass"` is the canary; an explicit assertion on `model.active_adapters
   is not None` is the safety net.

3. **Windows HF cache requires Developer Mode** (or admin PowerShell).
   `os.symlink` raises `WinError 1314` for non-admin processes, breaking
   `snapshot_download` in unpredictable ways. One-time toggle resolves
   this for all future HF / Git / pip operations.

4. **c-TF-IDF stopwords need bibliometric tuning**. Default English
   stopwords miss high-frequency-but-uninformative terms in scientific
   abstracts (`study`, `results`, `method`, `conclusion`, ...). A
   26-term `EXTRA_STOPWORDS` set is documented in Block 3.

---

## Headline Day-5 Findings (for paper §3.X Topic Modeling)

<<Fill after Block 5 complete:>>

- <<K>> distinct research topics identified at abstract level
- Top-3 topics: <<T1: terms>>, <<T2: terms>>, <<T3: terms>>
- <<X>>% convergent validity with Day-4 keyword co-occurrence clusters
  (ARI=<<>>, NMI=<<>>)
- Emerging topics (>3-fold increase Recent vs Early): <<list>>
- Declining topics (-2 percentage points or more): <<list>>
- Paradigm shift around <<year>>: <<narrative>>

---
```
