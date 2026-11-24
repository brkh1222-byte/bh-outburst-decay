# Results notes (bullets for Berkh to write from — not paper text)

Generated 2026-11-22 from the code in `src/`. Every number below can be regenerated with:
`.venv/bin/python -m src.literature && .venv/bin/python -m src.outbursts --raw && .venv/bin/python -m src.outbursts && .venv/bin/python -m src.catalogue && .venv/bin/python -m src.validate && .venv/bin/python -m src.tau_vs_porb > results/h1_run.log && .venv/bin/python -m src.hierarchical > results/h1_hierarchical.txt && .venv/bin/python -m src.h1_extra > results/h1_extra.log && .venv/bin/python -m src.paper_figures`
(MCMC is seeded since 22 Nov 2026, so reruns give identical numbers.)

## Data product
- Uniform catalogue `results/outburst_table.csv`: 55 MAXI windows in 2016–2026; 40 unflagged; **24 bright (>0.1 Crab, 2–10 keV) main outbursts from 13 sources**.
- Two-point e-folding rise/decay times (Yan & Yu 2015 rule), Monte Carlo errors (300 resamplings), smoothed-crossing variant, BAT 15–50 keV decay times, shape ratio τ_50–90/τ_10–50.

## Method findings (results/method_check.md)
- Injection–recovery into real quiescent MAXI data: no bias (|median| < 0.04 dex) for τ_d = 5–80 d; scatter 0.07–0.10 dex at 0.1 Crab peaks, < 0.04 dex at ≥ 0.3 Crab.
- This work vs Saraswati et al. 2025 (same MAXI outbursts, N = 6): median −0.04 dex, robust scatter 0.03 dex.
- This work vs Yan & Yu 2015 (ASM, same outbursts 2009–10, N = 5): +0.16 dex, scatter 0.19 dex; differences traced to (i) ASM noise at the 10% level for faint outbursts (H1743−322, MAXI J1659−152), (ii) re-flare handling (4U 1630−47).
- Yan & Yu vs Saraswati on the SAME ASM outbursts (N = 9): robust scatter 0.10 dex but outliers up to a factor 4.6 (XTE J1550−564 1998: 19 vs 89 d) → the "same" two-point method is not reproducible between groups for multi-peaked outbursts.
- Baseline subtraction matters near the Galactic Centre (non-zero MAXI floor up to ~0.02 Crab).
- **Source confusion found in Saraswati et al. 2025:** their "GS 1354−64 outburst at MJD 58524 (1.92 Crab)" coincides with MAXI J1348−630's peak (MJD 58523.5), 1.82° away; Swift/BAT shows GS 1354−64 quiet then (median 0.003 Crab). Also MAXI J1631−479's MAXI light curve is dominated by 4U 1630−47 (0.6° away).
- Soft-X-ray (MAXI 2–10 keV / ASM 2–12 keV) brightness cuts miss hard-only outbursts that are bright in BAT (e.g. GX 339−4 2013, 2017–18, 2018, 2022) → failed outbursts are under-represented in all three samples.

## H1: τ_d vs P_orb (primary, plan frozen in results/analysis_plan_v1.md)
- 13 systems with independent P_orb, 26 bright outbursts (13 this work, 13 literature).
- Power check (before the result): 84% power to detect B = 0.5, 39% for B = 0.3 (σ_int = 0.23 dex from the literature-only sample; 200 simulations, ±3%). [First, unseeded run gave 84%/41%.]
- **B = 0.17, 95% interval [−0.17, 0.52]** → H1 not supported; slope consistent with zero.
- Kendall τ = 0.31, permutation p = 0.16.
- Model comparison: M0 (constant) preferred — AIC 4.26 vs 4.91 (M1) vs 5.60 (M2); BIC same order; leave-one-source-out lpd −2.36 (M0) vs −5.67 (M1) vs −6.97 (M2).
- Intrinsic scatter σ_int = 0.24 dex (95%: 0.15–0.41).
- Robustness (results/h1_robustness.csv): every variant consistent with B = 0 — re-flares, faint outbursts, raw MAXI, smoothed crossings, σ_method 0 or 0.3, dynamical only, this-work only, literature only. Largest B_median 0.24 (literature only, wide interval).
- Hierarchical per-outburst model (results/h1_hierarchical.txt): B = 0.23 [−0.09, 0.55]; outburst-to-outburst scatter within a system σ_out ≈ 0.27 dex, between-system scatter σ_src consistent with zero → **each outburst's own conditions dominate, not the orbit** (GX 339−4 alone spans τ_d ≈ 19–110 d).
- Upper limit B < 0.52 (95%). Discuss with mentor: what slope does the irradiated DIM predict? (R_out ∝ P^(2/3); τ ∝ R^(4/5) → B ≈ 0.53; τ ∝ R^(5/4) → B ≈ 0.83.) If confirmed, the simple prediction is disfavoured at ~95%.
- Saraswati et al.'s qualitative "decay increases with P_orb" is not reproduced once (a) a formal test is used, (b) mini-outbursts below 0.1 Crab are treated consistently, (c) the GS 1354−64 confusion event is removed.

## H2 (exploratory): rise time vs P_orb
- 12 systems: B = 0.33, 95% [−0.38, 1.03]; Kendall τ = 0.42, p = 0.06. Hierarchical B = 0.33 [−0.36, 1.03]. Same direction as Yan & Yu's rise–P correlation, not significant here.

## Decay shapes (exploratory)
- Shape ratio τ_50–90/τ_10–50 among the 24 bright 2016–2026 outbursts spans 0.1–13; many < 1 (decay slows down, e.g. 4U 1543−47 2021: 0.21), which neither a pure exponential (1) nor exponential→linear (≥ 1, up to ~2.7) predicts.

## Post-review changes (22 Nov 2026, internal referee; results/h1_extra.json — NOT in the frozen plan)
- Fixed: GS 1354−64 re-flare window MJD 58560 (tail of the MAXI J1348−630 confusion event) now flagged → only the '+ re-flares' variant changes (13/27, B = 0.17).
- Plan record: v1 SHA-256 matches the plan text WITHOUT the appended 'Implementation clarifications'; those and data/literature_porb.csv were written 1–2 min after the hash, before the first H1 result (file times). Say so in the paper; commit + tag.
- Model comparison is weak: ΔAIC 0.65, AICc 5.46/7.58/10.60; ML-plug-in LOSO gap driven by GRS 1716−249; posterior-predictive LOSO −2.17/−3.18/−2.79.
- Leave-one-system-out: B median 0.06–0.25, upper 95% 0.44–0.61. Without GRS 1716−249: B = 0.25 (−0.01, 0.52), AIC prefers M1 by 2.3.
- Theory: irradiation-dominated disc → B = 2/3; Kramers SS disc → B = 5/6; edge pinned at T_ion → B = 1/3. P(B ≥ 2/3) = 0.006, P(B ≥ 5/6) = 0.001, P(B ≥ 1/3) = 0.16.
- Hierarchical σ_sys is prior-limited (report upper limit only: < 0.24 dex log-uniform, < 0.35 dex half-normal); σ_out ≈ 0.27 dex mostly from GX 339−4. Rise: σ_sys 0.50 dex ≫ σ_out 0.13 dex (opposite of decay).
- Validation with window matching (confused events removed): TW vs S25 N = 8, median −0.04, MAD 0.05, SD 0.24.

## Not done yet
- T1.1 manual ADS novelty search; T2.2 notebook; T2.4 MAXI on-demand 2–12 keV runs; T3.3 physical decay fits; T3.4 peak L/L_Edd; T3.5 hardness transitions; H3, H4.
- Verify the original references for periods taken from Yan & Yu / Saraswati tables (data/literature_porb.csv).
- Figure polish (labels overlap in results/fig_tau_porb.png).
