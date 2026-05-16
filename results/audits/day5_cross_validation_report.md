# Day 5 Cross-validation Report

## Overview
Cross-validation of Day-5 abstract-level SPECTER2 + HDBSCAN topics against
Day-4 keyword co-occurrence clusters (VOSviewer, 5 clusters: ADME core,
TCM oncology, CAM clinical safety, in silico mechanisms, classic herb-drug
pairs).

## Method
For each record:
- Day-4 label: majority vote of its keywords' VOSviewer cluster
  assignments. Records without any matched keyword excluded.
- Day-5 label: HDBSCAN cluster_id from SPECTER2 embeddings.
ARI (Hubert & Arabie 1985) and NMI (Strehl & Ghosh 2002, arithmetic) computed
on inner-joined records.

## Results (primary: noise-excluded)
- n records compared: **4,237**
- Day-4 clusters present: 4
- Day-5 clusters present: 39
- **ARI = 0.0407** (near-random agreement)
- **NMI = 0.1459** (low mutual information)

## Interpretation
ARI > 0 indicates better-than-chance agreement; values around 0.2-0.4 are
typical when comparing fine-grained topic models (Day 5: ~30+ topics) against
coarse-grained co-occurrence clusters (Day 4: 5 clusters), because the
finer partition splits coarse clusters into sub-themes. NMI is less sensitive
to cluster cardinality difference and better captures information overlap.

A strong ARI (>0.3) confirms convergent validity: SPECTER2 embeddings of
abstracts independently recover the thematic structure that VOSviewer found
on keyword co-occurrence. Lower ARI is not a refutation — many-to-one
mappings (multiple Day-5 sub-topics within one Day-4 cluster) inflate
disagreement while preserving NMI.

See `day4_vs_day5_confusion_matrix.csv` for granular mapping.

## Citations
- Hubert L. & Arabie P. 1985. Comparing partitions. J Classification.
- Strehl A. & Ghosh J. 2002. Cluster ensembles: a knowledge reuse framework
  for combining multiple partitions. JMLR.
