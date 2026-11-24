"""Exploratory follow-up to T3.3: does a model-fit decay time behave differently from the
two-point time in the tau-P_orb test? NOT part of plan v1.

Only outbursts measured by this work have light curves to fit, so this uses the
"this work only" subsample of the primary H1 sample (results/h1_outbursts_primary.csv).
For each of those outbursts the two-point log tau is replaced by
  (a) tau of the single-exponential fit,
  (b) tau of the exponential part of the broken (exponential -> linear) fit,
with half the 16-84% posterior width (in dex, floor 0.02) as the error, and the
same per-system regression as H1 is run (src/tau_vs_porb.py). Row (0) repeats the
two-point values on the same subsample for comparison.

Also counts the preferred decay shape. Writes results/decay_fits_porb.json.
Usage: nice .venv/bin/python -m src.fit_decay_porb
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src import config
from src import tau_vs_porb as tp


def main():
    fits = pd.read_csv(config.RESULTS / "decay_fits.csv")
    ob = pd.read_csv(config.RESULTS / "h1_outbursts_primary.csv")
    ob = ob[ob.origin == "this work"].copy()
    out = {}

    def run(label, o):
        ps = tp.per_source(o)
        ch = tp.mcmc(ps.x.values, ps.logtau.values, ps.sig.values, "M1", nstep=8000)
        q = np.percentile(ch[:, 1], [2.5, 50, 97.5])
        out[label] = {"N_sources": int(len(ps)), "N_outbursts": int(len(o)),
                      "B": [float(v) for v in q], "P_B_ge_2_3": float(np.mean(ch[:, 1] >= 2 / 3))}
        print(label, out[label], flush=True)

    run("two-point tau_d,10-90 (this work only)", ob)
    for kind, label in (("exp", "single-exponential fit tau"), ("broken", "exponential part of broken fit tau")):
        f = fits[fits.model == kind].set_index(["source", "t_peak"])
        o = ob.copy()
        keep = []
        for i, r in o.iterrows():
            key = (r.source, r.t_peak)
            if key not in f.index:
                continue
            g = f.loc[key]
            o.loc[i, "logtau"] = np.log10(g.tau_med)
            o.loc[i, "sig"] = max(0.5 * (np.log10(g.tau_hi) - np.log10(g.tau_lo)), tp.ERR_FLOOR)
            keep.append(i)
        run(label, o.loc[keep])
    # shape statistics
    best = fits.loc[fits.groupby(["source", "t_peak"]).BIC.idxmin()]
    for era, sel in (("all fitted", best), ("study era 2016-2026", best[best.era == "study"])):
        cnt = {k: int((sel.model == k).sum()) for k in ("exp", "linear", "broken")}
        clear = {}
        for k in cnt:
            n = 0
            for _, r in sel[sel.model == k].iterrows():
                others = fits[(fits.source == r.source) & (fits.t_peak == r.t_peak) & (fits.model != k)]
                n += int(others.dBIC.min() > 6)
            clear[k] = n
        out[f"preferred_model[{era}]"] = {"N": int(len(sel)), "best": cnt, "clear_dBIC_gt_6": clear}
    ex = fits[fits.model == "exp"]
    for era, e in (("all fitted", ex), ("study era 2016-2026", ex[ex.era == "study"])):
        r = np.log10(e.tau_med / e.two_point_tau_10_90)
        out[f"exp_tau_vs_two_point[{era}]"] = {"N": int(len(r)), "median_dex": float(np.median(r)),
                                               "robust_scatter_dex": float(1.4826 * np.median(np.abs(r - np.median(r)))),
                                               "SD_dex": float(np.std(r, ddof=1)),
                                               "max_abs_dex": float(np.abs(r).max())}
    jit = best.ljit_med
    out["jitter_best_model"] = {"median": float(10 ** jit.median()), "min": float(10 ** jit.min()), "max": float(10 ** jit.max())}
    out["chi2_red_lmfit_best_model"] = {"median": float(best.chi2_red_lmfit.median()), "min": float(best.chi2_red_lmfit.min()),
                                       "max": float(best.chi2_red_lmfit.max())}
    out["autocorr"] = {"max": float(fits.autocorr_max.max()), "median": float(fits.autocorr_max.median()),
                       "n_fits_chain_shorter_than_50_tau": int((fits.autocorr_max * 50 > fits.n_steps).sum()), "n_fits": int(len(fits))}
    (config.RESULTS / "decay_fits_porb.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if "preferred" in k or "exp_tau" in k or k in ("jitter_best_model", "chi2_red_lmfit_best_model", "autocorr")}, indent=1))


if __name__ == "__main__":
    main()
