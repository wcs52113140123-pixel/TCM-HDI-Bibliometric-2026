"""
Day 25 Block B: Write bilingual annotation instructions for shimei
Output: results/supp_methods_s2/s2_annotation_instructions.md
"""
from pathlib import Path

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
OUT_PATH = REPO / "results" / "supp_methods_s2" / "s2_annotation_instructions.md"

content = """# Supp Methods S2 标注说明
*Annotation Instructions — LLM Extraction Independent Validation*

---

## 任务背景

我们的研究使用 GPT-4o-mini 从 9,717 篇中药-药物相互作用 (TCM-HDI) 文献中自动提取了 16 个机制类别。
为量化 LLM 提取的可靠性，需要一个**独立标注者**对随机抽取的 50 篇文献做盲法人工标注，
然后计算 Cohen's kappa 评估一致性。这个 kappa 值会写入 Supplementary Methods S2，
是我们投稿 *Briefings in Bioinformatics* 的关键 validation 证据。

## 任务概述

- **任务**：阅读 50 条文献摘要，独立判定每条所属机制类别（16 选 1，外加 1 个 "不确定" 选项）
- **盲法**：你**看不到** LLM 的标注结果，仅基于 abstract 本身做判断
- **预计用时**：3-4 小时（单条 ~4 分钟）
- **可分多日完成**，建议单次不超过 25 条，避免疲劳影响一致性

## 工作流程

1. 打开 `s2_annotator_form.xlsx`（dropdown 下拉值已预设，直接选即可）
2. 阅读每条记录的 `title` 和 `abstract`
   - 建议先看 abstract 末尾的 *Results* 和 *Conclusions* 段，机制信息通常在那里
3. 在 `your_mechanism_label` 下拉中选择**主机制类别**（**必填**）
4. 如果有第二个同等适用的类别，在 `your_alternative_label_optional` 下拉选填（可选）
5. 在 `your_confidence_low_med_high` 下拉中选择把握度（**必填**）
6. 如有需要注明的特殊情况，在 `your_notes_optional` 列写（可选）

---

## 16 机制类别定义

### 药代动力学 (PK) 相关 — 9 类

| Category (下拉值) | 定义 |
|---|---|
| `CYP_inhibition` | 中药/成分抑制 CYP450 酶活性 → 降低药物代谢，升高血药浓度 |
| `CYP_induction` | 中药诱导 CYP450 酶 → 加速药物代谢，降低血药浓度（典型：贯叶连翘 × 环孢素） |
| `UGT_inhibition` | 抑制 UGT 葡萄糖醛酸结合反应 |
| `UGT_induction` | 诱导 UGT |
| `P-gp_inhibition` | 抑制 P-糖蛋白外排 → 增加药物吸收/累积 |
| `P-gp_induction` | 诱导 P-糖蛋白 |
| `transporter_modulation` | 影响非 P-gp 的转运体（OATP、BCRP、MRP、OCT 等） |
| `absorption_alteration` | 改变药物吸收（改变胃排空、肠 pH、溶解度等，非转运体特异性） |
| `protein_binding_displacement` | 中药将药物从血浆蛋白结合中置换出 |

### 药效动力学 (PD) 相关 — 4 类

| Category | 定义 |
|---|---|
| `receptor_synergism` | 中药与药物作用于同一受体 → 效应增强 |
| `receptor_antagonism` | 中药拮抗药物的受体作用 |
| `synergistic_efficacy` | 联合用药药效大于相加（机制非受体特异性） |
| `antagonistic_efficacy` | 联合用药药效小于相加 |

### 毒性与信号通路 — 3 类

| Category | 定义 |
|---|---|
| `additive_toxicity` | 毒性相加或协同（含 hepatotox、nephrotox 等不区分器官的总体毒性） |
| `organ_toxicity_modulation` | 特定器官毒性（肝、肾、心）被联合用药调节（可能升高或降低） |
| `signaling_pathway_modulation` | 联合用药影响下游信号通路（PXR、AhR、Nrf2、MAPK、NF-κB 等） |

### 不确定时 — 1 类

| Category | 定义 |
|---|---|
| `unsure_ambiguous` | 摘要过于简略/模糊无法判定，或多个类别同等适用无主次 — **必须给 confidence = low** |

---

## Confidence 把握度判定标准

| Level | 标准 |
|---|---|
| `high` | 摘要明确陈述机制 + 你 >= 85% 确定 |
| `medium` | 摘要暗示机制但未直接陈述，或机制类别非完美匹配 |
| `low` | 摘要过于简略，机制不清，或多类别同等适用 |

---

## 注意事项

- **不要尝试推测 LLM 会怎么判**：独立标注，依据 abstract 内容做判断
- **abstract 不完整时**：如果摘要被截断或缺失关键 results section，选 `unsure_ambiguous` + low confidence
- **多机制并存时**：选**主要机制**（abstract 中占主导地位的那个）作为 primary；第二个机制填 alternative 列
- **不要 Google 论文**：以 abstract 内容为准，不补充外部信息（保持与 LLM 的 fair comparison setting）
- **不需要追求完美**：你不确定的 case 我们用 kappa 计算时会单独分析；老实标 low confidence 比强行猜测 high 更有价值

---

## 完成后

完成后把 `s2_annotator_form.xlsx` 发回。Day 28 我会用你的标注计算 Cohen kappa，
写 Supplementary Methods S2 章节。论文 Acknowledgements 会署你的名字 + 致谢这部分工作。

---

## 任何疑问

任何机制定义疑问，或某条文献怎么也判不准 — 标 `unsure_ambiguous` + low confidence + 在 notes 里写一句你的疑问，
我们事后一起复核。不要纠结太久，整体节奏比单条精确更重要。
"""

OUT_PATH.write_text(content, encoding='utf-8')
print(f"[+] Wrote {OUT_PATH.relative_to(REPO)}")
print(f"  Size: {OUT_PATH.stat().st_size / 1024:.1f} KB")
print(f"  Lines: {len(content.splitlines())}")