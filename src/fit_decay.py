"""T3.3: decay-shape fits (exponential, linear, exponential -> linear). EXPLORATORY.

Not part of analysis plan v1. The H1 test uses the two-point timescales only.

What is fitted
--------------
For each bright, unflagged main outburst in results/timescales_maxi.csv, the
baseline-subtracted MAXI 2-10 keV daily light curve from the peak to the end of
the outburst window, in units of the daily peak flux, with t = days since peak.

Three models (King & Ritter 1998; Shahbaz, Charles & King 1998):
  exp     F = F0 exp(-t / tau)                           2 parameters
  linear  F = F0 (1 - t / t_end), zero after t_end       2 parameters
  broken  exponential until t_b, then a straight line    4 parameters
          that starts at the same flux and reaches zero
          t_lin days later:
              F = F0 exp(-t/tau)                      t <  t_b
              F = F_b (1 - (t - t_b) / t_lin)         t >= t_b,  F_b = F0 exp(-t_b/tau)
          (the flux is continuous at t_b; the slope is free to change)

Two stages
----------
1. lmfit least squares with the MAXI errors as weights, started from several
   points. Gives a starting point and the reduced chi-square. The reduced
   chi-square is far above 1 for almost every outburst: real light curves have
   flares, dips and state transitions that no smooth model follows, so the
   MAXI error bars alone are not the right noise model.
2. emcee with one extra parameter, a fractional "jitter" j, so that each point
   has variance err^2 + (j * model)^2 + (j * J_FLOOR)^2. The jitter absorbs the
   real variability around the smooth model and gives honest parameter
   uncertainties. Models are compared with BIC computed from the highest
   likelihood found (jitter included, so the three models are on equal terms).

Priors (flat inside the ranges): F0 in [0.2, 3]; log10 tau, log10 t_end and
log10 t_lin in [0, 3.5]; t_b in [1, T - 1] with T the length of the fitted
stretch; log10 j in [-3, 0.5].

Limits to keep in mind when reading the output
----------------------------------------------
* The fit follows the 2-10 keV flux, not the accretion rate; state transitions
  change the flux in the band without any change in the disc.
* BIC differences below about 6 are not strong evidence.
* "broken" contains "exp" (t_b near T) and "linear" (t_b near 0) as limits.

Outputs: results/decay_fits.csv, results/decay_fits_summary.md,
         results/decay_fits/<source>_<peak MJD>.png
Usage:   nice .venv/bin/python -m src.fit_decay [--source "GX 339-4"] [--steps 3000]
"""
from __future__ import annotations

import argparse

import emcee
import lmfit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import config
from src.lightcurves import load_maxi
from src.timescales import spike_mask

OUT_DIR = config.RESULTS / "decay_fits"
J_FLOOR = 0.02   # jitter floor in peak units, so the variance cannot vanish where the model is ~0
MIN_POINTS = 12
MODELS = ("exp", "linear", "broken")
PNAMES = {"exp": ["F0", "ltau"], "linear": ["F0", "ltend"], "broken": ["F0", "ltau", "tb", "ltlin"]}


# ------------------------------------------------------------------ models
def model(kind: str, p, t):
    if kind == "exp":
        return p[0] * np.exp(-t / 10 ** p[1])
    if kind == "linear":
        return np.clip(p[0] * (1 - t / 10 ** p[1]), 0, None)
    f0, ltau, tb, ltlin = p
    tau = 10 ** ltau
    fb = f0 * np.exp(-tb / tau)
    return np.where(t < tb, f0 * np.exp(-t / tau), np.clip(fb * (1 - (t - tb) / 10 ** ltlin), 0, None))


def bounds(kind: str, T: float):
    b = {"F0": (0.2, 3.0), "ltau": (0.0, 3.5), "ltend": (0.0, 3.5), "ltlin": (0.0, 3.5), "tb": (1.0, T - 1.0)}
    return [b[n] for n in PNAMES[kind]]


def starts(kind: str, T: float):
    if kind == "exp":
        return [[1.0, np.log10(x)] for x in (5, 15, 40, 100)]
    if kind == "linear":
        return [[1.0, np.log10(x)] for x in (0.5 * T, T, 2 * T)]
    return [[1.0, np.log10(tau), fb * T, np.log10(tl)]
            for tau in (10, 30, 100) for fb in (0.25, 0.5, 0.75) for tl in (0.3 * T, T)]


# ------------------------------------------------------------------ stage 1: lmfit
def fit_lmfit(kind, t, f, e):
    T = t.max()
    best = None
    for p0 in starts(kind, T):
        pars = lmfit.Parameters()
        for n, v, (lo, hi) in zip(PNAMES[kind], p0, bounds(kind, T)):
            pars.add(n, value=float(np.clip(v, lo + 1e-6, hi - 1e-6)), min=lo, max=hi)
        try:
            r = lmfit.minimize(lambda q: (f - model(kind, [q[n].value for n in PNAMES[kind]], t)) / e,
                               pars, method="least_squares")
        except Exception:
            continue
        if best is None or r.chisqr < best.chisqr:
            best = r
    return best


# ------------------------------------------------------------------ stage 2: emcee with jitter
def lnprob(theta, kind, t, f, e, bnd):
    *p, lj = theta
    if not -3 <= lj <= 0.5:
        return -np.inf
    for v, (lo, hi) in zip(p, bnd):
        if not lo <= v <= hi:
            return -np.inf
    m = model(kind, p, t)
    j = 10 ** lj
    var = e ** 2 + (j * m) ** 2 + (j * J_FLOOR) ** 2
    return -0.5 * np.sum((f - m) ** 2 / var + np.log(2 * np.pi * var))


def fit_emcee(kind, t, f, e, p_start, nwalk=32, nstep=3000, seed=0):
    bnd = bounds(kind, t.max())
    np.random.seed(seed % 2 ** 32)  # emcee uses numpy's global generator
    rng = np.random.default_rng(seed)
    x0 = np.array(list(p_start) + [-1.0])
    lo = np.array([b[0] for b in bnd] + [-3.0])
    hi = np.array([b[1] for b in bnd] + [0.5])
    p0 = np.clip(x0 + 1e-2 * rng.standard_normal((nwalk, len(x0))) * np.maximum(np.abs(x0), 0.1),
                 lo + 1e-4, hi - 1e-4)
    s = emcee.EnsembleSampler(nwalk, len(x0), lnprob, args=(kind, t, f, e, bnd))
    s.run_mcmc(p0, nstep, progress=False)
    chain = s.get_chain(discard=nstep // 3, flat=True)
    lp = s.get_log_prob(discard=nstep // 3, flat=True)
    try:
        act = float(np.max(s.get_autocorr_time(tol=0)))
    except Exception:
        act = np.nan
    return chain, lp, act


# ------------------------------------------------------------------ driver
def decay_data(row, maxi_id):
    d = load_maxi(maxi_id)
    d = d[(d.mjd >= row.win_start) & (d.mjd <= row.win_end)].copy()
    d = d[~spike_mask(d.flux.values, d.err.values)]
    d["flux"] = d.flux - row.baseline
    d = d[d.mjd >= row.t_peak]
    t = (d.mjd - row.t_peak).values
    return t, d.flux.values / row.f_peak, d.err.values / row.f_peak


def fit_outburst(row, maxi_id, nstep=3000, plot=True):
    t, f, e = decay_data(row, maxi_id)
    if len(t) < MIN_POINTS:
        return []
    recs, curves = [], {}
    for k, kind in enumerate(MODELS):
        r1 = fit_lmfit(kind, t, f, e)
        if r1 is None:
            continue
        p1 = [r1.params[n].value for n in PNAMES[kind]]
        seed = int(abs(row.t_peak) * 10) + 7 * k
        chain, lp, act = fit_emcee(kind, t, f, e, p1, nstep=nstep, seed=seed)
        npar = chain.shape[1]
        lnl_max = float(lp.max())  # priors are flat, so max posterior = max likelihood inside the box
        q = np.percentile(chain, [16, 50, 84], axis=0)
        rec = {"source": row.source, "t_peak": row.t_peak, "f_peak": row.f_peak, "era": row.era,
               "model": kind, "n_points": len(t), "t_span_d": float(t.max()),
               "chi2_red_lmfit": float(r1.chisqr / max(len(t) - len(p1), 1)),
               "lnL_max": lnl_max, "BIC": float(npar * np.log(len(t)) - 2 * lnl_max),
               "autocorr_max": act, "n_steps": nstep}
        for i, n in enumerate(PNAMES[kind] + ["ljit"]):
            rec[f"{n}_lo"], rec[f"{n}_med"], rec[f"{n}_hi"] = q[:, i]
        for n in ("ltau", "ltend", "ltlin"):
            if n in PNAMES[kind]:
                i = PNAMES[kind].index(n)
                nm = n[1:]
                rec[f"{nm}_lo"], rec[f"{nm}_med"], rec[f"{nm}_hi"] = 10 ** q[:, i]
        recs.append(rec)
        curves[kind] = chain[np.argmax(lp)][:-1]
    if not recs:
        return []
    bmin = min(r["BIC"] for r in recs)
    for r in recs:
        r["dBIC"] = r["BIC"] - bmin
        r["two_point_tau_10_90"] = row.tau_decay_10_90
        r["shape_ratio"] = row.shape_ratio_decay
    if plot:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
        tt = np.linspace(0, t.max(), 400)
        cols = {"exp": "#0072B2", "linear": "#E69F00", "broken": "#D55E00"}
        for ax in axes:
            ax.errorbar(t, f, e, fmt=".", ms=3, lw=0.5, color="0.4", zorder=1)
            for r in recs:
                ax.plot(tt, model(r["model"], curves[r["model"]], tt), color=cols[r["model"]], lw=1.3,
                        label=f"{r['model']}  dBIC = {r['dBIC']:.1f}")
            ax.set_xlabel("days since peak")
        axes[0].set_ylabel("flux / daily peak")
        axes[1].set_yscale("log"); axes[1].set_ylim(0.01, 3)
        axes[0].legend(fontsize=7)
        fig.suptitle(f"{row.source}  peak MJD {row.t_peak:.0f}  (two-point tau_d = {row.tau_decay_10_90:.1f} d, "
                     f"shape ratio {row.shape_ratio_decay:.2f})", fontsize=9)
        fig.tight_layout()
        tag = row.source.replace(" ", "_").replace("+", "p")
        fig.savefig(OUT_DIR / f"{tag}_{row.t_peak:.0f}.png", dpi=110)
        plt.close(fig)
    return recs


def select_outbursts() -> pd.DataFrame:
    ts = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    ok = (ts.flag.isna() | (ts.flag == "")) & ts.bright
    ok &= ~ts.win_note.fillna("").apply(lambda s: "re-flare" in [p.strip() for p in s.split(";")])
    return ts[ok].reset_index(drop=True)


def summary(df: pd.DataFrame) -> str:
    best = df[df.dBIC == 0]
    n = len(best)
    lines = ["# Decay-shape fits (T3.3, exploratory; not in analysis plan v1)", "",
             "Generated by `src/fit_decay.py`. One row per outburst in `results/decay_fits.csv` per model.",
             "Model with the lowest BIC, and how many of those wins are clear (next-best model worse by more than 6):", ""]
    lines.append("| Preferred model | N | of which clear (dBIC of runner-up > 6) |")
    lines.append("|---|---|---|")
    for kind in MODELS:
        b = best[best.model == kind]
        clear = 0
        for _, r in b.iterrows():
            others = df[(df.source == r.source) & (df.t_peak == r.t_peak) & (df.model != kind)]
            clear += int(others.dBIC.min() > 6)
        lines.append(f"| {kind} | {len(b)} | {clear} |")
    lines += ["", f"Outbursts fitted: {n}.", "",
              "| Source | Peak MJD | era | best | dBIC exp | dBIC linear | dBIC broken | tau exp (d) | tau broken (d) | t_b (d) | jitter (best) | chi2_red lmfit (best) | two-point tau_d | shape ratio |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (src, tp), g in df.groupby(["source", "t_peak"], sort=False):
        g = g.set_index("model")
        b = g.dBIC.idxmin()
        ex, br = g.loc["exp"], g.loc["broken"]
        lines.append(
            f"| {src} | {tp:.1f} | {ex.era} | {b} | {ex.dBIC:.1f} | {g.loc['linear'].dBIC:.1f} | {br.dBIC:.1f} | "
            f"{ex.tau_med:.1f} [{ex.tau_lo:.1f}, {ex.tau_hi:.1f}] | {br.tau_med:.1f} [{br.tau_lo:.1f}, {br.tau_hi:.1f}] | "
            f"{br.tb_med:.0f} [{br.tb_lo:.0f}, {br.tb_hi:.0f}] | {10 ** g.loc[b].ljit_med:.2f} | {g.loc[b].chi2_red_lmfit:.1f} | "
            f"{ex.two_point_tau_10_90:.1f} | {ex.shape_ratio:.2f} |")
    ex = df[df.model == "exp"]
    r = np.log10(ex.tau_med / ex.two_point_tau_10_90)
    lines += ["", f"Exponential-fit tau against two-point tau_d,10-90: median log ratio {np.median(r):+.3f} dex, "
              f"robust scatter {1.4826 * np.median(np.abs(r - np.median(r))):.3f} dex, SD {np.std(r, ddof=1):.3f} dex (N = {len(r)}).",
              "", f"Sampler: 32 walkers, {int(df.n_steps.iloc[0])} steps, first third discarded. "
              f"Largest integrated autocorrelation time over all fits: {df.autocorr_max.max():.0f} steps "
              f"(median {df.autocorr_max.median():.0f}).", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source")
    ap.add_argument("--steps", type=int, default=3000)
    a = ap.parse_args()
    ids = {r.source: r.maxi_id for _, r in pd.read_csv(config.SAMPLE_CSV).iterrows() if isinstance(r.maxi_id, str)}
    rows = select_outbursts()
    if a.source:
        rows = rows[rows.source == a.source]
    recs = []
    for _, row in rows.iterrows():
        got = fit_outburst(row, ids[row.source], nstep=a.steps)
        recs += got
        if got:
            b = min(got, key=lambda r: r["BIC"])
            print(f"{row.source:22s} {row.t_peak:8.1f}  best {b['model']:7s}  "
                  + "  ".join(f"{r['model']} dBIC {r['dBIC']:.1f}" for r in got), flush=True)
    df = pd.DataFrame(recs)
    if not a.source:
        df.to_csv(config.RESULTS / "decay_fits.csv", index=False)
        (config.RESULTS / "decay_fits_summary.md").write_text(summary(df))
    return df


if __name__ == "__main__":
    main()
