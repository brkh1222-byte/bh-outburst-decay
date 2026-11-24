# T1.1 Novelty search

Date: 2026-11-25. Done by the AI pilot agent with one helper agent, through public web APIs.
**This is not the by-hand ADS search that the task asks for:** NASA ADS could not be queried
(the web pages need JavaScript and the API needs a personal token). See "Limits".

## Question

Has any paper already
(i) measured uniform rise/decay timescales for the 2016+ black hole transient outbursts (MAXI, Swift/BAT), or
(ii) formally tested whether the outburst decay e-folding time depends on orbital period, using post-2016 outbursts?

## Verdict

- **No paper found that does (i) for the full 2016+ black hole and candidate population, or (ii) with post-2016 outbursts.**
- The test itself is **not new**: Yan & Yu (2015) already tested decay time against orbital period for
  1996–2011 RXTE/ASM outbursts (Spearman coefficients; no correlation for decay, positive for rise).
  The paper must present this work as a re-test and extension, with errors, intrinsic scatter, model
  comparison and a power estimate, not as the first test. (The draft already does this.)
- Saraswati et al. (2025) overlap partly with (i): two-point timescales for 15 outbursts and 18
  mini-outbursts of nine dynamical black holes, a few after 2016; their decay–period statement is
  qualitative (no coefficient, p-value or fit, as far as could be read; see Limits).
- The gate is passed, subject to the limits below. No reason to stop.

## Closest papers

| Paper | What it does | Overlap |
|---|---|---|
| Yan & Yu 2015, ApJ 805, 87 | 110 RXTE/ASM outbursts of 36 LMXB transients (BH + NS), 1996–2011; two-point e-folding rise/decay times; decay vs P_orb: no correlation, also below 40 d; rise vs P_orb: Spearman 0.51, 0.63, 0.29 | Does (ii) for the RXTE era |
| Saraswati, Vierdayanti & Premadi 2025, MNRAS 537, 1146 | 15 outbursts + 18 mini-outbursts, 9 dynamical BHs, RXTE + MAXI, 1996–2024; same timescales; says decay time "increased with the orbital period", no saturation | Partial (i); (ii) qualitative only |
| Maheshwari et al. 2026, JApA 47, 34 (arXiv:2602.20988) | 42 LMXBs, ~13 yr of MAXI + BAT; hardness and outburst durations; no "e-folding", "decay time", "orbital period" in the text | Same data, different measurements |
| Tetarenko et al. 2018, Nature 554, 69; MNRAS 480, 2 | Bayesian decay-profile fits of 21 BH outbursts to get viscosity α and irradiation | Background (decay fits, pre-2016) |
| Xu et al. 2026, arXiv:2607.05249 (submitted to ApJ) | RXTE/PCA, 26 BH binaries; disc luminosity decays exponentially in the soft state in 24 outbursts, then falls below the extrapolation (receding disc); no orbital-period test in the abstract (abstract read 2026-11-25) | Background; relevant to decay shapes |
| Lin, Yan, Han & Yu 2019, ApJ 870, 126 | Outburst rate vs orbital period | Background |
| Alabarta et al. 2021, MNRAS 507, 5507 | 128 outbursts of 56 BH LMXBs; failed-transition fraction | Background |
| Heinke et al. 2025, ApJS 279, 57 | Outburst catalogue of 87 neutron-star LMXBs; recurrence | Background |

Other titles scanned and judged unrelated to the question: Bhattacharya & Bhattacharyya 2025
(arXiv:2504.07621, NS outburst durations); Abdulghani et al. 2024 (distances); Saraswati et al. 2026
(GRS 1915+105); reviews by Marcel et al. 2026, Blaes et al. 2025, Hameury 2025 (arXiv:2512.21188).
These were not verified beyond title/abstract by the pilot; do not cite them without opening them.

## What was searched

Citing-paper lists (number returned):

| Target | OpenAlex | Semantic Scholar | INSPIRE | ADS |
|---|---|---|---|---|
| Yan & Yu 2015 | 87 | 42 | 75 | failed |
| Saraswati et al. 2025 | 2 | 1 | not indexed | failed |
| Maheshwari et al. 2026 | 0 | 0 | 0 | failed |
| Tetarenko et al. 2018 (Nature), 2024–2026 only | 37 | – | – | failed |

Also: 2020–2026 OpenAlex citers of Tetarenko et al. 2018 (MNRAS; 33), Lin et al. 2019 (15) and
WATCHDOG (312; first 200 by title). All lists were scanned by title. The two papers citing
Saraswati et al. 2025 (Jaisawal et al. 2026 on EP250916a; Saraswati et al. 2026) are not relevant.

Keyword searches: 15 arXiv API queries (outburst + decay + "orbital period" + black hole;
"e-folding" + X-ray binaries/outburst; disc instability + decay + orbital period; outburst light
curves + MAXI + catalogue/population; rise time + orbital period + LMXB; "decay timescale" + outburst;
King + Ritter + outburst; irradiated disc + outburst + decay), 4 OpenAlex full-text queries
(2023–2026, top 25 of each), 6 web searches.

## Limits

- **ADS was not searched.** It is the most complete index for astronomy. The researcher should
  repeat steps 1–2 on ADS by hand before submission (two clicks: "Citations" on
  2015ApJ...805...87Y and on 2025MNRAS.537.1146S). T1.1 stays open until then.
- arXiv searches cover titles and abstracts only. A decay–period test inside a paper body (as in
  Yan & Yu, where it is not in the abstract) would be missed.
- Semantic Scholar keyword search failed (rate limit); only its citation lists worked.
- The Saraswati et al. full text was read through a summarising tool, not directly; "no statistic
  for decay vs period" should be confirmed against the PDF.
- Not checked: conference proceedings, theses, citers of King & Ritter 1998, Chen, Shrader & Livio
  1997 and Shahbaz, Charles & King 1998.
