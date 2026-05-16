# Residual Mechanism Audit (post Schema v3 re-extraction)

Total interactions: **3,100**

- `other` bucket:       **226** (7.3%)
- `unspecified` bucket: **484** (15.6%)

**Decision goal**: is there a third hidden mechanism category worth a
Schema v4 extension? Or should residuals be accepted as-is?


---

# `other` bucket — 15 sample cases


### other-1: `Scopus:2-s2.0-30844451390` (year 2006)

- **Herb**: `ginseng` × **Drug**: `NSATDs`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > The observed adverse manifestations included the following: gastrointestinal after dandelion, propolis and fennel; cardiovascular after liquorice, ginseng, and green tea.

### other-2: `PubMed:34575923` (year 2021)

- **Herb**: `Hydroxygenkwanin` × **Drug**: `doxorubicin`
- **Target**: `DNA damage response proteins; RAD51` | **Direction**: `effect_increase` | **Conf**: 0.9
- **Evidence**:
  > HGK enhanced the sensitivity of liver cancer cells to doxorubicin without any physiological toxicity.

### other-3: `PubMed:27989101` (year 2016)

- **Herb**: `blister beetle` × **Drug**: `imatinib`
- **Target**: `BCR-ABL` | **Direction**: `effect_increase` | **Conf**: 0.9
- **Evidence**:
  > These findings indicated that CTD overcomes imatinib resistance through depletion of BCR-ABL.

### other-4: `PubMed:27657029` (year 2016)

- **Herb**: `Phyllanthus amarus` × **Drug**: `5-Fluorouracil`
- **Target**: `—` | **Direction**: `effect_decrease` | **Conf**: 0.85
- **Evidence**:
  > Combined use of 5-FU with PHA resulted in significant decreases in ATP, CTP, GTP, UTP and dTTP levels, while AMP, CMP, GMP and dUMP levels increased significantly compared with use of 5-FU alone.

### other-5: `Scopus:2-s2.0-85115386689` (year 2021)

- **Herb**: `Sanguisorba` × **Drug**: `CTX`
- **Target**: `hematopoietic stem cells` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > Additionally, the TPGS modified liposomes significantly enhanced the therapeutic effect of ZgI on CTX induced myelosuppression.

### other-6: `PubMed:17723077` (year 2007)

- **Herb**: `St. John's Wort` × **Drug**: `warfarin`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.9
- **Evidence**:
  > The CAM therapies associated with an increased risk of self-reported bleeding included cayenne, ginger, willow bark, St. John's wort, and coenzyme Q(10).

### other-7: `OpenAlex:W4417315793` (year 2025)

- **Herb**: `Tongxinluo` × **Drug**: `stroke`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > Results from 51 RCTs (9,577 patients) found Tongxinluo significantly improves stroke outcomes including enhancing the functional recovery.

### other-8: `PubMed:25781208` (year 2015)

- **Herb**: `Icariside II` × **Drug**: `insulin`
- **Target**: `AGEs-RAGE-oxidative stress axis` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > Better efficacy could be expected with tight glycemic control plus the antioxidant icariside II.

### other-9: `WoS:WOS:001383655500001` (year 2024)

- **Herb**: `Liuweizhiji Gegen-Sangshen beverage` × **Drug**: `MTDX`
- **Target**: `liver; gut microbiota; GPR43/GLP-1 pathway` | **Direction**: `effect_decrease` | **Conf**: 0.85
- **Evidence**:
  > Overall, LGS exerts a remarkable protective effect on ALD mice through the gut microbiota mediated specific hexanoic acid production and GPR43/GLP-1 pathway.

### other-10: `WoS:WOS:001353502200001` (year 2024)

- **Herb**: `Ligusticum wallichii` × **Drug**: `(unknown)`
- **Target**: `CYP3A4, CYP2C9` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > The qRT-PCR results showed that compared with the OA group, the mRNA expression of ESR1, CAT, C3, CYP3A4, CYP2C9, and ANXA1 in the TMP group increased (p < 0.05).

### other-11: `Scopus:2-s2.0-85072010229` (year 2020)

- **Herb**: `Polygonum multiflorum` × **Drug**: `(unknown)`
- **Target**: `liver` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > we considered EG was involved in the idiosyncratic liver injury of PM, and TSG played a synergetic role with EG, which contributed to the understanding of the hepatotoxic basis of PM.

### other-12: `Scopus:2-s2.0-85013974506` (year 2017)

- **Herb**: `ginger` × **Drug**: `carboplatin`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > ginger, European and Oriental mistletoe increased chemosensitivity in both cancer cell lines.

### other-13: `Scopus:2-s2.0-85206122077` (year 2024)

- **Herb**: `Wuzhi tablet` × **Drug**: `tacrolimus`
- **Target**: `—` | **Direction**: `exposure_increase` | **Conf**: 0.9
- **Evidence**:
  > Wuzhi tablet is widely used as a TAC-sparing agent in China that could significantly elevate TAC exposure.

### other-14: `PubMed:19188016` (year 2009)

- **Herb**: `Ganoderma` × **Drug**: `doxorubicin`
- **Target**: `—` | **Direction**: `effect_decrease` | **Conf**: 0.85
- **Evidence**:
  > Pre-incubation of drug-resistant SCLC cells with cytotoxic Ganoderma reduced the IC(50) for etoposide (3.4-0.21 microM) and doxorubicin (0.19-0.04 microM).

### other-15: `WoS:WOS:000257480200010` (year 2008)

- **Herb**: `valerian` × **Drug**: `haloperidol`
- **Target**: `delta-aminolevulinate dehydratase` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > Our findings suggest adverse interactions between haloperidol and valerian.

---

# `unspecified` bucket — 15 sample cases


### unspecified-1: `WoS:WOS:000444257100010` (year 2018)

- **Herb**: `lemongrass` × **Drug**: `(unknown)`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.8
- **Evidence**:
  > The most commonly used plants were Cymbopogon citratus and Matricaria recutita, interacting mainly with central nervous system targeting drugs, antihypertensives and anticoagulants possibly leading to increased sedation and coagulation disorders.

### unspecified-2: `PubMed:25141924` (year 2014)

- **Herb**: `xanthorrhizol` × **Drug**: `tamoxifen`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > However, using the MCF-7 implanted nude mice model, it was possible to detect significantly increased tumor volumes, a larger tumor size, and increased protein expression of P38 and P27(Kip1) in the xanthorrhizol + tamoxifen group compared to the tamoxifen-alone group.

### unspecified-3: `WoS:WOS:000256194200014` (year 2008)

- **Herb**: `ginseng` × **Drug**: `chemotherapy regimens`
- **Target**: `—` | **Direction**: `context_dependent` | **Conf**: 0.7
- **Evidence**:
  > Fifteen percent (15.3%) of patients took grapeseed and ginseng, which might affect the efficacy of some chemotherapy regimens.

### unspecified-4: `Scopus:2-s2.0-14844343192` (year 2005)

- **Herb**: `Centella` × **Drug**: `Phenytoin`
- **Target**: `—` | **Direction**: `no_change` | **Conf**: 0.8
- **Evidence**:
  > When CA was combined with PHT, though seizure protection was seen, this effect was not statistically significant.

### unspecified-5: `Scopus:2-s2.0-105017061854` (year 2025)

- **Herb**: `Jiegeng` × **Drug**: `pulegone`
- **Target**: `—` | **Direction**: `exposure_increase` | **Conf**: 0.85
- **Evidence**:
  > Peak concentration (Cmax), mean retention time from 0 to ∞ (MRT0→∞), and area under the curve (AUC0→10), (AUC0→∞) were 1.51, 1.14, 2.34, and 3.86 times higher in the co-administration group than in the individual administration group, respectively (P < 0.05).

### unspecified-6: `OpenAlex:W2045674001` (year 2010)

- **Herb**: `Shuang-huang-lian Injection` × **Drug**: `clindamycin`
- **Target**: `—` | **Direction**: `exposure_increase` | **Conf**: 0.85
- **Evidence**:
  > Shuang-huang-lian Injection inhibited the metabolism of clindamycin with a 1.34-fold increase in the t1/2 and a 1.37-fold increase in AUC value.

### unspecified-7: `WoS:WOS:001046573700004` (year 2023)

- **Herb**: `artichoke` × **Drug**: `(unknown)`
- **Target**: `hPXR` | **Direction**: `no_change` | **Conf**: 0.8
- **Evidence**:
  > M. glomerata (5.5 mg/mL dry extract), R. purshiana (1.5 mg/mL dry extract), and U. tomentosa (2.0 mg/mL dry extract) showed to be hPXR agonist, suggesting a potential interaction with the conventional drugs metabolized by the same isoforms of the CYP superfamily.

### unspecified-8: `Scopus:2-s2.0-85096833921` (year 2020)

- **Herb**: `Khat` × **Drug**: `warfarin`
- **Target**: `—` | **Direction**: `effect_decrease` | **Conf**: 0.9
- **Evidence**:
  > The results revealed that the mean of absolute INR readings was lower in khat-chewers than non-chewers by average 0.2 on the first and second visits (p = 0.038 and 0.002, respectively).

### unspecified-9: `PubMed:16722828` (year 2006)

- **Herb**: `St. John's Wort` × **Drug**: `(unknown)`
- **Target**: `—` | **Direction**: `context_dependent` | **Conf**: 0.8
- **Evidence**:
  > Although St John's wort was the first and most frequently reported source of induction-style herb-drug interactions, this knowledge has not yet changed its current availability.

### unspecified-10: `WoS:WOS:000308807900045` (year 2012)

- **Herb**: `Echinacea` × **Drug**: `etravirine`
- **Target**: `—` | **Direction**: `no_change` | **Conf**: 0.85
- **Evidence**:
  > The GMR for etravirine coadministered with E. purpurea relative to etravirine alone was 1.07 (90% CI, 0.81 to 1.42) for the maximum concentration, 1.04 (90% CI, 0.79 to 1.38) for the area under the concentration-time curve from 0 to 24 h, and 1.04 (90% CI, 0.74 to 1.44) for the concentration at the end of the dosing interval.

### unspecified-11: `Scopus:2-s2.0-85071420707` (year 2019)

- **Herb**: `Dandelion` × **Drug**: `nilotinib`
- **Target**: `—` | **Direction**: `context_dependent` | **Conf**: 0.8
- **Evidence**:
  > Mutual interference between a drug and a food constituent may result in altered pharmacokinetics of the drug and undesired or even dangerous clinical situations.

### unspecified-12: `Scopus:2-s2.0-85107358189` (year 2021)

- **Herb**: `Javanese turmeric` × **Drug**: `warfarin`
- **Target**: `—` | **Direction**: `exposure_increase` | **Conf**: 0.9
- **Evidence**:
  > The area under the curve (AUC) of R- and S-WF in the CX-2 group was a significantly higher value compared to the control (77.54 vs. 35.27 mg.h/L for R-WF and 316.26 vs. 40.16 mg.h/L for S-WF; p < 0.05; Kruskal-Wallis method).

### unspecified-13: `PubMed:17030294` (year 2006)

- **Herb**: `ginseng` × **Drug**: `antiplatelet or anticoagulant therapy`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.8
- **Evidence**:
  > Overall, almost 31% (n=23, N=76) of patients were taking one or more of the specified herbal medicines [ginseng (Panax ginseng), garlic (Allium sativum), ginkgo (Gingko biloba) thought to interact with antiplatelet or anticoagulant therapy.

### unspecified-14: `Scopus:2-s2.0-85138359773` (year 2022)

- **Herb**: `saffron` × **Drug**: `rivaroxaban`
- **Target**: `—` | **Direction**: `effect_increase` | **Conf**: 0.85
- **Evidence**:
  > It seems that coadministration of DOACs and saffron supplements should be avoided due to the potential drug-herbal interactions and possible risk of subsequent bleeding complications.

### unspecified-15: `PubMed:22533708` (year 2012)

- **Herb**: `Austrian wormwood` × **Drug**: `kanamycin`
- **Target**: `—` | **Direction**: `effect_decrease` | **Conf**: 0.85
- **Evidence**:
  > In case of kanamycin, extracts of Artemisia austriaca and Artemisia pontica increased MICs by four and eight times, respectively.

---

## Decision framework

After scanning the samples, choose:

1. **Schema v4 extension** — if ≥10 `other` cases cluster into a recognizable NEW category (e.g. `immunomodulation`, `gut_microbiota_mediated`, `autophagy`, `ferroptosis`, `ER_stress`, `epigenetic_modulation`). Then extend schema and re-extract affected records (~$0.4).
2. **Prompt improvement** — if `unspecified` actually contains describable mechanisms that the LLM was too cautious to categorize. Improve prompt to be more aggressive in low-confidence cases.
3. **Accept residual** — if cases are genuinely heterogeneous with no clear pattern. This is normal for LLM-based extraction and acceptable in Methods.

Tell Claude which decision to make and the proposed new category names.