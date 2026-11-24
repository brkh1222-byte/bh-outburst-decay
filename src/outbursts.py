"""T3.1: find outburst windows in MAXI light curves, then measure each one.

Detection (automatic, then reviewed by eye)
-------------------------------------------
1. Take the MAXI 2-10 keV daily light curve (Crab units).
2. Smooth it with a 7-point running median, which ignores single bad points.
3. Outburst cores: stretches where the smoothed flux exceeds 0.05 Crab,
   merged across gaps of up to 30 days. (MAXI's daily noise and background
   wiggles in crowded Galactic-plane fields reach ~0.02-0.03 Crab, so a lower
   seed level finds noise.)
4. Expand each core outward until the smoothed flux falls below 10% of that
   core's peak (but not below 0.01 Crab), then add 15 days on each side so
   the 10% points have room. Overlapping windows are split at the midpoint.

Any window can be overridden or removed in data/outburst_windows.yaml, e.g.
    GX 339-4:
      - {start: 58400, end: 58700, note: "manual: split double outburst"}
    MAXI J1820+070: {drop_peaks: [58557]}

Measurement: for each window, the Yan & Yu timescales (src/timescales.py),
their Monte Carlo errors, and the smoothed variant. Output:
results/timescales_maxi.csv plus a QC plot per window in results/qc/.

Usage:  .venv/bin/python -m src.outbursts [--source "GX 339-4"] [--no-mc]
"""
from __future__ import annotations

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from src import config
from src.lightcurves import load_bat, load_maxi
from src.timescales import monte_carlo, smoothed, spike_mask, yan_yu

SEED_CRAB = 0.05      # smoothed flux that marks the core of an outburst
MERGE_GAP_D = 30.0    # cores closer than this are one outburst
EDGE_FRAC = 0.10      # expand until the smoothed flux falls below 10% of the core's peak ...
EDGE_FLOOR = 0.01     # ... but never below 0.01 Crab (about MAXI's daily noise)
PAD_D = 15.0          # extra days on each side so the 10% points have room


def running_median(x: np.ndarray, width: int = 7) -> np.ndarray:
    h = width // 2
    return np.array([np.median(x[max(0, i - h): i + h + 1]) for i in range(len(x))])


SPLIT_FRAC = 0.25


def split_reflares(w: dict, t: np.ndarray, m: np.ndarray) -> list[dict]:
    sel = np.nonzero((t >= w["start"]) & (t <= w["end"]))[0]
    if len(sel) < 10:
        return [w]
    ip = sel[np.argmax(m[sel])]
    peak = m[ip]
    after = sel[sel > ip]
    lowest, imin = np.inf, None
    for i in after:
        if m[i] < lowest:
            lowest, imin = m[i], i
        if lowest < SPLIT_FRAC * peak and m[i] > max(2 * lowest, SEED_CRAB):
            cut = float(t[imin])
            first = dict(w, end=cut, note=w["note"] + "; split before re-flare")
            rest = dict(w, start=cut, note=w["note"] + "; re-flare")
            return [first] + split_reflares(rest, t, m)
    return [w]


def detect(df: pd.DataFrame) -> list[dict]:
    t, f = df.mjd.values, df.flux.values
    m = running_median(f)
    core = m > SEED_CRAB
    # 1. contiguous cores, merged across short gaps
    segs, start, last = [], None, None
    for i in np.nonzero(core)[0]:
        if start is None:
            start = last = i
        elif t[i] - t[last] > MERGE_GAP_D:
            segs.append((start, last)); start = last = i
        else:
            last = i
    if start is not None:
        segs.append((start, last))
    # 2. expand each core outward until the smoothed flux drops below its edge level
    windows = []
    for a, b in segs:
        peak_m = m[a:b + 1].max()
        edge = max(EDGE_FRAC * peak_m, EDGE_FLOOR)
        i = a
        while i > 0 and m[i - 1] > edge:
            i -= 1
        j = b
        while j < len(t) - 1 and m[j + 1] > edge:
            j += 1
        windows.append({"start": float(t[i] - PAD_D), "end": float(t[j] + PAD_D),
                        "note": "auto", "peak_smooth": float(peak_m)})
    # 3. split re-flares: after the main peak, if the smoothed flux dips below
    #    SPLIT_FRAC of that peak and then climbs back above max(2 x the dip, SEED_CRAB),
    #    the re-flare is a separate outburst (Yan & Yu 2015 also counted secondary
    #    outbursts separately, Section II.1).
    windows = [part for w in windows for part in split_reflares(w, t, m)]
    # 4. neighbouring windows must not overlap: split at the midpoint
    windows.sort(key=lambda w: w["start"])
    merged = []
    for w in windows:
        if merged and w["start"] <= merged[-1]["end"]:
            if w["end"] <= merged[-1]["end"]:
                continue
            mid = (merged[-1]["end"] + w["start"]) / 2
            merged[-1]["end"], w["start"] = mid, mid
        merged.append(w)
    return merged


def local_baseline(df: pd.DataFrame, w: dict, all_windows: list[dict], span: float = 60.0) -> float:
    """Quiescent level next to an outburst: median flux in the `span` days before the
    window start and after its end, excluding any other outburst window.
    Why: near the Galactic Centre the MAXI light curve sits on a non-zero floor
    (background, unresolved neighbours). Without removing it, the 10% level of a
    faint outburst is never crossed cleanly and the two-point method picks noise."""
    t = df.mjd.values
    sel = ((t >= w["start"] - span) & (t < w["start"])) | ((t > w["end"]) & (t <= w["end"] + span))
    for o in all_windows:
        sel &= ~((t >= o["start"]) & (t <= o["end"]))
    return float(np.median(df.flux.values[sel])) if sel.sum() >= 10 else 0.0


def load_overrides() -> dict:
    if config.WINDOWS_YAML.exists():
        return yaml.safe_load(config.WINDOWS_YAML.read_text()) or {}
    return {}


def windows_for(source: str, df: pd.DataFrame, overrides: dict) -> list[dict]:
    """Automatic windows, or the manual list if data/outburst_windows.yaml gives one."""
    ov = overrides.get(source)
    if isinstance(ov, list):
        return [dict(w, note=w.get("note", "manual")) for w in ov]
    wins = detect(df)
    if isinstance(ov, dict):
        wins += [dict(w, note=w.get("note", "manual")) for w in ov.get("add", [])]
    return sorted(wins, key=lambda w: w["start"])


def decide(source: str, t_peak: float, overrides: dict, tol: float = 5.0):
    """Apply the yaml rules to one measured window. Returns (keep, flag)."""
    ov = overrides.get(source)
    if not isinstance(ov, dict):
        return True, ""
    if "drop_all" in ov:
        return False, ""
    if "keep_between" in ov:
        lo, hi = ov["keep_between"]
        if not lo <= t_peak <= hi:
            return False, ""
    if any(abs(t_peak - p) <= tol for p in ov.get("drop_peaks", [])):
        return False, ""
    if "flag_all" in ov:
        return True, ov["flag_all"]
    for p, why in (ov.get("flag_peaks") or {}).items():
        if abs(t_peak - float(p)) <= tol:
            return True, why
    return True, ""


def qc_plot(source, w, d, res, bat, path):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.errorbar(d.mjd, d.flux, d.err, fmt=".", ms=3, lw=0.5, color="0.3", label="MAXI 2-10 keV")
    bad = spike_mask(d.flux.values, d.err.values)
    ax.plot(d.mjd[bad], d.flux[bad], "x", color="red", label="excluded spike")
    if bat is not None and len(bat):
        ax.plot(bat.mjd, bat.flux, ".", ms=2, color="tab:orange", alpha=0.6, label="BAT 15-50 keV")
    for lv, c in ((90, "tab:green"), (50, "tab:blue"), (10, "tab:purple")):
        for ph in ("rise", "decay"):
            tt = res.get(f"t{lv}_{ph}")
            if tt is not None and np.isfinite(tt):
                ax.axvline(tt, color=c, lw=0.8, ls="--" if ph == "rise" else "-")
        ax.axhline(lv / 100 * res["f_peak"], color=c, lw=0.5, alpha=0.4)
    ax.set_xlabel("MJD")
    ax.set_ylabel("Flux (Crab)")
    ax.set_title(f"{source}  peak MJD {res['t_peak']:.0f}  "
                 f"tau_d,10-90 = {res['tau_decay_10_90']:.1f} d  tau_r,10-90 = {res['tau_rise_10_90']:.1f} d",
                 fontsize=9)
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def run(only: str | None = None, do_mc: bool = True, subtract_baseline: bool = True) -> pd.DataFrame:
    sample = pd.read_csv(config.SAMPLE_CSV)
    overrides = load_overrides()
    config.QC.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, s in sample.iterrows():
        if only and s.source != only:
            continue
        if not isinstance(s.maxi_id, str):
            continue
        df = load_maxi(s.maxi_id)
        bat = load_bat(s.bat_name) if isinstance(s.bat_name, str) else None
        wins = windows_for(s.source, df, overrides)
        for w in wins:
            d = df[(df.mjd >= w["start"]) & (df.mjd <= w["end"])].copy()
            if len(d) < 10:
                continue
            base = local_baseline(df, w, wins) if subtract_baseline else 0.0
            d["flux"] = d["flux"] - base
            res = yan_yu(d.mjd.values, d.flux.values, d.err.values)
            keep, flag = decide(s.source, res["t_peak"], overrides)
            if not keep:
                continue
            era = ("validation" if res["t_peak"] < 55927 else
                   "study" if res["t_peak"] >= config.WINDOW_START_MJD else "other")
            rec = {"source": s.source, "win_start": w["start"], "win_end": w["end"],
                   "win_note": w.get("note", ""), "flag": flag, "era": era, "baseline": base, **res}
            # Yan & Yu selection: daily peak > 0.1 Crab at > 3 sigma
            ip = d.flux.values.argmax()
            rec["peak_err"] = d.err.values[ip]
            rec["bright"] = bool(res["f_peak"] > config.PEAK_MIN_CRAB and
                                 res["f_peak"] - config.PEAK_MIN_CRAB > 3 * rec["peak_err"])
            rec.update(smoothed(d.mjd.values, d.flux.values, d.err.values))
            if do_mc:
                rec.update(monte_carlo(d.mjd.values, d.flux.values, d.err.values, n=300))
            b = bat[(bat.mjd >= w["start"]) & (bat.mjd <= w["end"])] if bat is not None else None
            if b is not None and len(b) > 10:
                rb = yan_yu(b.mjd.values, b.flux.values, b.err.values)
                rec["bat_f_peak"] = rb["f_peak"]
                rec["bat_tau_decay_10_90"] = rb["tau_decay_10_90"]
                rec["bat_tau_rise_10_90"] = rb["tau_rise_10_90"]
            tag = s.source.replace(" ", "_").replace("+", "p")
            suffix = "" if subtract_baseline else "_raw"
            qc_plot(s.source, w, d, res, b, config.QC / f"{tag}_{res['t_peak']:.0f}{suffix}.png")
            rows.append(rec)
    out = pd.DataFrame(rows)
    if not only:
        name = "timescales_maxi.csv" if subtract_baseline else "timescales_maxi_raw.csv"
        out.to_csv(config.RESULTS / name, index=False)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source")
    ap.add_argument("--no-mc", action="store_true")
    ap.add_argument("--raw", action="store_true", help="no baseline subtraction (Yan & Yu exact)")
    a = ap.parse_args()
    r = run(a.source, not a.no_mc, not a.raw)
    cols = ["source", "era", "t_peak", "f_peak", "bright", "tau_rise_10_90", "tau_decay_10_90",
            "tau_decay_10_90_med", "tau_decay_10_90_lo", "tau_decay_10_90_hi",
            "tau_decay_10_90_smooth", "shape_ratio_decay", "bat_tau_decay_10_90", "flag"]
    with pd.option_context("display.width", 200, "display.max_rows", 500):
        print(r[[c for c in cols if c in r]].round(2).to_string())
