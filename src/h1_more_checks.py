"""Further robustness checks of the tau_d-P_orb test (2026-11-28). NOT part of plan v1.

Written after a referee-style read of the paper. None of these changes the H1 decision
rule; they probe assumptions a referee is likely to question. All use files that already
exist (results/h1_outbursts_primary.csv, results/timescales_maxi.csv, data/raw/).

 1. seeds            Monte Carlo precision: primary fit with five seeds; autocorrelation time.
 2. short_period     Systems with P_orb < 1 d only (King & Ritter 1998 predict the increase
                     only below about a day, with saturation above).
 3. M2_break_1d      Saturating model with the break fixed at 1 d, compared with M0 and M1.
 4. student_t        Residuals follow a Student-t (nu = 4) instead of a Gaussian (outliers).
 5. median           Per-system median instead of mean of log tau.
 6. flat_sigma       Prior flat in sigma_int instead of flat in log sigma_int.
 7. rv_strict        Only systems whose period comes from a radial-velocity orbit of the
                     companion (drops GRS 1716-249, MAXI J1659-152, MAXI J1803-298 and
                     Swift J1753.5-0127, whose period is from H-alpha line modulation).
 8. leave_two_out    All 78 pairs of systems removed in turn.
 9. power_posthoc    Power for true slopes 1/3 and 2/3 (same simulation as the plan's power check).
10. bat              This-work outbursts measured in Swift/BAT 15-50 keV instead of MAXI.
11. bands            This-work outbursts remeasured in MAXI 2-20, 2-4 and 4-10 keV (same windows).
12. bootstrap        Non-parametric bootstrap over systems (maximum-likelihood slope).
13. ols              Ordinary least-squares slope, no errors, as a sanity check.
14. gx339_trend      GX 339-4 alone: decay time against date (Kendall).

Writes results/h1_more_checks.json.   Usage: nice .venv/bin/python -m src.h1_more_checks
"""
from __future__ import annotations

import itertools
import json

import emcee
import numpy as np
import pandas as pd
from scipy import optimize, stats

from src import config
from src import tau_vs_porb as tp
from src.lightcurves import load_maxi
from src.outbursts import load_overrides, local_baseline, windows_for
from src.timescales import monte_carlo, yan_yu

RV_NOT_FULL = ["GRS 1716-249", "MAXI J1659-152", "MAXI J1803-298", "Swift J1753.5-0127"]
OUT = {}


def q3(ch):
    q = np.percentile(ch[:, 1], [2.5, 50, 97.5])
    return [round(float(v), 3) for v in q]


def fit_B(ob, seed=0, nstep=8000):
    ps = tp.per_source(ob)
    ch = tp.mcmc(ps.x.values, ps.logtau.values, ps.sig.values, "M1", nstep=nstep, seed=seed)
    return {"N_sources": int(len(ps)), "N_outbursts": int(len(ob)), "B": q3(ch),
            "P_B_gt_0": round(float(np.mean(ch[:, 1] > 0)), 3),
            "P_B_ge_2_3": round(float(np.mean(ch[:, 1] >= 2 / 3)), 4)}


def save():
    (config.RESULTS / "h1_more_checks.json").write_text(json.dumps(OUT, indent=1))


def generic_mcmc(lnprob, p0, nwalk=32, nstep=8000, seed=0):
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    p = np.array(p0) + 1e-3 * rng.standard_normal((nwalk, len(p0)))
    s = emcee.EnsembleSampler(nwalk, len(p0), lnprob)
    s.run_mcmc(p, nstep, progress=False)
    return s.get_chain(discard=nstep // 4, flat=True)


def main():
    ob = pd.read_csv(config.RESULTS / "h1_outbursts_primary.csv")
    ps = tp.per_source(ob)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values
    n = len(x)

    # 1 ---------------------------------------------------------------- seeds
    rows = []
    for seed in range(5):
        ch = tp.mcmc(x, y, s, "M1", nstep=8000, seed=seed)
        rows.append(q3(ch))
    p_ml, _ = tp.fit_ml(x, y, s, "M1")
    np.random.seed(0)
    sam = emcee.EnsembleSampler(32, 3, lambda p: tp.logprior(p, "M1") + tp.loglike(p, x, y, s, "M1")
                                if np.isfinite(tp.logprior(p, "M1")) else -np.inf)
    sam.run_mcmc(p_ml + 1e-3 * np.random.default_rng(0).standard_normal((32, 3)), 8000, progress=False)
    act = sam.get_autocorr_time(tol=0)
    a = np.array(rows)
    OUT["seeds"] = {"B_2.5_50_97.5_by_seed": rows, "range_lo": [float(a[:, 0].min()), float(a[:, 0].max())],
                    "range_med": [float(a[:, 1].min()), float(a[:, 1].max())],
                    "range_hi": [float(a[:, 2].min()), float(a[:, 2].max())],
                    "autocorr_steps_A_B_logsig": [round(float(v), 1) for v in act],
                    "kept_samples": int(32 * 6000), "effective_samples_B": int(32 * 6000 / act[1])}
    print("seeds", OUT["seeds"], flush=True); save()

    # 2 ---------------------------------------------------------------- P < 1 d
    OUT["short_period"] = fit_B(ob[ob.porb_d < 1.0])
    OUT["long_period"] = fit_B(ob[ob.porb_d >= 1.0])
    print("short", OUT["short_period"], "long", OUT["long_period"], flush=True); save()

    # 3 ---------------------------------------------------------------- M2 with break at 1 d
    def nll(p):
        A, B, lsig = p
        if not (-1 <= A <= 4 and -3 <= B <= 3 and -3 <= lsig <= 0.5):
            return 1e10
        var = s ** 2 + (10 ** lsig) ** 2
        r = y - (A + B * np.minimum(x, 0.0))
        return 0.5 * np.sum(r ** 2 / var + np.log(2 * np.pi * var))
    best = min((optimize.minimize(nll, [np.mean(y), b, -1], method="Nelder-Mead",
                                  options={"maxiter": 20000, "xatol": 1e-6, "fatol": 1e-8})
                for b in (-0.5, 0, 0.5, 1)), key=lambda r: r.fun)
    comp = tp.compare(x, y, s)
    k = 3
    OUT["M2_break_1d"] = {"params_A_B_logsig": [round(float(v), 3) for v in best.x], "logL": round(float(-best.fun), 3),
                          "AIC": round(float(2 * k + 2 * best.fun), 2),
                          "AICc": round(float(2 * k + 2 * best.fun + 2 * k * (k + 1) / (n - k - 1)), 2),
                          "BIC": round(float(k * np.log(n) + 2 * best.fun), 2),
                          "AIC_M0": round(comp["M0"]["AIC"], 2), "AIC_M1": round(comp["M1"]["AIC"], 2),
                          "tau_plateau_d": round(float(10 ** best.x[0]), 1)}
    print("M2_1d", OUT["M2_break_1d"], flush=True); save()

    # 4 ---------------------------------------------------------------- Student-t residuals
    NU = 4.0
    def lp_t(p):
        A, B, lsig = p
        if not (-1 <= A <= 4 and -3 <= B <= 3 and -3 <= lsig <= 0.5):
            return -np.inf
        sc = np.sqrt(s ** 2 + (10 ** lsig) ** 2)
        return float(np.sum(stats.t.logpdf((y - A - B * x) / sc, NU) - np.log(sc)))
    ch = generic_mcmc(lp_t, p_ml)
    OUT["student_t_nu4"] = {"B": q3(ch), "P_B_ge_2_3": round(float(np.mean(ch[:, 1] >= 2 / 3)), 4)}
    print("t", OUT["student_t_nu4"], flush=True); save()

    # 5 ---------------------------------------------------------------- per-system median
    g = ob.groupby("source")
    med = pd.DataFrame({"logtau": g.logtau.median(), "sig": g.sig.apply(lambda v: np.sqrt(np.sum(np.square(v))) / len(v)),
                        "x": np.log10(g.porb_d.first())}).reset_index()
    ch = tp.mcmc(med.x.values, med.logtau.values, med.sig.values, "M1", nstep=8000)
    OUT["per_system_median"] = {"B": q3(ch)}
    print("median", OUT["per_system_median"], flush=True); save()

    # 6 ---------------------------------------------------------------- prior flat in sigma
    def lp_flat(p):
        A, B, sig = p
        if not (-1 <= A <= 4 and -3 <= B <= 3 and 0 < sig <= 10 ** 0.5):
            return -np.inf
        var = s ** 2 + sig ** 2
        r = y - A - B * x
        return float(-0.5 * np.sum(r ** 2 / var + np.log(2 * np.pi * var)))
    ch = generic_mcmc(lp_flat, [p_ml[0], p_ml[1], 10 ** p_ml[2]])
    qs = np.percentile(ch[:, 2], [2.5, 50, 97.5])
    OUT["flat_sigma_prior"] = {"B": q3(ch), "sigma_int": [round(float(v), 3) for v in qs]}
    print("flat", OUT["flat_sigma_prior"], flush=True); save()

    # 7 ---------------------------------------------------------------- strict RV orbits
    OUT["rv_strict"] = fit_B(ob[~ob.source.isin(RV_NOT_FULL)])
    OUT["rv_strict"]["dropped"] = RV_NOT_FULL
    print("rv", OUT["rv_strict"], flush=True); save()

    # 8 ---------------------------------------------------------------- leave two out
    src = ps.source.values
    l2 = []
    for i, j in itertools.combinations(range(n), 2):
        m = np.ones(n, bool); m[[i, j]] = False
        ch = tp.mcmc(x[m], y[m], s[m], "M1", nstep=3000, seed=1000 + 13 * i + j)
        l2.append((src[i], src[j], *q3(ch)))
    l2 = pd.DataFrame(l2, columns=["a", "b", "lo", "med", "hi"])
    imax, imin, ihi = l2.med.idxmax(), l2.med.idxmin(), l2.hi.idxmax()
    OUT["leave_two_out"] = {"N_pairs": int(len(l2)), "median_range": [float(l2.med.min()), float(l2.med.max())],
                            "upper_range": [float(l2.hi.min()), float(l2.hi.max())],
                            "N_upper_below_2_3": int((l2.hi < 2 / 3).sum()), "N_lower_above_0": int((l2.lo > 0).sum()),
                            "largest_median": l2.loc[imax].tolist(), "smallest_median": l2.loc[imin].tolist(),
                            "largest_upper": l2.loc[ihi].tolist(),
                            "pairs_lower_above_0": l2[l2.lo > 0][["a", "b", "lo", "med", "hi"]].values.tolist(),
                            "pairs_upper_above_2_3": l2[l2.hi >= 2 / 3][["a", "b", "lo", "med", "hi"]].values.tolist()}
    print("l2o", {k: v for k, v in OUT["leave_two_out"].items() if not k.startswith("pairs")}, flush=True); save()

    # 9 ---------------------------------------------------------------- post-hoc power
    sig_lit = json.loads((config.RESULTS / "h1_results.json").read_text())["power"]["sigma_int_literature_M0_dex"]
    sig_fit = 10 ** np.percentile(tp.mcmc(x, y, s, "M1", nstep=8000)[:, 2], 50)
    OUT["power_posthoc"] = {"sigma_int_used": sig_lit,
                            "power_B_1_3": tp.power(x, s, sig_lit, 1 / 3), "power_B_2_3": tp.power(x, s, sig_lit, 2 / 3),
                            "sigma_int_fitted": round(float(sig_fit), 3),
                            "power_B_0.5_fitted_sigma": tp.power(x, s, sig_fit, 0.5),
                            "power_B_2_3_fitted_sigma": tp.power(x, s, sig_fit, 2 / 3), "n_sim": 200}
    print("power", OUT["power_posthoc"], flush=True); save()

    # 10 --------------------------------------------------------------- BAT instead of MAXI
    ts = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    o = ob.copy()
    keep = []
    for i, r in o.iterrows():
        if r.origin != "this work":
            keep.append(i); continue
        m = ts[(ts.source == r.source) & (abs(ts.t_peak - r.t_peak) < 0.6)]
        v = m.bat_tau_decay_10_90.iloc[0] if len(m) else np.nan
        if np.isfinite(v) and v > 0:
            o.loc[i, "logtau"] = np.log10(v); o.loc[i, "sig"] = 0.1  # no Monte Carlo error for BAT values
            keep.append(i)
    o = o.loc[keep]
    OUT["bat_for_this_work"] = fit_B(o)
    OUT["bat_for_this_work"]["N_this_work_with_BAT"] = int((o.origin == "this work").sum())
    OUT["bat_for_this_work"]["note"] = "BAT values given a fixed error of 0.1 dex"
    print("bat", OUT["bat_for_this_work"], flush=True); save()

    # 11 --------------------------------------------------------------- other MAXI bands
    sample = pd.read_csv(config.SAMPLE_CSV).set_index("source")
    overrides = load_overrides()
    for band in ("2-20", "2-4", "4-10"):
        o = ob.copy(); keep = []; detail = []
        for i, r in o.iterrows():
            if r.origin != "this work":
                keep.append(i); continue
            row = ts[(ts.source == r.source) & (abs(ts.t_peak - r.t_peak) < 0.6)].iloc[0]
            mid = sample.loc[r.source, "maxi_id"]
            wins = windows_for(r.source, load_maxi(mid), overrides)  # windows are defined in 2-10 keV
            df = load_maxi(mid, band=band)
            w = {"start": row.win_start, "end": row.win_end}
            d = df[(df.mjd >= w["start"]) & (df.mjd <= w["end"])].copy()
            d["flux"] = d.flux - local_baseline(df, w, wins)
            res = yan_yu(d.mjd.values, d.flux.values, d.err.values)
            v = res["tau_decay_10_90"]
            detail.append({"source": r.source, "t_peak_2_10": float(r.t_peak), "t_peak_band": float(res["t_peak"]),
                           "tau_2_10": round(float(10 ** r.logtau), 2), "tau_band": None if not np.isfinite(v) else round(float(v), 2)})
            if np.isfinite(v) and v > 0:
                mc = monte_carlo(d.mjd.values, d.flux.values, d.err.values, n=300)
                lo, hi = mc["tau_decay_10_90_lo"], mc["tau_decay_10_90_hi"]
                sg = 0.5 * (np.log10(hi) - np.log10(lo)) if np.isfinite(lo) and np.isfinite(hi) and lo > 0 else 0.1
                o.loc[i, "logtau"] = np.log10(v); o.loc[i, "sig"] = max(sg, tp.ERR_FLOOR)
                keep.append(i)
        o = o.loc[keep]
        res = fit_B(o)
        dd = [np.log10(k["tau_band"] / k["tau_2_10"]) for k in detail if k["tau_band"]]
        res.update({"N_this_work_measured": int((o.origin == "this work").sum()),
                    "log_ratio_band_over_2_10_median": round(float(np.median(dd)), 3),
                    "log_ratio_SD": round(float(np.std(dd, ddof=1)), 3),
                    "log_ratio_max_abs": round(float(np.max(np.abs(dd))), 3), "detail": detail})
        OUT[f"band_{band}"] = res
        print("band", band, {k: v for k, v in res.items() if k != "detail"}, flush=True); save()

    # 12 --------------------------------------------------------------- bootstrap over systems
    rng = np.random.default_rng(42)
    bs = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        if len(np.unique(x[idx])) < 3:
            continue
        p, _ = tp.fit_ml(x[idx], y[idx], s[idx], "M1")
        bs.append(p[1])
    bs = np.array(bs)
    OUT["bootstrap_systems"] = {"N_boot": int(len(bs)), "B_2.5_50_97.5": [round(float(v), 3) for v in np.percentile(bs, [2.5, 50, 97.5])],
                                "frac_B_gt_0": round(float(np.mean(bs > 0)), 3), "frac_B_ge_2_3": round(float(np.mean(bs >= 2 / 3)), 4),
                                "B_ML_full_sample": round(float(p_ml[1]), 3)}
    print("boot", OUT["bootstrap_systems"], flush=True); save()

    # 13 --------------------------------------------------------------- OLS
    lr = stats.linregress(x, y)
    tcrit = stats.t.ppf(0.975, n - 2)
    OUT["ols"] = {"slope": round(float(lr.slope), 3), "stderr": round(float(lr.stderr), 3),
                  "ci95": [round(float(lr.slope - tcrit * lr.stderr), 3), round(float(lr.slope + tcrit * lr.stderr), 3)],
                  "p_two_sided": round(float(lr.pvalue), 3), "rms_dex": round(float(np.std(y - lr.intercept - lr.slope * x, ddof=2)), 3)}
    print("ols", OUT["ols"], flush=True)

    # 14 --------------------------------------------------------------- GX 339-4 trend with date
    gx = ob[ob.source == "GX 339-4"].sort_values("t_peak")
    tau, p = tp.kendall_perm(gx.t_peak.values, gx.logtau.values, n=10000)
    lr = stats.linregress((gx.t_peak.values - 50000) / 365.25, gx.logtau.values)
    OUT["gx339_trend"] = {"N": int(len(gx)), "kendall_tau": round(tau, 3), "p_perm": round(p, 4),
                          "slope_dex_per_yr": round(float(lr.slope), 4), "slope_stderr": round(float(lr.stderr), 4),
                          "this_work_only": None}
    gm = gx[gx.origin == "this work"]
    tau2, p2 = tp.kendall_perm(gm.t_peak.values, gm.logtau.values, n=10000)
    OUT["gx339_trend"]["this_work_only"] = {"N": int(len(gm)), "kendall_tau": round(tau2, 3), "p_perm": round(p2, 4)}
    print("gx", OUT["gx339_trend"], flush=True)
    save()


if __name__ == "__main__":
    main()
