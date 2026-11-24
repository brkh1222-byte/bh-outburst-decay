"""Project-wide constants and paths.

Every number here has a source. If you change one, change the comment too.
"""
from pathlib import Path

# --- Paths -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_MAXI = RAW / "maxi"
RAW_BAT = RAW / "bat"
RESULTS = ROOT / "results"
QC = RESULTS / "qc"
SAMPLE_CSV = DATA / "sample.csv"
WINDOWS_YAML = DATA / "outburst_windows.yaml"

# --- Data URLs (checked 2026-11-22) ------------------------------------------
# MAXI/GSC standard per-source light curves (MAXI readme, http://maxi.riken.jp/top/readme.html)
MAXI_URL = "http://maxi.riken.jp/star_data/{id}/{id}_g_lc_{binning}_all.dat"
# Swift/BAT Transient Monitor (Krimm et al. 2013, ApJS 209, 14). Some bright
# sources sit at the top level instead of in weak/; download.py tries both.
BAT_URLS = (
    "https://swift.gsfc.nasa.gov/results/transients/weak/{name}.lc.txt",
    "https://swift.gsfc.nasa.gov/results/transients/{name}.lc.txt",
)

# --- Crab normalisation -------------------------------------------------------
# MAXI readme (versions v7.7L, v7Lrkn, v6m): 1 Crab = 3.8 ph/cm^2/s (2-20 keV),
# 2.2 (2-4), 1.25 (4-10), 0.40 (10-20). The 2-20 keV value is not the sum of the
# sub-bands because each band is corrected assuming a Crab spectrum.
MAXI_CRAB = {"2-20": 3.8, "2-4": 2.2, "4-10": 1.25, "10-20": 0.40}
# Primary band in this project: 2-10 keV = (2-4) + (4-10) photon fluxes.
MAXI_CRAB["2-10"] = MAXI_CRAB["2-4"] + MAXI_CRAB["4-10"]  # 3.45 ph/cm^2/s
# Swift/BAT: 1 mCrab = 0.00022 count/cm^2/s in 15-50 keV (Krimm et al. 2013).
BAT_CRAB = 0.220

# --- Timescale method (Yan & Yu 2015; Saraswati et al. 2025) -----------------
LEVELS = (0.1, 0.5, 0.9)          # fractions of the daily peak flux
PEAK_MIN_CRAB = 0.1               # Yan & Yu keep outbursts peaking above 0.1 Crab

# --- Physics --------------------------------------------------------------
L_EDD_PER_MSUN = 1.26e38          # erg/s, pure hydrogen

# --- Data-quality masks for BAT (BAT Transient Monitor synopsis page) --------
BAT_BAD_MJD_RANGES = (
    (58736.0, 58747.0),  # 10-20 Sep 2019 inclusive: no data
    (58571.0, 58573.0),  # 29-30 Mar 2019: spurious zeros
)

# --- Study window ---------------------------------------------------------
WINDOW_START_MJD = 57388.0        # 2016-01-01
