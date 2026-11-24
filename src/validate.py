"""T3.6 + T3.7: validation gate. Writes results/method_check.md and results/injection_recovery.csv.

Four checks
-----------
1. This work (MAXI 2-10 keV) vs Yan & Yu 2015 (RXTE/ASM 2-12 keV) for outbursts
   both instruments saw (Aug 2009 - 2011).
2. This work vs Saraswati et al. 2025 for the same outbursts (MAXI era).
3. Yan & Yu vs Saraswati for outbursts both papers measured from the SAME ASM
   data. This measures how reproducible the "same" two-point method is
   between groups.
4. Injection-recovery: synthetic outbursts with known rise/decay added to real
   quiescent MAXI light curves (so they inherit MAXI's real noise, baseline
   and gaps), then measured with the same code.

Comparisons use log10(tau_this / tau_other): the median is the offset, and the
scatter is 1.4826 x MAD (a robust standard deviation, insensitive to one bad pair).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config
from src.lightcurves import load_maxi
from src.timescales import yan_yu

MATCH_D = 20.0


def robust_stats(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan, np.nan, 0
    med = np.median(x)
    return med, 1.4826 * np.median(np.abs(x - med)), len(x)


def match(a: pd.DataFrame, b: pd.DataFrame, ta="t_peak", tb="t_peak_mjd") -> pd.DataFrame:
    rows = []
    for _, r in a.iterrows():
        m = b[(b.source == r.source) & ((b[tb] - r[ta]).abs() <= MATCH_D)]
        if len(m):
            j = (m[tb] - r[ta]).abs().idxmin()
            rows.append((r, b.loc[j]))
    return rows


def compare_table(pairs, label_a, label_b, cols=("tau_decay_10_90", "tau_rise_10_90")):
    lines = [f"| Source | Peak MJD ({label_a} / {label_b}) | " +
             " | ".join(f"{c} ({label_a} / {label_b})" for c in cols) + " |",
             "|---|---|" + "---|" * len(cols)]
    logr = {c: [] for c in cols}
    for a, b in pairs:
        cells = []
        for c in cols:
            va, vb = a.get(c, np.nan), b.get(c, np.nan)
            cells.append(f"{va:.1f} / {vb:.1f}")
            if np.isfinite(va) and np.isfinite(vb) and va > 0 and vb > 0:
                logr[c].append(np.log10(va / vb))
        ta = a.get("t_peak", a.get("t_peak_mjd"))
        tb = b.get("t_peak_mjd", b.get("t_peak"))
        lines.append(f"| {a.source} | {ta:.0f} / {tb:.0f} | " + " | ".join(cells) + " |")
    stats = {c: robust_stats(v) for c, v in logr.items()}
    lines.append("")
    for c, (med, sig, n) in stats.items():
        lines.append(f"- {c}: median log10 ratio {med:+.2f} dex (factor {10**med:.2f}), "
                     f"robust scatter {sig:.2f} dex, N = {n}")
    return "\n".join(lines), stats


# ---------------------------------------------------------------- injection
QUIET = [  # (MAXI id, MJD range with no outburst) -- chosen from results/overview/*.png
    ("J1820+071", 55100, 58150),   # high latitude, clean
    ("J1719-250", 58100, 61300),   # GRS 1716-249 after its outburst
    ("J1746-322", 58000, 59900),   # H1743-322: Galactic-Centre region, non-zero floor
    ("J1849-030", 55100, 58600),   # EXO 1846-031 before 2019
]


def fred(t, t0, f_peak, tau_r, tau_d):
    """Exponential rise to the peak at t0, then exponential decay."""
    return np.where(t < t0, f_peak * np.exp((t - t0) / tau_r), f_peak * np.exp(-(t - t0) / tau_d))


def injection_recovery(n_per=12, seed=1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    quiet = {mid: load_maxi(mid) for mid, _, _ in QUIET}
    for mid, lo, hi in QUIET:
        q = quiet[mid]
        q = q[(q.mjd >= lo) & (q.mjd <= hi)]
        for f_peak in (0.1, 0.3, 1.0, 3.0):
            for tau_d in (5, 10, 20, 40, 80):
                for k in range(n_per):
                    tau_r = rng.uniform(2, 15)
                    t0 = rng.uniform(lo + 6 * tau_r + 20, hi - 6 * tau_d - 20)
                    w = q[(q.mjd > t0 - 6 * tau_r - 15) & (q.mjd < t0 + 5 * tau_d + 15)]
                    if len(w) < 20:
                        continue
                    model = fred(w.mjd.values, t0, f_peak, tau_r, tau_d)
                    # source-count noise grows with flux: ~2% of the flux per day (MAXI bright-source level)
                    extra = 0.02 * model
                    flux = w.flux.values + model + rng.normal(0, 1, len(w)) * extra
                    err = np.hypot(w.err.values, extra)
                    base = np.median(q.flux.values)
                    r = yan_yu(w.mjd.values, flux - base, err)
                    rows.append({"quiet_field": mid, "f_peak": f_peak, "tau_d_true": tau_d, "tau_r_true": tau_r,
                                 "tau_d_meas": r["tau_decay_10_90"], "tau_r_meas": r["tau_rise_10_90"],
                                 "shape_ratio": r["shape_ratio_decay"]})
    return pd.DataFrame(rows)


def main():
    ours = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    ours = ours[ours.flag.isna() | (ours.flag == "")]
    lit = pd.read_csv(config.DATA / "literature_timescales.csv")
    yy = lit[lit.paper == "Yan & Yu 2015"]
    sa = lit[(lit.paper == "Saraswati et al. 2025") & (lit.flag.isna())]
    out = ["# Method check (validation gate T3.7)", "",
           "Generated by `src/validate.py`. Timescales in days; 'this work' = MAXI 2-10 keV, "
           "baseline-subtracted, Yan & Yu two-point rule.", ""]

    out += ["## 1. This work vs Yan & Yu 2015 (same outbursts, MAXI vs RXTE/ASM)", ""]
    t1, s1 = compare_table(match(ours, yy), "this", "YY15")
    out += [t1, ""]

    out += ["## 2. This work vs Saraswati et al. 2025 (same outbursts)", ""]
    t2, s2 = compare_table(match(ours, sa), "this", "S25")
    out += [t2, ""]

    out += ["## 3. Yan & Yu 2015 vs Saraswati et al. 2025 (same outbursts, same ASM data)", ""]
    yy_named = yy.rename(columns={"t_peak_mjd": "t_peak"})
    t3, s3 = compare_table(match(yy_named, sa), "YY15", "S25")
    out += [t3, ""]

    inj = injection_recovery()
    inj.to_csv(config.RESULTS / "injection_recovery.csv", index=False)
    inj["logr_d"] = np.log10(inj.tau_d_meas / inj.tau_d_true)
    out += ["## 4. Injection-recovery (exponential rise and decay injected into real quiescent MAXI data)", "",
            "| Peak (Crab) | true tau_d (d) | N | recovered fraction | median log10(meas/true) | robust scatter (dex) |",
            "|---|---|---|---|---|---|"]
    for (fp, td), g in inj.groupby(["f_peak", "tau_d_true"]):
        med, sig, n = robust_stats(g.logr_d)
        out.append(f"| {fp} | {td} | {len(g)} | {n/len(g):.2f} | {med:+.3f} | {sig:.3f} |")
    out.append("")

    # Summary and the method-scatter term used in the analysis
    sig_between = np.nanmax([s1["tau_decay_10_90"][1], s2["tau_decay_10_90"][1], s3["tau_decay_10_90"][1]])
    out += ["## Summary", "",
            f"- Between-study scatter in tau_d,10-90 (largest of checks 1-3): {sig_between:.2f} dex. "
            "This is added in quadrature to every literature value's error in the tau-P_orb fit "
            "(`sigma_method`).",
            "- Read the tables above before trusting the merged analysis; see the QC plots in results/qc/.", ""]
    (config.RESULTS / "method_check.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
