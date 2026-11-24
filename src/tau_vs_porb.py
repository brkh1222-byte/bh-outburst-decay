"""T4.0 + T4.1: test whether the decay timescale grows with orbital period (H1).

Follows results/analysis_plan_v1.md exactly. Do not change the primary choices here
without writing a new plan version.

Statistics, in plain words
--------------------------
* One point per SOURCE (the mean log10 tau of its bright outbursts), so a system
  with many outbursts (GX 339-4) cannot dominate.
* Model: log10 tau = A + B log10(P/1 d) + scatter. The scatter has two parts:
  each point's own measurement error, and an "intrinsic scatter" sigma_int
  that the fit estimates (real differences between systems that P does not explain).
  Leaving sigma_int out would make the error bars far too small.
* emcee draws samples from the posterior of (A, B, sigma_int); the 95% credible
  interval of B is the range containing 95% of those samples.
* Model comparison: AIC and BIC penalise extra parameters; leave-one-source-out
  cross-validation fits without each source in turn and scores how well the
  model predicts it, which is the most direct test of a model with few points.
* Kendall's tau: a rank correlation that ignores the error bars entirely; its
  p-value comes from shuffling the periods 10,000 times.
"""
from __future__ import annotations

import json

import emcee
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, stats

from src import config

SIGMA_METHOD = 0.19      # dex, from results/method_check.md
ERR_FLOOR = 0.02         # dex
NAME_ALIASES = {"V4641 Sgr": "SAX J1819.3-2525"}
EXCLUDE_SOURCES = {"MAXI J0637-430"}  # period inferred from its own decay (circular)


# ------------------------------------------------------------------ sample
def periods() -> dict:
    p = {}
    lit = pd.read_csv(config.DATA / "literature_porb.csv")
    for _, r in lit.iterrows():
        p[r.source] = (r.porb_h / 24.0, r.bh_status)
    s = pd.read_csv(config.SAMPLE_CSV)
    for _, r in s.iterrows():
        name = NAME_ALIASES.get(r.source, r.source)
        if np.isfinite(r.porb_d) and r.porb_method != "inferred from decay":
            p[name] = (r.porb_d, r.bh_status)  # verified value wins
    for k in EXCLUDE_SOURCES:
        p.pop(k, None)
    return p


def outburst_table(col="tau_decay_10_90", include_reflares=False, include_faint=False,
                   ours_file="timescales_maxi.csv", smooth=False, sigma_method=SIGMA_METHOD) -> pd.DataFrame:
    """One row per outburst with log10 tau and its error, following the plan's priority rules."""
    P = periods()
    ours = pd.read_csv(config.RESULTS / ours_file)
    ours["source"] = ours.source.replace(NAME_ALIASES)
    ours = ours[ours.flag.isna() | (ours.flag == "")]
    lit = pd.read_csv(config.DATA / "literature_timescales.csv")
    lit = lit[lit.flag.isna()]
    rows = []
    for _, r in ours.iterrows():
        if r.source not in P:
            continue
        is_reflare = "re-flare" in [part.strip() for part in str(r.win_note).split(";")]
        if not include_reflares and is_reflare:
            continue
        if not include_faint and not r.bright:
            continue
        val = r[f"{col}_smooth"] if smooth else r[col]
        lo, hi = r.get(f"{col}_lo"), r.get(f"{col}_hi")
        if not (np.isfinite(val) and val > 0):
            continue
        sig = 0.5 * (np.log10(hi) - np.log10(lo)) if np.isfinite(lo) and np.isfinite(hi) and lo > 0 else 0.1
        rows.append({"source": r.source, "t_peak": r.t_peak, "logtau": np.log10(val),
                     "sig": max(sig, ERR_FLOOR), "origin": "this work", "era": r.era})
    # Every window we measured (bright or faint, flagged or not) "covers" a literature
    # outburst whose peak lies inside it: our value or our decision wins (plan item 3a).
    allours = pd.read_csv(config.RESULTS / ours_file)
    allours["source"] = allours.source.replace(NAME_ALIASES)
    windows = allours[["source", "win_start", "win_end"]].values.tolist()
    maxi_ids = {NAME_ALIASES.get(r.source, r.source): r.maxi_id
                for _, r in pd.read_csv(config.SAMPLE_CSV).iterrows() if isinstance(r.maxi_id, str)}
    maxi_cache = {}
    for (src, grp), g in lit.groupby(["source", lit.dup_group.fillna(lit.index.to_series().astype(str))]):
        if src not in P:
            continue
        t0 = g.t_peak_mjd.mean()
        if any(s == src and a <= t0 <= b for s, a, b in windows):
            continue  # this work measured it (bright or not): our value/decision wins
        if not include_faint and not (g.f_peak_crab > 0.1).any():
            continue
        # MAXI-era outburst that our detection did not pick up: apply the plan's brightness
        # rule with our own 2-10 keV data (implementation clarification, see plan v1 note).
        if not include_faint and t0 > 55054 and src in maxi_ids:
            if src not in maxi_cache:
                from src.lightcurves import load_maxi
                maxi_cache[src] = load_maxi(maxi_ids[src])
            d = maxi_cache[src]
            near = d[(d.mjd > t0 - 15) & (d.mjd < t0 + 15)]
            if len(near) and near.flux.max() < 0.1:
                continue
        vals, errs = [], []
        for _, r in g.iterrows():
            v, e = r[col], r[f"{col}_err"]
            if np.isfinite(v) and v > 0:
                vals.append(np.log10(v))
                errs.append(max(e / (v * np.log(10)) if np.isfinite(e) else 0.1, ERR_FLOOR))
        if not vals:
            continue
        sig = np.sqrt(np.mean(np.square(errs)) / len(errs) + sigma_method ** 2)
        rows.append({"source": src, "t_peak": t0, "logtau": float(np.mean(vals)), "sig": sig,
                     "origin": " + ".join(sorted(set(g.paper))), "era": "literature"})
    df = pd.DataFrame(rows)
    df["porb_d"] = df.source.map(lambda s: P[s][0])
    df["status"] = df.source.map(lambda s: P[s][1])
    return df


def per_source(ob: pd.DataFrame) -> pd.DataFrame:
    g = ob.groupby("source")
    out = pd.DataFrame({
        "logtau": g.logtau.mean(),
        "sig": g.sig.apply(lambda s: np.sqrt(np.sum(np.square(s))) / len(s)),
        "n_outbursts": g.size(),
        "porb_d": g.porb_d.first(),
        "status": g.status.first(),
        "origins": g.origin.apply(lambda s: ", ".join(sorted(set(s)))),
    }).reset_index()
    out["x"] = np.log10(out.porb_d)
    return out


# ------------------------------------------------------------------ models
def model(theta, x, kind):
    if kind == "M0":
        return np.full_like(x, theta[0])
    if kind == "M1":
        return theta[0] + theta[1] * x
    return theta[0] + theta[1] * np.minimum(x, theta[2])  # M2


NPAR = {"M0": 1, "M1": 2, "M2": 3}  # plus sigma_int


def loglike(params, x, y, s, kind):
    *theta, lsig = params
    var = s ** 2 + (10 ** lsig) ** 2
    r = y - model(np.array(theta), x, kind)
    return -0.5 * np.sum(r ** 2 / var + np.log(2 * np.pi * var))


def logprior(params, kind):
    *theta, lsig = params
    if not -3 <= lsig <= 0.5 or not -1 <= theta[0] <= 4:
        return -np.inf
    if kind != "M0" and not -3 <= theta[1] <= 3:
        return -np.inf
    if kind == "M2" and not -0.7 <= theta[2] <= 0.7:
        return -np.inf
    return 0.0


def fit_ml(x, y, s, kind):
    best = None
    starts = {"M0": [[np.mean(y), -1]], "M1": [[np.mean(y), b, -1] for b in (-0.5, 0, 0.5)],
              "M2": [[np.mean(y), b, xb, -1] for b in (0, 0.5, 1) for xb in (-0.4, 0, 0.4)]}[kind]
    for p0 in starts:
        res = optimize.minimize(lambda p: -(loglike(p, x, y, s, kind) + (0 if np.isfinite(logprior(p, kind)) else -1e10)),
                                p0, method="Nelder-Mead", options={"maxiter": 20000, "xatol": 1e-6, "fatol": 1e-8})
        if best is None or res.fun < best.fun:
            best = res
    return best.x, -best.fun


def mcmc(x, y, s, kind="M1", nwalk=32, nstep=4000, seed=0):
    p_ml, _ = fit_ml(x, y, s, kind)
    np.random.seed(seed % 2**32)  # emcee draws from numpy's global RNG: seed it so runs are reproducible
    rng = np.random.default_rng(seed)
    ndim = len(p_ml)
    p0 = p_ml + 1e-3 * rng.standard_normal((nwalk, ndim))
    lp = lambda p: (logprior(p, kind) + loglike(p, x, y, s, kind)) if np.isfinite(logprior(p, kind)) else -np.inf
    sampler = emcee.EnsembleSampler(nwalk, ndim, lp)
    sampler.run_mcmc(p0, nstep, progress=False)
    return sampler.get_chain(discard=nstep // 4, flat=True)


def compare(x, y, s):
    n = len(x)
    out = {}
    for kind in ("M0", "M1", "M2"):
        p, ll = fit_ml(x, y, s, kind)
        k = NPAR[kind] + 1
        # leave-one-source-out cross-validated log predictive density
        cv = 0.0
        for i in range(n):
            m = np.arange(n) != i
            pi, _ = fit_ml(x[m], y[m], s[m], kind)
            *th, lsig = pi
            var = s[i] ** 2 + (10 ** lsig) ** 2
            mu = model(np.array(th), x[i:i + 1], kind)[0]
            cv += -0.5 * ((y[i] - mu) ** 2 / var + np.log(2 * np.pi * var))
        out[kind] = {"params": [float(v) for v in p], "logL": float(ll), "AIC": float(2 * k - 2 * ll),
                     "BIC": float(k * np.log(n) - 2 * ll), "LOSO_lpd": float(cv)}
    return out


def kendall_perm(x, y, n=10000, seed=0):
    tau = stats.kendalltau(x, y).statistic
    rng = np.random.default_rng(seed)
    null = np.array([stats.kendalltau(rng.permutation(x), y).statistic for _ in range(n)])
    return float(tau), float((np.sum(np.abs(null) >= abs(tau)) + 1) / (n + 1))


def power(x, s, sigma_int, b_true=0.5, nsim=200, seed=3):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(nsim):
        y = 1.3 + b_true * x + rng.normal(0, np.sqrt(s ** 2 + sigma_int ** 2))
        ch = mcmc(x, y, s, "M1", nwalk=16, nstep=1200, seed=int(rng.integers(1e9)))
        if np.percentile(ch[:, 1], 2.5) > 0:
            hits += 1
    return hits / nsim


def summarize(ch):
    q = np.percentile(ch, [2.5, 16, 50, 84, 97.5], axis=0)
    return {"A": q[:, 0].tolist(), "B": q[:, 1].tolist(), "log10_sigma_int": q[:, -1].tolist()}


def run_variant(name, **kw):
    ob = outburst_table(**kw)
    ps = per_source(ob)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values
    ch = mcmc(x, y, s, "M1")
    tau, p = kendall_perm(x, y, n=2000)
    q = np.percentile(ch[:, 1], [2.5, 50, 97.5])
    return {"variant": name, "N_sources": len(ps), "N_outbursts": len(ob),
            "B_median": q[1], "B_lo95": q[0], "B_hi95": q[2], "kendall_tau": tau, "kendall_p": p}


def main():
    res = {}
    # ---- primary sample
    ob = outburst_table()
    ps = per_source(ob)
    ob.to_csv(config.RESULTS / "h1_outbursts_primary.csv", index=False)
    ps.to_csv(config.RESULTS / "h1_sources_primary.csv", index=False)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values

    # ---- power check first (uses x and errors, and sigma_int of the literature-only sample)
    lit_ps = ps[ps.origins.str.contains("Yan|Saraswati") & ~ps.origins.str.contains("this work")]
    p0, _ = fit_ml(lit_ps.x.values, lit_ps.logtau.values, lit_ps.sig.values, "M0")
    sig_int_lit = 10 ** p0[-1]
    res["power"] = {"sigma_int_literature_M0_dex": float(sig_int_lit),
                    "power_B0.5": power(x, s, sig_int_lit, 0.5),
                    "power_B0.3": power(x, s, sig_int_lit, 0.3)}
    print("power:", res["power"])

    # ---- primary H1 result
    ch = mcmc(x, y, s, "M1", nstep=8000)
    res["H1_M1_posterior"] = summarize(ch)
    res["model_comparison"] = compare(x, y, s)
    res["kendall"] = dict(zip(["tau", "p_perm"], kendall_perm(x, y)))
    print(json.dumps({k: res[k] for k in ("H1_M1_posterior", "kendall")}, indent=1))
    print(json.dumps(res["model_comparison"], indent=1))

    # ---- robustness variants
    variants = [
        run_variant("primary"),
        run_variant("+ re-flares", include_reflares=True),
        run_variant("+ faint outbursts", include_faint=True),
        run_variant("raw MAXI (no baseline subtraction)", ours_file="timescales_maxi_raw.csv"),
        run_variant("smoothed crossings", smooth=True),
        run_variant("sigma_method = 0", sigma_method=0.0),
        run_variant("sigma_method = 0.3", sigma_method=0.3),
    ]
    obd = ob[ob.status == "dynamical"]
    psd = per_source(obd)
    chd = mcmc(psd.x.values, psd.logtau.values, psd.sig.values, "M1")
    qd = np.percentile(chd[:, 1], [2.5, 50, 97.5])
    variants.append({"variant": "dynamical BHs only", "N_sources": len(psd), "N_outbursts": len(obd),
                     "B_median": qd[1], "B_lo95": qd[0], "B_hi95": qd[2],
                     **dict(zip(["kendall_tau", "kendall_p"], kendall_perm(psd.x.values, psd.logtau.values, 2000)))})
    for label, sel in (("this work only (2016-2026 + MAXI era)", ob.origin == "this work"),
                       ("literature only", ob.origin != "this work")):
        o = ob[sel]
        pss = per_source(o)
        if len(pss) >= 4:
            c = mcmc(pss.x.values, pss.logtau.values, pss.sig.values, "M1")
            q = np.percentile(c[:, 1], [2.5, 50, 97.5])
            variants.append({"variant": label, "N_sources": len(pss), "N_outbursts": len(o),
                             "B_median": q[1], "B_lo95": q[0], "B_hi95": q[2],
                             **dict(zip(["kendall_tau", "kendall_p"], kendall_perm(pss.x.values, pss.logtau.values, 2000)))})
    rob = pd.DataFrame(variants)
    rob.to_csv(config.RESULTS / "h1_robustness.csv", index=False)
    print(rob.round(3).to_string())

    # ---- H2 (exploratory): rise time
    obr = outburst_table(col="tau_rise_10_90")
    psr = per_source(obr)
    chr_ = mcmc(psr.x.values, psr.logtau.values, psr.sig.values, "M1")
    res["H2_rise_M1_posterior"] = summarize(chr_)
    res["H2_kendall"] = dict(zip(["tau", "p_perm"], kendall_perm(psr.x.values, psr.logtau.values)))
    res["H2_N_sources"] = len(psr)
    print("H2:", res["H2_rise_M1_posterior"]["B"], res["H2_kendall"])

    (config.RESULTS / "h1_results.json").write_text(json.dumps(res, indent=1))
    figure(ob, ps, ch, res["model_comparison"])


def figure(ob, ps, ch, comp):
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    colors = {"this work": "tab:blue"}
    for _, r in ob.iterrows():
        c = colors.get(r.origin, "0.6")
        ax.plot(r.porb_d, 10 ** r.logtau, "o", ms=3.5, color=c, alpha=0.45, mec="none")
    ax.errorbar(ps.porb_d, 10 ** ps.logtau,
                yerr=[10 ** ps.logtau - 10 ** (ps.logtau - ps.sig), 10 ** (ps.logtau + ps.sig) - 10 ** ps.logtau],
                fmt="s", ms=6, color="k", mfc="white", capsize=2, lw=1, label="per-source mean", zorder=5)
    for _, r in ps.iterrows():
        ax.annotate(r.source, (r.porb_d, 10 ** r.logtau), fontsize=6, xytext=(4, 3), textcoords="offset points")
    xx = np.linspace(np.log10(ps.porb_d.min()) - 0.2, np.log10(ps.porb_d.max()) + 0.2, 100)
    draws = ch[np.random.default_rng(0).choice(len(ch), 300)]
    lines = np.array([d[0] + d[1] * xx for d in draws])
    lo, mid, hi = np.percentile(lines, [2.5, 50, 97.5], axis=0)
    ax.fill_between(10 ** xx, 10 ** lo, 10 ** hi, color="tab:red", alpha=0.15, label="M1 power law, 95% band")
    ax.plot(10 ** xx, 10 ** mid, color="tab:red", lw=1.5)
    a0 = comp["M0"]["params"][0]
    ax.axhline(10 ** a0, color="0.4", ls="--", lw=1, label="M0 constant")
    p2 = comp["M2"]["params"]
    ax.plot(10 ** xx, 10 ** (p2[0] + p2[1] * np.minimum(xx, p2[2])), color="tab:green", lw=1, ls=":", label="M2 saturating")
    ax.plot([], [], "o", color="tab:blue", alpha=0.5, label="outbursts, this work")
    ax.plot([], [], "o", color="0.6", alpha=0.5, label="outbursts, Yan & Yu / Saraswati")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$P_{\rm orb}$ (d)"); ax.set_ylabel(r"$\tau_{\rm d,10-90\%}$ (d)")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(config.RESULTS / "fig_tau_porb.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
