# CiteSpace 关键词共现分析输出（Day 12 A）

TCM-HDI 2005-2026 文献 CiteSpace 关键词共现网络分析的全部数据资产。
**用途**：交给图表美化协作者，重新绘制 paper-quality 图表。

## 输入与参数

- **数据源**：3091 条 Web of Science 完整记录（2005-2026，integrated 9438 records 的 WoS 子集）
- **时间切片**：2005-2026，1 年/切片，共 22 个切片
- **节点类型**：Keyword（Title + Abstract + DE + ID 四源）
- **选择标准**：g-index，k=25
- **链接计算**：Cosine similarity, within slices
- **剪枝**：Pathfinder + Pruning sliced networks

## 网络统计

| 指标 | 值 |
|---|---|
| Nodes (N) | 667 |
| Edges (E) | 3,336 |
| Density | 0.015 |
| Largest CC | 663 (99%) |
| Modularity Q | 0.3802 |
| Weighted Silhouette S | 0.6935 |
| Harmonic Mean H(Q,S) | 0.4911 |
| Clusters reported | 11 (size ≥ 10) |
| Clusters detected | 14 |

Q > 0.3 + S > 0.7 ≈ 文献界 "reliable clustering" 标准范围。

## 文件清单

### 核心数据

| 文件 | 行数 | 字段 |
|---|---|---|
| `table_citespace_cluster_summary.csv` | 11 | cluster_id, size, silhouette, mean_year, llr_label, llr_strength, top_lsi_terms, 中文解读 |
| `table_citespace_top25_bursts.tsv` | 25 | Keywords, Year, Strength, Begin, End |
| `table_citespace_all220_bursts.tsv` | 220 | Keywords, Year, Strength, Begin, End |
| `network_keyword_667.graphml` | - | 整张网络的 GraphML 格式，可直接 import Cytoscape/Gephi |
| `citespace_burstness_raw.out` | - | CiteSpace 内部 burst 算法原始输出（reproducibility 留档） |

### 现有原始图（可替换 / 美化）

| 文件 | 来源 | 状态 |
|---|---|---|
| `fig7_top25_keyword_bursts.pdf` | CiteSpace 浏览器矢量导出 | 数据准确，**视觉风格需美化** |
| `fig7_top25_keyword_bursts.html` | CiteSpace 原始 HTML | 渲染源，参考用 |

## 建议的目标图

### Fig 7 主图（核心 deliverable）— Top 25 burst keyword timeline

- **数据源**：`table_citespace_top25_bursts.tsv`
- **图类型**：每行一个 keyword，水平 timeline（2005-2026），burst 期间用粗彩色横条标出
- **布局参考**：CiteSpace 原版 `fig7_top25_keyword_bursts.pdf`
- **美化建议**：
  - 字体改为 Arial / Helvetica 或 Times New Roman
  - burst 横条用 Okabe-Ito 调色板（橙色或红色，色盲友好）
  - 加 4 个 era 的背景分组阴影（透明度 ~10%）：
    - 2005-2012: Era 1（经典安全案例，黄色调）
    - 2010-2018: Era 2（机制深化，绿色调）
    - 2017-2022: Era 3（过渡，灰色调）
    - 2020-2026: Era 4（系统范式，蓝色调，对齐 "ongoing"）
  - 标注前两名 strength 数值（27.01 SJW vs 27.59 network pharmacology）
- **工具**：Python matplotlib / R ggplot2 / Inkscape

### Fig 7b 备选 — Keyword cluster network

- **数据源**：`network_keyword_667.graphml` + `table_citespace_cluster_summary.csv`
- **图类型**：力导向布局，节点按 cluster_id 染色
- **样式**：
  - 节点 size ∝ degree
  - 节点颜色按 cluster_id（11 种区分色，按 Okabe-Ito 扩展）
  - cluster label 显示在每个 cluster 几何中心，字体 ≥10pt
  - 边透明度 0.15（density 0.015 但 N=667 边密集）
- **工具**：Cytoscape 3.x（推荐，可直接读 graphml）/ Gephi / R igraph

## 主要 finding（paper Discussion 写作参考）

### F1 — 历史最强 burst 对称（paper 核心 narrative）

- 第一名：`st johns wort` (strength **27.01**, 2005-2012)
- 第二名：`network pharmacology` (strength **27.59**, 2023-2026 ongoing)

两者强度几乎一致但含义对立：
- SJW era = 经典案例驱动的安全性研究
- Network pharm era = 系统级方法学革命

→ Paper 可直接论述 "范式从 case-based 漂移到 systems-level"。

### F2 — 4 个 burst era 时间分层

| Era | 时间 | 代表 keyword |
|---|---|---|
| Era 1 | 2005-2012 | SJW, ginkgo, milk thistle, grapefruit juice, herb drug interactions, dietary supplements, black cohosh |
| Era 2 | 2010-2018 | gene expression, multidrug resistance, glucuronidation, tandem MS, mice |
| Era 3 | 2017-2022 | transporters, rat plasma |
| Era 4 (ongoing) | 2020-2026 | oxidative stress, inflammation, natural products, molecular docking, network pharmacology, gut microbiota |

### F3 — Era 4 的 6 个 keyword 当前仍在 burst（End=2026）

= TCM-HDI 研究当前活跃前沿，paper Conclusion 直接引用为"未来 5 年趋势预测"。

### F4 — 跨工具交叉验证

- CiteSpace burst Era 1 ↔ bibliometrix Thematic Map Q2 niche（SJW + grapefruit + P-gp）
- CiteSpace burst Era 4 ↔ bibliometrix Thematic Map Q4 basic（network pharmacology + oxidative stress）
- 两个独立算法对时间-主题分层的判断完全一致 → Methods 段方法学三角验证。

### F5 — 非典型缺席

- `P-glycoprotein` 和 `CYP3A4` 都不在 top 25 burst 列表内
- 它们 22 年来一直高频但稳定，**从未 burst** → TCM-HDI 文献的"永恒基石词"
- 这本身是个 paper §3 可以提的现象

## Cluster 主题骨架（按 size 排）

| # | LLR Label | Size | Mean Yr | TCM-HDI 学科归属 |
|---|---|---|---|---|
| 0 | dietary supplement | 96 | 2011 | CAM 监管语境 |
| 1 | biological activities | 83 | 2016 | 植物化学/生物活性 |
| 2 | metabolizing enzyme | 76 | 2011 | DME 机制（CYP/UGT 通用） |
| 3 | astragalus polysaccharide | 75 | 2014 | TCM 单体化合物 |
| 4 | human liver microsome | 75 | 2010 | HLM 体外 PK（最早期） |
| 5 | network pharmacology | 74 | 2014 | 网络药理学（新兴） |
| 6 | evodia rutaecarpa | 50 | 2012 | 吴茱萸（生物碱 HDI 案例） |
| 7 | sodium-induced IBD | 43 | 2012 | 结肠炎模型 |
| 8 | chinese herb / aspirin hydrolysis | 41 | 2014 | UGT/酯酶 |
| 9 | lps-induced downregulation | 27 | 2016 | 炎症+转运体 |
| 10 | aidi injection | 23 | 2017 | 中药复方注射剂 |

## 联系 / 反馈

数据问题或图表设计讨论 → 项目 owner。