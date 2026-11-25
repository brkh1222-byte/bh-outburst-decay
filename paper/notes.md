# Results notes (working notes behind paper/main.tex)

> 2026-11-25: sections below dated 22 Nov are kept as written; corrections and the number audit are in the section "2026-11-25 audit" at the end. Where they disagree, the audit section is right.

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


## 2026-11-25 audit (AI pilot agent)

### Corrections to the notes above
- "40 unflagged" windows → **39** (after the GS 1354−64 MJD 58560 flag; results/outburst_table.csv).
- H2 slope "B = 0.33 [−0.38, 1.03]" → **0.34 [−0.34, 1.06]** (results/h1_results.json; 0.33 [−0.39, 1.02] is the hierarchical value).
- "plan frozen" → the plan was written before the first run but is **not verifiably frozen and not pre-registered**; see results/analysis_plan_amendment_1.md.
- GS 1354−64 "confusion found" → "most likely contamination"; evidence and limits in notes/confusion_check.md. BAT median for MJD 58505–58545 is 0.005 Crab (the 0.003 above was for a different interval).
- "+ re-flares" check: 13/27, B = 0.17 with the late flag; **13/28, B = 0.05 [−0.36, 0.47]** with the fingerprinted files. Both are reported in the paper.
- Five last-digit rounding errors in Table 2 of the paper were corrected against results/outburst_table.csv.

### Number audit: every number in paper/main.tex and its source
Recomputed with `.venv/bin/python -m src.audit_numbers` (writes results/paper_numbers.json). "OK" = the paper value equals the file value at the quoted precision. Checked 2026-11-25.

| Where in paper | Statement (paper value) | Value in file | Source file | Status |
|---|---|---|---|---|
| Abstract, §5.1 | 55 outburst windows, 17 sources | 55, 17 | results/outburst_table.csv | OK |
| Abstract, §5.1 | 24 bright main outbursts, 13 sources | 24, 13 | results/outburst_table.csv | OK |
| §5.1 | 16 flagged, 13 of them MAXI J1631−479; 39 unflagged | 16, 13, 39 | results/outburst_table.csv | OK |
| §5.1 | τ_d 15–86 d, median 31 d | 15.28, 85.86, 30.57 | results/outburst_table.csv | OK |
| §5.1, §6.1 | BAT/MAXI decay-time ratio median 0.61 (18 outbursts); ≈0.2 dex | 0.610, N = 18, 0.215 dex | results/outburst_table.csv | OK |
| §4.2 | 6 of 24 measured values outside their own 16–84% range | 6 | results/outburst_table.csv | OK |
| §3.3 | 27 table entries; 24 with a MAXI light curve; 19 with a window | 27, 24, 19 | data/sample.csv; results/timescales_maxi.csv | OK |
| §3.4 | 42 Yan & Yu BH outbursts; 33 Saraswati events; 9 in both | 42, 33, 9 | data/literature_timescales.csv | OK |
| Table 1 | periods, n, ⟨τ_d⟩, status, origin of 13 systems | all 13 rows equal | results/h1_sources_primary.csv | OK |
| Abstract, §3.3, §7 | P_orb = 0.10–2.62 d (0.100 and 2.62) | 0.1004, 2.6217 | results/h1_sources_primary.csv | OK |
| Table 2 | 24 rows (peak MJD, F_pk, τ_r, τ_d [range], SR, τ_BAT) | all rows equal after 5 rounding fixes | results/outburst_table.csv | FIXED |
| §5.2, Table 3 | TW/YY: N 5, +0.16, MAD 0.20, SD 0.18 | 5, +0.162, 0.195, 0.182 | results/h1_extra.json (validation_window_matched) | OK |
| §5.2, Table 3 | TW/S: N 8, −0.04, 0.05, 0.24 | 8, −0.038, 0.046, 0.240 | results/h1_extra.json | OK |
| §5.2, Table 3 | YY/S: N 9, −0.05, 0.10, 0.25 | 9, −0.049, 0.098, 0.245 | results/h1_extra.json | OK |
| §5.2 | 4U 1543−47 2022: 4.6 vs 20.4 d, 0.06 Crab; GS 1354−64 2015 differs by 0.17 dex | 4.60, 20.4, 0.061; log(21.65/14.74) = 0.167 | results/h1_extra.json; results/outburst_table.csv | OK |
| §5.2, abstract | XTE J1550−564 1998: 19 vs 89 d, factor 4.6; GRO J1655−40 1996: 172 vs 97 d | 19.2, 89.2 (4.65); 172.3, 97.3 | results/method_check.md | OK |
| §5.2 | injection: bias ≤ 0.035 dex; scatter 0.07–0.10 dex at 0.1 Crab, ≤ 0.04 at ≥ 0.3 Crab; ≥ 96% recovered | 0.035; 0.074–0.101; 0.040; 0.96 | results/method_check.md | OK |
| §4.2 | σ_method = 0.19 (0.195); plain SDs 0.18–0.25 | 0.195; 0.182–0.245 | results/h1_extra.json | OK |
| §4.4 | fingerprint time 2026-11-21 21:54 UTC | frozen 2026-11-21T21:54:19Z | results/analysis_plan_v1.sha256 | OK |
| §4.4, §5.3 | power 0.84 (B = 0.5), 0.39 (B = 0.3); σ_int(lit) 0.23; 200 simulations | 0.84, 0.39, 0.230 | results/h1_results.json | OK |
| §5.3 | 26 outbursts, 13 systems; 13 ours, 13 literature | 26, 13, 13, 13 | results/h1_outbursts_primary.csv | OK |
| Abstract, §5.3, §7 | B = 0.17 (−0.17, 0.52) | 0.169 (−0.169, 0.521) | results/h1_results.json | OK |
| §5.3 | A = 1.52 (1.34–1.69); τ_d = 33 d at 1 d | 1.518 (1.341–1.690); 32.9 | results/h1_results.json | OK |
| Abstract, §5.3 | σ_int = 0.24 dex (0.15–0.41) | 0.239 (0.154–0.413) | results/h1_results.json | OK |
| §5.3 | P(B > 0) = 0.85 | 0.853 | results/h1_extra.json | OK |
| §5.3 | Kendall τ = 0.31, p = 0.16 | 0.308, 0.164 | results/h1_results.json | OK |
| §5.3, Table 4 | AIC 4.26/4.91/5.60; BIC 5.39/6.61/7.86; LOSO −2.36/−5.67/−6.97 | same | results/h1_results.json | OK |
| §5.3, Table 4 | AICc 5.46/7.58/10.60; posterior-predictive LOSO −2.17/−3.18/−2.79 | 5.46/7.58/10.60; −2.172/−3.175/−2.794 | results/h1_extra.json | OK |
| §5.3 | M2 break at P = 0.2 d | 0.1995 | results/h1_results.json | OK |
| §7 | constant decay time of about 30 d | 30.2 (M0) | results/h1_results.json | OK |
| Table 4, plan rows | (i)–(vii) N, B, interval, τ_K, p | all equal | results/h1_robustness.csv | OK |
| Table 4, §5.4 | (i) before the late flag: 13/28, 0.05 (−0.36, 0.47), 0.15, 0.50 | 13/28, 0.051 (−0.356, 0.469), 0.154, 0.497 | re-run on fingerprinted inputs; results/analysis_plan_amendment_1.md §4 | OK (not regenerated by the pipeline; see amendment) |
| Table 4 | (viii) hierarchical 0.23 (−0.09, 0.55) | 0.229 (−0.089, 0.546) | results/h1_hierarchical.txt | OK |
| Table 4 | added checks: RV only 0.12 (−0.21, 0.50) 10/23; no J1550 2001 0.18 (−0.14, 0.51) 13/25; ASM shift 0.20 (−0.13, 0.54); duplicates 0.17 (−0.16, 0.50); variance 0.23 (−0.09, 0.53); half-normal 0.21 (−0.16, 0.58); τ_50–90 0.05 (−0.54, 0.66) | all equal | results/h1_extra.json | OK |
| Table 4, §5.4 | clarifications undone: 0.18 (−0.16, 0.52) 13/28; 0.15 (−0.18, 0.48) 13/28; 0.15 (−0.18, 0.49) 13/30 | 0.177 (−0.159, 0.519); 0.147 (−0.176, 0.485); 0.149 (−0.177, 0.487) | results/amendment_1_checks.json | OK |
| §5.4 | GRS 1716−249 as candidate: 0.12 (−0.21, 0.50) | 0.122 (−0.211, 0.501) | results/h1_extra.json | OK |
| §5.4 | corrections change B by < 0.07 | max 0.063 | results/h1_extra.json | OK |
| §5.4 | leave-one-out medians 0.06–0.25; upper limits 0.44–0.61 | 0.059–0.247; 0.443–0.607 | results/h1_extra.json | OK |
| §5.4 | without GRS 1716−249: 0.25 (−0.01, 0.52); ΔAIC 2.3 | 0.247 (−0.014, 0.518); 2.26 | results/h1_extra.json | OK |
| Abstract, §5.4, §6.1, §7 | P(B ≥ 1/3) = 0.16; P(B ≥ 2/3) = 0.006; P(B ≥ 5/6) = 0.001 | 0.160, 0.006, 0.001 | results/h1_extra.json | OK |
| §5.4 | 2/3 above the upper limit in all 13 leave-one-out fits and both hierarchical fits | 13 of 13 (max 0.607); 0.546, 0.578 | results/h1_extra.json; results/h1_hierarchical.txt | OK |
| Abstract, §5.5 | σ_out = 0.27 dex (0.19–0.40); σ_sys < 0.24 | 10^−0.561 = 0.275 (0.193–0.401); 10^−0.628 = 0.236 | results/h1_hierarchical.txt | OK |
| §5.5 | half-normal: σ_out 0.28 (0.19–0.41); σ_sys < 0.35 | 0.276 (0.192–0.408); 0.346 | results/h1_extra.json | OK |
| §5.5 | 9 of 13 systems with one outburst; GX 339−4 gives 9 of 13 within-system comparisons | 9; 9 of 13 | results/h1_sources_primary.csv | OK |
| §5.5, §6.1 | GX 339−4: ten outbursts, 19–123 d, 0.80 dex, factor six; system means span 0.76 dex | 10; 19.4–123.5; 0.804; 6.36; 0.756 | results/h1_outbursts_primary.csv; results/h1_sources_primary.csv | OK |
| §5.6 | H2: 12 systems, 25 outbursts; B = 0.34 (−0.34, 1.06); τ_K = 0.42, p = 0.06 | 12; 25; 0.343 (−0.344, 1.060); 0.424, 0.061 | results/h1_results.json; results/h1_hierarchical.txt | OK |
| §5.6 | hierarchical rise: 0.33 (−0.39, 1.02); σ_sys 0.50 (0.33–0.87); σ_out 0.13 (0.08–0.23) | 0.330 (−0.386, 1.022); 0.503 (0.325–0.865); 0.131 (0.080–0.230) | results/h1_hierarchical.txt | OK |
| §5.6 | rises 0.7 d (4U 1543−47) and 57.7 d (MAXI J1820+070) | 0.7, 57.7 | results/outburst_table.csv | OK |
| §5.7 | shape ratio 0.11–13, median 1.6; ten > 2; ten < 1; examples 0.21, 0.32, 0.30, 0.11 | 0.106–13.02, 1.60; 10; 10; same | results/outburst_table.csv | OK |
| §6.1 | period range 1.42 dex; slope 1/3 → 0.47 dex | 1.417; 0.472 | results/h1_sources_primary.csv | OK |
| §6.2 | Saraswati peak fluxes 1.6–2.0 × ours (bright, after 2015); 4 × for GS 1354−64 2015 | 1.59–1.95 (five outbursts); 0.25/0.065 = 3.8 | data/literature_timescales.csv; results/timescales_maxi.csv | OK (hand calculation, 2026-11-25) |
| §6.4 | separation 1.82°; J1348 peak 3.1 Crab at MJD 58523.5; r = 0.84; 0.002 → 0.4 Crab; 0.001 Crab before; BAT median 0.005 Crab; BAT 0.26 and ≈0.2 Crab in 2015 and 2025–26 | 1.822; 3.11, 58523.5; 0.837; 0.002, 0.41–0.44; 0.0014; 0.0048–0.0051; 0.262, 0.19–0.25 | notes/confusion_check.md (recomputed from data/raw); results/h1_extra.json (bat_checks) | OK |
| §6.5 | GX 339−4 hard-only outbursts: 0.03–0.06 Crab MAXI, 0.10–0.18 Crab BAT | 0.029–0.059; 0.099–0.178 | results/h1_extra.json (bat_checks) | OK |
| §2 | theory slopes 2/3, 5/6, 1/3; factor 2 in mass → 0.2 dex | (2/3)·log 2 = 0.20 | derivation in the text | OK (algebra re-checked) |
| §1 | Yan & Yu: 110 outbursts, 36 transients; Saraswati: nine black holes, to 2024; Maheshwari: 42 LMXBs | same | abstracts via Crossref/arXiv (notes/novelty.md) | OK |
| §5.8 | χ²_red (lmfit, preferred model) median 15, range 1.9–270; scatter term median 0.20 | 14.6, 1.89–270.7; 0.201 | results/decay_fits_porb.json | OK |
| §5.8 | 2016–2026 (24): broken 17 (12 clear), linear 4 (3), exponential 3 (1); all 35: 25 (19), 4 (3), 6 (2) | same | results/decay_fits_porb.json | OK |
| §5.8 | exponential-fit τ vs two-point τ (24): median 0.00, robust 0.11, SD 0.14, max 0.46 dex | 0.002, 0.109, 0.142, 0.461 | results/decay_fits_porb.json | OK |
| §5.8 | this-work subsample (8 systems, 13 outbursts): B = 0.19 (−0.29, 0.69) two-point; 0.16 (−0.40, 0.71) exponential; 0.08 (−0.85, 0.91) broken | 0.193 (−0.288, 0.691); 0.159 (−0.397, 0.714); 0.083 (−0.855, 0.907) | results/decay_fits_porb.json | OK |
| §5.8 | 14 of 105 fits with chains shorter than 50 autocorrelation times; preferred model changed for one outburst between the 4000-step and 16000-step runs | 14 of 105; exp 7→6, broken 24→25 | results/decay_fits_porb.json; first run not kept (counts recorded in git history of notes/STATUS.md only) | OK |
| §6.5 | XTE J1650−500 period 0.3205 ± 0.0007 d vs 7.63 h (0.8% low); refit B = 0.17 (−0.16, 0.51) | 0.3205 d = 7.692 h; 0.171 (−0.161, 0.506) | notes/porb_check.md; results/amendment_1_checks.json (porb_1650_corrected) | OK |

Not checked against a file because they are settings stated in the code: detection thresholds (§3.2; src/outbursts.py), selection rules (§4.1; src/timescales.py), priors (§4.4; src/tau_vs_porb.py, src/hierarchical.py), Crab rates (§3.1; src/config.py). These were compared with the code by eye on 2026-11-25 and agree.

### Reference check (2026-11-25)
All 47 entries of paper/references.bib: 46 DOIs resolve (45 on Crossref, lmfit on DataCite) and match authors, year, journal, volume and page. Corrected: titles of Saraswati2025, Tetarenko2018b, Maheshwari2026. Added and verified: Tominaga2020 (ApJ 899, L20), Orosz2004 (ApJ 616, 376), Newville2014 (Zenodo, doi:10.5281/zenodo.11813). ShakuraSunyaev1973 has no DOI; only the ADS bibcode (1973A&A....24..337S) was confirmed to resolve. Every \cite key has an entry and every entry is cited. Not done: opening each paper to confirm that it says what the text attributes to it (only abstracts were read for the papers named in notes/novelty.md).
