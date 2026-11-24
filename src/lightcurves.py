"""Load MAXI/GSC and Swift/BAT light curves into a common format.

Every loader returns a pandas DataFrame with columns
    mjd   - time (MJD, bin centre)
    flux  - flux in Crab units for the chosen band
    err   - 1-sigma error in Crab units
sorted by time, with bad rows removed.

Why Crab units? A source's count rate depends on the instrument. Dividing by
the Crab Nebula's rate in the same band and instrument gives a number that is
roughly instrument-independent ("this source was 0.3 times as bright as the
Crab"). Timescales are flux *ratios*, so the Crab factor cancels in them; it
matters only for the 0.1 Crab selection cut and for luminosities.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config

MAXI_COLUMNS = ["mjd", "r2_20", "e2_20", "r2_4", "e2_4", "r4_10", "e4_10", "r10_20", "e10_20"]


def load_maxi(maxi_id: str, binning: str = "1day", band: str = "2-10") -> pd.DataFrame:
    """MAXI/GSC standard light curve in Crab units.

    band: "2-10" (primary; sum of the 2-4 and 4-10 keV photon fluxes),
          "2-20", "2-4", "4-10" or "10-20".
    """
    path = config.RAW_MAXI / f"{maxi_id}_{binning}.dat"
    raw = pd.read_csv(path, sep=r"\s+", header=None, comment="#")
    if raw.shape[1] == 11:  # version-specific files have centre, low, high MJD
        raw = raw.drop(columns=[1, 2])
    raw.columns = MAXI_COLUMNS
    if band == "2-10":
        rate = raw["r2_4"] + raw["r4_10"]
        err = np.hypot(raw["e2_4"], raw["e4_10"])  # independent errors add in quadrature
    else:
        lo, hi = band.split("-")
        rate, err = raw[f"r{lo}_{hi}"], raw[f"e{lo}_{hi}"]
    crab = config.MAXI_CRAB[band]
    df = pd.DataFrame({"mjd": raw["mjd"], "flux": rate / crab, "err": err / crab})
    df = df[np.isfinite(df["flux"]) & np.isfinite(df["err"]) & (df["err"] > 0)]
    return df.sort_values("mjd").reset_index(drop=True)


def load_maxi_bands(maxi_id: str, binning: str = "1day") -> pd.DataFrame:
    """All MAXI bands in Crab units (for hardness ratios)."""
    path = config.RAW_MAXI / f"{maxi_id}_{binning}.dat"
    raw = pd.read_csv(path, sep=r"\s+", header=None, comment="#")
    if raw.shape[1] == 11:
        raw = raw.drop(columns=[1, 2])
    raw.columns = MAXI_COLUMNS
    out = pd.DataFrame({"mjd": raw["mjd"]})
    for band in ("2-4", "4-10", "10-20", "2-20"):
        lo, hi = band.split("-")
        out[f"f{lo}_{hi}"] = raw[f"r{lo}_{hi}"] / config.MAXI_CRAB[band]
        out[f"e{lo}_{hi}"] = raw[f"e{lo}_{hi}"] / config.MAXI_CRAB[band]
    return out.sort_values("mjd").reset_index(drop=True)


def load_bat(name: str) -> pd.DataFrame:
    """Swift/BAT Transient Monitor daily light curve (15-50 keV) in Crab units.

    Keeps DATA_FLAG == 0 only and masks the date ranges listed in config.
    """
    path = config.RAW_BAT / f"{name}.lc.txt"
    cols = ["mjd", "rate", "err", "year", "day", "stat_err", "sys_err", "flag",
            "t_expo", "t_coded", "t_dith"]
    raw = pd.read_csv(path, sep=r"\s+", comment="#", header=None, names=cols, usecols=range(len(cols)))
    raw = raw[raw["flag"] == 0]
    for lo, hi in config.BAT_BAD_MJD_RANGES:
        raw = raw[~((raw["mjd"] >= lo) & (raw["mjd"] <= hi))]
    df = pd.DataFrame({"mjd": raw["mjd"].astype(float),
                       "flux": raw["rate"] / config.BAT_CRAB,
                       "err": raw["err"] / config.BAT_CRAB})
    df = df[np.isfinite(df["flux"]) & (df["err"] > 0)]
    return df.sort_values("mjd").reset_index(drop=True)
