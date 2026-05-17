# Topic × Mechanism × Era Trajectory Findings (Day 14)

## Overview

Day 14 把 Day 13 静态分析（37 topics × 16 mechanisms × 1,738 record-mechanism pairs）扩展到时间维度。将语料分为 3 个不重叠的 7-9 年 period，对 Day 13 识别出的 top 20 强富集 + top 20 强排斥（共 40 pair）做 per-era Fisher exact + BH-FDR 检验，按 8 类 trajectory pattern 分类。

**核心结论**：TCM-HDI 文献的 PK/PD 结构二分（Day 13 F12）**主要是历史性的，非近年才形成**。45% 的最强 Day 13 富集/排斥模式在三个 era 都达到统计显著；72.5% 是历史锚定型。Period 3 (2020-2026) 仅添加 3 个 EMERGING 富集，且都在已有的 PK 或 PD 空间内**深化**，没有桥接两个空间。

数据资产：`results/tables/table_topic_x_mechanism_era_matrix_period{1,2,3}.csv` + `*_trajectory_{enrichment,depletion}.csv` + `results/figures/fig10_topic_x_mechanism_x_era_trajectory.{png,pdf,svg}`。

## Era binning rationale (paper §2.x 候选)

| Period | Year range | Duration | Pairs | % | Conceptual mapping |
|---|---|---|---|---|---|
| Period 1 | 2005-2013 | 9y | 517 | 29.7% | Classical case-based era (≈ Day 12 A Era 1) |
| Period 2 | 2014-2019 | 6y | 687 | 39.5% | Mechanistic deepening era (≈ Day 12 A Era 2-3) |
| Period 3 | 2020-2026 | 7y | 534 | 30.7% | Systems-level era (≈ Day 12 A Era 4) |

设计选择：
- **3 个 disjoint period** 而非 Day 12 A 的 4 个 overlapping era：disjoint 保证 Fisher 测试的 sample 独立性
- **样本量大致均衡** (30/40/30 split)：避免 P2 过大主导
- **概念对齐 Day 12 A burst era**：narrative 在三种工具栈间一致

## Methods 摘要

- **per-era Fisher exact two-sided** per cell in era matrix
- **BH-FDR within each era** (每 era 30 测试) - 不跨 era 联合 FDR (维持 era 内 power)
- **direction-aware significance**: enrichment 要求 (obs > exp) AND (q < 0.05); depletion 要求 (obs < exp) AND (q < 0.05)
- **Trajectory classification** based on 3 era's significance booleans (8 classes via Cartesian product)

## Trajectory class 定义 (8 类)

| Pattern (sig_P1, P2, P3) | Class | 含义 |
|---|---|---|
| (1, 1, 1) | **STABLE** | 三 era 都显著 |
| (0, 0, 1) | **EMERGING** | 仅 Period 3 显著 (Era 4 新现象) |
| (1, 0, 0) | **DECLINING** | 仅 Period 1 显著 (Era 1 ghost) |
| (0, 1, 1) | **RISING** | Period 2 + 3 (起势) |
| (1, 1, 0) | **FADING** | Period 1 + 2 (衰减) |
| (0, 1, 0) | **TRANSIENT_MIDDLE** | 仅 P2 |
| (1, 0, 1) | **BIMODAL** | P1 + P3, P2 不显著 |
| (0, 0, 0) | **WEAK_NONE** | 全局显著但 era 内被 marginal 稀释 |

## Trajectory 分布

| Class | Enrichment (n=20) | Depletion (n=20) | Total | % of 40 |
|---|---|---|---|---|
| STABLE | 10 | 8 | 18 | 45% |
| FADING | 3 | 4 | 7 | 17.5% |
| EMERGING | 3 | 0 | 3 | 7.5% |
| DECLINING | 1 | 3 | 4 | 10% |
| TRANSIENT_MIDDLE | 2 | 1 | 3 | 7.5% |
| WEAK_NONE | 0 | 3 | 3 | 7.5% |
| RISING | 1 | 1 | 2 | 5% |
| BIMODAL | 0 | 0 | 0 | 0% |

**关键聚合统计**：
- 历史锚定型 (STABLE + FADING + DECLINING) = 14 enr + 15 dep = **29/40 = 72.5%**
- 新现象 (EMERGING + RISING) = 4 enr + 1 dep = **5/40 = 12.5%**

---

## Findings (F17-F23)

### F17 — H1 confirmed: PK/PD bifurcation is historically established ⭐

72.5% of strongest patterns are historically anchored. Day 13 的结构性发现**不是近年才形成的**——从 2005-2013 就已经显著。

→ paper §4 narrative refinement: 从"近年 PK/PD 极化"修正为"PK/PD 极化是 TCM-HDI 研究领域的奠基属性"。

### F18 — Three EMERGING enrichments all map to Era 4 paradigm

| Pair | P1 obs | P2 obs | P3 obs | Mechanism axis |
|---|---|---|---|---|
| #27 metabolites × **absorption_alteration** | 0 | 0 | 10 | PK |
| #10 hormone × **signaling_pathway_modulation** | 0 | 0 | 7 | PD |
| #20 cancer/networkPharm × **signaling_pathway_modulation** | 0 | 1 | 5 | PD |

两个 EMERGING 集中在 `signaling_pathway_modulation` —— 这个机制是 Period 3 的标志性新轴，对应 Day 12 A burst Era 4 的 `signaling pathway` + `network pharmacology` + `molecular docking` 系统范式。

**关键观察**：3 个 EMERGING 都在**已有的 PK 或 PD 空间内深化**，没有桥接两个空间。Era 4 范式漂移**扩张了原有结构而非合并**。

### F19 — One DECLINING enrichment: #6 warfarin × additive_toxicity (4/1/0)

| Period | obs | sig |
|---|---|---|
| P1 (2005-2013) | 4 | ✓ |
| P2 (2014-2019) | 1 | ✗ |
| P3 (2020-2026) | 0 | ✗ |

Era 1 case-based safety paradigm 最经典案例（warfarin-ginkgo, warfarin-SJW additive bleeding risk）的机制层级**已经在 Period 3 完全消失**。

→ paper §4 narrative: 经典 HDI case-based 文献并未消亡（#6 warfarin 仍是 220-doc 大 cluster），但**研究焦点从"事件记录"转向了别的机制**——具体的 additive_toxicity 信号被代谢机制研究取代。

### F20 — STABLE enrichment backbone: 22-year invariants

Top STABLE pairs (三 era 都显著)：
- `#30 cyp inhibition × CYP_inhibition`: 96 / 166 / 76 — canonical CYP backbone
- `#24 inhibition ugt × UGT_inhibition`: 23 / 36 / 6 — UGT (peak P2, decay P3)
- `#11 anticancer × receptor_synergism`: stable PD signature
- `#11 anticancer × P-gp_inhibition`: stable MDR literature
- `#32 drug transporters × transporter_modulation`: 8 / 22 / 11
- `#9 PXR × CYP_induction`: 19 / 11 / 5
- `#23 antimicrobial × synergistic_efficacy`: 22 / 11 / 10
- `#28 medicinal plants × receptor_synergism`: 19 / 9 / 6
- `#17 hepatotoxicity × organ_toxicity_modulation`: 15 / 14 / 27 (P3 strengthening within STABLE)

### F21 — STABLE depletion backbone: 22-year systematic rejections ⭐⭐

PK-pure topics persistently reject PD across all eras:
- `#30 × synergistic_efficacy`: **0 / 0 / 0** (零 PD synergy in CYP 文献 22 年)
- `#30 × receptor_synergism`: **0 / 0 / 0**
- `#30 × additive_toxicity`: **0 / 0 / 0**
- `#11 × CYP_inhibition`: 0 / 4 / 1 (anticancer 22 年 CYP 回避)
- `#11 × CYP_induction`: 1 / 0 / 0
- `#23 × CYP_inhibition`: **0 / 0 / 0** (antimicrobial 完全不写 CYP)

→ paper §4 强论据 ⭐⭐："The PK/PD bifurcation has been a foundational property of TCM-HDI mechanism literature since the field's inception, with several topic-mechanism pairs showing **complete 22-year exclusion** (#30 cyp inhibition × synergistic_efficacy / receptor_synergism / additive_toxicity all maintain observed = 0 across Periods 1-3)."

### F22 — Emerging topics absent from trajectory analysis (keyword-mechanism lag)

Day 12 A 最强 Era 4 burst topics：
- `#15 gut microbiome` (median 2024, burst strength 8.74)
- `#22 network pharmacology` (median 2023, burst strength 27.59 — **历史最强 burst**)

Neither reached Day 13 enrichment significance (no mechanism × topic pair survived q<0.05 + OR>2 + obs≥5). Therefore absent from Day 14 trajectory analysis.

→ paper §4 方法学观察 (paper §4.x.12): keyword-level emergence (CiteSpace burst) precedes mechanism-level stabilization. 文献最热的 burst keyword 还没生成足够的 mechanism-resolved literature 达到统计显著。**两个 bibliometric 方法学操作在互补 timescale 上**。

### F23 — Refined 4-method triangulation

| Method | Sample | Day 14-relevant finding |
|---|---|---|
| bibliometrix R (Day 12 B) | WoS 3,091 | Q2 Niche cluster: SJW + grapefruit + P-gp + ginkgo + milk thistle |
| CiteSpace (Day 12 A) | WoS 3,091 | Burst Era 1 (2005-2012): SJW + ginkgo + milk thistle + grapefruit |
| Static enrichment (Day 13) | 1,662 | #5 antidepressants × CYP_induction enriched (OR=26.7, q=9.5e-15) |
| Trajectory (Day 14) | 1,662 | **#6 warfarin × additive_toxicity DECLINING** (4/1/0) |

四个独立工具 / 算法 / 数据子集 / 时间维度**收敛于同一现象**：classical case-based herb-drug safety research (SJW-warfarin canon)
- bibliometrix 显示 closed citation community
- CiteSpace 显示 Era 1 强 burst
- Day 13 显示 mechanism × topic 强富集
- Day 14 显示 trajectory 已 DECLINING

paper §4 方法学三角验证全面闭环。

---

## Discussion §4 段草稿（4 个新段，paper 直接可用）

### §4.x.9 — Historical persistence of PK/PD bifurcation

"Temporal stratification of the Day 13 enrichment patterns across three TCM-HDI eras reveals that the structural bifurcation between PK-pure and PD-pure topic-mechanism associations is not a recent phenomenon. Of the 40 strongest Day 13 enrichment and depletion pairs, 18 (45%) show STABLE significance across all three periods (2005-2013, 2014-2019, 2020-2026), and an additional 11 (27.5%) are historically anchored as FADING or DECLINING. Only 5 pairs (12.5%) show patterns consistent with recent emergence or rising trajectories. The bifurcation we documented in Day 13 has been structurally present since the earliest period of TCM-HDI mechanism research, suggesting that the methodological-vs-clinical divide is a foundational property of the field rather than an emergent stratification."

### §4.x.10 — Era 4 emerging enrichments expand depth rather than bridge

"Three (topic, mechanism) pairs show EMERGING trajectory — statistically null in Periods 1 and 2, then reaching significance in Period 3 (2020-2026). All three concentrate in mechanisms consistent with the CiteSpace burst Era 4 systems-level paradigm: #27 (metabolites topic) × absorption_alteration captures recent emphasis on TCM bioavailability characterization; #10 (hormone) × signaling_pathway_modulation and #20 (cancer / network pharmacology) × signaling_pathway_modulation both reflect the methodological shift toward intracellular signaling pathway analysis. Critically, these three new enrichments do not bridge the PK/PD bifurcation. Two are pharmacodynamic enrichments embedded within already-PD-leaning topics (#10, #20), and one is a pharmacokinetic enrichment within an already-PK-leaning metabolite topic (#27). The Era 4 paradigm shift therefore expands depth within rather than collapses the bifurcated structure."

### §4.x.11 — One DECLINING enrichment as case-based safety era ghost

"A single enrichment shows DECLINING trajectory: #6 (warfarin) × additive_toxicity, statistically significant in Period 1 (observed=4, expected=0.77, OR=8.4, q=9e-3) but not in Periods 2 or 3 (observed=1 and 0 respectively). This pattern is consistent with the CiteSpace burst Era 1 (2005-2012) identification of the warfarin-herb safety case canon (St. John's wort, grapefruit juice, ginkgo biloba) as the field's strongest historical phenomenon. Despite the warfarin topic remaining among the largest in the corpus (n=220 papers), the specific additive-toxicity mechanism that characterized its initial burst era has decayed below mechanism-extraction detection thresholds in recent literature. This is consistent with case-based safety research evolving from event documentation in Period 1 toward mechanism investigation in Periods 2 and 3."

### §4.x.12 — The keyword-mechanism lag (methodological observation)

"Notably, the two topics most strongly emerging in keyword space (CiteSpace Era 4 burst: #15 gut microbiome, median publication year 2024; #22 network pharmacology, median 2023, burst strength 27.59 — the field's all-time strongest burst) did not register significant mechanism enrichment in our static Day 13 analysis and therefore do not appear in the Day 14 trajectory analysis. This indicates a structural lag between keyword emergence and mechanism stabilization: the field's most recently bursting concepts (network pharmacology, gut microbiota) have not yet generated sufficient mechanism-level extraction signal to reach statistical significance, despite their prominence in keyword co-occurrence networks. This lag is methodologically informative: burst-keyword analysis surfaces concept emergence earlier than mechanism-frequency analysis, suggesting these two bibliometric approaches operate on complementary timescales of research evolution."

---

## Data assets

| File | Rows / dims | Paper use |
|---|---|---|
| `results/figures/fig10_topic_x_mechanism_x_era_trajectory.{png,pdf,svg}` | - | **Paper Fig 10** (trajectory slopegraph w/ anti-collision labels + leader lines) |
| `results/tables/table_topic_x_mechanism_era_matrix_period1.csv` | 37×16 | Supp Table S10 |
| `results/tables/table_topic_x_mechanism_era_matrix_period2.csv` | 37×16 | Supp Table S11 |
| `results/tables/table_topic_x_mechanism_era_matrix_period3.csv` | 37×16 | Supp Table S12 |
| `results/tables/table_topic_x_mechanism_trajectory_enrichment.csv` | 20 | Paper Table 5 |
| `results/tables/table_topic_x_mechanism_trajectory_depletion.csv` | 20 | Supp Table S13 |

## Engineering notes

- **Disjoint era scheme over overlapping**: Day 12 A's Era 1-4 share years (2010-2012 in Era 1 ∩ Era 2). For per-era Fisher, disjoint binning required for sample independence.
- **Within-era BH-FDR over cross-era pooled**: 30 tests per era vs 120 pooled. Within-era preserves effect size for era-level claims.
- **Direction-aware significance**: Fisher two-sided + manual (obs >/< exp) check avoids classifying a pair as STABLE-enriched when one era is sig-depleted.
- **Haldane-Anscombe (+0.5) for log2(OR)** in fig10 visualization handles era-specific zeros without ±inf.
- **Anti-collision label placement**: iterative 1D repel (MIN_GAP = 0.85 log2 units), 200 max iterations, leader lines.

## Next: Day 15

Herb tier × Mechanism (Linnaean botanical family / `flavonoid_compound` / `TCM_formula` three-tier Schema v3) orthogonal analysis. Combines with Day 13/14 findings for fig11 synthesis (Sankey or chord: herb tier → topic → mechanism → era).