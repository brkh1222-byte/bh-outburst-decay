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

The last uniform tests of this used RXTE-era outbursts up to about 2011:
- Yan & Yu (2015) found *no* clear decay-time vs period trend below 40 days.
- Saraswati et al. (2025) covered nine dynamically confirmed black holes, with only one post-2016 outburst.

Since 2016, MAXI and Swift/BAT have caught about 25–35 new black hole outbursts, including well-measured systems such as MAXI J1820+070 and Swift J1727.8−1613. This project builds a **uniform set of rise and decay timescales, light-curve shapes and Eddington-scaled peaks** for 2016–2026 outbursts. It then tests the decay-time vs orbital-period relation with the combined old and new sample.

## 2. Background

- **Outburst light curves:** a fast rise, then a decay that is exponential or linear. Irradiation by central X-rays keeps the disc hot and sets an exponential decay whose e-folding time scales with the disc's outer radius. When the irradiated region shrinks, the decay turns linear (King & Ritter 1998; Tetarenko et al. 2018, *Nature*, used decays to measure disc viscosity α ≈ 0.2–1).
- **State transitions:** outbursts move through hard and soft X-ray states. The soft-to-hard transition happens at about 1–2% of the Eddington luminosity (Maccarone 2003; Vahdat Motlagh et al. 2019).
- **Failed outbursts:** about one third never reach the soft state (Alabarta et al. 2021).

## 3. Prior work and the gap

| Work | Sample | What it measured | Gap |
|---|---|---|---|
| Yan & Yu 2015 (arXiv:1408.5146) | 110 RXTE/ASM outbursts, 36 transients | Rise/decay times vs P_orb; decay–P trend not found below 40 d | Pre-2012 |
| WATCHDOG, Tetarenko et al. 2016, ApJS 222, 15 | 132 outbursts | Peak L vs P_orb (successful outbursts) | Ends about 2015 |
| Tetarenko et al. 2018, *Nature* (arXiv:1801.07203) | 21 decays | Disc viscosity α | Pre-2016 |
| Alabarta et al. 2021, MNRAS 507, 5507 | 128 outbursts | Failed-transition fraction | — |
| Saraswati et al. 2025, MNRAS 537, 1146 | 9 dynamical black holes, RXTE + MAXI to 2024 | 10/50/90% rise and decay, shapes, peak L, energy vs P_orb | Dynamical black holes only; just one post-2016 outburst (MAXI J1820) |
| Maheshwari et al. 2026, JApA (arXiv:2602.20988) | 42 LMXBs, MAXI + BAT 13 years | Hardness distributions, state durations, outburst durations | **No decay timescales or peak luminosities** |

**Gap:** No uniform rise and decay timescales or Eddington-scaled peaks exist for the 2016–2026 black hole and black hole candidate outbursts. The decay–orbital-period relation has not been retested with them.

> **Task T1.1 (novelty gate):** Before starting, do a final ADS/arXiv search for "black hole transient outburst decay timescale 2016–2026 MAXI sample".

## 4. Hypotheses

- **H1 (main):** The e-folding decay time τ_d increases with orbital period for P_orb ≲ 1 day and saturates near ~40 days for longer periods (King & Ritter 1998), in the combined sample: Yan & Yu 2015 + Saraswati 2025 + new outbursts.
- **H2:** The decay time is independent of peak luminosity at fixed P_orb.
- **H3 (secondary, needs distances and masses):** For sources with distance and mass estimates, the soft-to-hard transition clusters at L/L_Edd ≈ 1–2%.

## 5. Data and sample

**Light curves (public, tested Nov 2026):**
- **MAXI/GSC:** per-source files `http://maxi.riken.jp/star_data/<ID>/<ID>_g_lc_1day_all.dat`. Columns: MJD, 2–20, 2–4, 4–10 and 10–20 keV rates with errors. On-demand tool: `http://maxi.riken.jp/mxondem/`.
- **Swift/BAT Transient Monitor (15–50 keV):** `https://swift.gsfc.nasa.gov/results/transients/weak/<NAME>.lc.txt`.
- System parameters from **BlackCAT** (Corral-Santana et al. 2016, updated online) and the literature.

**Core sample: outbursts with known P_orb (tests H1):**

| Source | Outburst(s) | P_orb | Notes |
|---|---|---|---|
| MAXI J1820+070 | 2018 (+2019–20) | 0.6855 d | d = 2.96 ± 0.33 kpc (radio parallax); M ≈ 8–9 M☉ |
| Swift J1727.8−1613 | 2023–24 | 10.80 h | d = 3.4 ± 0.3 kpc; M > 3.12 M☉ |
| 4U 1543−47 | 2021 | 26.8 h | d ≈ 7.5 kpc |
| GX 339−4 | 2017–2023 (several) | 1.76 d | distance uncertain |
| Swift J1357.2−0933 | 2017, 2019 | 2.8 h | |
| GRS 1716−249 | 2016–17 | ~0.28 d | d ≈ 2.4 kpc |
| MAXI J1803−298 | 2021 | ~0.29 d (dips) | |

**Extended sample (timescales, peaks):** MAXI J1348−630, MAXI J1535−571, H1743−322, 4U 1630−472, IGR J17091−3624, MAXI J1631−479, MAXI J0637−430, MAXI J1727−203, MAXI J1813−095, Swift J1658.2−4242, MAXI J1810−222, EXO 1846−031, AT2019wey, Swift J151857.0−572147, MAXI J1744−294 (Galactic Centre confusion risk).

**Expected:** about 25–35 outbursts, 8–10 with P_orb. Verify every parameter against BlackCAT and the original papers.

## 6. Method

Python: numpy, scipy, lmfit/emcee, astropy.
1. **Outburst windows:** define the start and end of each outburst from MAXI 2–20 keV (and BAT) above a threshold over the quiescent level.
2. **Timescales:**
   - fit the rise and decay with exponential, linear and broken exponential-to-linear models (as in Tetarenko 2018);
   - also compute model-free 10/50/90% rise and decay times (the Yan & Yu / Saraswati method), for direct comparability with the older samples.
3. **Peaks:** convert MAXI counts to flux (Crab-normalised), then to luminosity with distance, then to L/L_Edd with mass. Propagate uncertainties by Monte Carlo.
4. **Hardness:** hardness ratio (4–10)/(2–4) keV; identify the soft-to-hard transition time and luminosity (H3).
5. **Combined analysis:**
   - merge with the Yan & Yu 2015 and Saraswati 2025 tabulated values (check the method is consistent by refitting overlap systems, e.g. GX 339−4);
   - fit τ_d vs P_orb with the King & Ritter-like form and with a constant;
   - compare models (AIC/BIC); Kendall's τ correlation.

## 7. Timeline

| Week | Tasks |
|---|---|
| 1 | Novelty gate; build the outburst list and system-parameter table; download MAXI and BAT light curves |
| 2 | Outburst windows, timescale fits, QC plots for each outburst |
| 3 | Peaks, hardness, combined τ_d–P_orb analysis, figures |
| 4 | Write-up, mentor review, submission |

## 8. Venue

- **RNAAS** for a short note on H1 only.
- **MNRAS / ApJ** for the full uniform table plus H1–H3, with the mentor as co-author.
- **JEI** as the student alternative.
- arXiv (mentor endorsement).

## 9. Where the mentor helps most

Disc-instability physics and the interpretation of τ_d; choosing defensible masses and distances; the Eddington scaling; how the H1 test is framed.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Few systems with P_orb (small N for H1) | Combine with the literature samples; report as an update, not a definitive test |
| MAXI gaps (solar constraints, ISS) | Use BAT to fill; flag poorly sampled decays |
| Source confusion near the Galactic Centre | Exclude or flag (MAXI PSF ~1.5°) |
| Black hole vs neutron star ambiguity | Separate "confirmed" and "candidate" in the analysis |
| Maheshwari or Saraswati groups extend their work | Move quickly; cite them clearly |

## 11. Key references

- King, A. R. & Ritter, H. (1998). MNRAS 293, L42
- Yan, Z. & Yu, W. (2015). ApJ 805, 87. arXiv:1408.5146
- Tetarenko, B. E. et al. (2016). WATCHDOG. ApJS 222, 15
- Tetarenko, B. E. et al. (2018). *Nature* 554, 69. arXiv:1801.07203
- Alabarta, K. et al. (2021). MNRAS 507, 5507. arXiv:2107.10035
- Vahdat Motlagh, A., Kalemci, E. & Maccarone, T. J. (2019). MNRAS 485, 2744. arXiv:1903.00837
- Saraswati, Vierdayanti & Premadi (2025). MNRAS 537, 1146. doi:10.1093/mnras/staf042
- Maheshwari, Pahari, Sarkar & Sharma (2026). JApA. arXiv:2602.20988
- Corral-Santana, J. M. et al. (2016). BlackCAT. A&A 587, A61
- Matsuoka, M. et al. (2009). MAXI. PASJ 61, 999
- Krimm, H. A. et al. (2013). Swift/BAT Transient Monitor. ApJS 209, 14

> ⚠️ These references were compiled by an AI research assistant. Verify every citation and every system parameter against the source before using it.
