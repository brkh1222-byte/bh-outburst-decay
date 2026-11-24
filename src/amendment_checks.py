"""Checks for results/analysis_plan_amendment_1.md (2026-11-25). NOT part of plan v1.

The plan's SHA-256 fingerprint covers the plan text WITHOUT the two
"Implementation clarifications" that were appended about two minutes later.
Both clarifications decide which outbursts enter the primary sample, so this
script measures how much the H1 result depends on them:

  A  as run (both clarifications)                      -> must reproduce results/h1_results.json
  B  clarification 1 undone: a literature outburst counts as "measured by this
     work" only if its peak is within +-20 d of one of OUR peaks (the rule used
     in src/validate.py), instead of lying inside one of our windows
  C  clarification 2 undone: MAXI-era literature outbursts that our detection
     did not find are kept if the literature peak exceeds 0.1 Crab (2-12 keV),
     without the check against our own 2-10 keV data
  D  both undone

It also refits the primary sample with the five literature orbital periods
replaced by any values given on the command line (not used by default).

Writes results/amendment_1_checks.json.
Usage: nice .venv/bin/python -m src.amendment_checks
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src import config
from src import tau_vs_porb as tp


def outburst_table(window_match=True, own_brightness_rule=True, match_d=20.0) -> pd.DataFrame:
    """Copy of tau_vs_porb.outburst_table (primary settings) with the two clarifications switchable."""
    P = tp.periods()
    ours = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    ours["source"] = ours.source.replace(tp.NAME_ALIASES)
    allours = ours.copy()
    ours = ours[ours.flag.isna() | (ours.flag == "")]
    lit = pd.read_csv(config.DATA / "literature_timescales.csv")
    lit = lit[lit.flag.isna()]
    rows = []
    for _, r in ours.iterrows():
        if r.source not in P:
            continue
        if "re-flare" in [p.strip() for p in str(r.win_note).split(";")] or not r.bright:
            continue
        val, lo, hi = r.tau_decay_10_90, r.tau_decay_10_90_lo, r.tau_decay_10_90_hi
        if not (np.isfinite(val) and val > 0):
            continue
        sig = 0.5 * (np.log10(hi) - np.log10(lo)) if np.isfinite(lo) and np.isfinite(hi) and lo > 0 else 0.1
        rows.append({"source": r.source, "t_peak": r.t_peak, "logtau": np.log10(val),
                     "sig": max(sig, tp.ERR_FLOOR), "origin": "this work"})
    windows = allours[["source", "win_start", "win_end"]].values.tolist()
    peaks = allours[["source", "t_peak"]].values.tolist()
    maxi_ids = {tp.NAME_ALIASES.get(r.source, r.source): r.maxi_id
                for _, r in pd.read_csv(config.SAMPLE_CSV).iterrows() if isinstance(r.maxi_id, str)}
    cache = {}
    for (src, grp), g in lit.groupby(["source", lit.dup_group.fillna(lit.index.to_series().astype(str))]):
        if src not in P:
            continue
        t0 = g.t_peak_mjd.mean()
        if window_match:
            covered = any(s == src and a <= t0 <= b for s, a, b in windows)
        else:
            covered = any(s == src and abs(t0 - tpk) <= match_d for s, tpk in peaks)
        if covered:
            continue
        if not (g.f_peak_crab > 0.1).any():
            continue
        if own_brightness_rule and t0 > 55054 and src in maxi_ids:
            if src not in cache:
                from src.lightcurves import load_maxi
                cache[src] = load_maxi(maxi_ids[src])
            d = cache[src]
            near = d[(d.mjd > t0 - 15) & (d.mjd < t0 + 15)]
            if len(near) and near.flux.max() < 0.1:
                continue
        vals, errs = [], []
        for _, r in g.iterrows():
            v, e = r.tau_decay_10_90, r.tau_decay_10_90_err
            if np.isfinite(v) and v > 0:
                vals.append(np.log10(v))
                errs.append(max(e / (v * np.log(10)) if np.isfinite(e) else 0.1, tp.ERR_FLOOR))
        if not vals:
            continue
        sig = np.sqrt(np.mean(np.square(errs)) / len(errs) + tp.SIGMA_METHOD ** 2)
        rows.append({"source": src, "t_peak": t0, "logtau": float(np.mean(vals)), "sig": sig,
                     "origin": " + ".join(sorted(set(g.paper)))})
    df = pd.DataFrame(rows)
    df["porb_d"] = df.source.map(lambda s: P[s][0])
    df["status"] = df.source.map(lambda s: P[s][1])
    return df


def fit(ob: pd.DataFrame) -> dict:
    ps = tp.per_source(ob)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values
    ch = tp.mcmc(x, y, s, "M1", nstep=8000)
    q = np.percentile(ch[:, 1], [2.5, 50, 97.5])
    return {"N_sources": int(len(ps)), "N_outbursts": int(len(ob)),
            "B_lo95": float(q[0]), "B_median": float(q[1]), "B_hi95": float(q[2]),
            "P_B_gt_0": float(np.mean(ch[:, 1] > 0)), "P_B_ge_2_3": float(np.mean(ch[:, 1] >= 2 / 3))}


def main():
    out = {}
    base = None
    for key, wm, br, label in (("A", True, True, "as run (both clarifications)"),
                               ("B", False, True, "clarification 1 undone (+-20 d peak matching)"),
                               ("C", True, False, "clarification 2 undone (literature flux cut only)"),
                               ("D", False, False, "both undone")):
        ob = outburst_table(wm, br)
        res = fit(ob)
        res["label"] = label
        keyset = set(zip(ob.source, ob.t_peak.round(1), ob.origin))
        if base is None:
            base = keyset
        res["added_vs_A"] = sorted(f"{a} MJD {b} ({c})" for a, b, c in keyset - base)
        res["removed_vs_A"] = sorted(f"{a} MJD {b} ({c})" for a, b, c in base - keyset)
        out[key] = res
        print(key, json.dumps(res), flush=True)
    ref = json.loads((config.RESULTS / "h1_results.json").read_text())["H1_M1_posterior"]["B"]
    out["reference_h1_results_B"] = [ref[0], ref[2], ref[4]]
    (config.RESULTS / "amendment_1_checks.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
