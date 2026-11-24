"""T2.2: plot every 2016-2026 light curve, MAXI + BAT, with hardness ratios.

One figure per source in results/lightcurves/<source>.png, three panels:
  1. MAXI 2-10 keV and Swift/BAT 15-50 keV daily flux in Crab units (log axis).
     Outburst windows from results/timescales_maxi.csv are shaded:
     blue = used, red = flagged (source confusion), grey = re-flare or faint.
  2. MAXI hardness (4-10 keV)/(2-4 keV), both in Crab units, so the Crab = 1.
  3. BAT/MAXI ratio, (15-50 keV)/(2-10 keV), both in Crab units.
Ratios are shown only for days where both fluxes are detected at > 3 sigma;
values are ratios of Crab-normalised fluxes, not of count rates.

Also writes results/lightcurves/overview_2016_2026.png (all sources, flux only).

Why hardness? A black hole transient is "hard" (ratio high, BAT bright) at the
start and end of an outburst and "soft" in between. An outburst that never
softens is a "failed" (hard-only) outburst. The 2-4 keV MAXI band is the least
well calibrated, so treat the absolute hardness values with care.

Usage:  nice .venv/bin/python -m src.plot_lightcurves [--source "GX 339-4"]
"""
from __future__ import annotations

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import config
from src.lightcurves import load_bat, load_maxi, load_maxi_bands

OUT = config.RESULTS / "lightcurves"
T0 = config.WINDOW_START_MJD
SNR = 3.0
C = {"maxi": "#0072B2", "bat": "#E69F00", "used": "#0072B2", "flag": "#D55E00", "other": "#7f7f7f"}


def tag(source: str) -> str:
    return source.replace(" ", "_").replace("+", "p")


def window_kind(w) -> str:
    if isinstance(w.flag, str) and w.flag:
        return "flag"
    reflare = "re-flare" in [p.strip() for p in str(w.win_note).split(";")]
    return "used" if (w.bright and not reflare) else "other"


def ratios(source_row):
    """Daily hardness ratios for one source (only > 3 sigma detections in both bands)."""
    out = {}
    b = load_maxi_bands(source_row.maxi_id)
    b = b[b.mjd >= T0]
    ok = (b.f2_4 > SNR * b.e2_4) & (b.f4_10 > SNR * b.e4_10) & (b.e2_4 > 0) & (b.e4_10 > 0)
    h = b[ok]
    hr = h.f4_10 / h.f2_4
    out["maxi"] = pd.DataFrame({"mjd": h.mjd, "hr": hr,
                                "err": hr * np.hypot(h.e4_10 / h.f4_10, h.e2_4 / h.f2_4)})
    if isinstance(source_row.bat_name, str):
        try:
            bat = load_bat(source_row.bat_name)
        except FileNotFoundError:
            bat = None
        if bat is not None:
            m = load_maxi(source_row.maxi_id)
            bat = bat.assign(day=np.floor(bat.mjd))
            m = m.assign(day=np.floor(m.mjd))
            x = m.merge(bat, on="day", suffixes=("_m", "_b"))
            x = x[(x.mjd_m >= T0) & (x.flux_m > SNR * x.err_m) & (x.flux_b > SNR * x.err_b)]
            r = x.flux_b / x.flux_m
            out["bat"] = pd.DataFrame({"mjd": x.mjd_m, "hr": r,
                                       "err": r * np.hypot(x.err_b / x.flux_b, x.err_m / x.flux_m)})
    return out


def plot_source(s, ts) -> dict:
    m = load_maxi(s.maxi_id)
    m = m[m.mjd >= T0]
    bat = None
    if isinstance(s.bat_name, str):
        try:
            bat = load_bat(s.bat_name)
            bat = bat[bat.mjd >= T0]
        except FileNotFoundError:
            bat = None
    r = ratios(s)
    fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True,
                             gridspec_kw={"height_ratios": [2.2, 1, 1], "hspace": 0.05})
    ax = axes[0]
    pos = m[m.flux > 0]
    ax.plot(pos.mjd, pos.flux, ".", ms=2.5, color=C["maxi"], label="MAXI 2-10 keV")
    if bat is not None and len(bat):
        pb = bat[bat.flux > SNR * bat.err]
        ax.plot(pb.mjd, pb.flux, ".", ms=2.5, color=C["bat"], alpha=0.8, label="BAT 15-50 keV (> 3 sigma)")
    ax.axhline(config.PEAK_MIN_CRAB, color="0.3", lw=0.6, ls="--")
    ax.set_yscale("log"); ax.set_ylim(2e-3, 30)
    ax.set_ylabel("Flux (Crab)")
    w = ts[(ts.source == s.source) & (ts.win_end >= T0)]
    for _, row in w.iterrows():
        k = window_kind(row)
        for a in axes:
            a.axvspan(max(row.win_start, T0), row.win_end, color=C[k], alpha=0.10, lw=0)
    ax.plot([], [], "s", color=C["used"], alpha=0.3, label="window: bright main outburst")
    ax.plot([], [], "s", color=C["flag"], alpha=0.3, label="window: flagged (confusion)")
    ax.plot([], [], "s", color=C["other"], alpha=0.3, label="window: re-flare or faint")
    ax.legend(fontsize=7, ncol=3, loc="upper left")
    ax.set_title(f"{s.source}   (MAXI {s.maxi_id}; BAT {s.bat_name if isinstance(s.bat_name, str) else 'none'}; "
                 f"{s.bh_status})", fontsize=10)
    h = r["maxi"]
    axes[1].errorbar(h.mjd, h.hr, h.err, fmt=".", ms=2.5, lw=0.3, color=C["maxi"])
    axes[1].set_yscale("log"); axes[1].set_ylim(0.03, 10)
    axes[1].set_ylabel("MAXI (4-10)/(2-4)")
    if "bat" in r and len(r["bat"]):
        hb = r["bat"]
        axes[2].errorbar(hb.mjd, hb.hr, hb.err, fmt=".", ms=2.5, lw=0.3, color=C["bat"])
    axes[2].set_yscale("log"); axes[2].set_ylim(0.003, 30)
    axes[2].set_ylabel("BAT / MAXI")
    axes[2].set_xlabel("MJD")
    axes[2].set_xlim(T0, max(m.mjd.max(), T0 + 1))
    for a in axes[1:]:
        a.axhline(1, color="0.3", lw=0.6, ls=":")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{tag(s.source)}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return {"source": s.source, "n_maxi_days": len(m), "n_bat_days": 0 if bat is None else len(bat),
            "n_hr_maxi": len(h), "n_hr_bat": len(r.get("bat", [])), "n_windows": len(w),
            "n_used": int(sum(window_kind(x) == "used" for _, x in w.iterrows())),
            "n_flagged": int(sum(window_kind(x) == "flag" for _, x in w.iterrows()))}


def overview(sample, ts):
    srcs = [s for _, s in sample.iterrows() if isinstance(s.maxi_id, str)]
    fig, axes = plt.subplots(len(srcs), 1, figsize=(11, 1.05 * len(srcs)), sharex=True,
                             gridspec_kw={"hspace": 0})
    for ax, s in zip(axes, srcs):
        m = load_maxi(s.maxi_id)
        m = m[(m.mjd >= T0) & (m.flux > 0)]
        ax.plot(m.mjd, m.flux, ".", ms=1.5, color=C["maxi"])
        if isinstance(s.bat_name, str):
            try:
                b = load_bat(s.bat_name)
                b = b[(b.mjd >= T0) & (b.flux > SNR * b.err)]
                ax.plot(b.mjd, b.flux, ".", ms=1.5, color=C["bat"], alpha=0.7)
            except FileNotFoundError:
                pass
        for _, row in ts[(ts.source == s.source) & (ts.win_end >= T0)].iterrows():
            ax.axvspan(max(row.win_start, T0), row.win_end, color=C[window_kind(row)], alpha=0.12, lw=0)
        ax.set_yscale("log"); ax.set_ylim(3e-3, 30); ax.set_yticks([0.01, 0.1, 1, 10])
        ax.tick_params(labelsize=6)
        ax.text(0.005, 0.80, s.source, transform=ax.transAxes, fontsize=7, va="top")
    axes[-1].set_xlabel("MJD")
    axes[len(axes) // 2].set_ylabel("Flux (Crab): MAXI 2-10 keV (blue), BAT 15-50 keV (orange)")
    fig.savefig(OUT / "overview_2016_2026.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source")
    a = ap.parse_args()
    sample = pd.read_csv(config.SAMPLE_CSV)
    ts = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, s in sample.iterrows():
        if not isinstance(s.maxi_id, str) or (a.source and s.source != a.source):
            continue
        rows.append(plot_source(s, ts))
        print(rows[-1], flush=True)
    if not a.source:
        overview(sample, ts)
        pd.DataFrame(rows).to_csv(OUT / "index.csv", index=False)


if __name__ == "__main__":
    main()
