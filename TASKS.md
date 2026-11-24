# TASKS: bh-outburst-decay

Work top to bottom. Tick boxes as tasks complete. Read PROPOSAL.md and CLAUDE.md first.
Background, verified references and the reasoning behind each task: Claude Doc "Does Disc Size Set the Decay? — Research Understanding & Plan".

## Phase 0: Setup
- [x] **T0.1** Create `requirements.txt` (numpy, scipy, pandas, astropy, lmfit, emcee, matplotlib, requests, pyyaml) and `src/config.py`.

## Phase 1: Novelty gate and sample
- [ ] **T1.1 GATE.** Repeat the novelty search on ADS by hand (citation lists of Yan & Yu 2015 and Saraswati et al. 2025; 2024–2026 papers on decay timescales of BH transients). An AI-assisted search (Nov 2026) found no paper testing τ_d vs P_orb with post-2016 outbursts. Summarise in `notes/novelty.md`. **Stop and flag if a paper already does this.**
- [x] **T1.2** *(done 2026-11-22; still to check: periods/statuses marked "to verify")* Write `data/sample.csv`, one row per source: name, MAXI ID, BAT name, BH status (dynamical/candidate), P_orb ± error, **P_orb method** (spectroscopy/photometry/dips/inferred) and **quality flag**, distance (± error, or a range where studies disagree), mass ± error, and a reference for each parameter. Unknowns are NaN.
- [x] **T1.3** Write `data/literature_timescales.csv` from Yan & Yu 2015 (**BH entries only**) and Saraswati et al. 2025 Table 2 (source, outburst, peak MJD, rise/decay timescales, P_orb, paper). Mark outbursts appearing in both papers; keep one.

## Phase 2: Data
- [x] **T2.1** Write `src/download.py`: MAXI 1-day and 1-orbit standard light curves and BAT daily light curves, cached in `data/raw/`. Filter BAT to DATA_FLAG = 0; mask 10–20 Sep 2019 and 29–30 Mar 2019.
- [ ] **T2.2** Write `notebooks/01_lightcurves.ipynb` to plot all 2016–2026 light curves, MAXI + BAT, with hardness ratios.
- [x] **T2.3** Build the Aug 2009–Jan 2012 ASM–MAXI overlap set (outbursts in Yan & Yu also seen by MAXI) for calibration.
- [ ] **T2.4 (manual, Berkh)** Run MAXI on-demand 2–12 keV light curves for the core sample (matches RXTE/ASM and Saraswati et al.), for the band robustness check.

## Phase 3: Measurements
- [x] **T3.1** Write `src/outbursts.py`: automatic outburst start, peak and end, with a manual-override file `data/outburst_windows.yaml`.
- [x] **T3.2** Write `src/timescales.py`: two-point e-folding times τ = Δt / ln A between the 10/50/90% of peak levels (Yan & Yu-exact and smoothed-interpolation versions), Monte Carlo errors, the shape ratio τ_50–90/τ_10–50. One QC plot per outburst in `results/qc/`.
- [ ] **T3.3** Write `src/fit_decay.py`: exponential, linear and broken exponential→linear decay fits (lmfit, then emcee).
- [ ] **T3.4** Write `src/peak_luminosity.py`: Crab-normalised flux → L → L/L_Edd, with Monte Carlo errors over d, M and the bolometric correction.
- [ ] **T3.5** Write `src/hardness.py`: soft-to-hard transition time and luminosity (BAT/MAXI ratio and (4–10)/(2–4) keV).
- [x] **T3.6** Injection–recovery: synthetic exponential and linear decays with known τ, sampled at MAXI's real cadence and gaps → bias and scatter of the estimator.
- [x] **T3.7 VALIDATION GATE.** Compare with Yan & Yu (ASM–MAXI overlap) and Saraswati et al. (post-2011 overlap). *Done when:* `results/method_check.md` shows agreement within errors or an explained offset. **Do not run T4.1 until this passes.**
- [ ] **T3.8 GATE.** *(plan written and fingerprinted in results/analysis_plan_v1.md + .sha256; commit and tag it)* Freeze the analysis plan as a tagged git commit (`analysis-plan-v1`) before making the τ_d–P_orb figure.

## Phase 4: Analysis
- [x] **T4.0** Power simulation: with the real P_orb values and the intrinsic scatter measured in the old sample, how often is a true slope B = 0.5 detected?
- [x] **T4.1** Write `src/tau_vs_porb.py`: per-source median τ_d; regression log τ_d = A + B log P with intrinsic scatter (emcee); models M0/M1/M2 by AIC, BIC and leave-one-source-out cross-validation; Kendall's τ with permutation p; figure `results/fig_tau_porb.png`. Controls: without failed outbursts, dynamical only, new vs old, band, smoothing, BAT.
- [ ] **T4.2** Exploratory: H2 (rise time vs P_orb), H3 (τ_d vs peak L/L_Edd split by period), H4 (L_trans/L_Edd distribution).
- [x] **T4.3** Write `results/outburst_table.csv`, the uniform catalogue (the main data product).

## Phase 5: Write-up
- [x] **T5.1** *(bullets in paper/notes.md)* Write `paper/notes.md` with bullet results.
- [x] **T5.2** *(22 Nov 2026; Berkh chose a full AI-assisted draft instead of writing it personally)* Draft manuscript `paper/main.tex` + `paper/references.bib` (MNRAS), figures from `src/paper_figures.py` → `paper/figures/`. AI use is disclosed in the Acknowledgements.
- [ ] **T5.3** Berkh: read every section, check each number against `results/`, open each cited paper, fill in surname/affiliation/repository URL, compile on Overleaf (mnras template).
- [ ] **T5.4** Before submission: T1.1 ADS novelty search, T3.8 commit + tag the plan, verify the five literature periods in `data/literature_porb.csv` against the original papers.
