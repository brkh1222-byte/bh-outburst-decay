# TASKS: bh-outburst-decay

Work top to bottom. Tick boxes as tasks complete. Read PROPOSAL.md and CLAUDE.md first.

## Phase 0: Setup
- [ ] **T0.1** Create `requirements.txt` (numpy, scipy, pandas, astropy, lmfit, emcee, matplotlib, requests) and `src/config.py`.

## Phase 1: Novelty gate and sample
- [ ] **T1.1 GATE.** Run a final literature search (ADS/arXiv, 2024–2026) for uniform decay-timescale studies of 2016–2026 black hole transients. Summarise in `notes/novelty.md`. **Stop and flag if a paper already measures τ_d vs P_orb with the new outbursts.**
- [ ] **T1.2** Write `data/sample.csv` with one row per outburst: source, MAXI ID, BAT name, outburst year(s), black hole status (dynamical/candidate), P_orb ± error, distance ± error, mass ± error, and a reference for each parameter. Start from the PROPOSAL §5 tables and verify each one.
- [ ] **T1.3** Write `data/literature_timescales.csv` with the tabulated values from Yan & Yu 2015 and Saraswati et al. 2025 (source, outburst, rise/decay times, P_orb).

## Phase 2: Data
- [ ] **T2.1** Write `src/download.py` to fetch the MAXI 1-day and 1-orbit light curves and BAT daily light curves for every source, cached in `data/raw/`. Log sources needing the MAXI on-demand tool.
- [ ] **T2.2** Write `notebooks/01_lightcurves.ipynb` to plot all 2016–2026 light curves, MAXI + BAT, with the hardness ratio.

## Phase 3: Measurements
- [ ] **T3.1** Write `src/outbursts.py` to detect outburst start, peak and end automatically, with a manual-override file `data/outburst_windows.yaml`.
- [ ] **T3.2** Write `src/fit_decay.py`: exponential, linear and broken exponential→linear fits (lmfit/emcee), plus model-free 10/50/90% rise and decay times. Save one QC plot per outburst to `results/qc/`.
- [ ] **T3.3** Write `src/peak_luminosity.py`: Crab-normalised flux → L → L/L_Edd, with Monte Carlo errors.
- [ ] **T3.4** Write `src/hardness.py` to find the soft-to-hard transition time and its luminosity.
- [ ] **T3.5** Consistency check: refit GX 339−4 and other literature-overlap outbursts and compare with the Yan & Yu / Saraswati values.
  *Done when:* `results/method_check.md` is written.

## Phase 4: Analysis
- [ ] **T4.1** Write `src/tau_vs_porb.py`: combined sample, King & Ritter-like model vs constant, AIC/BIC, Kendall's τ, and the figure `results/fig_tau_porb.png`.
- [ ] **T4.2** Test H2 (τ_d vs peak L/L_Edd at fixed P_orb) and H3 (L_trans/L_Edd distribution).
- [ ] **T4.3** Write `results/outburst_table.csv`, the uniform catalogue (the main data product).

## Phase 5: Write-up
- [ ] **T5.1** Write `paper/notes.md` with bullet results. **The student writes the paper text personally.**
