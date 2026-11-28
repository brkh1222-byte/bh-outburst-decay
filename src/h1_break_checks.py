"""Checks of the saturating form of the prediction (2026-11-28). NOT part of plan v1.

King & Ritter (1998) predict that the decay time increases with orbital period only up
to about a day and then levels off near 40 d. The single power law of H1 does not
represent that. This script asks what the data say about the slope BELOW the break.

 a. M2_fixed_1d   log tau = A + B min(x, 0), x = log10(P / 1 d): posterior of B and of the
                  plateau 10^A; same priors as the plan (A in [-1, 4], B in [-3, 3],
                  log sigma_int in [-3, 0.5]).
 b. M2_free       the plan's M2 with the break free in [-0.7, 0.7]: posterior of B.
 c. power_short   power of a test on the 8 systems with P < 1 d alone, for true slopes
                  1/3, 2/3 and 5/6 (sigma_int = 0.23 dex, 200 simulations each).
 d. power_M2      power to detect a slope of 2/3 below a 1 d break with the full sample,
                  fitting the fixed-break model (95% interval of B above zero).

Writes results/h1_break_checks.json.  Usage: nice .venv/bin/python -m src.h1_break_checks
"""
from __future__ import annotations

import json

import emcee
import numpy as np
import pandas as pd

from src import config
from src import tau_vs_porb as tp


def sample(lnprob, p0, nwalk=32, nstep=8000, seed=0):
    np.random.seed(seed % 2 ** 32)
    rng = np.random.default_rng(seed)
    p = np.array(p0) + 1e-3 * rng.standard_normal((nwalk, len(p0)))
    s = emcee.EnsembleSampler(nwalk, len(p0), lnprob)
    s.run_mcmc(p, nstep, progress=False)
    return s.get_chain(discard=nstep // 4, flat=True)


def make_fixed(x, y, s, xb=0.0):
    def lp(p):
        A, B, lsig = p
        if not (-1 <= A <= 4 and -3 <= B <= 3 and -3 <= lsig <= 0.5):
            return -np.inf
        var = s ** 2 + (10 ** lsig) ** 2
        r = y - (A + B * np.minimum(x, xb))
        return float(-0.5 * np.sum(r ** 2 / var + np.log(2 * np.pi * var)))
    return lp


def summ(v):
    return [round(float(q), 3) for q in np.percentile(v, [2.5, 50, 97.5])]


def main():
    out = {}
    ob = pd.read_csv(config.RESULTS / "h1_outbursts_primary.csv")
    ps = tp.per_source(ob)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values
    # a
    ch = sample(make_fixed(x, y, s), [1.55, 0.2, -0.7])
    out["M2_fixed_1d"] = {"B_below_break": summ(ch[:, 1]), "plateau_d": summ(10 ** ch[:, 0]),
                          "sigma_int": summ(10 ** ch[:, 2]),
                          "P_B_gt_0": round(float(np.mean(ch[:, 1] > 0)), 3),
                          "P_B_ge_1_3": round(float(np.mean(ch[:, 1] >= 1 / 3)), 3),
                          "P_B_ge_2_3": round(float(np.mean(ch[:, 1] >= 2 / 3)), 3),
                          "P_B_ge_5_6": round(float(np.mean(ch[:, 1] >= 5 / 6)), 3)}
    print("fixed", out["M2_fixed_1d"], flush=True)
    for xb, key in ((np.log10(0.5), "M2_fixed_0.5d"), (np.log10(2.0), "M2_fixed_2d")):
        c = sample(make_fixed(x, y, s, xb), [1.5, 0.2, -0.7])
        out[key] = {"B_below_break": summ(c[:, 1]), "P_B_ge_2_3": round(float(np.mean(c[:, 1] >= 2 / 3)), 3)}
        print(key, out[key], flush=True)
    # b
    ch2 = tp.mcmc(x, y, s, "M2", nstep=16000)
    out["M2_free"] = {"B_below_break": summ(ch2[:, 1]), "break_log10P": summ(ch2[:, 2]),
                      "P_B_ge_2_3": round(float(np.mean(ch2[:, 1] >= 2 / 3)), 3),
                      "note": "break prior flat in [-0.7, 0.7]; posterior of the break is broad"}
    print("free", out["M2_free"], flush=True)
    # c
    m = x < 0
    out["power_short"] = {"N_systems": int(m.sum()), "sigma_int": 0.23, "n_sim": 200}
    for b in (1 / 3, 2 / 3, 5 / 6):
        out["power_short"][f"B_{b:.3f}"] = tp.power(x[m], s[m], 0.23, b)
    print("power short", out["power_short"], flush=True)
    # d
    rng = np.random.default_rng(11)
    hits = 0
    nsim = 200
    for i in range(nsim):
        ysim = 1.55 + (2 / 3) * np.minimum(x, 0) + rng.normal(0, np.sqrt(s ** 2 + 0.23 ** 2))
        c = sample(make_fixed(x, ysim, s), [1.55, 0.5, -0.7], nwalk=16, nstep=1200, seed=int(rng.integers(1e9)))
        hits += np.percentile(c[:, 1], 2.5) > 0
    out["power_M2_fixed_1d_B_2_3"] = {"power": hits / nsim, "n_sim": nsim, "sigma_int": 0.23, "plateau_logtau": 1.55}
    print("power M2", out["power_M2_fixed_1d_B_2_3"], flush=True)
    (config.RESULTS / "h1_break_checks.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
