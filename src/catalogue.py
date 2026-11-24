"""T4.3: write the uniform 2016-2026 outburst catalogue results/outburst_table.csv (full precision).

One row per MAXI outburst window with a peak in the study era (MJD >= 57388), built from
results/timescales_maxi.csv (baseline-subtracted). Includes the dates and peak-normalised fluxes of
the selected 90/50/10 per cent points so that every timescale can be checked by hand.
Run after src.outbursts:  .venv/bin/python -m src.catalogue
"""
import pandas as pd

from src import config

COLS = ["source", "bh_status", "t_peak", "f_peak", "peak_err", "bright", "reflare", "flag",
        "win_start", "win_end", "baseline",
        "t90_rise", "f90_rise", "t50_rise", "f50_rise", "t10_rise", "f10_rise",
        "t90_decay", "f90_decay", "t50_decay", "f50_decay", "t10_decay", "f10_decay",
        "tau_rise_10_90", "tau_rise_10_90_lo", "tau_rise_10_90_hi", "tau_rise_10_50", "tau_rise_50_90",
        "tau_decay_10_90", "tau_decay_10_90_lo", "tau_decay_10_90_hi",
        "tau_decay_10_50", "tau_decay_10_50_lo", "tau_decay_10_50_hi",
        "tau_decay_50_90", "tau_decay_50_90_lo", "tau_decay_50_90_hi",
        "shape_ratio_decay", "tau_decay_10_90_smooth", "bat_f_peak", "bat_tau_decay_10_90"]


def main():
    t = pd.read_csv(config.RESULTS / "timescales_maxi.csv")
    t = t[t.era == "study"].copy()
    status = pd.read_csv(config.SAMPLE_CSV).set_index("source").bh_status
    t["bh_status"] = t.source.map(status)
    t["reflare"] = t.win_note.fillna("").apply(lambda s: "re-flare" in [p.strip() for p in s.split(";")])
    out = t[COLS].rename(columns={"t_peak": "t_peak_mjd", "f_peak": "f_peak_crab_2_10keV"})
    out.sort_values(["t_peak_mjd", "source"]).to_csv(config.RESULTS / "outburst_table.csv", index=False,
                                                     float_format="%.6g")
    main_ = out[out.bright & ~out.reflare & out.flag.isna()]
    print(f"{len(out)} windows, {out.flag.notna().sum()} flagged, {len(main_)} bright main outbursts "
          f"from {main_.source.nunique()} sources")


if __name__ == "__main__":
    main()
