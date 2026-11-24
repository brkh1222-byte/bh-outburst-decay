# Research Proposal

## Does Disc Size Set the Decay? Outburst Timescales of Black Hole X-ray Transients in the MAXI Era (2016–2026)

**Author:** Berkh (independent student researcher)
**Mentor / prospective co-author:** [mentor name] (cosmology & black holes)
**Field:** High-energy astrophysics / accretion onto stellar-mass black holes
**Planned duration:** 3–4 weeks
**Status:** Proposal, Nov 2026

---

## 1. Summary

Black hole low-mass X-ray binaries (LMXBs) are black holes that pull gas from a companion star into an accretion disc. Most of the time they are faint. Every few years the disc becomes unstable and the system flares in X-rays for weeks to months (an "outburst"). The **disc instability model with X-ray irradiation** (King & Ritter 1998) predicts that the **exponential decay timescale depends on disc size**, and so on the **orbital period**, with longer periods giving bigger discs and slower decays. The decay time is expected to saturate at about 40 days for longer orbits.

Two uniform studies have tested this, and they disagree:
- Yan & Yu (2015), using 110 RXTE/ASM outbursts (1996–2011, black holes and neutron stars), found *no* decay-time vs period correlation, even below 40 days. They did find that the *rise* time grows with period (Spearman 0.51–0.63).
- Saraswati et al. (2025), using nine dynamically confirmed black holes (RXTE/ASM + MAXI 2–12 keV, 1996–2024, including about 14 events from 2016 on), state that the decay time "increased with the orbital period" and saw no saturation, but give no statistic, and their own table has strong outliers (e.g. XTE J1118+480: P = 4.07 h, τ_d ≈ 142 d).

Since 2016, MAXI and Swift/BAT have caught about 25–35 new black hole outbursts, including well-measured systems such as MAXI J1820+070 and Swift J1727.8−1613. This project builds a **uniform set of rise and decay timescales, light-curve shapes and Eddington-scaled peaks** for 2016–2026 outbursts, including black hole candidates and newly confirmed systems (Swift J1727.8−1613, GRS 1716−249) that Saraswati et al. did not use. It then runs the first formal statistical test (regression with intrinsic scatter, model comparison, power check) of the decay-time vs orbital-period relation on the combined old and new sample.

## 2. Background

- **Outburst light curves:** a fast rise, then a decay that is exponential or linear. Irradiation by central X-rays keeps the disc hot and sets an exponential decay whose e-folding time scales with the disc's outer radius. When the X-rays can no longer ionize the disc out to its edge, the decay turns linear (King & Ritter 1998; Shahbaz, Charles & King 1998). Tetarenko et al. (2018, *Nature*) used decays to measure disc viscosity α ≈ 0.2–1.
- **State transitions:** outbursts move through hard and soft X-ray states. The soft-to-hard transition happens at about 2% of the Eddington luminosity, range ~1–4% (Maccarone 2003; Vahdat Motlagh et al. 2019).
- **Failed outbursts:** about one third never reach the soft state (Alabarta et al. 2021).

## 3. Prior work and the gap

| Work | Sample | What it measured | Gap |
|---|---|---|---|
| Yan & Yu 2015, ApJ 805, 87 (arXiv:1408.5146) | 110 RXTE/ASM outbursts, 36 transients (BH + NS), 1996–2011 | Two-point e-folding rise/decay times vs P_orb; no decay–P correlation (even below 40 d); rise–P correlation found | Pre-2012 |
| WATCHDOG, Tetarenko et al. 2016, ApJS 222, 15 | 132 outbursts, 1996–2015 | Peak L vs P_orb (their §5.2) | Ends 2015 |
| Tetarenko et al. 2018, *Nature* 554, 69 | 21 decays | Disc viscosity α ≈ 0.2–1 (winds) | Pre-2016 |
| Alabarta et al. 2021, MNRAS 507, 5507 | 128 outbursts, 56 BH LMXBs | ~33% failed-transition outbursts | — |
| Saraswati et al. 2025, MNRAS 537, 1146 (no arXiv version) | 15 outbursts + 18 mini-outbursts, 9 dynamical BHs, ASM + MAXI 2–12 keV, 1996–2024 (~14 events from 2016 on) | Same two-point timescales; light-curve shapes; "decay increased with P_orb" stated qualitatively, no saturation | Dynamical BHs only; no candidates; no BAT; no Swift J1727.8−1613 or GRS 1716−249; **no statistical test** |
| Maheshwari et al. 2026, JApA 47, 34 | 42 LMXBs, MAXI + BAT, ~13 years | Hardness, state and outburst durations | **No decay timescales, no P_orb test** |

**Gap:** No uniform decay timescales or Eddington-scaled peaks exist for the 2016–2026 black hole *and candidate* outbursts, and the decay–orbital-period relation has never been tested statistically (with uncertainties, intrinsic scatter and a power check) on a merged old + new sample.

> **Task T1.1 (novelty gate):** an AI-assisted search (Nov 2026, OpenAlex/Semantic Scholar citation lists of Yan & Yu 2015 and Saraswati 2025) found no paper doing this. Repeat the search on ADS by hand before submission.

## 4. Hypotheses

| # | Hypothesis | Role |
|---|---|---|
| H1 | τ_d,10–90 increases with P_orb: slope B > 0 in log τ_d = A + B log(P_orb/1 d), one point per source, merged sample | Primary, confirmatory |
| H1b | The increase levels off above P_orb ≈ 1 d near ~40 d (King & Ritter 1998) | Confirmatory, expected weak |
| H2 | τ_rise,10–90 increases with P_orb (replicates Yan & Yu) | Exploratory |
| H3 | At short P_orb, τ_d does not depend on peak L/L_Edd; at long P_orb it increases with it (irradiated radius R_h grows with L) | Exploratory; check the physics with the mentor |
| H4 | The soft-to-hard transition happens at ~2% L_Edd (≈1–4%) | Exploratory; needs d and M |

Fixed in advance: primary measure τ_d,10–90; primary sample all outbursts peaking above 0.1 Crab (Yan & Yu cut), failed outbursts included, aggregated to one median per source. Everything else is a robustness check.

## 5. Data and sample

**Light curves (public, tested 22 Nov 2026):**
- **MAXI/GSC:** `http://maxi.riken.jp/star_data/<ID>/<ID>_g_lc_1day_all.dat` (9 columns, no header: MJD, then rate and error in 2–20, 2–4, 4–10, 10–20 keV, ph/cm²/s). 1 Crab = 3.8 (2–20), 2.2 (2–4), 1.25 (4–10), 0.40 (10–20) ph/cm²/s (MAXI readme, versions v7.7L/v7Lrkn/v6m). Primary band here: 2–10 keV = (2–4) + (4–10), 1 Crab = 3.45 ph/cm²/s. The 2–12 keV band used by Saraswati et al. needs the interactive on-demand tool (`http://maxi.riken.jp/mxondem/`) and is a robustness check.
- **Swift/BAT Transient Monitor (15–50 keV):** `https://swift.gsfc.nasa.gov/results/transients/weak/<NAME>.lc.txt` ("+" written as "p"); 1 Crab = 0.220 count/cm²/s; use DATA_FLAG = 0; mask 10–20 Sep 2019 (no data) and 29–30 Mar 2019 (bad zeros).
- System parameters from **BlackCAT** (Corral-Santana et al. 2016; online page updated Sep 2025), always checked against the original paper.

**Core sample: outbursts with independently measured P_orb (tests H1):**

| Source | Outburst(s) | P_orb (method) | d | M | Refs |
|---|---|---|---|---|---|
| MAXI J1820+070 | 2018 (+ rebrightenings 2019–20) | 0.68549 ± 0.00001 d (spectroscopy) | 2.96 ± 0.33 kpc (radio parallax) | 8.48 (+0.79/−0.72) M☉ (jet inclination) | Torres+2019, 2020; Atri+2020 |
| Swift J1727.8−1613 | 2023–24 | 10.8038 ± 0.0010 h (spectroscopy) | 3.4 ± 0.3 kpc; 5.5 (+1.4/−1.1) kpc in Burridge+2025 → carry 3.4–5.5 | > 3.12 M☉ | Mata Sánchez+2025; Burridge+2025 |
| 4U 1543−47 | 2021 | 26.794 h (spectroscopy) | 7.5 ± 0.5 kpc | 9.4 ± 1.0 M☉ | Orosz+1998; Orosz 2003; BlackCAT |
| GX 339−4 | 2017–2023 (several; some hard-only) | 1.76 d (spectroscopy) | uncertain, ~5–9 kpc | 2.3–9.5 M☉ | Heida+2017 |
| Swift J1357.2−0933 | 2017, 2019 | 2.8 ± 0.3 h (Hα modulation) | > 2.29 kpc | > 9.3 M☉ | Corral-Santana+2013; Mata Sánchez+2015 |
| GRS 1716−249 | 2016–17 | 0.278 ± 0.008 d (photometry only) | 6.9 ± 1.1 kpc | 6.4 (+3.2/−2.0) M☉ | Casares+2023 |
| MAXI J1803−298 | 2021 | 7.02 ± 0.18 h (X-ray dips; candidate) | — | ~3–10 M☉ (Hα width) | Jana+2022; Mata Sánchez+2022 |
| GS 1354−64 | 2025–26 (MAXI detection 25 Dec 2025, ATel #17563) | 61.068 ± 0.002 h (spectroscopy) | ~25 kpc, very uncertain | — | Casares+2009 |
| Swift J1753.5−0127 | 2023–24? (to verify) | 3.26 ± 0.02 h | 3.9 ± 0.7 kpc | 8.8 ± 1.3 M☉ | Yanes-Rizo+2025 (to open) |

**Excluded from the τ–P test:** MAXI J0637−430 (its 2.2 h period is inferred *from its own decay*, Soria+2022 — circular); IGR J17091−3624 (2.83 d dip period unconfirmed).

**Extended sample (timescales, peaks):** MAXI J1348−630, MAXI J1535−571, H1743−322, 4U 1630−472, IGR J17091−3624, MAXI J1631−479, MAXI J0637−430, MAXI J1727−203, MAXI J1813−095, Swift J1658.2−4242, MAXI J1810−222, EXO 1846−031, AT2019wey, Swift J151857.0−572147, MAXI J1744−294 (Galactic Centre confusion risk).

**Expected:** about 25–35 outbursts, 8–10 with independent P_orb.

## 6. Method

Python: numpy, scipy, pandas, astropy, lmfit, emcee.

1. **Outburst windows:** automatic start/peak/end from MAXI 2–10 keV (and BAT) above a threshold over the quiescent level, with a manual-override file.
2. **Timescales (Yan & Yu 2015; Saraswati et al. 2025 definition):** two-point e-folding times τ = Δt / ln A between the 10%, 50% and 90% of the daily peak flux, for rise and decay (A = 9, 5, 1.8). Primary: the Yan & Yu-exact version (nearest data point to each level). Upgrade: crossing times interpolated on a lightly smoothed curve, errors by Monte Carlo resampling. The ratio τ_50–90 / τ_10–50 is a shape diagnostic (1 for exponential, ≈2.7 for linear).
3. **Model fits (secondary):** exponential, linear and exponential→linear decay fits (lmfit, then emcee).
4. **Peaks:** Crab-normalised peak → flux → bolometric correction → L = 4πd²F → L/L_Edd (L_Edd = 1.26 × 10³⁸ M/M☉ erg/s); Monte Carlo over d, M and the correction.
5. **Hardness:** BAT/MAXI ratio and (4–10)/(2–4) keV (the 2–4 keV band is less well calibrated); soft-to-hard transition time and luminosity (H4).
6. **Validation (gate before the main result):** (a) remeasure Aug 2009–Jan 2012 outbursts seen by both RXTE/ASM and MAXI and compare with Yan & Yu; (b) remeasure post-2011 outbursts in Saraswati et al.; (c) injection–recovery of synthetic exponential and linear decays with MAXI's real cadence and gaps.
7. **Combined analysis:** merge with Yan & Yu (BH entries only) and Saraswati et al., one measurement per outburst; per-source median τ_d; Bayesian regression log τ_d = A + B log P with intrinsic scatter (emcee); models M0 constant / M1 power law / M2 saturating power law compared by AIC, BIC and leave-one-source-out cross-validation; Kendall's τ with a permutation p-value; a power simulation before looking at the result.
8. **Controls:** with and without failed outbursts; dynamical BHs only; new sample alone vs old; 2–20 vs 2–10 keV; smoothed vs Yan & Yu-exact; BAT vs MAXI.
9. **Plan freeze:** the analysis plan is committed and tagged (`analysis-plan-v1`) before the τ_d–P_orb figure is made.

## 7. Timeline

| Week | Tasks |
|---|---|
| 1 | Novelty gate; sample and parameter table; download MAXI and BAT light curves |
| 2 | Outburst windows, timescales, QC plots; **validation gate** (ASM–MAXI overlap, Saraswati overlap, injection–recovery) |
| 3 | Freeze plan; peaks, hardness, combined τ_d–P_orb analysis, figures; Berkh starts writing |
| 4 | Writing, mentor review, submission |

## 8. Venue

- **MNRAS** for the full uniform catalogue plus H1–H4, with the mentor as co-author (Saraswati et al. published there). Check open-access charges with the mentor.
- **RNAAS** as the fallback for a short note on H1 only.
- **JEI** as the student alternative.
- arXiv on submission (mentor endorsement).

## 9. Where the mentor helps most

Disc-instability physics and the interpretation of τ_d (including the H3 period split); choosing defensible masses, distances and a bolometric correction; how the H1 test is framed.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Saraswati et al. already cover part of the new sample | Focus on candidates, short-period systems and the statistical test; the catalogue is new regardless |
| Few systems with P_orb (small N for H1) | Merge with the literature samples; power simulation; report as an update, not a definitive test |
| MAXI vs ASM calibration offset (no published cross-calibration) | Calibrate on the 2009–2012 overlap |
| MAXI gaps (Sun angle, ISS) | Use BAT to fill; injection–recovery; flag poorly sampled decays |
| Source confusion near the Galactic Centre | Exclude or flag (MAXI PSF ~1.5°) |
| Weak or circular periods | P_orb method/quality flag; rerun without weak periods; exclude decay-inferred periods |
| Black hole vs neutron star ambiguity | Separate "dynamical" and "candidate" in the analysis |
| Timeline slip | RNAAS fallback; drop H4 first |
| Another group publishes first | Move quickly; post to arXiv; cite them clearly |

## 11. Key references

- King, A. R. & Ritter, H. (1998). MNRAS 293, L42. doi:10.1046/j.1365-8711.1998.01295.x
- Shahbaz, T., Charles, P. A. & King, A. R. (1998). MNRAS 301, 382. arXiv:astro-ph/9807174
- Lasota, J.-P. (2001). New Astron. Rev. 45, 449. arXiv:astro-ph/0102072
- Hameury, J.-M. (2020). Adv. Space Res. 66, 1004. arXiv:1910.01852
- Yan, Z. & Yu, W. (2015). ApJ 805, 87. doi:10.1088/0004-637X/805/2/87. arXiv:1408.5146
- Tetarenko, B. E., Sivakoff, G. R., Heinke, C. O. & Gladstone, J. C. (2016). WATCHDOG. ApJS 222, 15. arXiv:1512.00778
- Tetarenko, B. E. et al. (2018a). *Nature* 554, 69. doi:10.1038/nature25159. arXiv:1801.07203
- Tetarenko, B. E., Dubus, G., Lasota, J.-P., Heinke, C. O. & Sivakoff, G. R. (2018b). MNRAS 480, 2. arXiv:1807.01360
- Dubus, G. et al. (2019). A&A 632, A40. arXiv:1909.13601
- Alabarta, K. et al. (2021). MNRAS 507, 5507. doi:10.1093/mnras/stab2241. arXiv:2107.10035
- Maccarone, T. J. (2003). A&A 409, 697. arXiv:astro-ph/0308036
- Vahdat Motlagh, A., Kalemci, E. & Maccarone, T. J. (2019). MNRAS 485, 2744. arXiv:1903.00837
- Saraswati, T. A., Vierdayanti, K. & Premadi, P. W. (2025). MNRAS 537, 1146. doi:10.1093/mnras/staf042 (no arXiv version)
- Maheshwari, P., Pahari, M., Sarkar, A. & Sharma, S. (2026). J. Astrophys. Astron. 47, 34. doi:10.1007/s12036-026-10152-5. arXiv:2602.20988
- Corral-Santana, J. M. et al. (2016). BlackCAT. A&A 587, A61. arXiv:1510.08869
- Matsuoka, M. et al. (2009). MAXI. PASJ 61, 999. arXiv:0906.0631
- Krimm, H. A. et al. (2013). Swift/BAT Transient Monitor. ApJS 209, 14. arXiv:1309.0755
- System parameters: Torres et al. 2019 (arXiv:1907.00938), 2020 (arXiv:2003.02360); Atri et al. 2020 (arXiv:1912.04525); Mata Sánchez et al. 2025 (arXiv:2408.13310); Burridge et al. 2025 (arXiv:2502.06448); Heida et al. 2017 (arXiv:1708.04667); Corral-Santana et al. 2013 (arXiv:1303.0034); Casares et al. 2023 (arXiv:2310.11561); Jana et al. 2022 (arXiv:2202.00479); Soria et al. 2022 (arXiv:2207.01631)

> ⚠️ These references were compiled and checked by an AI research assistant (Nov 2026) against arXiv, Crossref and publisher pages. Verify every citation and every system parameter against the source yourself before using it. Full verification notes: the Claude Doc "Does Disc Size Set the Decay? — Research Understanding & Plan".
