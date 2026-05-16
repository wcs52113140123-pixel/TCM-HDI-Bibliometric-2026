# Day-4 Keyword Cluster Re-derivation (Louvain)

- Algorithm: NetworkX + python-louvain (Blondel et al. 2008)
- Parameters: resolution=0.8, min_cluster_size=5, seed=42
- Graph: 100 nodes, 1,485 edges
- Modularity: 0.2221
- Final clusters: 4

## Verification: top keywords per cluster

**Action required**: compare these against Day-4 published 5-cluster labels (ADME core / TCM oncology / CAM clinical safety / in silico mechanisms / classic herb-drug pairs).

### Cluster 0 (n=43 keywords)

Top 15 by within-cluster weighted degree:
- `pharmacokinetics` (strength=2028)
- `cytochrome p450` (strength=1358)
- `inhibition` (strength=1125)
- `p-glycoprotein` (strength=1083)
- `interaction` (strength=833)
- `extract` (strength=595)
- `bioavailability` (strength=466)
- `induction` (strength=458)
- `drug` (strength=453)
- `mechanism` (strength=434)
- `drug-drug interaction` (strength=433)
- `cyp3a4` (strength=416)
- `enzymes` (strength=387)
- `herb-drug` (strength=356)
- `identification` (strength=321)

### Cluster 1 (n=29 keywords)

Top 15 by within-cluster weighted degree:
- `herb-drug interaction` (strength=1349)
- `drug interaction` (strength=656)
- `st johns wort` (strength=559)
- `alternative medicine` (strength=510)
- `dietary supplements` (strength=434)
- `complementary` (strength=387)
- `medicine` (strength=361)
- `phytotherapy` (strength=317)
- `medicinal plants` (strength=275)
- `cancer` (strength=243)
- `safety` (strength=203)
- `warfarin` (strength=190)
- `plant preparations` (strength=177)
- `ginkgo-biloba extract` (strength=157)
- `chemotherapy` (strength=149)

### Cluster 2 (n=23 keywords)

Top 15 by within-cluster weighted degree:
- `traditional chinese medicine` (strength=1384)
- `drug synergism` (strength=1185)
- `cell line, tumor` (strength=582)
- `apoptosis` (strength=547)
- `cell proliferation` (strength=410)
- `plant extract` (strength=393)
- `antineoplastic agents` (strength=334)
- `signal transduction` (strength=316)
- `dose-response relationship, drug` (strength=286)
- `rats, sprague-dawley` (strength=274)
- `oxidative stress` (strength=222)
- `disease models, animal` (strength=208)
- `liver` (strength=202)
- `antioxidant` (strength=175)
- `cytochrome p-450 cyp3a` (strength=137)

### Cluster 3 (n=5 keywords)

Top 15 by within-cluster weighted degree:
- `network pharmacology` (strength=159)
- `molecular docking` (strength=113)
- `metabolomics` (strength=57)
- `alzheimer's disease` (strength=19)
- `gut microbiota` (strength=14)
