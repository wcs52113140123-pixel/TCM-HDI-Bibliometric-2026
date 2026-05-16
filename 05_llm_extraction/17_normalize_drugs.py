"""
Day 9 T3: Drug normalization.

Maps free-text `drug_name` values to canonical generic names and
groups them into ATC-style functional classes for downstream analysis.

Approach:
  1. Lowercase + strip + remove non-essential chars
  2. Look up alias map (e.g., "adriamycin" → "doxorubicin")
  3. Look up class map (canonical → ATC-style class)
  4. Long-tail drugs (not in alias map) get drug.lower().strip() as canonical

Output columns added to interactions_normalized.parquet:
  - drug_canonical : lowercase canonical generic name
  - drug_class     : ATC-style functional class

Usage:
    python 05_llm_extraction/17_normalize_drugs.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"


# =====================================================================
# DRUG_ALIAS_MAP — synonym → canonical lowercase generic name
# Only includes entries where canonical name differs from alias (i.e. real
# synonyms). Other drugs pass through unchanged (lowercased + stripped).
# =====================================================================
DRUG_ALIAS_MAP: dict[str, str] = {
    # --- Antineoplastics ---
    "adriamycin": "doxorubicin",
    "dox": "doxorubicin",
    "5-fu": "fluorouracil",
    "5-fluorouracil": "fluorouracil",
    "five-fu": "fluorouracil",
    "cddp": "cisplatin",
    "cis-platinum": "cisplatin",
    "ddp": "cisplatin",
    "atra": "tretinoin",
    "all-trans retinoic acid": "tretinoin",
    "all trans retinoic acid": "tretinoin",
    "vp-16": "etoposide",
    "vp16": "etoposide",
    "ara-c": "cytarabine",
    "araba": "cytarabine",
    "cytosine arabinoside": "cytarabine",
    "mtx": "methotrexate",
    "amethopterin": "methotrexate",
    "cyclophosphamide a": "cyclophosphamide",
    "cytoxan": "cyclophosphamide",
    "endoxan": "cyclophosphamide",
    "ifosfamide a": "ifosfamide",
    "taxol": "paclitaxel",
    "taxotere": "docetaxel",
    "navelbine": "vinorelbine",
    "gleevec": "imatinib",
    "iressa": "gefitinib",
    "herceptin": "trastuzumab",
    "avastin": "bevacizumab",
    "tarceva": "erlotinib",
    "carboplatinum": "carboplatin",
    "oxaliplatinum": "oxaliplatin",
    "epirubicin hcl": "epirubicin",
    "daunoblastin": "daunorubicin",
    "mitoxantrone hcl": "mitoxantrone",
    "leucovorin": "folinic acid",
    "5-aza": "azacitidine",

    # --- Anticoagulants / Antiplatelets ---
    "coumarin": "warfarin",
    "coumadin": "warfarin",
    "warfarin sodium": "warfarin",
    "asa": "aspirin",
    "acetylsalicylic acid": "aspirin",
    "asetylsalisilik asit": "aspirin",
    "plavix": "clopidogrel",
    "iscover": "clopidogrel",
    "pradaxa": "dabigatran",
    "dabigatran etexilate": "dabigatran",
    "xarelto": "rivaroxaban",
    "eliquis": "apixaban",
    "lixiana": "edoxaban",

    # --- Immunosuppressants ---
    "ciclosporin": "cyclosporine",
    "ciclosporin a": "cyclosporine",
    "cyclosporine a": "cyclosporine",
    "cyclosporin a": "cyclosporine",
    "cyclosporin": "cyclosporine",
    "csa": "cyclosporine",
    "sandimmune": "cyclosporine",
    "fk506": "tacrolimus",
    "fk-506": "tacrolimus",
    "prograf": "tacrolimus",
    "tac": "tacrolimus",
    "sirolimus a": "sirolimus",
    "rapamycin": "sirolimus",
    "rapamune": "sirolimus",
    "everolimus a": "everolimus",
    "mycophenolate mofetil": "mycophenolate",
    "mmf": "mycophenolate",
    "cellcept": "mycophenolate",
    "azathioprine a": "azathioprine",

    # --- Antidiabetics ---
    "glucophage": "metformin",
    "metformin hcl": "metformin",
    "metformin hydrochloride": "metformin",
    "diamicron": "gliclazide",
    "amaryl": "glimepiride",
    "actos": "pioglitazone",
    "avandia": "rosiglitazone",
    "januvia": "sitagliptin",
    "byetta": "exenatide",
    "trulicity": "dulaglutide",
    "victoza": "liraglutide",

    # --- Antihypertensives ---
    "norvasc": "amlodipine",
    "amlodipine besylate": "amlodipine",
    "cardene": "nicardipine",
    "calan": "verapamil",
    "isoptin": "verapamil",
    "procardia": "nifedipine",
    "adalat": "nifedipine",
    "diltzac": "diltiazem",
    "cardizem": "diltiazem",
    "tenormin": "atenolol",
    "lopressor": "metoprolol",
    "metoprolol tartrate": "metoprolol",
    "metoprolol succinate": "metoprolol",
    "inderal": "propranolol",
    "coreg": "carvedilol",
    "cozaar": "losartan",
    "diovan": "valsartan",
    "avapro": "irbesartan",
    "benicar": "olmesartan",
    "atacand": "candesartan",
    "lasix": "furosemide",
    "frusemide": "furosemide",
    "vasotec": "enalapril",
    "altace": "ramipril",
    "monopril": "fosinopril",
    "captopril a": "captopril",

    # --- Statins / Lipid-lowering ---
    "lipitor": "atorvastatin",
    "atorvastatin calcium": "atorvastatin",
    "zocor": "simvastatin",
    "crestor": "rosuvastatin",
    "pravachol": "pravastatin",
    "mevacor": "lovastatin",
    "lescol": "fluvastatin",
    "lovaza": "omega3_acid_ethyl_esters",
    "trilipix": "fenofibrate",

    # --- NSAIDs / Analgesics ---
    "paracetamol": "acetaminophen",
    "tylenol": "acetaminophen",
    "panadol": "acetaminophen",
    "apap": "acetaminophen",
    "n-acetyl-p-aminophenol": "acetaminophen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "voltaren": "diclofenac",
    "naproxen sodium": "naproxen",
    "aleve": "naproxen",
    "indocin": "indomethacin",
    "celebrex": "celecoxib",
    "vioxx": "rofecoxib",
    "demerol": "meperidine",
    "pethidine": "meperidine",
    "ms contin": "morphine",
    "ms-contin": "morphine",
    "oxycontin": "oxycodone",
    "vicodin": "hydrocodone",

    # --- Anticonvulsants / Mood ---
    "tegretol": "carbamazepine",
    "carbamazepine cr": "carbamazepine",
    "dilantin": "phenytoin",
    "depakote": "valproate",
    "depakene": "valproate",
    "valproic acid": "valproate",
    "lamictal": "lamotrigine",
    "topamax": "topiramate",
    "neurontin": "gabapentin",
    "keppra": "levetiracetam",
    "klonopin": "clonazepam",
    "ativan": "lorazepam",
    "xanax": "alprazolam",
    "valium": "diazepam",
    "versed": "midazolam",
    "midazolam maleate": "midazolam",

    # --- SSRIs / Antidepressants ---
    "prozac": "fluoxetine",
    "zoloft": "sertraline",
    "paxil": "paroxetine",
    "celexa": "citalopram",
    "lexapro": "escitalopram",
    "effexor": "venlafaxine",
    "wellbutrin": "bupropion",
    "remeron": "mirtazapine",
    "elavil": "amitriptyline",
    "imipramine hcl": "imipramine",

    # --- Antibiotics / Antifungals / Antivirals ---
    "ciprofloxacin hcl": "ciprofloxacin",
    "cipro": "ciprofloxacin",
    "levaquin": "levofloxacin",
    "augmentin": "amoxicillin_clavulanate",
    "z-pak": "azithromycin",
    "zithromax": "azithromycin",
    "biaxin": "clarithromycin",
    "erythromycin a": "erythromycin",
    "rifampin": "rifampicin",
    "rifadin": "rifampicin",
    "diflucan": "fluconazole",
    "sporanox": "itraconazole",
    "nizoral": "ketoconazole",
    "vfend": "voriconazole",
    "cancidas": "caspofungin",
    "tamiflu": "oseltamivir",
    "viread": "tenofovir",
    "epivir": "lamivudine",
    "retrovir": "zidovudine",
    "azt": "zidovudine",
    "kaletra": "lopinavir_ritonavir",
    "norvir": "ritonavir",

    # --- PPIs / GI ---
    "prilosec": "omeprazole",
    "nexium": "esomeprazole",
    "protonix": "pantoprazole",
    "prevacid": "lansoprazole",
    "aciphex": "rabeprazole",
    "zantac": "ranitidine",
    "pepcid": "famotidine",
    "metoclopramide hcl": "metoclopramide",
    "reglan": "metoclopramide",

    # --- Cardiovascular other ---
    "lanoxin": "digoxin",
    "digoxin sodium": "digoxin",
    "cordarone": "amiodarone",
    "pacerone": "amiodarone",
    "nitrostat": "nitroglycerin",
    "imdur": "isosorbide_mononitrate",

    # --- Hormones / Endocrine ---
    "synthroid": "levothyroxine",
    "thyroxine": "levothyroxine",
    "t4": "levothyroxine",
    "t3": "liothyronine",
    "premarin": "conjugated_estrogens",
    "estradiol valerate": "estradiol",
    "provera": "medroxyprogesterone",
    "danazol a": "danazol",
    "nolvadex": "tamoxifen",
    "tamoxifen citrate": "tamoxifen",
    "arimidex": "anastrozole",
    "femara": "letrozole",
    "casodex": "bicalutamide",
    "lupron": "leuprolide",

    # --- Antihistamines / Allergy ---
    "claritin": "loratadine",
    "zyrtec": "cetirizine",
    "allegra": "fexofenadine",
    "benadryl": "diphenhydramine",
    "diphenhydramine hcl": "diphenhydramine",

    # --- Respiratory ---
    "ventolin": "albuterol",
    "salbutamol": "albuterol",
    "advair": "fluticasone_salmeterol",
    "spiriva": "tiotropium",
    "singulair": "montelukast",
    "theophylline a": "theophylline",
    "theo-dur": "theophylline",
    "aminophylline": "theophylline",

    # --- Misc CYP probes (research compounds) ---
    "midazolam (cyp3a4 probe)": "midazolam",
    "phenacetin a": "phenacetin",
    "tolbutamide a": "tolbutamide",
    "dextromethorphan hbr": "dextromethorphan",
    "chlorzoxazone a": "chlorzoxazone",
    "bupropion a": "bupropion",

    # --- Hepatotoxic models / Solvents ---
    "ccl4": "carbon_tetrachloride",
    "carbon tetrachloride": "carbon_tetrachloride",
    "tetrachloromethane": "carbon_tetrachloride",
    "ethanol a": "ethanol",
    "alcohol": "ethanol",
    "dmba": "dimethylbenzanthracene",
    "tcdd": "tetrachlorodibenzodioxin",
}


# =====================================================================
# DRUG_CLASS_MAP — canonical drug name → ATC-style functional class
# Covers top ~200 drugs in our corpus + classic CYP probes
# =====================================================================
DRUG_CLASS_MAP: dict[str, str] = {}

_ANTHRACYCLINE = ["doxorubicin", "daunorubicin", "epirubicin", "idarubicin",
                  "mitoxantrone", "valrubicin", "pirarubicin"]
for d in _ANTHRACYCLINE:
    DRUG_CLASS_MAP[d] = "antineoplastic_anthracycline"

_PLATINUM = ["cisplatin", "carboplatin", "oxaliplatin", "nedaplatin"]
for d in _PLATINUM:
    DRUG_CLASS_MAP[d] = "antineoplastic_platinum"

_ALKYLATING = ["cyclophosphamide", "ifosfamide", "chlorambucil",
               "melphalan", "busulfan", "carmustine", "temozolomide",
               "dacarbazine", "thiotepa"]
for d in _ALKYLATING:
    DRUG_CLASS_MAP[d] = "antineoplastic_alkylating"

_TAXANE = ["paclitaxel", "docetaxel", "cabazitaxel"]
for d in _TAXANE:
    DRUG_CLASS_MAP[d] = "antineoplastic_taxane"

_ANTIMETABOLITE = ["fluorouracil", "methotrexate", "gemcitabine", "cytarabine",
                   "capecitabine", "fludarabine", "cladribine", "pemetrexed",
                   "azacitidine", "decitabine", "tegafur"]
for d in _ANTIMETABOLITE:
    DRUG_CLASS_MAP[d] = "antineoplastic_antimetabolite"

_VINCA = ["vincristine", "vinblastine", "vinorelbine", "vindesine"]
for d in _VINCA:
    DRUG_CLASS_MAP[d] = "antineoplastic_vinca_alkaloid"

_TOPO = ["etoposide", "irinotecan", "topotecan", "teniposide"]
for d in _TOPO:
    DRUG_CLASS_MAP[d] = "antineoplastic_topoisomerase"

_TKI = ["imatinib", "gefitinib", "erlotinib", "sorafenib", "sunitinib",
        "dasatinib", "nilotinib", "lapatinib", "pazopanib", "vandetanib",
        "regorafenib", "ibrutinib", "ruxolitinib", "tofacitinib", "crizotinib",
        "vemurafenib", "dabrafenib", "trametinib", "everolimus", "temsirolimus"]
for d in _TKI:
    DRUG_CLASS_MAP[d] = "antineoplastic_kinase_inhibitor"

_ANTI_HORMONE = ["tamoxifen", "anastrozole", "letrozole", "exemestane",
                 "bicalutamide", "flutamide", "leuprolide", "goserelin",
                 "fulvestrant", "raloxifene"]
for d in _ANTI_HORMONE:
    DRUG_CLASS_MAP[d] = "antineoplastic_hormone_modulator"

_BIOLOGIC_ONCO = ["trastuzumab", "bevacizumab", "rituximab", "cetuximab",
                  "panitumumab", "nivolumab", "pembrolizumab", "ipilimumab"]
for d in _BIOLOGIC_ONCO:
    DRUG_CLASS_MAP[d] = "antineoplastic_biologic"

# Anticoagulants / Antiplatelets
DRUG_CLASS_MAP.update({
    "warfarin": "anticoagulant_VKA",
    "dabigatran": "anticoagulant_DOAC",
    "rivaroxaban": "anticoagulant_DOAC",
    "apixaban": "anticoagulant_DOAC",
    "edoxaban": "anticoagulant_DOAC",
    "heparin": "anticoagulant_heparin",
    "enoxaparin": "anticoagulant_LMWH",
    "fondaparinux": "anticoagulant_other",
    "aspirin": "antiplatelet",
    "clopidogrel": "antiplatelet",
    "prasugrel": "antiplatelet",
    "ticagrelor": "antiplatelet",
    "dipyridamole": "antiplatelet",
    "cilostazol": "antiplatelet",
})

# Immunosuppressants
for d in ["cyclosporine", "tacrolimus", "sirolimus", "everolimus",
          "mycophenolate", "azathioprine"]:
    DRUG_CLASS_MAP[d] = "immunosuppressant"

# Antidiabetics
DRUG_CLASS_MAP.update({
    "metformin": "antidiabetic_biguanide",
    "glipizide": "antidiabetic_sulfonylurea",
    "glyburide": "antidiabetic_sulfonylurea",
    "glibenclamide": "antidiabetic_sulfonylurea",
    "gliclazide": "antidiabetic_sulfonylurea",
    "glimepiride": "antidiabetic_sulfonylurea",
    "tolbutamide": "antidiabetic_sulfonylurea",
    "chlorpropamide": "antidiabetic_sulfonylurea",
    "pioglitazone": "antidiabetic_thiazolidinedione",
    "rosiglitazone": "antidiabetic_thiazolidinedione",
    "sitagliptin": "antidiabetic_DPP4i",
    "saxagliptin": "antidiabetic_DPP4i",
    "linagliptin": "antidiabetic_DPP4i",
    "exenatide": "antidiabetic_GLP1RA",
    "liraglutide": "antidiabetic_GLP1RA",
    "dulaglutide": "antidiabetic_GLP1RA",
    "empagliflozin": "antidiabetic_SGLT2i",
    "dapagliflozin": "antidiabetic_SGLT2i",
    "canagliflozin": "antidiabetic_SGLT2i",
    "acarbose": "antidiabetic_alpha_glucosidase",
    "insulin": "antidiabetic_insulin",
})

# Antihypertensives
for d in ["amlodipine", "nifedipine", "felodipine", "nicardipine",
          "nimodipine", "isradipine"]:
    DRUG_CLASS_MAP[d] = "antihypertensive_CCB_dihydropyridine"
for d in ["verapamil", "diltiazem"]:
    DRUG_CLASS_MAP[d] = "antihypertensive_CCB_nondihydropyridine"
for d in ["atenolol", "metoprolol", "propranolol", "bisoprolol", "carvedilol",
          "labetalol", "nebivolol", "esmolol"]:
    DRUG_CLASS_MAP[d] = "antihypertensive_beta_blocker"
for d in ["losartan", "valsartan", "irbesartan", "candesartan", "olmesartan",
          "telmisartan", "azilsartan"]:
    DRUG_CLASS_MAP[d] = "antihypertensive_ARB"
for d in ["enalapril", "lisinopril", "ramipril", "captopril", "fosinopril",
          "perindopril", "quinapril", "benazepril"]:
    DRUG_CLASS_MAP[d] = "antihypertensive_ACEi"
for d in ["furosemide", "bumetanide", "torsemide"]:
    DRUG_CLASS_MAP[d] = "diuretic_loop"
for d in ["hydrochlorothiazide", "chlorthalidone", "indapamide"]:
    DRUG_CLASS_MAP[d] = "diuretic_thiazide"
for d in ["spironolactone", "eplerenone", "amiloride", "triamterene"]:
    DRUG_CLASS_MAP[d] = "diuretic_K_sparing"

# Statins / Lipid-lowering
for d in ["atorvastatin", "simvastatin", "rosuvastatin", "pravastatin",
          "lovastatin", "fluvastatin", "pitavastatin"]:
    DRUG_CLASS_MAP[d] = "lipid_lowering_statin"
DRUG_CLASS_MAP.update({
    "ezetimibe": "lipid_lowering_other",
    "fenofibrate": "lipid_lowering_fibrate",
    "gemfibrozil": "lipid_lowering_fibrate",
    "cholestyramine": "lipid_lowering_other",
    "niacin": "lipid_lowering_other",
})

# NSAIDs / Analgesics
for d in ["ibuprofen", "naproxen", "diclofenac", "ketoprofen", "indomethacin",
          "piroxicam", "meloxicam", "celecoxib", "rofecoxib", "etoricoxib",
          "ketorolac", "tolmetin"]:
    DRUG_CLASS_MAP[d] = "NSAID"
DRUG_CLASS_MAP.update({
    "acetaminophen": "analgesic_non_NSAID",
    "morphine": "analgesic_opioid",
    "fentanyl": "analgesic_opioid",
    "oxycodone": "analgesic_opioid",
    "hydrocodone": "analgesic_opioid",
    "codeine": "analgesic_opioid",
    "tramadol": "analgesic_opioid_atypical",
    "meperidine": "analgesic_opioid",
    "methadone": "analgesic_opioid",
    "buprenorphine": "analgesic_opioid",
})

# CNS - antidepressants
for d in ["fluoxetine", "sertraline", "paroxetine", "citalopram",
          "escitalopram", "fluvoxamine"]:
    DRUG_CLASS_MAP[d] = "antidepressant_SSRI"
for d in ["venlafaxine", "duloxetine", "desvenlafaxine"]:
    DRUG_CLASS_MAP[d] = "antidepressant_SNRI"
for d in ["amitriptyline", "imipramine", "nortriptyline", "clomipramine",
          "desipramine"]:
    DRUG_CLASS_MAP[d] = "antidepressant_TCA"
DRUG_CLASS_MAP.update({
    "bupropion": "antidepressant_other",
    "mirtazapine": "antidepressant_other",
    "trazodone": "antidepressant_other",
})

# CNS - antipsychotics / mood stabilizers
for d in ["haloperidol", "chlorpromazine", "fluphenazine", "thiothixene"]:
    DRUG_CLASS_MAP[d] = "antipsychotic_typical"
for d in ["risperidone", "olanzapine", "quetiapine", "aripiprazole",
          "clozapine", "ziprasidone", "paliperidone"]:
    DRUG_CLASS_MAP[d] = "antipsychotic_atypical"

# Anticonvulsants / Benzodiazepines
for d in ["carbamazepine", "phenytoin", "valproate", "lamotrigine", "topiramate",
          "gabapentin", "pregabalin", "levetiracetam", "oxcarbazepine",
          "phenobarbital"]:
    DRUG_CLASS_MAP[d] = "anticonvulsant"
for d in ["diazepam", "lorazepam", "alprazolam", "clonazepam", "midazolam",
          "temazepam", "oxazepam", "triazolam", "flurazepam"]:
    DRUG_CLASS_MAP[d] = "benzodiazepine"

# Antibiotics / Antifungals / Antivirals
for d in ["ciprofloxacin", "levofloxacin", "moxifloxacin", "ofloxacin",
          "norfloxacin", "gatifloxacin"]:
    DRUG_CLASS_MAP[d] = "antibiotic_fluoroquinolone"
for d in ["amoxicillin", "ampicillin", "penicillin", "piperacillin",
          "amoxicillin_clavulanate"]:
    DRUG_CLASS_MAP[d] = "antibiotic_penicillin"
for d in ["azithromycin", "clarithromycin", "erythromycin", "telithromycin"]:
    DRUG_CLASS_MAP[d] = "antibiotic_macrolide"
for d in ["doxycycline", "tetracycline", "minocycline", "tigecycline"]:
    DRUG_CLASS_MAP[d] = "antibiotic_tetracycline"
for d in ["gentamicin", "tobramycin", "amikacin", "streptomycin"]:
    DRUG_CLASS_MAP[d] = "antibiotic_aminoglycoside"
for d in ["vancomycin", "linezolid", "metronidazole", "trimethoprim",
          "sulfamethoxazole", "cotrimoxazole", "rifampicin", "isoniazid",
          "pyrazinamide", "ethambutol", "chloramphenicol"]:
    DRUG_CLASS_MAP[d] = "antibiotic_other"
for d in ["fluconazole", "itraconazole", "ketoconazole", "voriconazole",
          "posaconazole", "amphotericin_b", "caspofungin", "terbinafine"]:
    DRUG_CLASS_MAP[d] = "antifungal"
for d in ["acyclovir", "valacyclovir", "ganciclovir", "valganciclovir",
          "oseltamivir", "zanamivir", "ribavirin", "tenofovir", "lamivudine",
          "zidovudine", "ritonavir", "lopinavir_ritonavir", "darunavir",
          "raltegravir", "efavirenz"]:
    DRUG_CLASS_MAP[d] = "antiviral"

# PPIs / H2 / GI
for d in ["omeprazole", "esomeprazole", "pantoprazole", "lansoprazole",
          "rabeprazole", "dexlansoprazole"]:
    DRUG_CLASS_MAP[d] = "gastric_PPI"
for d in ["ranitidine", "famotidine", "cimetidine", "nizatidine"]:
    DRUG_CLASS_MAP[d] = "gastric_H2_blocker"
DRUG_CLASS_MAP.update({
    "metoclopramide": "gastric_prokinetic",
    "ondansetron": "antiemetic_5HT3",
    "loperamide": "antidiarrheal",
})

# Cardiovascular other
DRUG_CLASS_MAP.update({
    "digoxin": "cardiac_glycoside",
    "amiodarone": "antiarrhythmic_class_III",
    "lidocaine": "antiarrhythmic_class_IB",
    "quinidine": "antiarrhythmic_class_IA",
    "flecainide": "antiarrhythmic_class_IC",
    "nitroglycerin": "vasodilator_nitrate",
    "isosorbide_mononitrate": "vasodilator_nitrate",
})

# Hormones / Endocrine
DRUG_CLASS_MAP.update({
    "levothyroxine": "thyroid_hormone",
    "liothyronine": "thyroid_hormone",
    "estradiol": "estrogen",
    "conjugated_estrogens": "estrogen",
    "medroxyprogesterone": "progestin",
    "danazol": "androgen_modulator",
    "testosterone": "androgen",
    "prednisone": "corticosteroid",
    "dexamethasone": "corticosteroid",
    "hydrocortisone": "corticosteroid",
    "methylprednisolone": "corticosteroid",
    "prednisolone": "corticosteroid",
    "budesonide": "corticosteroid",
})

# Allergy
for d in ["loratadine", "cetirizine", "fexofenadine", "desloratadine"]:
    DRUG_CLASS_MAP[d] = "antihistamine_H1_second_gen"
for d in ["diphenhydramine", "chlorpheniramine", "hydroxyzine", "promethazine"]:
    DRUG_CLASS_MAP[d] = "antihistamine_H1_first_gen"

# Respiratory
for d in ["albuterol", "salmeterol", "formoterol", "terbutaline"]:
    DRUG_CLASS_MAP[d] = "bronchodilator_beta2_agonist"
for d in ["ipratropium", "tiotropium"]:
    DRUG_CLASS_MAP[d] = "bronchodilator_anticholinergic"
DRUG_CLASS_MAP.update({
    "theophylline": "bronchodilator_methylxanthine",
    "montelukast": "antiasthmatic_leukotriene",
    "fluticasone_salmeterol": "respiratory_combination",
})

# Anesthetics / Muscle relaxants
DRUG_CLASS_MAP.update({
    "propofol": "anesthetic_iv",
    "ketamine": "anesthetic_iv",
    "etomidate": "anesthetic_iv",
    "succinylcholine": "muscle_relaxant",
    "rocuronium": "muscle_relaxant",
})

# CYP probe / research compounds (some overlap with NSAIDs above)
DRUG_CLASS_MAP.update({
    "phenacetin": "CYP_probe_CYP1A2",
    "tolbutamide": "CYP_probe_CYP2C9",
    "s-warfarin": "CYP_probe_CYP2C9",
    "omeprazole_probe": "CYP_probe_CYP2C19",
    "dextromethorphan": "CYP_probe_CYP2D6",
    "debrisoquine": "CYP_probe_CYP2D6",
    "bufuralol": "CYP_probe_CYP2D6",
    "chlorzoxazone": "CYP_probe_CYP2E1",
    "midazolam_probe": "CYP_probe_CYP3A4",
    "testosterone_probe": "CYP_probe_CYP3A4",
    "nifedipine_probe": "CYP_probe_CYP3A4",
})

# Hepatotoxicants / Solvents (used in CCl4-injury models etc.)
DRUG_CLASS_MAP.update({
    "carbon_tetrachloride": "hepatotoxicant_model",
    "ethanol": "hepatotoxicant_model",
    "dimethylbenzanthracene": "carcinogen_model",
    "tetrachlorodibenzodioxin": "AhR_ligand_toxin",
    "lipopolysaccharide": "inflammation_inducer",
    "lps": "inflammation_inducer",
})

# Other notable
DRUG_CLASS_MAP.update({
    "rifampicin": "antibiotic_other",  # also a strong PXR agonist / CYP3A4 inducer
    "nateglinide": "antidiabetic_meglitinide",
    "repaglinide": "antidiabetic_meglitinide",
})


# =====================================================================
# Helpers
# =====================================================================
_UNKNOWN_TOKENS = {
    "(unknown)", "unknown", "null", "none", "n/a", "na", "not specified",
    "not reported", "various drugs", "various", "unspecified drug", "",
    "drug", "drugs", "test drug", "probe drug",
}

_CLEAN_REGEX = re.compile(r"[\(\)\[\]\"']")


def normalize_drug(name) -> str | None:
    if pd.isna(name):
        return None
    s = str(name).strip().lower()
    s = _CLEAN_REGEX.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s or s in _UNKNOWN_TOKENS:
        return None
    if s in DRUG_ALIAS_MAP:
        return DRUG_ALIAS_MAP[s]
    # else: pass through cleaned name as canonical
    return s


def get_class(canonical) -> str | None:
    if not canonical:
        return None
    return DRUG_CLASS_MAP.get(canonical, "other")


# =====================================================================
# Main
# =====================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    args = ap.parse_args()

    safe = args.model.replace("/", "__").replace(".", "_")
    path = LLM_DIR / f"{args.prefix}_{safe}.interactions_normalized.parquet"
    if not path.exists():
        print(f"FATAL: {path.relative_to(REPO)} not found")
        return

    df = pd.read_parquet(path)
    n = len(df)
    print(f"{'='*72}\n  Day 9 T3: Drug normalization\n{'='*72}")
    print(f"  Input/Output: {path.relative_to(REPO)} ({n:,} rows)")

    df["drug_canonical"] = df["drug_name"].apply(normalize_drug)
    df["drug_class"] = df["drug_canonical"].apply(get_class)
    df.to_parquet(path, index=False)

    # ---- Summary ----
    n_named = df["drug_name"].apply(
        lambda x: pd.notna(x) and str(x).strip().lower() not in _UNKNOWN_TOKENS
    ).sum()
    n_canonical = df["drug_canonical"].notna().sum()
    n_classified = ((df["drug_class"].notna()) & (df["drug_class"] != "other")).sum()

    print(f"\n  Coverage:")
    print(f"    Records with named drug (non-unknown): {n_named:,} "
          f"({n_named/n*100:.1f}%)")
    print(f"    Normalized to canonical:               {n_canonical:,} "
          f"({n_canonical/n*100:.1f}%)")
    print(f"    Classified (non-'other'):              {n_classified:,} "
          f"({n_classified/n*100:.1f}%, "
          f"{n_classified/n_canonical*100:.1f}% of canonical)")

    print(f"\n  drug_class distribution (top 25):")
    cls_counts = df["drug_class"].value_counts(dropna=False).head(25)
    for cls, cnt in cls_counts.items():
        pct = cnt / n * 100
        print(f"    {(cls or '(null)'):40s} {cnt:>5,} ({pct:>5.1f}%)")

    print(f"\n  Top 25 canonical drugs (post-normalization):")
    for d, cnt in df["drug_canonical"].value_counts().head(25).items():
        cls = get_class(d)
        print(f"    {d[:35]:35s} {cnt:>5,}   [{cls}]")

    # Audit: drugs not in class map (would be class='other')
    unclassified = df[
        df["drug_canonical"].notna() & (df["drug_class"] == "other")
    ]["drug_canonical"]
    if len(unclassified) > 0:
        print(f"\n  ⚠️  Canonical drugs NOT in DRUG_CLASS_MAP (top 20):")
        print(f"      (manual review candidates)")
        for d, cnt in unclassified.value_counts().head(20).items():
            print(f"    {d[:50]:50s} {cnt:>4,}")
        print(f"\n    Total in 'other' class: {len(unclassified):,} interactions "
              f"({len(unclassified)/n*100:.1f}%)")

    # Audit: merge wins from alias map
    print(f"\n  Notable synonym merges (canonical name = original count):")
    merge_check = [
        ("doxorubicin", ["doxorubicin", "adriamycin"]),
        ("acetaminophen", ["acetaminophen", "paracetamol"]),
        ("cyclosporine", ["cyclosporine", "ciclosporin", "cyclosporine a", "cyclosporin a"]),
        ("fluorouracil", ["fluorouracil", "5-fluorouracil", "5-fu"]),
        ("midazolam", ["midazolam", "versed"]),
        ("tacrolimus", ["tacrolimus", "fk506", "fk-506"]),
        ("warfarin", ["warfarin", "coumadin", "coumarin"]),
    ]
    for canon, aliases in merge_check:
        n_canon = (df["drug_canonical"] == canon).sum()
        if n_canon > 0:
            print(f"    {canon:25s} → {n_canon:>4,} (merged from {aliases})")

    print(f"\n  ✓ T3 done. Next: 18_normalize_herbs.py (T2 — the big one)")


if __name__ == "__main__":
    main()
