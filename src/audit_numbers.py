"""Recompute every derived number quoted in paper/main.tex from the result files.

Prints "name = value   [source file]" lines and writes results/paper_numbers.json.
The audit table in paper/notes.md compares these with the text of the paper.
Light: reads CSV/JSON only, no fitting.   Usage: .venv/bin/python -m src.audit_numbers
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src import config

R = config.RESULTS
out = {}


def put(name, value, src):
    if isinstance(value, (np.floating, float)):
        value = float(np.round(value, 4))
    elif isinstance(value, (np.integer,)):
        value = int(value)
    out[name] = {"value": value, "source": src}
    print(f"{name} = {value}   [{src}]")


def main():
    # ---- catalogue
    t = pd.read_csv(R / "outburst_table.csv")
    fl = t.flag.notna() & (t.flag != "")
    put("cat_windows", len(t), "outburst_table.csv")
    put("cat_sources", t.source.nunique(), "outburst_table.csv")
    put("cat_flagged", int(fl.sum()), "outburst_table.csv")
    put("cat_flagged_J1631", int((t[fl].source == "MAXI J1631-479").sum()), "outburst_table.csv")
    put("cat_unflagged", int((~fl).sum()), "outburst_table.csv")
    b = t[(~fl) & t.bright & (~t.reflare)]
    put("cat_bright_main", len(b), "outburst_table.csv")
    put("cat_bright_main_sources", b.source.nunique(), "outburst_table.csv")
    put("cat_taud_min", b.tau_decay_10_90.min(), "outburst_table.csv")
    put("cat_taud_max", b.tau_decay_10_90.max(), "outburst_table.csv")
    put("cat_taud_median", b.tau_decay_10_90.median(), "outburst_table.csv")
    r = (b.bat_tau_decay_10_90 / b.tau_decay_10_90).dropna()
    put("cat_bat_ratio_n", len(r), "outburst_table.csv")
    put("cat_bat_ratio_median", r.median(), "outburst_table.csv")
    put("cat_bat_ratio_log10", np.log10(r.median()), "outburst_table.csv")
    outside = ((b.tau_decay_10_90 < b.tau_decay_10_90_lo) | (b.tau_decay_10_90 > b.tau_decay_10_90_hi)).sum()
    put("cat_measured_outside_mc_range", int(outside), "outburst_table.csv")
    sr = b.shape_ratio_decay
    put("shape_min", sr.min(), "outburst_table.csv")
    put("shape_max", sr.max(), "outburst_table.csv")
    put("shape_median", sr.median(), "outburst_table.csv")
    put("shape_n_gt2", int((sr > 2).sum()), "outburst_table.csv")
    put("shape_n_lt1", int((sr < 1).sum()), "outburst_table.csv")
    put("shape_n_valid", int(sr.notna().sum()), "outburst_table.csv")
    # ---- sample table
    s = pd.read_csv(config.SAMPLE_CSV)
    put("sample_rows", len(s), "data/sample.csv")
    put("sample_with_maxi_id", int(s.maxi_id.notna().sum()), "data/sample.csv")
    ts = pd.read_csv(R / "timescales_maxi.csv")
    put("sources_with_window_all_eras", ts.source.nunique(), "timescales_maxi.csv")
    # ---- literature
    lit = pd.read_csv(config.DATA / "literature_timescales.csv")
    for p, n in lit.groupby("paper").size().items():
        put(f"lit_rows[{p}]", int(n), "data/literature_timescales.csv")
    put("lit_duplicate_groups", int(lit.dup_group.dropna().nunique()), "data/literature_timescales.csv")
    # ---- H1 primary
    ob = pd.read_csv(R / "h1_outbursts_primary.csv")
    ps = pd.read_csv(R / "h1_sources_primary.csv")
    put("h1_outbursts", len(ob), "h1_outbursts_primary.csv")
    put("h1_systems", len(ps), "h1_sources_primary.csv")
    put("h1_outbursts_this_work", int((ob.origin == "this work").sum()), "h1_outbursts_primary.csv")
    put("h1_porb_min_d", ps.porb_d.min(), "h1_sources_primary.csv")
    put("h1_porb_max_d", ps.porb_d.max(), "h1_sources_primary.csv")
    put("h1_porb_range_dex", np.log10(ps.porb_d.max() / ps.porb_d.min()), "h1_sources_primary.csv")
    put("h1_slope_third_times_range_dex", np.log10(ps.porb_d.max() / ps.porb_d.min()) / 3, "h1_sources_primary.csv")
    put("h1_system_means_span_dex", ps.logtau.max() - ps.logtau.min(), "h1_sources_primary.csv")
    for _, r_ in ps.sort_values("porb_d").iterrows():
        put(f"table1[{r_.source}]", f"P={r_.porb_d:.4f} d, n={r_.n_outbursts}, <tau>={10 ** r_.logtau:.1f} d, {r_.status}, {r_.origins}",
            "h1_sources_primary.csv")
    gx = ob[ob.source == "GX 339-4"]
    put("gx339_n", len(gx), "h1_outbursts_primary.csv")
    put("gx339_tau_min", 10 ** gx.logtau.min(), "h1_outbursts_primary.csv")
    put("gx339_tau_max", 10 ** gx.logtau.max(), "h1_outbursts_primary.csv")
    put("gx339_range_dex", gx.logtau.max() - gx.logtau.min(), "h1_outbursts_primary.csv")
    put("gx339_factor", 10 ** (gx.logtau.max() - gx.logtau.min()), "h1_outbursts_primary.csv")
    n = ps.n_outbursts
    put("systems_with_one_outburst", int((n == 1).sum()), "h1_sources_primary.csv")
    put("systems_with_multiple_outbursts", int((n > 1).sum()), "h1_sources_primary.csv")
    put("within_system_comparisons_total", int((n - 1).sum()), "h1_sources_primary.csv")
    put("within_system_comparisons_gx339", int(len(gx) - 1), "h1_sources_primary.csv")
    # ---- H1 fit
    h = json.loads((R / "h1_results.json").read_text())
    for k in ("A", "B", "log10_sigma_int"):
        q = h["H1_M1_posterior"][k]
        put(f"h1_{k}_2.5_50_97.5", [round(q[0], 3), round(q[2], 3), round(q[4], 3)], "h1_results.json")
    q = h["H1_M1_posterior"]["log10_sigma_int"]
    put("h1_sigma_int_dex_2.5_50_97.5", [round(10 ** q[0], 3), round(10 ** q[2], 3), round(10 ** q[4], 3)], "h1_results.json")
    put("h1_tau_at_1d", 10 ** h["H1_M1_posterior"]["A"][2], "h1_results.json")
    put("h1_M0_tau_d", 10 ** h["model_comparison"]["M0"]["params"][0], "h1_results.json")
    put("h1_M2_break_porb_d", 10 ** h["model_comparison"]["M2"]["params"][2], "h1_results.json")
    put("power", h["power"], "h1_results.json")
    put("kendall", h["kendall"], "h1_results.json")
    for m in ("M0", "M1", "M2"):
        c = h["model_comparison"][m]
        put(f"model_{m}", {k: round(c[k], 2) for k in ("AIC", "BIC", "LOSO_lpd")}, "h1_results.json")
    q = h["H2_rise_M1_posterior"]["B"]
    put("h2_B", [round(q[0], 3), round(q[2], 3), round(q[4], 3)], "h1_results.json")
    put("h2_kendall", h["H2_kendall"], "h1_results.json")
    put("h2_N_sources", h["H2_N_sources"], "h1_results.json")
    rob = pd.read_csv(R / "h1_robustness.csv")
    for _, r_ in rob.iterrows():
        put(f"robust[{r_.variant}]", f"{r_.N_sources}/{r_.N_outbursts} B={r_.B_median:.2f} ({r_.B_lo95:.2f}, {r_.B_hi95:.2f}) tauK={r_.kendall_tau:.2f} p={r_.kendall_p:.2f}",
            "h1_robustness.csv")
    x = json.loads((R / "h1_extra.json").read_text())
    loo = x["leave_one_system_out"]
    med = {k: v["B"][1] for k, v in loo.items()}
    hi = {k: v["B"][2] for k, v in loo.items()}
    put("loo_B_median_min", f"{min(med.values()):.3f} (without {min(med, key=med.get)})", "h1_extra.json")
    put("loo_B_median_max", f"{max(med.values()):.3f} (without {max(med, key=med.get)})", "h1_extra.json")
    put("loo_B_upper_min_max", [round(min(hi.values()), 3), round(max(hi.values()), 3)], "h1_extra.json")
    put("loo_n_upper_below_2_3", int(sum(v < 2 / 3 for v in hi.values())), "h1_extra.json")
    put("P_B_gt", {str(round(float(k), 3)): v for k, v in x["P_B_gt"].items()}, "h1_extra.json")
    print(open(R / "h1_hierarchical.txt").read())
    json.dump(out, open(R / "paper_numbers.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
