"""T2.1: download MAXI/GSC and Swift/BAT light curves for every source in data/sample.csv.

Files are cached in data/raw/ and only re-downloaded with --force.

How the two archives are organised
----------------------------------
* MAXI/GSC standard products: one text file per source and time binning,
  9 columns, no header: MJD, then rate and error in 2-20, 2-4, 4-10 and
  10-20 keV (photons/cm^2/s). Binning "1day" or "1orb" (one ISS orbit, ~92 min).
* Swift/BAT Transient Monitor: one text file per source, 15-50 keV,
  counts/cm^2/s, with a DATA_FLAG column (0 = good). Most sources live in the
  weak/ directory; a few bright ones live at the top level.

Usage:  .venv/bin/python -m src.download [--force]
"""
from __future__ import annotations

import argparse
import sys
import time

import pandas as pd
import requests

from src import config

HEADERS = {"User-Agent": "bh-outburst-decay research script (python-requests)"}


def fetch(url: str, dest, force: bool = False) -> str:
    """Download url to dest. Returns 'cached', 'ok' or an error string."""
    if dest.exists() and not force:
        return "cached"
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
    except requests.RequestException as exc:
        return f"error: {exc.__class__.__name__}"
    # Some servers answer 200 with an HTML error page; real light curves are plain text.
    if r.status_code != 200 or r.text.lstrip().startswith("<"):
        return f"http {r.status_code}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(r.text)
    time.sleep(1.0)  # be polite to public archives
    return "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-download cached files")
    args = ap.parse_args()

    sample = pd.read_csv(config.SAMPLE_CSV)
    log = []
    for _, row in sample.iterrows():
        src = row["source"]
        if isinstance(row["maxi_id"], str):
            for binning in ("1day", "1orb"):
                url = config.MAXI_URL.format(id=row["maxi_id"], binning=binning)
                dest = config.RAW_MAXI / f"{row['maxi_id']}_{binning}.dat"
                log.append((src, f"MAXI {binning}", fetch(url, dest, args.force)))
        else:
            log.append((src, "MAXI", "no standard file: needs on-demand tool"))

        if isinstance(row["bat_name"], str):
            dest = config.RAW_BAT / f"{row['bat_name']}.lc.txt"
            status = "not tried"
            for pattern in config.BAT_URLS:
                status = fetch(pattern.format(name=row["bat_name"]), dest, args.force)
                if status in ("ok", "cached"):
                    break
            log.append((src, "BAT", status))
        else:
            log.append((src, "BAT", "no BAT name in sample.csv"))

    width = max(len(s) for s, _, _ in log)
    for src, what, status in log:
        print(f"{src:<{width}}  {what:<10}  {status}")
    failed = [x for x in log if x[2].startswith(("error", "http"))]
    print(f"\n{len(log)} requests, {len(failed)} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
