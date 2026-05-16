# Day 6 Benchmark Hand-Review

Compare 4 models on 10 sample abstracts (out of 50). Use this to qualitatively judge extraction accuracy.


---

## Case 1: `OpenAlex:W2276879834` (cluster 31)

**Title**: Herb-drug interactions among commonly used psychoactive substances by healthcare students

**Abstract** (first 600 chars):
> The concurrent use of herbs and/or nutritional supplements with psychoactive effect and prescription medications is common among college students. College students are a particularly vulnerable population, for they are under less social/familiar surveillance and seek greater independence, as well as under greater intellectual effort, stress, anxiety and depression, which predispose them to a higher consumption of psychoactive substances. Herbs, vitamins, and other dietary supplements may influence the effects of prescription and nonprescription drugs leading to adverse consequences, by increas...


### Model: `openai/gpt-5-mini`
- contains_hdi: **False**, n=0, validation_attempts=2

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 2: `OpenAlex:W2352419135` (cluster 7)

**Title**: Analysis on the Status Quo and Requirement of Medication in Gestational Women and Effect of Pharmaceutical Care

**Abstract** (first 600 chars):
> OBJECTIVE:To analyze the status quo and requirement of medication in gestational women and effect of pharmaceutical care in order to provide reference for safe medication service model during the gestational period. METHODS:Questionnaire for the medication of gestational women was adopted to investigate 562 gestational women who received diagnosis,physical examination and maternal health education. Comprehensive pharmaceutical care was performed in following manners for three months,such as promotional materials,special lecture,consultation and education video. The changes in the knowledge,att...


### Model: `openai/gpt-5-mini`
- contains_hdi: **False**, n=0, validation_attempts=2

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 3: `OpenAlex:W2379559537` (cluster 11)

**Title**: Preliminary study of the effects of β-elemene on breast cancer stem cells in cell line MCF-7/ADM

**Abstract** (first 600 chars):
> Objective To investigate the differences between breast cancer cell line MCF-7/ADM resistant to adriamycin(ADM) and sensitive cell line MCF-7/S in proportion of breast cancer stem cells(BCSCs) and expression levels of breast cancer resistance protein(BCRP) and P-glycoprotein(P-gp),and to further observe the effects of traditional Chinese medicine β-elemene(βELE) on BCSCs and expressions of BCRP and P-gp.Methods MCF-7 / ADM and MCF-7 / S cell lines were cultured in the serum-free medium(SFM) and microspheres formation ratio was observed under phase contrast microscope.The expression levels of r...


### Model: `openai/gpt-5-mini`
- contains_hdi: **True**, n=1, validation_attempts=3
  - **Interaction 1**: `β-elemene` × `adriamycin (ADM; doxorubicin)` | transporter_modulation | effect_increase | conf=0.6
    > βELE inhibited obviously microspheres formation ratio,decreased mRNA and protein levels of BCRP and P-gp.

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 4: `OpenAlex:W2565143075` (cluster 38)

**Title**: A study to determine the knowledge and level of awareness of medical undergraduates about herbal medicines and herb-drug interactions

**Abstract** (first 600 chars):
> Background: The increasing usage of herbal medicines worldwide has increased the probability of co-administration of herbal and allopathic medicines. This may lead to serious safety concerns, including herb-drug interactions (HDIs). Many HDIs may be overlooked due to poor doctor-patient communication about herbal drug usage probably because of lack of knowledge of herbal medicines and HDIs among physicians. The study was thus planned to identify the knowledge and awareness of medical students regarding the use of herbal medicines and about HDIs, to help improve the teaching skills and curricul...


### Model: `openai/gpt-5-mini`
- contains_hdi: **False**, n=0, validation_attempts=2

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 5: `OpenAlex:W2993783040` (cluster 3)

**Title**: EFFECTIVNESS OF COMPLEMENTARY AND ALTERNATIVE THERAPY FOR HIV/AIDS -

**Abstract** (first 600 chars):
> A therapy is called complementary when it is used in addition to conventional treatments. Complementary therapies” refer to a broad group of natural healing methods and approaches that are different than the conventional Allopathy medicine (or pharmaceutical medicine). Many of these healing methods have been used for centuries in
many different cultures. Since the beginning of the AIDS epidemic, a wide variety of complementary therapies have been used by people with HIV for various purposes including general health promotion, relief of symptoms and cure of certain ailments. These include Trad...


### Model: `openai/gpt-5-mini`
- contains_hdi: **False**, n=0, validation_attempts=2

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 6: `OpenAlex:W4214741111` (cluster 32)

**Title**: INHIBITORY EFFECT OF AQUEOUS ROOT EXTRACT OF DECALEPIS HAMILTONII ON rOAT1

**Abstract** (first 600 chars):
> About three quarters population around the world is depended upon traditional medicines for treatment of diseases. The medicinal plants are source of natural product having various phytochemicals. Presence of phenolic acids and other root specific compounds in Aqueous Root Extract of Decalepis hamiltonii, major component in herbal drink, Nannari may also inhibit the hOAT1 transporter and may precipitate herb-drug interaction with hOAT1 substrate drugs. Therefore the study is conducted to evaluate the inhibitory effect of aqueous root extract of Decalepis hamiltonii (AREDH) on rat Oat1, a homol...


### Model: `openai/gpt-5-mini`
- contains_hdi: **True**, n=2, validation_attempts=3
  - **Interaction 1**: `Nannari` × `para-aminohippuric acid (PAH)` | transporter_modulation | exposure_increase | conf=0.8
    > The results shows significant decrease in CL & k 10 , and significant elevation in t 1/2 , AUC 0- & V ss of PAH in test group compared to control group clearly indicates the cumulative inhibitory effe
  - **Interaction 2**: `Nannari` × `hOAT1 substrate drugs` | transporter_modulation | exposure_increase | conf=0.75
    > Further, the co-administration of AREDH with any hOAT1 substrate, results in decrease in clearance and increase in the bioavailability and half-life of the substrate drugs.

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **True**, n=1, validation_attempts=1
  - **Interaction 1**: `Nannari` × `None` | transporter_modulation | exposure_increase | conf=0.85
    > The results shows significant decrease in CL & k 10 , and significant elevation in t 1/2 , AUC 0- & V ss of PAH in test group compared to control group clearly indicates the cumulative inhibitory effe

### Model: `openai/gpt-5.5`
- contains_hdi: **True**, n=1, validation_attempts=2
  - **Interaction 1**: `Nannari` × `para-aminohippuric acid` | transporter_modulation | exposure_increase | conf=0.88
    > The results shows significant decrease in CL & k 10 , and significant elevation in t 1/2 , AUC 0- & V ss of PAH in test group compared to control group clearly indicates the cumulative inhibitory effe

---

## Case 7: `OpenAlex:W4310697240` (cluster 29)

**Title**: THE NEED FOR HERBOVIGILANCE

**Abstract** (first 600 chars):
> <strong>Objective:</strong> This communication outlines herbal drug safety, interactions between herbals and modern medicines, and factors that contribute to herb-drug interactions, including pharmacodynamic and pharmacokinetic interactions and their mechanisms. <strong>Methods:</strong> The study reviewed the various factors influencing the present pharmacovigilance system in comparison with the herbs related parameters, identified the advantages and disadvantage of the present system and derived modifications which are relevant to herbal drugs safety, efficacy and quality. <strong>Conclusion...


### Model: `openai/gpt-5-mini`
- contains_hdi: **False**, n=0, validation_attempts=2

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 8: `PubMed:16459039` (cluster 36)

**Title**: A role for physicians in ethnopharmacology and drug discovery.

**Abstract** (first 600 chars):
> Ethnopharmacology investigations classically involved traditional healers, botanists, anthropologists, chemists and pharmacologists. The role of some groups of researchers but not of physician has been highlighted and well defined in ethnopharmacological investigations. Historical data shows that discovery of several important modern drugs of herbal origin owe to the medical knowledge and clinical expertise of physicians. Current trends indicate negligible role of physicians in ethnopharmacological studies. Rising cost of modern drug development is attributed to the lack of classical ethnophar...


### Model: `openai/gpt-5-mini`
- contains_hdi: **False**, n=0, validation_attempts=2

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **False**, n=0, validation_attempts=2

---

## Case 9: `PubMed:17925494` (cluster 5)

**Title**: Lack of pharmacokinetic interaction between St. John's wort and prednisone.

**Abstract** (first 600 chars):
> St. John's wort (SJW) is a popular dietary supplement involved in numerous dietary supplement-drug interactions with prescription and non-prescription drugs. The supplement has been shown to affect the metabolism of various CYP3A4 substrates. The CYP3A4 pathway mediates the metabolism of a large number of drug entities, including the corticosteroids prednisone and prednisolone. To examine the effects of long-term SJW administration on the pharmacokinetics of prednisone and its reversible metabolite prednisolone in male subjects. Eight male subjects participated in this single-dose study. The p...


### Model: `openai/gpt-5-mini`
- contains_hdi: **True**, n=2, validation_attempts=2
  - **Interaction 1**: `St. John's wort` × `prednisone` | unspecified | no_change | conf=0.8
    > Twenty-eight days of SJW treatment resulted in no significant alterations in the pharmacokinetic parameters for prednisone or prednisolone.
  - **Interaction 2**: `St. John's wort` × `prednisolone` | unspecified | no_change | conf=0.8
    > Twenty-eight days of SJW treatment resulted in no significant alterations in the pharmacokinetic parameters for prednisone or prednisolone.

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **True**, n=2, validation_attempts=1
  - **Interaction 1**: `St. John's wort` × `prednisone` | CYP_induction | no_change | conf=0.88
    > Twenty-eight days of SJW treatment resulted in no significant alterations in the pharmacokinetic parameters for prednisone or prednisolone. Oral administration of prednisone resulted in prednisone mea
  - **Interaction 2**: `St. John's wort` × `prednisolone` | CYP_induction | no_change | conf=0.88
    > Prednisolone mean AUCs were 714.19 +/- 153.29 microg x h/L before SJW administration and 700.74 +/- 89.68 microg x h/L after treatment. Concurrent administration of SJW had no significant effect on th

### Model: `openai/gpt-5.5`
- contains_hdi: **True**, n=2, validation_attempts=2
  - **Interaction 1**: `St. John's wort` × `prednisone` | unspecified | no_change | conf=0.93
    > Twenty-eight days of SJW treatment resulted in no significant alterations in the pharmacokinetic parameters for prednisone or prednisolone. Oral administration of prednisone resulted in prednisone mea
  - **Interaction 2**: `St. John's wort` × `prednisolone` | unspecified | no_change | conf=0.92
    > Prednisolone mean AUCs were 714.19 +/- 153.29 microg x h/L before SJW administration and 700.74 +/- 89.68 microg x h/L after treatment. Concurrent administration of SJW had no significant effect on th

---

## Case 10: `PubMed:23861780` (cluster 11)

**Title**: Tanshinone IIA increases the bystander effect of herpes simplex virus thymidine kinase/ganciclovir gene therapy via enhanced gap junctional intercellular communication.

**Abstract** (first 600 chars):
> The bystander effect is an intriguing phenomenon by which adjacent cells become sensitized to drug treatment during gene therapy with herpes simplex virus thymidine kinase/ganciclovir (HSV-tk/GCV). This effect is reported to be mediated by gap junctional intercellular communication (GJIC), and therefore, we postulated that upregulation of genes that facilitate GJIC may enhance the HSV-tk/GCV bystander effect. Previous findings have shown Tanshinone IIA (Tan IIA), a chemical substance derived from a Chinese medicine herb, promotes the upregulation of the connexins Cx26 and Cx43 in B16 cells. Be...


### Model: `openai/gpt-5-mini`
- contains_hdi: **True**, n=1, validation_attempts=2
  - **Interaction 1**: `Tanshinone IIA` × `ganciclovir` | other | effect_increase | conf=0.9
    > Tan IIA increased GJIC in B16 melanoma cells, leading to more efficient GCV-induced bystander killing in cells stably expressing HSV-tk. Additionally, in vivo experiments demonstrated that tumors in m

### Model: `anthropic/claude-haiku-4.5`
- contains_hdi: **False**, n=0, validation_attempts=1

### Model: `openai/gpt-5.5`
- contains_hdi: **True**, n=1, validation_attempts=2
  - **Interaction 1**: `None` × `ganciclovir` | synergistic_efficacy | effect_increase | conf=0.9
    > Tan IIA increased GJIC in B16 melanoma cells, leading to more efficient GCV-induced bystander killing in cells stably expressing HSV-tk. Additionally, in vivo experiments demonstrated that tumors in m