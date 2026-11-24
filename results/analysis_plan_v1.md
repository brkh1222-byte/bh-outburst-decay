# Analysis plan v1 (frozen before the tau_d–P_orb result was made)

Frozen: 2026-11-22, after the validation gate (results/method_check.md) and before running
src/tau_vs_porb.py for the first time. A SHA-256 fingerprint of this file is printed by
`shasum -a 256 results/analysis_plan_v1.md`; Berkh should commit this file and tag the commit
`analysis-plan-v1` so the freeze is on record in git. Any later change to the plan must go in a
new version (v2) with the reason, and both results must be reported.

## Sample (primary)

1. **Outbursts:** daily peak > 0.1 Crab (2–10 keV for this work; 2–12 keV for the literature),
   following Yan & Yu (2015). Re-flares (secondary outbursts split off by `src/outbursts.py`) are
   excluded. Outbursts flagged for source confusion are excluded.
2. **Sources:** only systems with an orbital period measured independently of the X-ray decay
   (spectroscopy, photometry, Hα modulation or X-ray dips). MAXI J0637−430 is excluded (period
   inferred from its decay). Neutron stars are excluded.
3. **Which measurement per outburst:**
   (a) this work (MAXI, baseline-subtracted, Yan & Yu two-point rule) if the outburst is in the
       MAXI era and we measured it;
   (b) otherwise the mean of log10 τ from Yan & Yu (2015) and Saraswati et al. (2025) if both
       measured it, or the single available value.
4. **Orbital periods:** data/sample.csv (verified, with references) for sources in our sample;
   otherwise the value tabulated by Saraswati et al. (2025, Table 1) or Yan & Yu (2015, Table 1),
   cited as such in data/literature_porb.csv.

## Uncertainties

- This work: σ = half the 16–84% Monte Carlo range in log10 τ.
- Literature: published ± error converted to dex, floored at 0.02 dex, plus σ_method = 0.19 dex
  (between-study scatter from results/method_check.md) in quadrature.
- Per source: mean of log10 τ over its outbursts; σ_source² = Σ σ_j² / n².

## Primary test (H1)

log10 τ_d,10–90 = A + B log10(P_orb / 1 d) + ε, ε ~ N(0, σ_int² + σ_source²), one point per source.
Posterior with emcee (flat priors: A ∈ [−1, 4], B ∈ [−3, 3], log10 σ_int ∈ [−3, 0.5]).
**H1 is supported if the 95% credible interval of B lies above 0.**

Model comparison on the same per-source data:
- M0: constant (B = 0).
- M1: power law.
- M2: saturating power law, log τ = A + B·min(x, x_b), x = log10(P/1 d), break x_b free in [−0.7, 0.7].
Ranked by AIC, BIC (maximum likelihood) and leave-one-source-out cross-validated log predictive
density (higher is better). Kendall's τ between per-source log τ_d and log P_orb with a
10,000-permutation p-value.

## Power check (run before reading the H1 result)

Simulate the real P_orb values and per-source errors with a true B = 0.5 and σ_int equal to the
M0 scatter of the literature-only sample; report the fraction of simulations whose 95% interval of
B excludes 0.

## Robustness (reported, not used to decide H1)

(i) include re-flares; (ii) include faint outbursts (all Saraswati mini-outbursts and peaks < 0.1 Crab);
(iii) dynamically confirmed BHs only; (iv) this work's outbursts only (2016–2026) and literature only;
(v) raw (no baseline subtraction) MAXI timescales; (vi) smoothed-crossing timescales;
(vii) σ_method = 0 and 0.3 dex; (viii) per-outburst hierarchical model with a source random effect.

## Exploratory

H2: same regression with τ_rise,10–90. H3 and H4 need distances, masses and a bolometric
correction and are deferred to the next stage.

## Implementation clarifications (added before the first H1 result; no rule changed)

1. *Matching literature outbursts to ours:* a literature outburst counts as "measured by this work"
   when its peak MJD lies inside one of our outburst windows (not within ±20 d of our peak). Reason:
   multi-peaked outbursts (MAXI J1820+070 2018, GX 339−4 2021) have peaks >20 d apart in different
   bands; matching by peak date double-counted them.
2. *Brightness rule for MAXI-era literature outbursts we did not detect:* item 1 says the cut is applied
   in 2–10 keV for this work. For a MAXI-era literature outburst outside all our windows, the cut is
   applied to our MAXI 2–10 keV daily maximum within ±15 d of the literature peak. (Affects GX 339−4
   2013 and 2017–18, listed at 0.13 and 0.11 Crab in 2–12 keV by Saraswati et al.)
