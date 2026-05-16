"""
Day 9 T2: Herb normalization (Day 9 capstone).

Maps the 3 LLM herb fields (herb_common_name / herb_name_latin /
herb_active_compound) to canonical Latin binomials + plant families,
with optional Chinese pinyin annotation for TCM herbs.

Handles 4 entity types observed in data:
  1. Whole-herb common names (e.g. "St. John's Wort")
  2. Latin binomials (e.g. "Hypericum perforatum")
  3. Active compounds (e.g. "hyperforin" → maps to parent plant)
  4. TCM compound names in Chinese pinyin (e.g. "danshen", "gan cao")

Also handles cases where LLM put an active compound in the DRUG field
(common LLM noise — e.g. "berberine", "tanshinone IIA").

Output columns added to interactions_normalized.parquet:
  - herb_canonical_latin   : Latin binomial (e.g. "Hypericum perforatum")
  - herb_canonical_english : Common name (e.g. "St. John's Wort")
  - herb_canonical_pinyin  : Chinese pinyin if TCM (e.g. "danshen", else None)
  - herb_family            : Plant family (e.g. "Hypericaceae")
  - herb_type              : "plant" / "compound" / "multi_source" / "formula"

Usage:
    python 05_llm_extraction/18_normalize_herbs.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"


# =====================================================================
# HERB_ENTRIES — single source of truth for herb mapping
# Each entry covers one canonical plant species (or compound entity)
# `aliases` covers ALL synonyms across all 3 fields + active compounds
# =====================================================================
HERB_ENTRIES: list[dict] = [
    # ===================== TOP 20 HERBS =====================
    {
        "latin": "Hypericum perforatum", "english": "St. John's Wort",
        "pinyin": "guanyelianqiao", "family": "Hypericaceae", "type": "plant",
        "aliases": ["st. john's wort", "st johns wort", "st john's wort",
                    "sjw", "hypericum perforatum", "hypericum",
                    "hypericin", "hyperforin", "pseudohypericin",
                    "saint john's wort", "saint johns wort"],
    },
    {
        "latin": "Salvia miltiorrhiza", "english": "Danshen",
        "pinyin": "danshen", "family": "Lamiaceae", "type": "plant",
        "aliases": ["danshen", "dan shen", "salvia miltiorrhiza",
                    "red sage", "chinese sage", "tanshinone",
                    "tanshinone i", "tanshinone ii", "tanshinone iia",
                    "tanshinone iib", "cryptotanshinone", "miltirone",
                    "salvianolic acid", "salvianolic acid a",
                    "salvianolic acid b", "salvianolate"],
    },
    {
        "latin": "Schisandra chinensis", "english": "Schisandra",
        "pinyin": "wuweizi", "family": "Schisandraceae", "type": "plant",
        "aliases": ["schisandra", "schizandra", "schisandra chinensis",
                    "schizandra chinensis", "wu wei zi", "wuweizi",
                    "five-flavor berry", "magnolia berry",
                    "schisandrin", "schisandrin a", "schisandrin b",
                    "schisandrin c", "schisandrol", "schisandrol a",
                    "schisandrol b", "deoxyschisandrin", "wuzhi"],
    },
    {
        "latin": "Schisandra sphenanthera", "english": "Southern Schisandra",
        "pinyin": "huazhongwuweizi", "family": "Schisandraceae",
        "type": "plant",
        "aliases": ["schisandra sphenanthera", "wuzhi capsule",
                    "wuzhi tablet", "wuzhi"],
    },
    {
        "latin": "Panax ginseng", "english": "Korean Ginseng",
        "pinyin": "renshen", "family": "Araliaceae", "type": "plant",
        "aliases": ["ginseng", "panax ginseng", "korean ginseng",
                    "asian ginseng", "chinese ginseng", "ren shen",
                    "renshen", "ginsenoside", "ginsenosides",
                    "ginsenoside rb1", "ginsenoside rb2",
                    "ginsenoside rg1", "ginsenoside rg3",
                    "ginsenoside rd", "ginsenoside re",
                    "ginsenoside rh1", "ginsenoside rh2"],
    },
    {
        "latin": "Panax quinquefolius", "english": "American Ginseng",
        "pinyin": "xiyangshen", "family": "Araliaceae", "type": "plant",
        "aliases": ["american ginseng", "panax quinquefolius",
                    "xi yang shen", "xiyangshen"],
    },
    {
        "latin": "Panax notoginseng", "english": "Notoginseng",
        "pinyin": "sanqi", "family": "Araliaceae", "type": "plant",
        "aliases": ["notoginseng", "panax notoginseng", "san qi",
                    "sanqi", "tian qi", "tianqi", "pseudoginseng",
                    "notoginsenoside r1"],
    },
    {
        "latin": "Glycyrrhiza uralensis", "english": "Licorice (Chinese)",
        "pinyin": "gancao", "family": "Fabaceae", "type": "plant",
        "aliases": ["licorice", "liquorice", "glycyrrhiza",
                    "glycyrrhiza uralensis", "gan cao", "gancao",
                    "chinese licorice", "glycyrrhizin", "glycyrrhetinic acid",
                    "18β-glycyrrhetinic acid", "18-glycyrrhetinic acid",
                    "isoliquiritigenin", "liquiritigenin",
                    "glabridin"],
    },
    {
        "latin": "Glycyrrhiza glabra", "english": "Licorice (European)",
        "pinyin": None, "family": "Fabaceae", "type": "plant",
        "aliases": ["glycyrrhiza glabra", "european licorice",
                    "common licorice"],
    },
    {
        "latin": "Camellia sinensis", "english": "Green Tea",
        "pinyin": "lucha", "family": "Theaceae", "type": "plant",
        "aliases": ["green tea", "tea", "black tea", "white tea",
                    "camellia sinensis", "lu cha", "lucha",
                    "egcg", "epigallocatechin gallate",
                    "epigallocatechin-3-gallate", "tea polyphenols",
                    "tea catechins", "catechin", "catechins",
                    "epicatechin", "epigallocatechin", "epicatechin gallate"],
    },
    {
        "latin": "Allium sativum", "english": "Garlic",
        "pinyin": "dasuan", "family": "Amaryllidaceae", "type": "plant",
        "aliases": ["garlic", "allium sativum", "da suan", "dasuan",
                    "allicin", "ajoene", "diallyl disulfide",
                    "diallyl sulfide", "diallyl trisulfide",
                    "s-allyl cysteine", "garlic extract"],
    },
    {
        "latin": "Coptis chinensis", "english": "Coptis (Goldthread)",
        "pinyin": "huanglian", "family": "Ranunculaceae", "type": "plant",
        "aliases": ["coptis", "coptis chinensis", "rhizoma coptidis",
                    "coptidis rhizoma", "huang lian", "huanglian",
                    "chinese goldthread", "berberine",
                    "berberine hydrochloride", "palmatine", "coptisine"],
    },
    {
        "latin": "Berberis vulgaris", "english": "Barberry",
        "pinyin": None, "family": "Berberidaceae", "type": "plant",
        "aliases": ["berberis", "berberis vulgaris", "barberry",
                    "european barberry"],
    },
    {
        "latin": "Astragalus membranaceus", "english": "Astragalus",
        "pinyin": "huangqi", "family": "Fabaceae", "type": "plant",
        "aliases": ["astragalus", "astragalus membranaceus",
                    "astragalus mongholicus", "astragalus propinquus",
                    "huang qi", "huangqi", "milk vetch",
                    "astragaloside", "astragaloside iv",
                    "astragalan", "astragalus polysaccharide",
                    "cycloastragenol"],
    },
    {
        "latin": "Ginkgo biloba", "english": "Ginkgo",
        "pinyin": "yinxing", "family": "Ginkgoaceae", "type": "plant",
        "aliases": ["ginkgo", "ginkgo biloba", "yin xing", "yinxing",
                    "maidenhair tree", "egb 761", "egb761",
                    "ginkgolide", "ginkgolide a", "ginkgolide b",
                    "ginkgolide c", "bilobalide", "ginkgo extract"],
    },
    {
        "latin": "Curcuma longa", "english": "Turmeric",
        "pinyin": "jianghuang", "family": "Zingiberaceae", "type": "plant",
        "aliases": ["turmeric", "curcuma longa", "jiang huang", "jianghuang",
                    "curcumin", "curcuminoid", "curcuminoids",
                    "demethoxycurcumin", "bisdemethoxycurcumin",
                    "tetrahydrocurcumin", "curcumenol"],
    },
    {
        "latin": "Zingiber officinale", "english": "Ginger",
        "pinyin": "shengjiang", "family": "Zingiberaceae", "type": "plant",
        "aliases": ["ginger", "zingiber officinale", "sheng jiang",
                    "shengjiang", "gan jiang", "ganjiang",
                    "gingerol", "6-gingerol", "8-gingerol", "10-gingerol",
                    "shogaol", "6-shogaol", "ginger extract"],
    },
    {
        "latin": "Catha edulis", "english": "Khat",
        "pinyin": None, "family": "Celastraceae", "type": "plant",
        "aliases": ["khat", "qat", "miraa", "catha edulis",
                    "cathinone", "cathine", "norpseudoephedrine"],
    },
    {
        "latin": "Andrographis paniculata", "english": "Andrographis",
        "pinyin": "chuanxinlian", "family": "Acanthaceae", "type": "plant",
        "aliases": ["andrographis", "andrographis paniculata",
                    "chuan xin lian", "chuanxinlian", "kalmegh",
                    "king of bitters", "andrographolide",
                    "neoandrographolide"],
    },
    {
        "latin": "Echinacea purpurea", "english": "Purple Coneflower",
        "pinyin": None, "family": "Asteraceae", "type": "plant",
        "aliases": ["echinacea", "echinacea purpurea",
                    "purple coneflower", "echinacoside",
                    "cichoric acid"],
    },
    {
        "latin": "Echinacea angustifolia", "english": "Narrow-leaved Echinacea",
        "pinyin": None, "family": "Asteraceae", "type": "plant",
        "aliases": ["echinacea angustifolia", "narrow-leaved echinacea"],
    },
    {
        "latin": "Centella asiatica", "english": "Gotu Kola",
        "pinyin": "jixuecao", "family": "Apiaceae", "type": "plant",
        "aliases": ["centella", "centella asiatica", "gotu kola",
                    "ji xue cao", "jixuecao", "indian pennywort",
                    "asiaticoside", "asiatic acid",
                    "madecassoside", "madecassic acid"],
    },

    # ===================== TCM CORE HERBS =====================
    {
        "latin": "Salvia miltiorrhiza × Panax notoginseng", "english": "Compound formula",
        "pinyin": "fufang", "family": "TCM_formula", "type": "formula",
        "aliases": ["fufang danshen", "compound danshen", "fufang_danshen",
                    "compound danshen dripping pill"],
    },
    {
        "latin": "Rehmannia glutinosa", "english": "Chinese Foxglove",
        "pinyin": "dihuang", "family": "Orobanchaceae", "type": "plant",
        "aliases": ["rehmannia", "rehmannia glutinosa", "di huang",
                    "dihuang", "sheng di huang", "shengdihuang",
                    "shu di huang", "shudihuang", "shenghuang",
                    "catalpol", "rehmanioside"],
    },
    {
        "latin": "Cinnamomum cassia", "english": "Chinese Cinnamon",
        "pinyin": "rougui", "family": "Lauraceae", "type": "plant",
        "aliases": ["cinnamon", "chinese cinnamon", "cassia",
                    "cinnamomum cassia", "rou gui", "rougui",
                    "cinnamaldehyde", "cinnamic acid"],
    },
    {
        "latin": "Cinnamomum verum", "english": "Ceylon Cinnamon",
        "pinyin": None, "family": "Lauraceae", "type": "plant",
        "aliases": ["cinnamomum verum", "ceylon cinnamon",
                    "cinnamomum zeylanicum", "true cinnamon"],
    },
    {
        "latin": "Magnolia officinalis", "english": "Magnolia Bark",
        "pinyin": "houpo", "family": "Magnoliaceae", "type": "plant",
        "aliases": ["magnolia", "magnolia officinalis", "hou po", "houpo",
                    "magnolol", "honokiol"],
    },
    {
        "latin": "Pueraria lobata", "english": "Kudzu",
        "pinyin": "gegen", "family": "Fabaceae", "type": "plant",
        "aliases": ["pueraria", "pueraria lobata", "ge gen", "gegen",
                    "kudzu", "puerarin", "daidzein", "daidzin"],
    },
    {
        "latin": "Bupleurum chinense", "english": "Bupleurum",
        "pinyin": "chaihu", "family": "Apiaceae", "type": "plant",
        "aliases": ["bupleurum", "bupleurum chinense", "chai hu", "chaihu",
                    "saikosaponin", "saikosaponin a", "saikosaponin d"],
    },
    {
        "latin": "Angelica sinensis", "english": "Dong Quai",
        "pinyin": "danggui", "family": "Apiaceae", "type": "plant",
        "aliases": ["angelica sinensis", "dong quai", "dang gui", "danggui",
                    "female ginseng", "ferulic acid", "ligustilide",
                    "z-ligustilide"],
    },
    {
        "latin": "Lycium barbarum", "english": "Goji Berry",
        "pinyin": "gouqi", "family": "Solanaceae", "type": "plant",
        "aliases": ["lycium", "lycium barbarum", "goji", "goji berry",
                    "wolfberry", "gou qi", "gouqi", "gou qi zi",
                    "lycium barbarum polysaccharide", "lbp"],
    },
    {
        "latin": "Scutellaria baicalensis", "english": "Chinese Skullcap",
        "pinyin": "huangqin", "family": "Lamiaceae", "type": "plant",
        "aliases": ["scutellaria", "scutellaria baicalensis",
                    "chinese skullcap", "huang qin", "huangqin",
                    "baicalin", "baicalein", "wogonin", "wogonoside",
                    "oroxylin"],
    },
    {
        "latin": "Paeonia lactiflora", "english": "Chinese Peony",
        "pinyin": "baishao", "family": "Paeoniaceae", "type": "plant",
        "aliases": ["paeonia lactiflora", "chinese peony",
                    "white peony", "bai shao", "baishao",
                    "paeoniflorin", "albiflorin"],
    },
    {
        "latin": "Rheum officinale", "english": "Chinese Rhubarb",
        "pinyin": "dahuang", "family": "Polygonaceae", "type": "plant",
        "aliases": ["rheum", "rheum officinale", "rheum palmatum",
                    "rhubarb", "chinese rhubarb", "da huang", "dahuang",
                    "emodin", "aloe-emodin", "rhein", "chrysophanol",
                    "physcion"],
    },
    {
        "latin": "Reynoutria multiflora", "english": "Fo-Ti",
        "pinyin": "heshouwu", "family": "Polygonaceae", "type": "plant",
        "aliases": ["polygonum multiflorum", "reynoutria multiflora",
                    "fallopia multiflora", "fo-ti", "fo ti",
                    "he shou wu", "heshouwu", "tetrahydroxystilbene glucoside",
                    "thsg"],
    },
    {
        "latin": "Atractylodes macrocephala", "english": "White Atractylodes",
        "pinyin": "baizhu", "family": "Asteraceae", "type": "plant",
        "aliases": ["atractylodes", "atractylodes macrocephala",
                    "bai zhu", "baizhu", "atractylenolide",
                    "atractylenolide i", "atractylenolide ii",
                    "atractylenolide iii"],
    },
    {
        "latin": "Wolfiporia cocos", "english": "Poria",
        "pinyin": "fuling", "family": "Polyporaceae", "type": "fungus",
        "aliases": ["poria", "poria cocos", "wolfiporia cocos",
                    "wolfiporia extensa", "fu ling", "fuling",
                    "pachymic acid", "tumulosic acid"],
    },
    {
        "latin": "Lonicera japonica", "english": "Japanese Honeysuckle",
        "pinyin": "jinyinhua", "family": "Caprifoliaceae", "type": "plant",
        "aliases": ["lonicera", "lonicera japonica", "honeysuckle",
                    "japanese honeysuckle", "jin yin hua", "jinyinhua",
                    "chlorogenic acid", "luteoloside"],
    },
    {
        "latin": "Forsythia suspensa", "english": "Forsythia",
        "pinyin": "lianqiao", "family": "Oleaceae", "type": "plant",
        "aliases": ["forsythia", "forsythia suspensa", "lian qiao",
                    "lianqiao", "forsythin", "phillyrin", "pinoresinol"],
    },
    {
        "latin": "Ephedra sinica", "english": "Ephedra (Ma Huang)",
        "pinyin": "mahuang", "family": "Ephedraceae", "type": "plant",
        "aliases": ["ephedra", "ephedra sinica", "ma huang", "mahuang",
                    "ephedrine", "pseudoephedrine", "ephedrae herba"],
    },
    {
        "latin": "Artemisia annua", "english": "Sweet Wormwood",
        "pinyin": "qinghao", "family": "Asteraceae", "type": "plant",
        "aliases": ["artemisia", "artemisia annua", "sweet wormwood",
                    "qing hao", "qinghao", "artemisinin",
                    "artesunate", "artemether", "dihydroartemisinin"],
    },
    {
        "latin": "Silybum marianum", "english": "Milk Thistle",
        "pinyin": "shuifeiji", "family": "Asteraceae", "type": "plant",
        "aliases": ["silybum", "silybum marianum", "milk thistle",
                    "shui fei ji", "shuifeiji", "silymarin",
                    "silybin", "silibinin", "silibinin a",
                    "silydianin", "silicristin"],
    },
    {
        "latin": "Ophiopogon japonicus", "english": "Dwarf Lilyturf",
        "pinyin": "maidong", "family": "Asparagaceae", "type": "plant",
        "aliases": ["ophiopogon", "ophiopogon japonicus",
                    "mai dong", "maidong", "mai men dong",
                    "ophiopogonin", "ophiopogonin d"],
    },
    {
        "latin": "Codonopsis pilosula", "english": "Dang Shen",
        "pinyin": "dangshen", "family": "Campanulaceae", "type": "plant",
        "aliases": ["codonopsis", "codonopsis pilosula",
                    "dang shen", "dangshen", "poor man's ginseng",
                    "codonopsis polysaccharide"],
    },
    {
        "latin": "Reynoutria japonica", "english": "Japanese Knotweed",
        "pinyin": "huzhang", "family": "Polygonaceae", "type": "plant",
        "aliases": ["polygonum cuspidatum", "reynoutria japonica",
                    "japanese knotweed", "hu zhang", "huzhang",
                    "polydatin", "piceid", "resveratrol"],
    },
    {
        "latin": "Eucommia ulmoides", "english": "Eucommia",
        "pinyin": "duzhong", "family": "Eucommiaceae", "type": "plant",
        "aliases": ["eucommia", "eucommia ulmoides", "du zhong", "duzhong",
                    "aucubin", "geniposide", "pinoresinol diglucoside"],
    },
    {
        "latin": "Cnidium monnieri", "english": "Cnidium",
        "pinyin": "shechuangzi", "family": "Apiaceae", "type": "plant",
        "aliases": ["cnidium monnieri", "she chuang zi", "shechuangzi",
                    "osthole"],
    },
    {
        "latin": "Crataegus pinnatifida", "english": "Chinese Hawthorn",
        "pinyin": "shanzha", "family": "Rosaceae", "type": "plant",
        "aliases": ["crataegus", "crataegus pinnatifida",
                    "chinese hawthorn", "hawthorn", "shan zha", "shanzha",
                    "hyperoside", "rutin"],
    },
    {
        "latin": "Ziziphus jujuba", "english": "Jujube",
        "pinyin": "dazao", "family": "Rhamnaceae", "type": "plant",
        "aliases": ["ziziphus", "ziziphus jujuba", "jujube",
                    "chinese date", "da zao", "dazao",
                    "ziziphus saponin", "jujuboside"],
    },
    {
        "latin": "Morus alba", "english": "White Mulberry",
        "pinyin": "sangbaipi", "family": "Moraceae", "type": "plant",
        "aliases": ["morus alba", "white mulberry", "mulberry",
                    "sang bai pi", "sangbaipi", "sang ye", "sangye",
                    "morin", "kuwanon"],
    },
    {
        "latin": "Tripterygium wilfordii", "english": "Thunder God Vine",
        "pinyin": "leigongteng", "family": "Celastraceae", "type": "plant",
        "aliases": ["tripterygium", "tripterygium wilfordii",
                    "thunder god vine", "lei gong teng", "leigongteng",
                    "triptolide", "celastrol"],
    },
    {
        "latin": "Ganoderma lucidum", "english": "Reishi",
        "pinyin": "lingzhi", "family": "Ganodermataceae", "type": "fungus",
        "aliases": ["ganoderma", "ganoderma lucidum", "reishi",
                    "lingzhi", "ling zhi",
                    "ganoderic acid", "ganoderma polysaccharide"],
    },
    {
        "latin": "Cordyceps sinensis", "english": "Cordyceps",
        "pinyin": "dongchongxiacao", "family": "Cordycipitaceae",
        "type": "fungus",
        "aliases": ["cordyceps", "cordyceps sinensis", "cordyceps militaris",
                    "ophiocordyceps sinensis", "dong chong xia cao",
                    "dongchongxiacao", "cordycepin", "adenosine"],
    },
    {
        "latin": "Tribulus terrestris", "english": "Tribulus",
        "pinyin": "jili", "family": "Zygophyllaceae", "type": "plant",
        "aliases": ["tribulus", "tribulus terrestris", "ji li", "jili",
                    "puncture vine", "protodioscin"],
    },
    {
        "latin": "Eleutherococcus senticosus", "english": "Siberian Ginseng",
        "pinyin": "ciwujia", "family": "Araliaceae", "type": "plant",
        "aliases": ["eleutherococcus", "eleutherococcus senticosus",
                    "siberian ginseng", "ci wu jia", "ciwujia",
                    "eleutheroside", "eleutheroside e"],
    },
    {
        "latin": "Trigonella foenum-graecum", "english": "Fenugreek",
        "pinyin": None, "family": "Fabaceae", "type": "plant",
        "aliases": ["fenugreek", "trigonella foenum-graecum",
                    "trigonelline", "diosgenin", "4-hydroxyisoleucine"],
    },
    {
        "latin": "Hibiscus sabdariffa", "english": "Hibiscus",
        "pinyin": None, "family": "Malvaceae", "type": "plant",
        "aliases": ["hibiscus", "hibiscus sabdariffa", "roselle",
                    "hibiscus extract"],
    },
    {
        "latin": "Cimicifuga racemosa", "english": "Black Cohosh",
        "pinyin": None, "family": "Ranunculaceae", "type": "plant",
        "aliases": ["black cohosh", "cimicifuga racemosa",
                    "actaea racemosa", "sheng ma", "shengma"],
    },
    {
        "latin": "Serenoa repens", "english": "Saw Palmetto",
        "pinyin": None, "family": "Arecaceae", "type": "plant",
        "aliases": ["saw palmetto", "serenoa repens", "sabal serrulata"],
    },
    {
        "latin": "Valeriana officinalis", "english": "Valerian",
        "pinyin": None, "family": "Caprifoliaceae", "type": "plant",
        "aliases": ["valerian", "valeriana officinalis", "valerian root",
                    "valerenic acid"],
    },
    {
        "latin": "Vitis vinifera", "english": "Grape",
        "pinyin": None, "family": "Vitaceae", "type": "plant",
        "aliases": ["grape", "grape seed", "vitis vinifera",
                    "grape seed extract", "proanthocyanidin",
                    "grape seed proanthocyanidin"],
    },
    {
        "latin": "Stephania tetrandra", "english": "Tetrandra",
        "pinyin": "fangji", "family": "Menispermaceae", "type": "plant",
        "aliases": ["stephania tetrandra", "tetrandrine",
                    "fang ji", "fangji", "han fang ji"],
    },
    {
        "latin": "Sinomenium acutum", "english": "Sinomenium",
        "pinyin": "qingfengteng", "family": "Menispermaceae", "type": "plant",
        "aliases": ["sinomenium acutum", "sinomenine",
                    "qing feng teng", "qingfengteng"],
    },
    {
        "latin": "Epimedium brevicornum", "english": "Epimedium",
        "pinyin": "yinyanghuo", "family": "Berberidaceae", "type": "plant",
        "aliases": ["epimedium", "epimedium brevicornum",
                    "horny goat weed", "yin yang huo", "yinyanghuo",
                    "icariin", "epimedin", "icaritin",
                    "icariside", "icariside ii"],
    },
    {
        "latin": "Aconitum carmichaelii", "english": "Sichuan Aconite",
        "pinyin": "fuzi", "family": "Ranunculaceae", "type": "plant",
        "aliases": ["aconitum", "aconitum carmichaelii", "monkshood",
                    "fu zi", "fuzi", "aconitine", "hypaconitine",
                    "mesaconitine", "benzoylaconitine"],
    },
    {
        "latin": "Cassia angustifolia", "english": "Senna",
        "pinyin": "fanxieye", "family": "Fabaceae", "type": "plant",
        "aliases": ["senna", "cassia angustifolia", "senna leaf",
                    "fan xie ye", "fanxieye", "sennoside",
                    "sennoside a", "sennoside b"],
    },
    {
        "latin": "Nigella sativa", "english": "Black Cumin",
        "pinyin": None, "family": "Ranunculaceae", "type": "plant",
        "aliases": ["nigella sativa", "black cumin", "black seed",
                    "thymoquinone"],
    },
    {
        "latin": "Hypericum japonicum", "english": "Field St John's Wort",
        "pinyin": None, "family": "Hypericaceae", "type": "plant",
        "aliases": ["hypericum japonicum"],
    },
    {
        "latin": "Foeniculum vulgare", "english": "Fennel",
        "pinyin": None, "family": "Apiaceae", "type": "plant",
        "aliases": ["fennel", "foeniculum vulgare", "anethole"],
    },
    {
        "latin": "Thymus vulgaris", "english": "Thyme",
        "pinyin": None, "family": "Lamiaceae", "type": "plant",
        "aliases": ["thyme", "thymus vulgaris", "thymol", "carvacrol"],
    },
    {
        "latin": "Camptotheca acuminata", "english": "Happy Tree",
        "pinyin": "xishu", "family": "Nyssaceae", "type": "plant",
        "aliases": ["camptotheca", "camptotheca acuminata",
                    "happy tree", "xi shu", "xishu",
                    "camptothecin", "10-hydroxycamptothecin"],
    },
    {
        "latin": "Taxus brevifolia", "english": "Pacific Yew",
        "pinyin": None, "family": "Taxaceae", "type": "plant",
        "aliases": ["taxus", "taxus brevifolia", "pacific yew",
                    "yew tree"],
    },
    {
        "latin": "Catharanthus roseus", "english": "Madagascar Periwinkle",
        "pinyin": None, "family": "Apocynaceae", "type": "plant",
        "aliases": ["catharanthus", "catharanthus roseus",
                    "madagascar periwinkle", "vincristine_source",
                    "vinblastine_source"],
    },
    {
        "latin": "Citrus aurantium", "english": "Bitter Orange",
        "pinyin": "zhishi", "family": "Rutaceae", "type": "plant",
        "aliases": ["citrus aurantium", "bitter orange",
                    "zhi shi", "zhishi", "zhi ke", "zhike",
                    "synephrine", "p-synephrine",
                    "naringin", "naringenin", "hesperidin", "hesperetin"],
    },
    {
        "latin": "Citrus sinensis", "english": "Sweet Orange",
        "pinyin": None, "family": "Rutaceae", "type": "plant",
        "aliases": ["orange juice", "citrus sinensis", "sweet orange"],
    },
    {
        "latin": "Citrus paradisi", "english": "Grapefruit",
        "pinyin": None, "family": "Rutaceae", "type": "plant",
        "aliases": ["grapefruit", "grapefruit juice", "citrus paradisi",
                    "bergamottin", "furanocoumarin"],
    },
    {
        "latin": "Piper nigrum", "english": "Black Pepper",
        "pinyin": "huijiao", "family": "Piperaceae", "type": "plant",
        "aliases": ["piper nigrum", "black pepper", "hui jiao",
                    "huijiao", "piperine"],
    },
    {
        "latin": "Capsicum annuum", "english": "Chili Pepper",
        "pinyin": "lajiao", "family": "Solanaceae", "type": "plant",
        "aliases": ["capsicum", "capsicum annuum", "chili", "chili pepper",
                    "la jiao", "lajiao", "capsaicin"],
    },
    {
        "latin": "Camellia oleifera", "english": "Tea Oil Camellia",
        "pinyin": "youcha", "family": "Theaceae", "type": "plant",
        "aliases": ["camellia oleifera", "tea seed oil"],
    },

    # ===================== EXPANSION v2 (Day 9 patch) =====================
    # Top 25 unmapped from initial run; adds ~150 records coverage
    {
        "latin": "Labisia pumila", "english": "Kacip Fatimah",
        "pinyin": None, "family": "Primulaceae", "type": "plant",
        "aliases": ["kacip fatimah", "labisia pumila"],
    },
    {
        "latin": "Zanthoxylum nitidum", "english": "Two-faced Prickly Ash",
        "pinyin": "lianglianzhen", "family": "Rutaceae", "type": "plant",
        "aliases": ["zanthoxylum nitidum", "liang lian zhen",
                    "lianglianzhen", "nitidine", "nitidine chloride",
                    "two-faced prickly ash"],
    },
    {
        "latin": "Momordica charantia", "english": "Bitter Melon",
        "pinyin": "kugua", "family": "Cucurbitaceae", "type": "plant",
        "aliases": ["bitter melon", "bitter gourd", "momordica charantia",
                    "ku gua", "kugua", "charantin"],
    },
    {
        "latin": "Phyllanthus amarus", "english": "Phyllanthus",
        "pinyin": None, "family": "Phyllanthaceae", "type": "plant",
        "aliases": ["phyllanthus", "phyllanthus amarus",
                    "phyllanthus niruri", "phyllanthus emblica",
                    "amla", "indian gooseberry"],
    },
    {
        "latin": "Salvia officinalis", "english": "Common Sage",
        "pinyin": None, "family": "Lamiaceae", "type": "plant",
        "aliases": ["sage", "common sage", "salvia officinalis",
                    "garden sage"],
    },
    {
        "latin": "Ligusticum chuanxiong", "english": "Sichuan Lovage",
        "pinyin": "chuanxiong", "family": "Apiaceae", "type": "plant",
        "aliases": ["chuanxiong", "chuan xiong", "ligusticum chuanxiong",
                    "ligusticum striatum", "ligustrazine",
                    "tetramethylpyrazine", "tmp", "senkyunolide",
                    "senkyunolide a"],
    },
    {
        "latin": "Aspalathus linearis", "english": "Rooibos",
        "pinyin": None, "family": "Fabaceae", "type": "plant",
        "aliases": ["rooibos", "aspalathus linearis", "red bush tea",
                    "rooibos tea"],
    },
    {
        "latin": "Tetradium ruticarpum", "english": "Evodia",
        "pinyin": "wuzhuyu", "family": "Rutaceae", "type": "plant",
        "aliases": ["evodia", "evodia rutaecarpa", "tetradium ruticarpum",
                    "wu zhu yu", "wuzhuyu", "evodiamine", "rutaecarpine"],
    },
    {
        "latin": "Marsdenia tenacissima", "english": "Marsdenia",
        "pinyin": "tongguanteng", "family": "Apocynaceae", "type": "plant",
        "aliases": ["marsdenia tenacissima", "tong guan teng",
                    "tongguanteng", "xiao-ai-ping", "xiaoaiping"],
    },
    {
        "latin": "Garcinia indica", "english": "Kokum",
        "pinyin": None, "family": "Clusiaceae", "type": "plant",
        "aliases": ["garcinia indica", "garcinia mangostana", "kokum",
                    "garcinol", "gambogic acid", "mangosteen",
                    "alpha-mangostin"],
    },
    {
        "latin": "Coix lacryma-jobi", "english": "Job's Tears",
        "pinyin": "yiyiren", "family": "Poaceae", "type": "plant",
        "aliases": ["coix lacryma-jobi", "coix lachryma-jobi",
                    "job's tears", "jobs tears", "yi yi ren", "yiyiren",
                    "coixenolide", "coixol"],
    },
    {
        "latin": "Gardenia jasminoides", "english": "Cape Jasmine",
        "pinyin": "zhizi", "family": "Rubiaceae", "type": "plant",
        "aliases": ["gardenia", "gardenia jasminoides", "zhi zi", "zhizi",
                    "geniposide", "genipin", "crocin", "crocetin",
                    "genipinic acid"],
    },
    {
        "latin": "Mangifera indica", "english": "Mango",
        "pinyin": None, "family": "Anacardiaceae", "type": "plant",
        "aliases": ["mango", "mangifera indica", "mangiferin"],
    },
    {
        "latin": "Sophora flavescens", "english": "Ku Shen",
        "pinyin": "kushen", "family": "Fabaceae", "type": "plant",
        "aliases": ["sophora flavescens", "ku shen", "kushen",
                    "matrine", "oxymatrine", "sophocarpine",
                    "compound kushen injection", "compound kushen",
                    "kushen injection"],
    },
    {
        "latin": "Tilia cordata", "english": "Linden Flower",
        "pinyin": None, "family": "Malvaceae", "type": "plant",
        "aliases": ["linden", "linden flower", "tilia", "tilia cordata",
                    "tilia americana", "flor de tila"],
    },
    {
        "latin": "Terminalia arjuna", "english": "Arjuna",
        "pinyin": None, "family": "Combretaceae", "type": "plant",
        "aliases": ["terminalia arjuna", "arjuna", "arjunic acid",
                    "arjunolic acid"],
    },
    {
        "latin": "Melissa officinalis", "english": "Lemon Balm",
        "pinyin": None, "family": "Lamiaceae", "type": "plant",
        "aliases": ["lemon balm", "melissa officinalis", "balm mint",
                    "rosmarinic acid"],
    },
    # TCM compound formulas (multi-herb prescriptions)
    {
        "latin": "TCM_formula_suxiao_jiuxin", "english": "Suxiao Jiuxin Pill",
        "pinyin": "suxiaojiuxin", "family": "TCM_formula", "type": "formula",
        "aliases": ["suxiao jiuxin pill", "suxiao jiuxin", "suxiaojiuxin"],
    },
    {
        "latin": "TCM_formula_baoyuan", "english": "Baoyuan Decoction",
        "pinyin": "baoyuan", "family": "TCM_formula", "type": "formula",
        "aliases": ["baoyuan decoction", "baoyuan tang"],
    },
    {
        "latin": "TCM_formula_re_du_ning", "english": "Re Du Ning Injection",
        "pinyin": "reduning", "family": "TCM_formula", "type": "formula",
        "aliases": ["re du ning injection", "reduning injection",
                    "reduning"],
    },
    # Animal-derived (TCM Chan Su; technically not plant)
    {
        "latin": "Bufo_bufo_gargarizans", "english": "Chan Su (Toad Venom)",
        "pinyin": "chansu", "family": "Animal_derived",
        "type": "animal_derived",
        "aliases": ["chan su", "chansu", "bufalin", "cinobufotalin",
                    "cinobufagin", "resibufogenin", "toad venom",
                    "bufadienolide"],
    },
    # Generic compound class placeholder (e.g. "flavonoids" mentioned without source)
    {
        "latin": "multi_source_flavonoids", "english": "Flavonoids (class)",
        "pinyin": None, "family": "flavonoid_compound",
        "type": "multi_source",
        "aliases": ["flavonoids", "flavonoid", "polyphenols", "polyphenol",
                    "anthocyanins"],
    },

    # ===================== MULTI-SOURCE COMPOUNDS =====================
    {
        "latin": "multi_source_quercetin", "english": "Quercetin",
        "pinyin": None, "family": "flavonoid_compound",
        "type": "multi_source",
        "aliases": ["quercetin", "quercitrin", "rutin",
                    "isoquercitrin"],
    },
    {
        "latin": "multi_source_resveratrol", "english": "Resveratrol",
        "pinyin": None, "family": "stilbene_compound",
        "type": "multi_source",
        "aliases": ["resveratrol", "trans-resveratrol"],
    },
    {
        "latin": "multi_source_kaempferol", "english": "Kaempferol",
        "pinyin": None, "family": "flavonoid_compound",
        "type": "multi_source",
        "aliases": ["kaempferol"],
    },
    {
        "latin": "multi_source_luteolin", "english": "Luteolin",
        "pinyin": None, "family": "flavonoid_compound",
        "type": "multi_source",
        "aliases": ["luteolin"],
    },
    {
        "latin": "multi_source_apigenin", "english": "Apigenin",
        "pinyin": None, "family": "flavonoid_compound",
        "type": "multi_source",
        "aliases": ["apigenin"],
    },
    {
        "latin": "multi_source_genistein", "english": "Genistein",
        "pinyin": None, "family": "isoflavonoid_compound",
        "type": "multi_source",
        "aliases": ["genistein", "soy isoflavones", "soybean isoflavones",
                    "daidzein"],  # also from kudzu but more from soy
    },
]


# =====================================================================
# Build alias and info maps from HERB_ENTRIES (single source of truth)
# =====================================================================
HERB_ALIAS_MAP: dict[str, str] = {}
HERB_INFO_MAP: dict[str, dict] = {}

for _entry in HERB_ENTRIES:
    canon = _entry["latin"]
    HERB_INFO_MAP[canon] = {
        "english": _entry["english"],
        "pinyin": _entry["pinyin"],
        "family": _entry["family"],
        "type": _entry["type"],
    }
    for alias in _entry["aliases"]:
        # Apply SAME cleaning that normalize_token() applies to inputs
        # (lowercase + strip + remove brackets/quotes/apostrophes + collapse ws)
        cleaned = alias.lower().strip()
        cleaned = re.sub(r"[\(\)\[\]\"']", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        HERB_ALIAS_MAP[cleaned] = canon


_UNKNOWN_TOKENS = {
    "(unknown)", "unknown", "null", "none", "n/a", "na", "not specified",
    "not reported", "", "herb", "herbal", "various herbs", "various",
    "tcm herb", "tcm", "chinese herb",
}

_CLEAN_REGEX = re.compile(r"[\(\)\[\]\"']")


def normalize_token(s) -> str | None:
    """Normalize a single string to canonical Latin binomial, or None."""
    if pd.isna(s) or not isinstance(s, str):
        return None
    t = s.strip().lower()
    t = _CLEAN_REGEX.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    if not t or t in _UNKNOWN_TOKENS:
        return None
    return HERB_ALIAS_MAP.get(t)


def clean_for_passthrough(s) -> str | None:
    """Clean string to use as pass-through canonical (for unmapped herbs).
    Returns None if string is empty or in unknown tokens."""
    if pd.isna(s) or not isinstance(s, str):
        return None
    t = s.strip().lower()
    t = _CLEAN_REGEX.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    if not t or t in _UNKNOWN_TOKENS:
        return None
    return t


def normalize_herb_row(row) -> dict:
    """
    Normalization with 3-tier resolution:
    1. Mapped: check all 3 herb fields + drug field (compound leak) against alias map
    2. Pass-through: if named but unmapped, use cleaned text as canonical
                     with herb_in_map=False (downstream can filter)
    3. None: if no herb info available anywhere
    """
    # Tier 1: try mapping each named field
    for field in ["herb_common_name", "herb_name_latin",
                  "herb_active_compound"]:
        canon = normalize_token(row.get(field))
        if canon:
            info = HERB_INFO_MAP[canon]
            return {
                "herb_canonical_latin": canon,
                "herb_canonical_english": info["english"],
                "herb_canonical_pinyin": info["pinyin"],
                "herb_family": info["family"],
                "herb_type": info["type"],
                "herb_in_map": True,
            }
    # Tier 1b: drug field fallback (active compounds sometimes leak there)
    canon = normalize_token(row.get("drug_name"))
    if canon:
        info = HERB_INFO_MAP[canon]
        return {
            "herb_canonical_latin": canon,
            "herb_canonical_english": info["english"],
            "herb_canonical_pinyin": info["pinyin"],
            "herb_family": info["family"],
            "herb_type": info["type"],
            "herb_in_map": True,
        }
    # Tier 2: pass-through using cleaned best-available named field
    #   Priority: latin > common > active_compound (most specific first)
    for field in ["herb_name_latin", "herb_common_name",
                  "herb_active_compound"]:
        cleaned = clean_for_passthrough(row.get(field))
        if cleaned:
            return {
                "herb_canonical_latin": cleaned,
                "herb_canonical_english": None,
                "herb_canonical_pinyin": None,
                "herb_family": None,
                "herb_type": "unmapped",
                "herb_in_map": False,
            }
    # Tier 3: no herb info at all
    return {
        "herb_canonical_latin": None,
        "herb_canonical_english": None,
        "herb_canonical_pinyin": None,
        "herb_family": None,
        "herb_type": None,
        "herb_in_map": False,
    }


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
    print(f"{'='*72}\n  Day 9 T2: Herb normalization (Day 9 capstone)\n{'='*72}")
    print(f"  Input/Output: {path.relative_to(REPO)} ({n:,} rows)")
    print(f"  Herb entries in map: {len(HERB_ENTRIES)}")
    print(f"  Total aliases: {len(HERB_ALIAS_MAP):,}")

    norm_results = df.apply(normalize_herb_row, axis=1)
    df_norm = pd.DataFrame(list(norm_results))
    for col in df_norm.columns:
        df[col] = df_norm[col].values

    df.to_parquet(path, index=False)

    # ---- Summary ----
    n_named = (df["herb_common_name"].notna() |
               df["herb_name_latin"].notna() |
               df["herb_active_compound"].notna()).sum()
    n_any_canonical = df["herb_canonical_latin"].notna().sum()
    n_in_map = df["herb_in_map"].sum()
    n_passthrough = n_any_canonical - n_in_map

    print(f"\n  Coverage (3-tier):")
    print(f"    Records with named herb:                 {n_named:,} "
          f"({n_named/n*100:.1f}%)")
    print(f"    Tier 1 — mapped to canonical (in HGNC):  {n_in_map:,} "
          f"({n_in_map/n*100:.1f}%, {n_in_map/n_named*100:.1f}% of named)")
    print(f"    Tier 2 — pass-through cleaned text:      {n_passthrough:,} "
          f"({n_passthrough/n*100:.1f}%)")
    print(f"    Tier 1+2 — total with herb_canonical_id: {n_any_canonical:,} "
          f"({n_any_canonical/n*100:.1f}%, "
          f"{n_any_canonical/n_named*100:.1f}% of named)")
    print(f"    Tier 3 — no herb info at all:            {n-n_any_canonical:,} "
          f"({(n-n_any_canonical)/n*100:.1f}%)")

    print(f"\n  herb_type distribution:")
    for t, cnt in df["herb_type"].value_counts(dropna=False).items():
        pct = cnt / n * 100
        marker = " ⭐" if t == "unmapped" else ""
        print(f"    {(t or '(null)'):20s} {cnt:>5,} ({pct:>5.1f}%){marker}")

    print(f"\n  herb_family distribution (top 20, mapped only):")
    fam_counts = df[df["herb_in_map"]]["herb_family"].value_counts().head(20)
    for fam, cnt in fam_counts.items():
        print(f"    {fam:30s} {cnt:>5,}")

    print(f"\n  Top 30 canonical herbs (mapped only):")
    mapped_top = (
        df[df["herb_in_map"]]["herb_canonical_latin"]
        .value_counts().head(30)
    )
    for h, cnt in mapped_top.items():
        info = HERB_INFO_MAP[h]
        pinyin = f" / {info['pinyin']}" if info['pinyin'] else ""
        print(f"    {h:35s} {cnt:>5,}   [{info['english']}{pinyin}]")

    # Pass-through top 25 (these are network nodes but unmapped)
    if n_passthrough > 0:
        pass_top = (
            df[df["herb_type"] == "unmapped"]["herb_canonical_latin"]
            .value_counts().head(25)
        )
        print(f"\n  Top 25 pass-through (unmapped) canonical herbs:")
        print(f"    (these are still network nodes; just lack family metadata)")
        for h, cnt in pass_top.items():
            print(f"    {h[:50]:50s} {cnt:>4,}")

    # Notable merges
    print(f"\n  Notable merges (canonical → counts):")
    merge_check = [
        "Hypericum perforatum",
        "Salvia miltiorrhiza",
        "Curcuma longa",
        "Coptis chinensis",
        "Camellia sinensis",
        "Panax ginseng",
        "Glycyrrhiza uralensis",
        "Schisandra chinensis",
        "Epimedium brevicornum",  # icaritin patch
        "Sophora flavescens",  # kushen + matrine v2 patch
    ]
    for canon in merge_check:
        n_canon = (df["herb_canonical_latin"] == canon).sum()
        if n_canon > 0 and canon in HERB_INFO_MAP:
            info = HERB_INFO_MAP[canon]
            print(f"    {canon:30s} → {n_canon:>4,}  [{info['english']}]")

    print(f"\n  ✓ T2 DONE. Day 9 entity normalization complete!")
    print(f"  Output parquet now contains these normalized columns:")
    print(f"    target_canonical, target_family, target_list, target_n")
    print(f"    drug_canonical, drug_class")
    print(f"    drug_known, target_known, mech_specific, interaction_class")
    print(f"    herb_canonical_latin, herb_canonical_english,")
    print(f"    herb_canonical_pinyin, herb_family, herb_type, herb_in_map")
    print(f"\n  For Day 10 network analysis:")
    print(f"    - Mapped herbs (herb_in_map=True): full family/type metadata")
    print(f"    - Pass-through herbs (herb_type='unmapped'): herb_canonical_latin")
    print(f"      contains cleaned original text; usable as network node id")


if __name__ == "__main__":
    main()
