"""Figures for the paper (paper/figures/*.pdf). Reads only files written by the pipeline.

Run after the pipeline:  .venv/bin/python -m src.paper_figures
"""
from __future__ import annotations

import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import config, tau_vs_porb as tp
from src.lightcurves import load_maxi

OUT = config.ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Okabe-Ito colour-blind-safe palette
C = {"this": "#0072B2", "lit": "#E69F00", "both": "#009E73", "grey": "#7f7f7f",
     "red": "#D55E00", "purple": "#CC79A7"}
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 7.5,
                     "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True, "savefig.dpi": 300})
COL1, COL2 = 3.32, 6.97  # MNRAS column widths (inches)


def _sample():
    s = pd.read_csv(config.SAMPLE_CSV)
    return {r.source: r.maxi_id for _, r in s.iterrows() if isinstance(r.maxi_id, str)}


# ------------------------------------------------------------------ Fig 1
def fig_lightcurves():
    ts = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    ids = _sample()
    picks = [("MAXI J1820+070", 58306.5), ("Swift J1727.8-1613", 60206.5),
             ("4U 1543-47", 59379.5), ("GX 339-4", 60351.5)]
    fig, axes = plt.subplots(2, 2, figsize=(COL2, 4.2))
    for ax, (src, tpk) in zip(axes.flat, picks):
        r = ts[(ts.source == src) & (abs(ts.t_peak - tpk) < 3)].iloc[0]
        d = load_maxi(ids[src])
        d = d[(d.mjd >= r.win_start) & (d.mjd <= r.win_end)]
        f = d.flux - r.baseline
        ax.errorbar(d.mjd - r.t_peak, f / r.f_peak, yerr=d.err / r.f_peak, fmt=".", ms=2.5,
                    color=C["grey"], elinewidth=0.5, zorder=1)
        for side, mk in (("rise", "^"), ("decay", "o")):
            for lev, col in ((90, C["red"]), (50, C["this"]), (10, C["both"])):
                t, fl = r[f"t{lev}_{side}"], r[f"f{lev}_{side}"]
                if np.isfinite(t):
                    ax.plot(t - r.t_peak, fl, mk,  # f* columns are already fractions of the peak
                            color=col, ms=5, mec="k", mew=0.4, zorder=3,
                            label=f"{lev}%" if side == "decay" else None)
        ax.set_yscale("log")
        ax.set_ylim(0.02, 6)
        for lev in (0.9, 0.5, 0.1):
            ax.axhline(lev, color="0.35", lw=0.6, ls=":")
        ax.set_title(f"{src.replace('-', '$-$')}  (peak {r.f_peak:.2f} Crab)", fontsize=8.5)
        ax.text(0.97, 0.95, rf"$\tau_{{\rm d}}={r.tau_decay_10_90:.1f}$ d" + "\n" +
                rf"$\tau_{{50-90}}/\tau_{{10-50}}={r.shape_ratio_decay:.2f}$",
                transform=ax.transAxes, ha="right", va="top", fontsize=7.5)
        ax.set_xlabel("Days from peak")
        ax.set_ylabel(r"$F/F_{\rm peak}$ (MAXI 2–10 keV)")
    from matplotlib.lines import Line2D
    h, l = axes[0, 0].get_legend_handles_labels()
    h += [Line2D([], [], marker="o", ls="", color="w", mec="k", label="decay point"),
          Line2D([], [], marker="^", ls="", color="w", mec="k", label="rise point")]
    axes[0, 0].legend(handles=h, loc="lower left", fontsize=6.5, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_lightcurves.pdf")
    plt.close(fig)


# ------------------------------------------------------------------ Fig 2
def _md_tables(path):
    """Parse the comparison tables in results/method_check.md -> {section_number: DataFrame}."""
    text = path.read_text().split("\n")
    out, sec, rows = {}, None, []
    for line in text:
        m = re.match(r"## (\d)\.", line)
        if m:
            sec, rows = int(m.group(1)), []
            out[sec] = rows
        elif sec in (1, 2, 3) and line.startswith("| ") and "---" not in line and "Source" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            a, b = (float(x) if x != "nan" else np.nan for x in cells[2].split(" / "))
            out[sec].append({"source": cells[0], "x": b, "y": a})
    return {k: pd.DataFrame(v) for k, v in out.items() if k in (1, 2, 3)}


def fig_validation():
    tabs = _md_tables(config.RESULTS / "method_check.md")
    # this-work comparisons: window-matched pairs from results/h1_extra.json (confused events removed)
    import json
    vm = json.loads((config.RESULTS / "h1_extra.json").read_text())["validation_window_matched"]
    for k, key in ((1, "TW_vs_YY15"), (2, "TW_vs_S25")):
        pr = pd.DataFrame(vm[key]["pairs"])
        tabs[k] = pd.DataFrame({"source": pr.source, "x": pr.tau_lit, "y": pr.tau_ours})
    inj = pd.read_csv(config.RESULTS / "injection_recovery.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL2, 3.0))
    sty = {1: ("o", C["lit"], "this work vs Yan & Yu (2015)"),
           2: ("s", C["this"], "this work vs Saraswati et al. (2025)"),
           3: ("D", C["purple"], "Yan & Yu vs Saraswati et al. (same ASM data)")}
    for k, (mk, col, lab) in sty.items():
        t = tabs[k]
        a1.plot(t.x, t.y, mk, color=col, mec="k", mew=0.4, ms=5, label=lab)
    g = np.array([2, 300])
    a1.plot(g, g, "k-", lw=0.7)
    a1.fill_between(g, g / 10 ** 0.19, g * 10 ** 0.19, color="k", alpha=0.08, lw=0)
    a1.set_xscale("log"); a1.set_yscale("log")
    a1.set_xlim(3, 250); a1.set_ylim(3, 250)
    a1.set_xlabel(r"$\tau_{\rm d,10-90}$, reference study (d)")
    a1.set_ylabel(r"$\tau_{\rm d,10-90}$, comparison (d)")
    a1.legend(loc="upper left", fontsize=6.5)
    a1.text(0.97, 0.04, "shaded: ±0.19 dex", transform=a1.transAxes, ha="right", fontsize=7)
    a1.set_title("(a) same outbursts, different studies", fontsize=8.5)
    for k, src, txt, dxy in ((2, "4U 1543-47", "4U 1543$-$47 2022\n(0.06 Crab)", (8, 7.5)),
                             (3, "XTE J1550-564", "XTE J1550$-$564\n1998", (120, 9))):
        t = tabs[k][tabs[k].source == src]
        t = t.loc[[(t.y / t.x).sub(1).abs().idxmax()]]
        a1.annotate(txt, (t.x.iloc[0], t.y.iloc[0]), xytext=dxy, fontsize=6,
                    arrowprops=dict(arrowstyle="-", lw=0.5), ha="center")

    inj = inj[np.isfinite(inj.tau_d_meas) & (inj.tau_d_meas > 0)]
    inj["dl"] = np.log10(inj.tau_d_meas / inj.tau_d_true)
    for fp, col, mk in zip(sorted(inj.f_peak.unique()), [C["red"], C["lit"], C["this"], C["both"]], "osD^"):
        s = inj[inj.f_peak == fp].groupby("tau_d_true").dl
        med = s.median()
        mad = s.apply(lambda v: 1.4826 * np.median(np.abs(v - np.median(v))))
        off = {0.1: 0.94, 0.3: 0.98, 1.0: 1.02, 3.0: 1.06}[fp]
        a2.errorbar(med.index * off, med.values, yerr=mad.values, fmt=mk, color=col, mec="k", mew=0.4,
                    ms=4.5, capsize=2, elinewidth=0.8, label=f"peak {fp:g} Crab")
    a2.axhline(0, color="k", lw=0.7)
    a2.set_xscale("log")
    a2.set_xticks([5, 10, 20, 40, 80])
    a2.set_xticks([], minor=True)
    a2.set_xticklabels(["5", "10", "20", "40", "80"])
    a2.set_xlabel(r"injected $\tau_{\rm d}$ (d)")
    a2.set_ylabel(r"$\log_{10}(\tau_{\rm meas}/\tau_{\rm true})$")
    a2.set_ylim(-0.2, 0.2)
    a2.legend(loc="upper right", ncol=2, fontsize=6.5)
    a2.set_title("(b) injection--recovery in real MAXI data", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_validation.pdf")
    plt.close(fig)


# ------------------------------------------------------------------ Fig 3
def _panel(ax, col, ylab, seed):
    ob = tp.outburst_table(col=col)
    ps = tp.per_source(ob)
    x, y, s = ps.x.values, ps.logtau.values, ps.sig.values
    chain = tp.mcmc(x, y, s, "M1", seed=seed)
    p0, _ = tp.fit_ml(x, y, s, "M0")
    xg = np.linspace(-1.1, 0.55, 100)
    pred = chain[:, 0][:, None] + chain[:, 1][:, None] * xg[None, :]
    lo, mid, hi = np.percentile(pred, [2.5, 50, 97.5], axis=0)
    ax.fill_between(10 ** xg, 10 ** lo, 10 ** hi, color=C["this"], alpha=0.15, lw=0, label="M1, 95% band")
    ax.plot(10 ** xg, 10 ** mid, color=C["this"], lw=1.0, label="M1 median")
    ax.axhline(10 ** p0[0], color="k", ls="--", lw=0.8, label="M0 (constant)")
    is_ours = ob.origin == "this work"
    ax.plot(ob.porb_d[is_ours], 10 ** ob.logtau[is_ours], ".", color=C["this"], alpha=0.45, ms=4,
            label="outburst, this work")
    ax.plot(ob.porb_d[~is_ours], 10 ** ob.logtau[~is_ours], ".", color=C["lit"], alpha=0.6, ms=4,
            label="outburst, literature")
    for st, mk in (("dynamical", "o"), ("candidate", "s")):
        m = ps.status == st
        ax.errorbar(ps.porb_d[m], 10 ** ps.logtau[m],
                    yerr=[10 ** ps.logtau[m] * (1 - 10 ** -ps.sig[m]), 10 ** ps.logtau[m] * (10 ** ps.sig[m] - 1)],
                    fmt=mk, color="k", mfc="w", ms=5.5, capsize=2, elinewidth=0.8, zorder=5,
                    label=f"source mean ({st})")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.08, 3.5)
    ax.set_xlabel(r"$P_{\rm orb}$ (d)")
    ax.set_ylabel(ylab)
    return ps, chain


NUMBERS = {  # system numbers, ordered by orbital period (same as Table 1)
    "MAXI J1659-152": 1, "Swift J1753.5-0127": 2, "XTE J1859+226": 3, "GRS 1716-249": 4,
    "MAXI J1803-298": 5, "XTE J1650-500": 6, "Swift J1727.8-1613": 7, "MAXI J1820+070": 8,
    "4U 1543-47": 9, "XTE J1550-564": 10, "GX 339-4": 11, "GS 1354-64": 12, "GRO J1655-40": 13,
}
BELOW = {"MAXI J1803-298", "XTE J1550-564", "GS 1354-64"}


def _number(ax, ps):
    for _, r in ps.iterrows():
        dy = 0.78 if r.source in BELOW else 1.25
        left = r.source == "XTE J1859+226"
        ax.text(r.porb_d * (0.88 if left else 1.09), 10 ** r.logtau * (1.0 if left else dy),
                str(NUMBERS[r.source]), fontsize=6.5, ha="right" if left else "left", va="center", color="0.15")


def fig_tau_porb():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL2, 3.9))
    ps, _ = _panel(a1, "tau_decay_10_90", r"$\tau_{\rm d,10-90}$ (d)", seed=0)
    _number(a1, ps)
    a1.set_ylim(4, 300)
    a1.set_title("(a) decay (H1, primary)", fontsize=8.5)
    h, l = a1.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=6.5, frameon=False)
    psr, _ = _panel(a2, "tau_rise_10_90", r"$\tau_{\rm r,10-90}$ (d)", seed=1)
    _number(a2, psr)
    a2.set_ylim(0.3, 200)
    a2.set_title("(b) rise (H2, exploratory)", fontsize=8.5)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig(OUT / "fig3_tau_porb.pdf")
    plt.close(fig)


# ------------------------------------------------------------------ Fig 4
def fig_shapes():
    t = pd.read_csv(config.RESULTS / "outburst_table.csv")
    main = t[t.bright & ~t.reflare & t.flag.isna()]
    sr = main.shape_ratio_decay.dropna()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL2, 2.8))
    bins = np.logspace(-1.1, 1.2, 14)
    a1.hist(sr, bins=bins, color=C["this"], alpha=0.8, edgecolor="k", lw=0.5)
    a1.axvline(1, color="k", ls="--", lw=0.8)
    a1.axvline(2.7, color=C["red"], ls=":", lw=1.0)
    a1.text(1.05, a1.get_ylim()[1] * 0.92, "exponential", fontsize=7, rotation=90, va="top")
    a1.text(3.0, a1.get_ylim()[1] * 0.92, "linear", fontsize=7, rotation=90, va="top", color=C["red"])
    a1.set_xscale("log")
    a1.set_xlabel(r"shape ratio $\tau_{\rm d,50-90}/\tau_{\rm d,10-50}$")
    a1.set_ylabel("outbursts")
    a1.set_title(f"(a) 2016–2026 bright main outbursts (N = {len(sr)})", fontsize=8.5)

    ob = tp.outburst_table()
    g = ob[ob.source == "GX 339-4"].sort_values("t_peak")
    ours = g.origin == "this work"
    yrs = 2000 + (g.t_peak - 51544.5) / 365.25
    a2.errorbar(yrs[~ours], 10 ** g.logtau[~ours], yerr=np.log(10) * g.sig[~ours] * 10 ** g.logtau[~ours],
                fmt="o", color=C["lit"], mec="k", mew=0.4, ms=5, capsize=2, label="literature (RXTE/ASM)")
    a2.errorbar(yrs[ours], 10 ** g.logtau[ours], yerr=np.log(10) * g.sig[ours] * 10 ** g.logtau[ours],
                fmt="s", color=C["this"], mec="k", mew=0.4, ms=5, capsize=2, label="this work (MAXI)")
    a2.set_yscale("log")
    a2.set_ylim(10, 250)
    a2.set_xlabel("year of peak")
    a2.set_ylabel(r"$\tau_{\rm d,10-90}$ (d)")
    a2.set_title(r"(b) GX 339$-$4: one orbit, ten outbursts", fontsize=8.5)
    a2.legend(loc="upper right", fontsize=6.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_shapes.pdf")
    plt.close(fig)
    return main


if __name__ == "__main__":
    fig_lightcurves()
    fig_validation()
    fig_tau_porb()
    main = fig_shapes()
    print("bright main 2016-2026 outbursts:", len(main), "sources:", main.source.nunique())
    print("figures in", OUT)
