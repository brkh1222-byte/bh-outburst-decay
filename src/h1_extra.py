"""Extra checks added after the internal referee review (22 Nov 2026). NOT part of the frozen plan.

None of these changes the primary H1 decision rule; they test how fragile the result is.
Writes results/h1_extra.json.

1. Posterior-predictive leave-one-system-out (LOSO) log predictive density for M0/M1/M2
   (the plan's LOSO used maximum-likelihood plug-in parameters), and AICc.
2. Leave-one-system-out influence on the slope B.
3. Posterior probabilities P(B > b) for the theory slopes 0, 1/3, 2/3, 5/6.
4. Variants: spectroscopic orbits only; without the XTE J1550-564 2001 mini-outburst;
   ASM values shifted by the measured +0.16 dex offset; discrepant duplicates inflated;
   per-system variance with an outburst-to-outburst term sigma_out^2/n; tau_d,50-90.
5. Hierarchical model with half-normal priors on the two scatters (prior sensitivity).
6. Validation statistics with window matching (adds MAXI J1820+070 2018, GX 339-4 2021),
   reporting both robust (MAD) and plain standard deviation.
7. BAT checks quoted in the paper (GS 1354-64 in Feb 2019; GX 339-4 hard-only outbursts).
"""
from __future__ import annotations

import json

import emcee
import numpy as np
import pandas as pd
from scipy.special import logsumexp

from src import config
from src import tau_vs_porb as tp
from src.lightcurves import load_bat, load_maxi

SIGMA_OUT = 10 ** -0.562  # hierarchical posterior median (results/h1_hierarchical.txt)


def ll_point(chain, xk, yk, sk, kind):
    th = chain[:, :-1]
    lsig = chain[:, -1]
    if kind == "M0":
        mu = th[:, 0]
    elif kind == "M1":
        mu = th[:, 0] + th[:, 1] * xk
    else:
        mu = th[:, 0] + th[:, 1] * np.minimum(xk, th[:, 2])
    var = sk ** 2 + (10 ** lsig) ** 2
    return -0.5 * ((yk - mu) ** 2 / var + np.log(2 * np.pi * var))


def pp_loso(x, y, s):
    out = {}
    for kind in ("M0", "M1", "M2"):
        pts = []
        for i in range(len(x)):
            m = np.arange(len(x)) != i
            ch = tp.mcmc(x[m], y[m], s[m], kind, nstep=3000, seed=100 + i)
            l = ll_point(ch, x[i], y[i], s[i], kind)
            pts.append(float(logsumexp(l) - np.log(len(l))))
        out[kind] = {"lpd": float(np.sum(pts)), "pointwise": pts}
    return out


def b_summary(x, y, s, seed=0, nstep=4000):
    ch = tp.mcmc(x, y, s, "M1", nstep=nstep, seed=seed)
    q = np.percentile(ch[:, 1], [2.5, 50, 97.5])
    return [round(float(v), 3) for v in q], ch


def hier_halfnormal(ob, scale=0.5, nstep=8000, seed=0):
    groups = [(np.log10(g.porb_d.values), g.logtau.values, g.sig.values) for _, g in ob.groupby("source")]

    def lp(p):
        A, B, s_src, s_out = p
        if not (-1 <= A <= 4 and -3 <= B <= 3 and s_src >= 0 and s_out >= 0):
            return -np.inf
        ll = -0.5 * (s_src ** 2 + s_out ** 2) / scale ** 2
        for x, yv, sv in groups:
            C = np.diag(s_out ** 2 + sv ** 2) + s_src ** 2
            r = yv - (A + B * x)
            ll += -0.5 * (r @ np.linalg.solve(C, r) + np.linalg.slogdet(C)[1] + len(yv) * np.log(2 * np.pi))
        return ll

    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    p0 = np.array([1.5, 0.2, 0.1, 0.2]) + 1e-3 * np.abs(rng.standard_normal((32, 4)))
    sam = emcee.EnsembleSampler(32, 4, lp)
    sam.run_mcmc(p0, nstep, progress=False)
    ch = sam.get_chain(discard=nstep // 4, flat=True)
    q = np.percentile(ch, [2.5, 50, 97.5], axis=0)
    return {"B": q[:, 1].round(3).tolist(), "sigma_src_dex": q[:, 2].round(3).tolist(),
            "sigma_out_dex": q[:, 3].round(3).tolist(), "prior": f"half-normal, scale {scale} dex"}


def validation_window_matched():
    ours = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    ours = ours[ours.flag.isna()]  # confused windows are not a test of the method
    lit = pd.read_csv(config.DATA / "literature_timescales.csv")
    lit = lit[lit.flag.isna()]

    def stats_(d):
        d = np.asarray(d)
        mad = 1.4826 * np.median(np.abs(d - np.median(d)))
        return {"N": int(len(d)), "median": round(float(np.median(d)), 3), "MAD_scatter": round(float(mad), 3),
                "SD": round(float(np.std(d, ddof=1)), 3), "rms": round(float(np.sqrt(np.mean(d ** 2))), 3)}

    res = {}
    for paper, key in (("Saraswati et al. 2025", "TW_vs_S25"), ("Yan & Yu 2015", "TW_vs_YY15")):
        pairs = []
        for _, r in lit[lit.paper == paper].iterrows():
            w = ours[(ours.source == r.source) & (ours.win_start <= r.t_peak_mjd) & (r.t_peak_mjd <= ours.win_end)]
            if len(w) and np.isfinite(r.tau_decay_10_90) and np.isfinite(w.iloc[0].tau_decay_10_90):
                pairs.append({"source": r.source, "t_lit": r.t_peak_mjd, "t_ours": float(w.iloc[0].t_peak),
                              "tau_lit": r.tau_decay_10_90, "tau_ours": float(w.iloc[0].tau_decay_10_90)})
        p = pd.DataFrame(pairs)
        res[key] = stats_(np.log10(p.tau_ours / p.tau_lit)) | {"pairs": p.round(2).to_dict("records")}
    d = lit[lit.dup_group.notna()].groupby("dup_group")
    diffs = [np.log10(g[g.paper == "Yan & Yu 2015"].tau_decay_10_90.iloc[0] /
                      g[g.paper != "Yan & Yu 2015"].tau_decay_10_90.iloc[0]) for _, g in d if g.paper.nunique() == 2]
    res["YY15_vs_S25"] = stats_(diffs)
    return res


def bat_checks():
    out = {}
    b = load_bat("Ginga1354-645")
    sel = b[(b.mjd > 58505) & (b.mjd < 58545)]
    out["GS1354-64_BAT_median_MJD58505-58545_crab"] = round(float(sel.flux.median()), 4)
    m = load_maxi("J1702-487")
    g = load_bat("GX339-4")
    for label, lo, hi in (("2013", 56350, 56650), ("2017-18", 57950, 58250), ("2022", 59580, 59945)):
        mm = m[(m.mjd > lo) & (m.mjd < hi)].flux.rolling(3, center=True).median().max()
        bb = g[(g.mjd > lo) & (g.mjd < hi)].flux.rolling(3, center=True).median().max()
        out[f"GX339-4_{label}_max3d_MAXI2-10_crab"] = round(float(mm), 3)
        out[f"GX339-4_{label}_max3d_BAT15-50_crab"] = round(float(bb), 3)
    return out


def main():
    res = {}
    ob = tp.outburst_table()
    ps = tp.per_source(ob)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values
    n = len(x)

    comp = tp.compare(x, y, s)
    res["AICc"] = {k: round(v["AIC"] + 2 * (tp.NPAR[k] + 1) * (tp.NPAR[k] + 2) / (n - tp.NPAR[k] - 2), 2)
                   for k, v in comp.items()}
    res["LOSO_plugin_ML"] = {k: round(v["LOSO_lpd"], 2) for k, v in comp.items()}
    res["LOSO_posterior_predictive"] = pp_loso(x, y, s)
    res["LOSO_posterior_predictive"]["sources"] = ps.source.tolist()

    qB, ch = b_summary(x, y, s, nstep=8000)
    res["primary_B"] = qB
    res["P_B_gt"] = {str(b): round(float(np.mean(ch[:, 1] > b)), 3) for b in (0, 1 / 3, 0.5, 2 / 3, 5 / 6)}

    infl = {}
    for i, src in enumerate(ps.source):
        m = np.arange(n) != i
        q, _ = b_summary(x[m], y[m], s[m], seed=i)
        _, llm1 = tp.fit_ml(x[m], y[m], s[m], "M1")
        _, llm0 = tp.fit_ml(x[m], y[m], s[m], "M0")
        infl[src] = {"B": q, "dAIC_M1_minus_M0": round(float(2 - 2 * (llm1 - llm0)), 2)}
    res["leave_one_system_out"] = infl

    var = {}

    def add(name, o):
        p = tp.per_source(o)
        q, _ = b_summary(p.x.values, p.logtau.values, p.sig.values)
        var[name] = {"N_sources": len(p), "N_outbursts": len(o), "B": q}

    add("spectroscopic orbits only (drop GRS 1716-249, MAXI J1659-152, MAXI J1803-298)",
        ob[~ob.source.isin(["GRS 1716-249", "MAXI J1659-152", "MAXI J1803-298"])])
    add("dynamical only, GRS 1716-249 counted as candidate",
        ob[(ob.status == "dynamical") & (ob.source != "GRS 1716-249")])
    add("without XTE J1550-564 2001 mini-outburst", ob[~((ob.source == "XTE J1550-564") & (abs(ob.t_peak - 51948) < 5))])
    o = ob.copy()
    o.loc[o.origin != "this work", "logtau"] += 0.16
    add("literature (ASM) values shifted by +0.16 dex", o)
    lit = pd.read_csv(config.DATA / "literature_timescales.csv")
    o = ob.copy()
    for j, r in o[o.origin.str.contains(r"\+")].iterrows():
        g = lit[(lit.source == r.source) & (abs(lit.t_peak_mjd - r.t_peak) < 15)]
        v = np.log10(g.tau_decay_10_90.dropna().values)
        if len(v) == 2:
            o.loc[j, "sig"] = max(r.sig, abs(v[0] - v[1]) / 2)
    add("discrepant duplicates: sigma = max(sigma, half the difference)", o)
    p = ps.copy()
    s_eff = np.sqrt(p.sig.values ** 2 + SIGMA_OUT ** 2 / p.n_outbursts.values)
    q, _ = b_summary(p.x.values, p.logtau.values, s_eff)
    var["per-system variance + sigma_out^2/n (sigma_out = 0.27 dex)"] = {"N_sources": len(p), "N_outbursts": len(ob), "B": q}
    add("tau_d,50-90 (early decay only; exploratory)", tp.outburst_table(col="tau_decay_50_90"))
    res["variants"] = var

    res["hierarchical_halfnormal"] = hier_halfnormal(ob)
    res["validation_window_matched"] = validation_window_matched()
    res["bat_checks"] = bat_checks()

    (config.RESULTS / "h1_extra.json").write_text(json.dumps(res, indent=1))
    short = {k: v for k, v in res.items() if k not in ("LOSO_posterior_predictive", "validation_window_matched")}
    short["LOSO_pp_lpd"] = {k: round(v["lpd"], 2) for k, v in res["LOSO_posterior_predictive"].items() if k != "sources"}
    short["validation"] = {k: {kk: vv for kk, vv in v.items() if kk != "pairs"} for k, v in res["validation_window_matched"].items()}
    print(json.dumps(short, indent=1))


if __name__ == "__main__":
    main()
