# Three-Tier Herb x Mechanism Findings (Day 15)

## Overview

Day 15 把 Day 13 (topic-level) 和 Day 14 (temporal) 的 mechanism cross-analysis 切换到**显式 herb 分类层级**。基于 Schema v3 的三层 herb-tier 字段（`herb_family` Linnaean / `herb_canonical_latin` species / `herb_active_compound` 单分子），对每 tier 独立做 Fisher exact + within-tier BH-FDR；再做 **cross-tier consistency analysis** 追踪每个 mechanism 在三层间的"自然分辨率层级"。

**核心发现**：HDI 文献中不同 mechanism 在 herb taxonomy 中的**自然信号分辨率不同**——CYP_induction 收敛到分子层 (hyperforin)，P-gp_inhibition / transporter_modulation 停在 family 层 (Lamiaceae)，UGT_inhibition 停在 species 层 (Glycyrrhiza)。**SJW (Hypericaceae → Hypericum perforatum → hyperforin → CYP_induction) 是文献中唯一的 FULL_CHAIN exemplar**。

数据资产：`results/figures/fig11_three_tier_heatmaps.{png,pdf,svg}` + `fig12_cross_tier_chain_sankey.html` + 23 个 CSV（matrix / marginal / Fisher / chain）。

## Methods 摘要 (paper §2.x 候选)

### Schema v3 herb-tier 字段

| Tier | 字段 | 密度 | 设计说明 |
|---|---|---|---|
| Tier 1 - Family (Linnaean) | `herb_family` | 54.1% (in_map=True 时填) | 55 unique families, 排除 placeholder "flavonoid_compound" (45 records) |
| Tier 2 - Species | `herb_canonical_latin` | 99.6% (但 in_map=True 时才 curated) | 944 unique species post-normalization |
| Tier 3 - Compound | `herb_active_compound` | 39.1% | 561 unique compounds (单分子活性成分) |
| Supp - Formula | `tcm_formula_name` | 16.4% | 322 unique formulas, underpowered for Fisher (median 1 record/formula) |

### 过滤规则

通用：`confidence >= 0.7` + `mechanism not in {unspecified, other}` (Day 13 alignment)

Tier-specific：
- **`herb_in_map = True` 限制应用于全部三 tier**：保证 cross-tier consistency 在**同一 record pool** 上分析，避免子集间比较的伪信号
- 清理字符串型空值: "null" / "unknown" / "not specified" / "" -> dropped
- Tier 1 排除 "flavonoid_compound" placeholder

### Entity 频次阈值（异构）

- Family: `>= 10 records` -> 24/54 entities retained
- Species: `>= 10 records` -> 32/97 entities retained
- Compound: `>= 5 records` -> 23/251 entities retained

**异构阈值的 paper Methods 措辞**：
"Given the inherent sparsity of compound-level data (single-compound study designs yielding a median of 1.8 records per compound after in-map normalization), we applied a heterogeneous entity threshold: 10 records minimum for family and species tiers and 5 records minimum for the compound tier. This preserved analytical power across all three tiers while acknowledging the structural difference in entity-level sample sizes."

### 统计方法 (与 Day 13 同构)

- per-cell Fisher exact two-sided
- BH-FDR within tier (3 个独立 FDR universes, 各 ~350-510 tests)
- Strong enrichment: `q<0.05 AND OR>2 AND obs>=5`
- Strong depletion: `q<0.05 AND OR<0.5 AND expected>=5`
- Haldane-Anscombe (+0.5) for log2(OR) visualization

### Cross-tier consistency classification (8 class)

Walk every (family, species, compound) co-occurrence in retained data; lookup tier-level sig status per mechanism; classify chain:

| Pattern (F_sig, S_sig, C_sig) | Class | 含义 |
|---|---|---|
| (T, T, T) | **FULL_CHAIN** | 三层都显著 (SJW 范式) |
| (T, T, no_compound_data) | FAMILY_SPECIES_NO_COMPOUND_DATA | compound 不在 retained set |
| (T, T, F) | F_S_COMPOUND_NOT_SIG | compound 在但不显著 |
| (T, F, -) | **FAMILY_PERVASIVE** | family 显著但 species 不（多 species 共贡献） |
| (F, T, -) | **SPECIES_SPECIFIC** | species 显著但 family 不（被同 family 其他物种稀释） |
| (F, F, T) | COMPOUND_ORPHAN | 仅 compound 显著（罕见） |
| (F, T, T) | SPECIES_COMPOUND_NO_FAMILY | species+compound 显著但 family 不 |
| (F, F, F) | ALL_NS | 全 ns（不计入 sig chain 统计） |

## 关键统计

| Tier | Cells | Strong Enr | Strong Dep | Weak Sig |
|---|---|---|---|---|
| Family | 384 | **6** | 1 | 1 |
| Species | 512 | **5** | 0 | 1 |
| Compound | 345 | **1** | 0 | 0 |
| **Total** | **1,241** | **12** | **1** | **2** |

**Chain class 分布 (sig chains only, n=15)**:

| Class | n | %  |
|---|---|---|
| FAMILY_PERVASIVE | 8 | 53% |
| SPECIES_SPECIFIC | 3 | 20% |
| FAMILY_SPECIES_NO_COMPOUND_DATA | 2 | 13% |
| **FULL_CHAIN** | **1** | **7%** |
| F_S_COMPOUND_NOT_SIG | 1 | 7% |

---

## Findings (F24-F29)

### F24 -- SJW: 唯一 FULL_CHAIN exemplar ⭐⭐⭐
Family    Hypericaceae         x CYP_induction  OR=14.20  q=2.91e-17
Species   Hypericum perforatum x CYP_induction  OR=14.71  q=4.41e-17
Compound  hyperforin           x CYP_induction  OR=18.73  q=3.89e-05
OR 沿三层 **14.20 → 14.71 → 18.73 递增**——信号越深越精纯。q 跨 17 个数量级。是文献中唯一三层全显著的完整追溯链。

**paper §4 narrative**: "The St. John's wort PXR/CYP3A4 induction axis is the only mechanism-herb relationship in our corpus that achieves complete taxonomic-to-molecular signal consistency. This reflects (1) Hypericaceae being a monogeneric family in our data (Hypericum perforatum is its sole retained representative), (2) hyperforin being the dominant pharmacologically-studied compound, and (3) the SJW-CYP3A4 paradigm being the field's most mechanistically resolved case (CiteSpace Era 1 burst, Day 12 A; bibliometrix Q2 niche, Day 12 B)."

### F25 -- Lamiaceae: FAMILY_PERVASIVE 标本

8 个 chain 全部模式 [F+S-C-]，涉及 2 个 mechanism × 2 个 species × 4 个 compound：

| Family | Species | Compound | Mechanism |
|---|---|---|---|
| Lamiaceae (sig) | Salvia miltiorrhiza (ns) | cryptotanshinone (ns) | P-gp_inhibition |
| Lamiaceae | Salvia miltiorrhiza | salvianolic acid B | P-gp_inhibition |
| Lamiaceae | Salvia miltiorrhiza | tanshinone IIA | P-gp_inhibition |
| Lamiaceae | Scutellaria baicalensis | wogonin | P-gp_inhibition |
| (同样四链 for transporter_modulation) |

**信号结构**: Lamiaceae 整体 P-gp_inh OR=3.16 (q<0.05) 但 Salvia 单独 OR=1.5 (ns), Scutellaria 单独 OR=1.2 (ns)。**Family layer 揭示了 latent PK 活性, 被 congeneric species 间的 record fragmentation 掩盖在 species 分辨率下**。

**paper §4 narrative**: "Lamiaceae shows a distinctive FAMILY_PERVASIVE signature for both P-gp_inhibition and transporter_modulation. Neither Salvia miltiorrhiza nor Scutellaria baicalensis individually meets species-level enrichment thresholds, yet their combined contribution generates statistically robust family-tier signals. This represents a methodological lesson: aggregating across congeneric species can surface PK activity that is invisible at the species resolution due to record fragmentation."

### F26 -- Glycyrrhiza x UGT_inhibition: SPECIES_SPECIFIC 教科书 case ⭐

3 个 chain 全部 [F-S+C-]：

| Family | Species | Compound | Mechanism | family_q | species_q |
|---|---|---|---|---|---|
| Fabaceae (ns) | Glycyrrhiza uralensis (sig, OR=5.12, q=0.04) | glycyrrhetinic acid (ns) | UGT_inhibition |
| Fabaceae | Glycyrrhiza uralensis | glycyrrhizic acid | UGT_inhibition |
| Fabaceae | Glycyrrhiza uralensis | glycyrrhizin | UGT_inhibition |

**关键**: Fabaceae 含 4 个 retained species（Astragalus, Glycyrrhiza, Pueraria, Sophora），但**只有 Glycyrrhiza uralensis 携带 UGT_inh 信号**，被其他三 species 的 non-UGT 研究稀释到 family 层不显著。

**paper §4 narrative**: "Glycyrrhiza uralensis × UGT_inhibition represents the cleanest SPECIES_SPECIFIC case in our analysis. While the family Fabaceae shows no UGT enrichment overall (q>0.05, diluted by Astragalus membranaceus, Pueraria lobata, and Sophora flavescens having distinct mechanistic profiles), licorice singularly drives the UGT inhibition signal at species resolution. Three structurally-related compounds (glycyrrhizin and its hydrolysis products glycyrrhizic acid + glycyrrhetinic acid) co-occur in this species but individually do not reach compound-tier statistical significance, suggesting the UGT inhibition is a class-effect of the glycyrrhizin chemotype rather than a single-compound property."

### F27 -- Piperaceae / Acanthaceae / Animal_derived: PARTIAL chains as corpus-coverage signals

3 chains terminate before compound tier:
- Piperaceae > Piper nigrum (CYP_inh, F+S+) > [None] -- piperine 不在 retained compounds (< 5 records)
- Acanthaceae > Andrographis paniculata (CYP_inh, F+S+) > andrographolide (compound F-) -- 化合物 retained 但不显著
- Animal_derived > Bufo bufo gargarizans (receptor_synergism, F+S+) > [None]

**paper §4 narrative**: "Three additional family-species enrichments do not propagate to the compound tier. For Piperaceae × CYP_inhibition, the obvious biochemical driver piperine is well-established as a CYP3A4 inhibitor in the broader literature but failed to meet our retention threshold (>=5 records) in this corpus, reflecting a coverage limitation rather than a biological discrepancy. For Acanthaceae × CYP_inhibition, andrographolide is retained but does not reach compound-tier statistical significance, indicating either multiple Andrographis compounds contribute to the inhibition phenotype or the per-compound sample size is below the FDR-corrected detection threshold."

### F28 -- Compound tier sparsity 是单成分研究范式的必然结果

1/23 entities (4.3%) 达 strong enrichment in compound tier
vs Family 6/24 (25%), Species 5/32 (15.6%).

**不是 FDR 校正过严**：compound tier 总 N=186 远小于 family/species (~750-850)，单成分文献天然 "1 compound per paper" 限制了 per-compound sample size。

**paper §4 Methods limitation narrative**: "The dramatic sparsity of compound-tier enrichments (1 of 23 retained compounds vs 5-6 enrichments per tier at family/species levels) is not a statistical artifact but reflects the structural nature of pharmacological literature: single-compound mechanistic studies generate one record per (paper, compound) pair, whereas species-level studies aggregate across multiple compounds and herbs aggregate across multiple species. This produces a power gradient (family > species > compound) that is intrinsic to the field's publication conventions, not to our analytical pipeline."

### F29 -- Mechanism-specific natural resolution layers ⭐⭐

| Mechanism | Dominant chain class | Natural resolution |
|---|---|---|
| CYP_induction | **FULL_CHAIN** (n=1, SJW) | Molecular (compound) |
| CYP_inhibition | PARTIAL (n=2, Piperaceae + Acanthaceae) | Species |
| UGT_inhibition | **SPECIES_SPECIFIC** (n=3, Glycyrrhiza) | Species |
| P-gp_inhibition | **FAMILY_PERVASIVE** (n=4, Lamiaceae) | Family |
| transporter_modulation | **FAMILY_PERVASIVE** (n=4, Lamiaceae) | Family |
| receptor_synergism | PARTIAL (n=1, Animal_derived) | Species |

**paper §4 novel finding**: 不同 mechanism 类型的研究文献在 herb 分类层级中**自然停在不同分辨率**——transport-related mechanisms (P-gp, transporter) 偏 family-level（多物种共享 PK barrier biology），CYP_induction 偏 compound-level（PXR 激活高度依赖单一 ligand 结构），UGT_inhibition 中间停在 species-level（chemotype-specific 但跨化合物变体一致）。

这是 cross-tier consistency 分析方法的**核心 paper §4 contribution**：bibliometric herb-mechanism 文献的第一次显式分层级 mapping。

---

## Discussion §4 paragraph drafts (5 个新段)

### §4.x.13 -- Three-tier herb stratification 作为 methodological novelty

"To our knowledge, no prior bibliometric study of TCM-HDI literature has stratified herb mentions across multiple taxonomic-to-molecular tiers. Most existing reviews pool all herb mentions at a single resolution (typically species or common name), or focus on a single herb of interest. By exploiting Schema v3's hierarchical herb mapping (Linnaean family / canonical Latin species / single active compound), we constructed three independent Fisher exact enrichment matrices on the same record pool (n=1,676 mapped interactions), enabling the first cross-tier consistency analysis of how mechanism-herb associations distribute across taxonomic resolution. The hierarchical structure necessitated a heterogeneous entity-frequency threshold (>=10 records for family/species, >=5 for compound) to reflect the intrinsic record-density gradient (family > species > compound) generated by pharmacological publication conventions."

### §4.x.14 -- SJW (Hypericum perforatum / hyperforin) 作为 FULL_CHAIN exemplar

"St. John's wort (Hypericaceae -> Hypericum perforatum -> hyperforin -> CYP_induction) is the unique FULL_CHAIN case in our corpus, with all three tiers reaching strong enrichment (q ranging from 4e-17 to 4e-5 across family, species, compound levels). The odds ratio increases monotonically with taxonomic depth (14.20 -> 14.71 -> 18.73), reflecting signal purification as the resolution narrows from family to compound. Three convergent factors enable this consistency: (1) Hypericaceae is a monogeneric family in our retained data, making family- and species-level analyses statistically equivalent; (2) hyperforin is the dominant pharmacologically-studied SJW constituent (vs hypericin, hyperoside, others) for PXR/CYP3A4 induction; (3) SJW-warfarin and SJW-cyclosporine clinical safety events drove sustained mechanistic research from 2005 onward (CiteSpace Era 1 burst, Day 12 A). No other (mechanism, herb) pair in our corpus combines monogeneric taxonomic isolation, single-compound dominance, and sustained safety-driven literature volume."

### §4.x.15 -- Mechanism-specific natural resolution layers as a generalizable principle

"A novel observation from cross-tier consistency analysis is that different HDI mechanism types stabilize at different taxonomic resolutions. CYP_induction reaches FULL_CHAIN resolution (compound-level) only for SJW; CYP_inhibition consistently resolves at the species level (Piper nigrum, Andrographis paniculata); UGT_inhibition is SPECIES_SPECIFIC (Glycyrrhiza uralensis alone within Fabaceae); P-gp_inhibition and transporter_modulation are FAMILY_PERVASIVE (Lamiaceae as a whole, not any single species). This pattern reflects underlying pharmacological biology: PXR/CYP3A4 induction requires specific ligand-receptor binding (high compound specificity, low taxonomic conservation); ABC transporter modulation reflects broader phytochemical interference with membrane proteins (low compound specificity, high taxonomic conservation). The bibliometric pattern thus recapitulates mechanistic biology, suggesting cross-tier consistency analysis is a valid epistemic tool for inferring mechanism specificity from literature."

### §4.x.16 -- Single-compound study design as compound-tier inference limit

"Our compound tier yielded only one strong enrichment (hyperforin x CYP_induction) of 345 tested cells (0.3%), in contrast to the family and species tiers' 25% and 15.6% enrichment rates respectively. This sparsity is not a statistical artifact but reflects the structural reality of pharmacological literature: mechanism-resolved studies of natural products typically investigate one compound at a time, generating a median 1.8 records per compound in our retained dataset even after restricting to mapped herbs. Family- and species-tier analyses aggregate signal across multiple records per entity, gaining statistical power. The compound tier thus represents the inferential floor in current literature; meaningful compound-level mechanism enrichment would require either (a) corpus expansion to 10x current scale, (b) deeper LLM-assisted compound extraction from semi-structured methods sections, or (c) integration of structured pharmacological databases (DrugBank, ChEMBL, TCMSP)."

### §4.x.17 -- Schema v3 herb_in_map curation enables cross-tier consistency

"A precondition for our cross-tier analysis is the curated `herb_in_map` flag in Schema v3, which restricts analysis to 1,676 interactions (54.1% of confidence-filtered records) where herbal entities are mapped to a normalized reference. Unmapped entities (45.9%) carry raw LLM-extracted Latin binomials that vary in spelling and synonymy, fragmenting frequency counts across orthographic variants. Applying the in_map=True restriction sacrifices half the records but enables three critical analytical properties: (1) identical record pool across all three tiers ensures cross-tier comparisons are tier-resolution comparisons, not subset comparisons; (2) Linnaean herb_family field is only populated for curated entities; (3) compound entities reference the same species canonicalization. Without Schema v3 mapping, cross-tier consistency analysis would be confounded by entity-identity ambiguity. This argues for curated entity normalization as a foundational step in any LLM-assisted bibliometric pipeline targeting hierarchical entity analyses."

---

## Data assets

| File | Type | Paper use |
|---|---|---|
| `results/figures/fig11_three_tier_heatmaps.{png,pdf,svg}` | Fig | **Paper Fig 11** (3-panel heatmap, log2_OR diverging, PK/PD groups) |
| `results/figures/fig12_cross_tier_chain_sankey.html` | Fig | Paper Fig 12 (PDF version pending Day 16 kaleido upgrade or mpl rewrite) |
| `data/processed/herb_tier_clean.parquet` | Data | Long-form clean data for downstream Day 16+ analyses |
| `results/tables/table_herb_{family,species,compound}_x_mechanism_matrix.csv` | Tables | 3 raw count matrices |
| `results/tables/table_herb_{family,species,compound}_{row,mech}_marginals.csv` | Tables | 6 marginal totals |
| `results/tables/table_herb_{family,species,compound}_x_mechanism_enrichment_{full,significant,top_enriched,top_depleted}.csv` | Tables | 12 Fisher result CSVs |
| `results/tables/table_herb_cross_tier_chains.csv` | Tables | **Paper Table 6** (15 sig chains) |
| `results/tables/table_herb_cross_tier_consistency_summary.csv` | Tables | Per-mechanism chain class breakdown |
| `results/tables/table_herb_formula_supp_descriptive.csv` | Tables | Supp Table SX (top-15 formula, descriptive only, no Fisher) |

## Engineering notes

- **Compound tier heterogeneous threshold (>=5 vs >=10)** justified by 1.8 records-per-compound median; reflects single-compound study design
- **in_map=True restriction across all three tiers** ensures same record pool for cross-tier consistency; sacrifices 45.9% records but enables tier-resolution comparisons rather than subset comparisons
- **flavonoid_compound placeholder removed** from family tier (45 records) -- Schema v3 hack for compound-only records with no plant source
- **Per-cell Fisher + within-tier BH-FDR** (3 separate FDR universes): preserves tier-level effect size for narrative claims
- **Haldane-Anscombe (+0.5) for log2(OR)** in fig11 visualization: handles cells with obs=0 without -inf
- **fig11 SciencePlots removed**: system lacks LaTeX, replaced with clean mpl base + DejaVu Sans
- **fig11 compact mechanism names** (CYP_inh / transporter / rec_synerg etc.) and 22x11 in figsize + wspace=0.95 to avoid inter-panel label collisions
- **fig12 kaleido < 1.0 hang issue**: HTML primary deliverable for Day 15; static PDF pending Day 16
- **fig12 dummy scatter trace axes hidden** via update_xaxes/yaxes visible=False (legend needed scatter traces, axes would leak ticks)
- **6 scripts in 09_herb_tier_mechanism/**: 34_block0 recon / 35_block1 clean+matrices / 36_block2 Fisher / 37_block3 cross-tier / 38_block4a fig11 / 39_block4b fig12

## Cross-day triangulation (5 sources converge for SJW)

| Source | Finding |
|---|---|
| bibliometrix R (Day 12 B) | SJW + grapefruit + P-gp in Q2 niche cluster |
| CiteSpace (Day 12 A) | Era 1 burst (2005-2012): SJW + ginkgo + milk thistle + grapefruit |
| Static topic enrichment (Day 13) | #5 antidepressants x CYP_induction (OR=26.7, q=9.5e-15) |
| Trajectory (Day 14) | #6 warfarin x additive_toxicity DECLINING (case-era ghost) |
| **Three-tier herb (Day 15)** | **Hypericaceae -> H. perforatum -> hyperforin x CYP_induction FULL_CHAIN** (OR 14.20->14.71->18.73) |

Five independent methods + data subsets all converge on SJW-CYP3A4 paradigm as the field's foundational mechanism case.

## Next: Day 16

(a) fig12 paper-grade PDF (upgrade kaleido OR write matplotlib alternative)
(b) Inkscape figure polish for fig9 / fig10 / fig11
(c) PRISMA flow diagram
(d) Cytoscape integration (data/citespace_workspace/project/667.graphml from Day 12 A)
(e) Initial Methods + Results section drafting