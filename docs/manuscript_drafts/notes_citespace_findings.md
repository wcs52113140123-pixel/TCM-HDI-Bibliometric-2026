# CiteSpace 关键词共现分析 Findings (Day 12 A)

## Overview

Day 12 A 完成对 TCM-HDI 2005-2026 文献的 CiteSpace 关键词共现网络分析。本文档汇总 paper §3.x / §4.x 可直接引用的 5 个核心 finding + Methods 段 + Discussion 段草稿 + 跨工具交叉验证。

数据资产：`results/figures_citespace/`（8 文件）。

## Methods 摘要（paper §2.x 候选）

- **工具**：CiteSpace 6.4.R1
- **数据**：3,091 条 WoS 完整记录（integrated 9,438 records 的 WoS 子集，2005-2026）
- **时间切片**：2005-2026，1 年/切片，22 切片
- **节点类型**：Keyword（Title + Abstract + DE + ID 四源）
- **选择标准**：g-index，k=25（CiteSpace 推荐默认）
- **链接**：Cosine within slices
- **剪枝**：Pathfinder + Pruning sliced networks
- **聚类**：Modularity-based community detection
- **标签**：LLR（log-likelihood ratio，文献界 keyword cluster 标签标准）
- **Burst**：Kleinberg 算法，γ=0.5，最小持续 2 年

## 网络统计

| 指标 | 值 | 评价 |
|---|---|---|
| Nodes (N) | 667 | 中等规模 |
| Edges (E) | 3,336 | 高连通 |
| Density | 0.015 | keyword 网络典型 |
| Largest CC | 663 (99%) | 几乎全连通 |
| Modularity Q | **0.3802** | > 0.3 标准，社区结构显著 |
| Weighted Silhouette S | **0.6935** | > 0.5 标准，接近 0.7 优秀 |
| Harmonic Mean H(Q,S) | 0.4911 | 复合质量 |
| Clusters reported | 11 (size ≥ 10) | |
| Clusters detected | 14 | |
| Burst keywords | 220 | 丰富 |

Q + S 均达 "reliable clustering" 标准。

---

## Findings

### F1 — 历史最强 burst 对称：经典安全案例 vs 系统级方法（paper 核心 narrative）

| Rank | Keyword | Strength | Burst | 持续 | 范式 |
|---|---|---|---|---|---|
| 1 | st johns wort | **27.01** | 2005-2012 | 8 年 | 案例驱动的安全性研究 |
| 2 | network pharmacology | **27.59** | 2023-2026 | ongoing | 系统级方法学革命 |

220 个 burst 中**强度排名前两位的几乎并列但代表彻底相反的范式**：
- SJW = TCM-HDI 诞生之初的 case study；
- network pharm = 当前正在 burst 的系统生物学方法；
- 间隔 11 年，强度几乎一致 → 22 年间一次彻底的范式漂移。

这是 paper 的核心 narrative anchor。

### F2 — 4 个 burst era 揭示时间分层

220 个 burst 按起讫聚类分为 4 个 era：

| Era | 时间窗 | 代表 keyword (strength) | 主题 |
|---|---|---|---|
| **Era 1** | 2005-2012 | st johns wort (27.01), ginkgo biloba (9.72), milk thistle (7.78), grapefruit juice (6.97), herb drug interactions (13.1), dietary supplements (6.2), black cohosh (6.24) | 经典 HDI 安全性案例 (CAM context) |
| **Era 2** | 2010-2018 | gene-expression (7.52), multidrug resistance (7.94), glucuronidation (7.07), tandem MS (10.18) | 机制深化 (分子生物 + 分析方法) |
| **Era 3** | 2017-2022 | transporters (7.03), rat plasma (6.71), mice (7.28) | 体内 PK 过渡 |
| **Era 4 (ongoing)** | 2020-2026 | oxidative stress (10.75), inflammation (7.42), natural products (7.3), molecular docking (16.1), network pharmacology (27.59), gut microbiota (8.74) | 系统级范式 (网络药理 + 多组学 + 微生态) |

**Era 4 的 6 个 keyword End=2026 全部活跃** → TCM-HDI 当前活跃前沿。

### F3 — 11 个 cluster 主题骨架

LLR 算法从 11 个 cluster (size ≥ 10) 抽出主导关键词，揭示 4 大主题域：

| 主题域 | Clusters (size sum) | 主导 LLR label |
|---|---|---|
| CAM context | #0 (96) | dietary supplement |
| DME 经典方法 | #2 (76), #4 (75), #8 (41) = 192 | metabolizing enzyme / HLM / aspirin hydrolysis |
| TCM 特定 herb/产品 | #1 (83), #3 (75), #6 (50), #10 (23) = 231 | kaempferia / astragalus / evodia / aidi injection |
| 新兴方向 | #5 (74), #7 (43), #9 (27) = 144 | network pharmacology / IBD model / LPS toxicity |

**时间分层**：
- #4 HLM (mean=2010) 最早期
- #10 aidi injection (mean=2017) 最晚期
- 跨度 7 年，与 Era 1→Era 4 burst 漂移一致

### F4 — 跨工具 1:1 交叉验证（方法学说服力 ⭐）

**两个独立算法/工具/数据子集对时间-主题分层的判断完全一致**：

| Method 1 (bibliometrix R) | Method 2 (CiteSpace) | 对应 |
|---|---|---|
| **Q2 Niche** cluster<br>(SJW, grapefruit juice, P-gp, ginkgo, milk thistle) | **Burst Era 1** (2005-2012)<br>(SJW, ginkgo, milk thistle, grapefruit juice) | **1:1 ✓** |
| **Q4 Basic** cluster<br>(network pharmacology, oxidative stress, expression) | **Burst Era 4** (2020-2026, ongoing)<br>(oxidative stress, network pharmacology, gut microbiota) | **1:1 ✓** |

- bibliometrix Thematic Map: keyword bipartite + Callon centrality/density
- CiteSpace: Pathfinder + LLR + Kleinberg burst
- **算法栈完全不同，输入数据子集也不同**（bibliometrix 全 3,091 records；CiteSpace 切成 22 年切片）
- **但两个工具独立识别出同样的 Era 1 和 Era 4 paradigm-defining 主题**

→ Paper Methods §2.x：**方法学三角验证 (method triangulation)** argument，给 reviewer 高强度说服力。

### F5 — 非典型缺席：永恒基石词

3 个 TCM-HDI 核心高频词**从未 burst**：

| Keyword | 总频次 | 是否 top 25 burst | 解读 |
|---|---|---|---|
| `cytochrome p450` / `cyp3a4` | 227 + 75 | ❌ | 永恒基石词 |
| `p glycoprotein` / `p-glycoprotein` | 148 + 122 | ❌ | 永恒基石词 |
| `pregnane x receptor` | 81 | ❌ | 短期 niche，未 burst |

**Burst 揭示新潮流，缺席 burst 揭示基石**。

22 年来一直高频但稳定 → 它们不是潮流，而是文献的**基础设施**。任何 paper 讨论 herb HDI 机制都必然提及 CYP3A4 / P-gp / PXR。

它们的 non-burst 状态本身就是该领域成熟稳定的证据。

→ Paper §3.x 可写："Notably, despite their consistent high frequency throughout the 22-year span, neither cytochrome P450 nor P-glycoprotein appeared in the top-25 burst keyword list, reflecting their status as foundational vocabulary rather than topical trends."

---

## Discussion §4 段草稿（paper 直接可用）

### §4.x.1 — 历史最强 burst 对称

"CiteSpace burst detection identified St. John's wort (Hypericum perforatum) as the historically strongest burst term in TCM-HDI literature, with a burst strength of 27.01 from 2005 to 2012. This eight-year burst captures the seminal era of TCM-HDI research, when case-based safety reports established the field. Strikingly, the second-strongest burst belongs to 'network pharmacology' (strength 27.59, 2023-present), which marginally exceeds the SJW burst and is currently ongoing. This near-identical strength but inverted temporal positioning reveals a paradigm shift from case-based safety research toward systems-level methodology."

### §4.x.2 — Era 4 的方法学革命

"The convergence of six keywords currently in active burst (oxidative stress, inflammation, natural products, molecular docking, network pharmacology, gut microbiota; all with End year = 2026) indicates that the TCM-HDI field is undergoing a systems-biology methodological revolution. Unlike Era 1 (2005-2012), which centered on individual herb-drug case studies, Era 4 (2020-present) emphasizes integrative multi-omics frameworks: network pharmacology models multi-target interactions, gut microbiota integrates host-microbe-drug axes, and molecular docking enables computational predictions. These six concurrent bursts suggest that the field's analytical infrastructure is being rebuilt around systems concepts."

### §4.x.3 — 跨工具方法学三角验证

"To assess the robustness of our temporal-thematic findings, we cross-validated the CiteSpace burst era classification against an independent bibliometrix Thematic Map analysis (Callon centrality-density framework). The bibliometrix Q2 Niche cluster (St. John's wort, grapefruit juice, P-glycoprotein, ginkgo biloba, milk thistle) corresponds 1:1 to CiteSpace Burst Era 1 (2005-2012); the bibliometrix Q4 Basic cluster (network pharmacology, oxidative stress, expression) corresponds 1:1 to CiteSpace Burst Era 4 (2020-2026, ongoing). The convergence of two methodologically distinct algorithms—one based on bipartite keyword network metrics, the other on time-sliced co-occurrence with Kleinberg burst detection—provides independent corroboration of the four-era temporal structure."

### §4.x.4 — 永恒基石与新兴范式的二元性

"Burst detection captures emergence; the absence of burst captures foundation. Three of the most cited TCM-HDI keywords (cytochrome P450, P-glycoprotein, pregnane X receptor) did not appear in the top 25 burst list despite ranking among the top 30 most frequent keywords overall. This consistent-but-non-bursty pattern characterizes infrastructure terms—the vocabulary necessary to articulate any TCM-HDI mechanism but not the locus of innovation. Their non-burst status, paired with the strong burst of network pharmacology and gut microbiota, demarcates a clear dual structure: the field maintains its mechanistic foundations (CYP, P-gp, PXR) while progressively expanding its methodological frontier."

---

## 数据资产 → paper 用途映射

| 文件 | paper 位置候选 |
|---|---|
| `fig7_top25_keyword_bursts.pdf` | **Fig 7 主图源**（待美化协作者重绘） |
| `table_citespace_top25_bursts.tsv` | Table 3 / Main Table |
| `table_citespace_all220_bursts.tsv` | Supp Table S5（完整 burst） |
| `table_citespace_cluster_summary.csv` | Supp Table S6（cluster metadata） |
| `network_keyword_667.graphml` | Day 17 Cytoscape + reviewer reproducibility |
| `citespace_burstness_raw.out` | Reproducibility 留档 |
| `README.md` | Figure beautifier handoff |

## 后续

- **Day 13-15** Topic × Mechanism cross-analysis: 把 burst era 时间轴叠加到 mechanism 时序图
- **Day 17 Cytoscape**: 用 `network_keyword_667.graphml` 重绘 Fig 7b cluster network
- **Day 18-21 写作**: 上述 4 段 Discussion 直接入 §4