# Day 3 Block 1-2: Discussion-ready Methods + Results Drafts

> Direct-quotable text generated from analysis outputs.

## Methods §2.3 — Annual trend analysis

Annual publication counts for 2005-2025 were derived from the integrated corpus 
(N=9,438). Compound annual growth rate (CAGR) was computed for the full period 
and four sub-periods. A 5-year centered moving average was applied to smooth 
short-term fluctuations. Year-over-year growth was used to identify acceleration 
years (>=20% YoY increase). Partial-year 2026 data (N=316 through mid-May) were 
retained separately for forecast purposes.

## Methods §2.4 — Country attribution and collaboration

Country-level information was extracted via a priority chain: OpenAlex's structured 
institution metadata (ISO 3166-1 alpha-2 country codes), followed by free-text 
affiliation parsing of Web of Science C1 and Scopus Affiliations fields using a 
curated 200-entry country alias dictionary, with corresponding author addresses as 
fallback. Country labels follow World Health Organization and United Nations 
conventions: the Chinese mainland, Hong Kong Special Administrative Region 
(Hong Kong, China), the Macao Special Administrative Region (Macao, China), and 
Taiwan, China are presented as distinct analytical units to reflect their 
respective research ecosystems and collaboration patterns, while collectively 
representing China. This disaggregation enables visibility of region-specific 
scholarly contributions without implying any political or sovereign distinction.

Country attribution was successful for 7,976 records (84.5%); remaining records—
predominantly PubMed-indexed publications lacking structured affiliation metadata—
were excluded from country-level analyses but retained for all other analyses.

International collaboration was defined as publications with author affiliations 
from two or more countries (Multiple Country Publications, MCP). Bilateral 
collaboration pairs were enumerated for all country pairs co-occurring on a single 
publication. Country collaboration networks were visualized using VOSviewer 1.6.20 
(van Eck & Waltman, 2010) with Association Strength normalization, VOS layout, 
and modularity-based clustering at resolution 0.50. Visualization included 
countries with >=10 publications and collaboration pairs with >=3 co-publications.

## Results §3.1 — Annual publication trend

Between 2005 and 2025, 9,413 publications on TCM herb-drug interactions were 
identified across four major bibliographic databases. The corpus exhibited a 
non-linear growth pattern characterized by four distinct phases: an early phase 
(2005-2010, CAGR 5.4%) establishing methodological foundations; a growth phase 
(2011-2017, CAGR 3.7%) with annual output rising from approximately 350 to 450 
publications; a plateau phase (2018-2023, CAGR 0.2%) during which annual output 
stabilized around 530 publications; and a recent acceleration phase (2024-2025, 
CAGR 16.6%) marked by a 34.2% year-over-year surge in 2024.

The apparent dip in 2023 (n=471) likely reflects PubMed's MeSH indexing lag for 
recent publications rather than a genuine decline; the WoS, Scopus, and OpenAlex 
databases—not subject to controlled-vocabulary indexing delays—collectively 
confirm sustained year-on-year growth from 2021 onwards.

The overall 21-year compound annual growth rate of 5.3% reflects steady, 
methodologically diverse scholarship. Partial-year data for 2026 (n=316 through 
mid-May) project approximately 842 publications for the full year, indicating 
TCM-HDI research has entered a sustained acceleration trajectory likely driven 
by the 2017 Law of the People's Republic of China on Traditional Chinese 
Medicine and concurrent rise of computational drug-interaction prediction 
methodologies.

## Results §3.2 — Geographic distribution

Geographic analysis of the 7,976 records with extractable affiliation data 
revealed a strongly Asia-Pacific-centered research landscape. Chinese Mainland 
(n=4,313, 54.1%) dominated the field, followed by the United States 
(n=1,094, 13.7%) and India (n=534, 6.7%). When the Chinese mainland and the 
Special Administrative Regions of Hong Kong (n=256), Macao (n=117), and 
Taiwan, China (n=208) were aggregated, collective contributions reached 4,894 
publications (61.4%), underscoring China's centrality in TCM-HDI research.

Notably, the Chinese mainland's multi-country publication (MCP) rate of 17.5% 
stood in stark contrast to those of the Special Administrative Regions and 
Taiwan, China (Hong Kong, China: 67.6%; Macao, China: 88.9%; Taiwan, China: 
51.0%), reflecting divergent collaboration models. India (19.1%) and South 
Korea (20.2%) exhibited similarly self-contained patterns, whereas Western 
contributors—the United Kingdom (67.9%), Australia (60.4%), and Germany 
(47.3%)—showed higher MCP rates consistent with global collaboration norms.

Citation impact diverged from publication volume: while the Chinese mainland 
averaged 25.9 citations per paper, European contributors achieved markedly 
higher averages—Italy (86.9), Spain (81.4), Switzerland (68.6), and Germany 
(59.2)—reflecting selectivity in journal targeting and quality-over-quantity 
publishing strategies.

## Results §3.3 — International collaboration network

Of the 7,976 country-attributed publications, 1,457 (18.3%) involved 
international collaboration, spanning 1,012 unique bilateral partnerships with 
a mean of 2.34 countries per multi-country publication. The Chinese 
Mainland-United States partnership (n=257) was the largest bilateral 
collaboration, followed by partnerships within Greater China (Chinese 
Mainland-Hong Kong: n=129; Chinese Mainland-Macao: n=92; Chinese 
Mainland-Taiwan: n=81) and Australia-Chinese Mainland (n=58).

VOSviewer modularity-based clustering at resolution 0.50 identified six 
functional collaboration communities (Figure 4a): (1) a Chinese-centered hub 
including Chinese Mainland, Hong Kong (China), Macao (China), Mongolia, France, 
and Norway; (2) a South Asian-Middle Eastern community led by India and 
including Saudi Arabia, Pakistan, Egypt, UAE, Iraq, Indonesia, Malaysia, 
Thailand, and Japan; (3) a US-centered international community including 
Israel, South Africa, Zimbabwe, and Russia; (4) a European core community 
including the United Kingdom, Germany, Italy, Spain, and surrounding 
Mediterranean-Iranian countries; (5) a Commonwealth bridge community 
including Australia, Canada, Singapore, and New Zealand; (6) an East Asian 
Sinographic community including South Korea, Taiwan (China), and Vietnam.

Density visualization (Figure 4b) confirmed the extreme research concentration: 
three hot-spots (Chinese Mainland, United States, India) accounted for 74.5% 
of country-attributed publications, while the remaining 25.5% were distributed 
across 60+ countries.
