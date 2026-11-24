"""T3.2: e-folding rise and decay timescales, following Yan & Yu (2015) exactly.

The method (Yan & Yu 2015, ApJ 805, 87, Sections II.3-II.4; also used by
Saraswati et al. 2025, MNRAS 537, 1146)
------------------------------------------------------------------------
1. Peak: the highest daily flux in the outburst, ignoring "spikes": a point
   more than 2x BOTH neighbours, or whose error is more than 2x BOTH
   neighbours' errors.
2. Walking away from the peak (backwards in time for the rise, forwards for
   the decay), pick three data points:
     F90: closest to 90% of peak, searched from the peak up to the first two
          consecutive points below 80%.
     F50: closest to 50%, searched from the first point below 66% up to the
          first two consecutive points below 33%.
     F10: closest to 10%, searched from the first point below 20% up to the
          first two consecutive points below 1% (or the end of the window).
   Points that jump by more than 2x relative to BOTH neighbours (up or down)
   are skipped during this search.
3. For each pair of chosen points (10-90, 10-50, 50-90):
        tau = |t_a - t_b| / ln(F_high / F_low)
   i.e. the time it takes the flux to change by a factor e, assuming the
   flux changes exponentially between the two points. We use the ACTUAL
   fluxes of the chosen points (they can be anywhere in 80-100%, 33-66%,
   1-20% of the peak), as the "e-folding time between two data points".

Why a two-point method? It needs no model of the light-curve shape and is
independent of instrument sensitivity. Its weakness is noise: a single noisy
point near a level moves tau. So we also give (a) Monte Carlo errors from
resampling each flux within its error bar, and (b) a "smoothed" variant that
interpolates crossing times on a 3-point running median.

The shape ratio tau_50-90 / tau_10-50 is 1 for a pure exponential decay and
about 2.7 for a pure linear decay, so it tells the two apart without a fit.
"""
from __future__ import annotations

import numpy as np

LEVEL_RULES = {
    # level: (target fraction, start: first point below this, stop: two consecutive below this)
    90: (0.90, None, 0.80),
    50: (0.50, 0.66, 0.33),
    10: (0.10, 0.20, 0.01),
}


def spike_mask(f: np.ndarray, e: np.ndarray) -> np.ndarray:
    """True for points Yan & Yu exclude: >2x or <0.5x both neighbours in flux,
    or error >2x both neighbours' errors. End points are never flagged."""
    bad = np.zeros(len(f), dtype=bool)
    for i in range(1, len(f) - 1):
        a, b, c = f[i - 1], f[i], f[i + 1]
        if a > 0 and c > 0 and b > 0:
            if (b > 2 * a and b > 2 * c) or (b < 0.5 * a and b < 0.5 * c):
                bad[i] = True
        if e[i] > 2 * e[i - 1] and e[i] > 2 * e[i + 1]:
            bad[i] = True
    return bad


def _select(t, f, fpeak, order):
    """Pick F90, F50, F10 indices walking along `order` (indices away from the peak,
    the peak itself first). Returns {level: index or None}."""
    frac = f[order] / fpeak
    out = {}
    n = len(order)
    for level, (target, start_below, stop_two_below) in LEVEL_RULES.items():
        if start_below is None:
            start = 0
        else:
            below = np.nonzero(frac < start_below)[0]
            if len(below) == 0:
                out[level] = None
                continue
            start = below[0]
        stop = n
        for k in range(start, n - 1):
            if frac[k] < stop_two_below and frac[k + 1] < stop_two_below:
                stop = k
                break
        cand = np.arange(start, stop)
        if level == 10:
            cand = cand[frac[cand] > 0]  # a non-positive flux cannot be used in a ratio
        if len(cand) == 0:
            out[level] = None
            continue
        best = cand[np.argmin(np.abs(frac[cand] - target))]
        out[level] = int(order[best])
    return out


def _tau(t, f, i, j):
    if i is None or j is None or f[i] <= 0 or f[j] <= 0 or f[i] == f[j]:
        return np.nan
    return abs(t[j] - t[i]) / abs(np.log(f[i] / f[j]))


def yan_yu(t: np.ndarray, f: np.ndarray, e: np.ndarray) -> dict:
    """Yan & Yu (2015) timescales for one outburst window.

    t, f, e: time (d), flux, error (any consistent units), for the outburst window only.
    Returns a dict with the peak, chosen points and the six timescales (days).
    """
    t, f, e = map(np.asarray, (t, f, e))
    ok = ~spike_mask(f, e)
    t, f, e = t[ok], f[ok], e[ok]
    ip = int(np.argmax(f))
    fpeak = f[ip]
    res = {"t_peak": t[ip], "f_peak": fpeak, "n_points": len(t)}
    rise = _select(t, f, fpeak, np.arange(ip, -1, -1))
    decay = _select(t, f, fpeak, np.arange(ip, len(t)))
    for name, sel in (("rise", rise), ("decay", decay)):
        for lv in (90, 50, 10):
            idx = sel[lv]
            res[f"t{lv}_{name}"] = t[idx] if idx is not None else np.nan
            res[f"f{lv}_{name}"] = f[idx] / fpeak if idx is not None else np.nan
        res[f"tau_{name}_10_90"] = _tau(t, f, sel[10], sel[90])
        res[f"tau_{name}_10_50"] = _tau(t, f, sel[10], sel[50])
        res[f"tau_{name}_50_90"] = _tau(t, f, sel[50], sel[90])
    res["shape_ratio_decay"] = res["tau_decay_50_90"] / res["tau_decay_10_50"]
    return res


def _crossing(t, s, level, order):
    """First time the smoothed curve s crosses `level` walking along `order`,
    linearly interpolated between the two bracketing points."""
    for a, b in zip(order[:-1], order[1:]):
        if s[a] >= level > s[b]:
            return t[a] + (s[a] - level) * (t[b] - t[a]) / (s[a] - s[b])
    return np.nan


def smoothed(t: np.ndarray, f: np.ndarray, e: np.ndarray, width: int = 3) -> dict:
    """Variant: 3-point running median, then interpolated level-crossing times."""
    t, f, e = map(np.asarray, (t, f, e))
    ok = ~spike_mask(f, e)
    t, f = t[ok], f[ok]
    h = width // 2
    s = np.array([np.median(f[max(0, i - h): i + h + 1]) for i in range(len(f))])
    ip = int(np.argmax(s))
    peak = s[ip]
    res = {"f_peak_smooth": peak}
    for name, order in (("rise", np.arange(ip, -1, -1)), ("decay", np.arange(ip, len(t)))):
        tc = {lv: _crossing(t, s, lv / 100 * peak, order) for lv in (90, 50, 10)}
        for (lo, hi), A in (((10, 90), 9.0), ((10, 50), 5.0), ((50, 90), 1.8)):
            res[f"tau_{name}_{lo}_{hi}_smooth"] = abs(tc[hi] - tc[lo]) / np.log(A)
    return res


def monte_carlo(t, f, e, n: int = 500, seed: int = 0) -> dict:
    """Resample each flux within its Gaussian error n times, rerun yan_yu,
    and return the 16th/50th/84th percentiles of each timescale."""
    rng = np.random.default_rng(seed)
    keys = [f"tau_{p}_{a}" for p in ("rise", "decay") for a in ("10_90", "10_50", "50_90")]
    draws = {k: [] for k in keys}
    for _ in range(n):
        r = yan_yu(t, f + rng.normal(0, e), e)
        for k in keys:
            draws[k].append(r[k])
    out = {}
    for k, v in draws.items():
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        if len(v) < 0.5 * n:  # measurement fails in most draws: unreliable
            out[f"{k}_lo"] = out[f"{k}_med"] = out[f"{k}_hi"] = np.nan
            out[f"{k}_mcfrac"] = len(v) / n
            continue
        lo, med, hi = np.percentile(v, [16, 50, 84])
        out[f"{k}_lo"], out[f"{k}_med"], out[f"{k}_hi"] = lo, med, hi
        out[f"{k}_mcfrac"] = len(v) / n
    return out
