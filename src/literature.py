"""T1.3: build data/literature_timescales.csv from the two RXTE/MAXI-era samples.

Inputs (verbatim extracts, kept in data/literature_raw/ for provenance):
  yanyu2015_table1.csv  - Yan & Yu 2015 Table 1 (system parameters), parsed from arXiv:1408.5146v2 HTML
  yanyu2015_table8.csv  - Yan & Yu 2015 Table 8 (per-outburst parameters), same source
  saraswati2025_table2_pdftext.txt - Saraswati et al. 2025 Table 2, text extracted from the
                          published PDF (doi:10.1093/mnras/staf042), page 1151
  Saraswati et al. 2025 Table 1 (orbital periods) was transcribed verbatim and is
  hard-coded below (SARASWATI_PORB_H).

Rules
  * Yan & Yu: black holes only (Table 1 rows 1-22; the remaining 14 are neutron stars).
  * Saraswati: rows marked with a star (alternative distance for GS 1354-64) are dropped,
    because they repeat the same timescales.
  * Each row records which paper it came from. Outbursts in both papers are flagged with
    `dup_group` so the analysis can keep one.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src import config

RAW = config.DATA / "literature_raw"

# Saraswati et al. 2025 Table 1, P_orb in hours, as printed.
SARASWATI_PORB_H = {
    "XTE J1118+480": 4.07, "XTE J1550-564": 37.0, "GRO J1655-40": 62.92, "GX 339-4": 42.21,
    "MAXI J1820+070": 16.45, "SAX J1819.3-2525": 67.61, "4U 1543-47": 26.79,
    "GS 1354-64": 61.06, "GS 2023+338": 155.30,
}

# Common names so the two papers and our sample line up.
ALIASES = {
    "4U 1543-475": "4U 1543-47", "SWIFT J1753.5-0127": "Swift J1753.5-0127",
    "SWIFT J1539.2-6227": "Swift J1539.2-6227", "SWIFT J1842.5-1124": "Swift J1842.5-1124",
    "MAXI J1820 + 070": "MAXI J1820+070", "XTE J1118 + 480": "XTE J1118+480",
    "GS 2023 + 338": "GS 2023+338", "SAX J1819.3-2525": "SAX J1819.3-2525",
    "4U 1630-472": "4U 1630-47", "H 1743-322": "H1743-322",
}


def _norm(name: str) -> str:
    name = name.replace("−", "-").replace("–", "-").strip()
    name = re.sub(r"\s*-\s*", "-", name)
    return ALIASES.get(name, name)


def _pm(cell: str):
    """'7.12\\pm 2.15' or '7.12 ± 2.15' -> (7.12, 2.15); '\\cdots' or '–' -> (nan, nan)."""
    cell = cell.replace("\\pm", "±")
    m = re.match(r"\s*([0-9.]+)\s*±\s*([0-9.]+)", cell)
    if m:
        return float(m.group(1)), float(m.group(2))
    try:
        return float(cell), np.nan
    except ValueError:
        return np.nan, np.nan


TAU_COLS = ["tau_rise_10_90", "tau_rise_10_50", "tau_rise_50_90",
            "tau_decay_10_90", "tau_decay_10_50", "tau_decay_50_90"]


def yan_yu() -> pd.DataFrame:
    t1 = pd.read_csv(RAW / "yanyu2015_table1.csv")
    bh = t1.iloc[:22]  # rows 1-22 are the 22 BH systems
    porb = {}
    for _, r in bh.iterrows():
        v = r.iloc[3]
        porb[_norm(r.iloc[0])] = float(v) if re.fullmatch(r"[0-9.]+", str(v)) else np.nan
    t8 = pd.read_csv(RAW / "yanyu2015_table8.csv", header=None, skiprows=2)
    rows, current = [], None
    for _, r in t8.iterrows():
        if isinstance(r[0], str) and r[0].strip():
            current = _norm(r[0])
        if current not in porb:
            continue  # neutron star
        rec = {"source": current, "paper": "Yan & Yu 2015", "instrument": "RXTE/ASM 2-12 keV",
               "t_peak_mjd": float(r[1])}
        rec["f_peak_crab"], rec["f_peak_err"] = _pm(str(r[2]))
        for col, cell in zip(TAU_COLS, r[3:9]):
            rec[col], rec[col + "_err"] = _pm(str(cell))
        rec["porb_h_paper"] = porb[current]
        rows.append(rec)
    return pd.DataFrame(rows)


def saraswati() -> pd.DataFrame:
    text = (RAW / "saraswati2025_table2_pdftext.txt").read_text()
    body = text.split("(10 −10 M ⊙ yr −1 )", 1)[1].split("Notes.", 1)[0]
    num = r"(?:[0-9.]+ ± [0-9.]+|–)"
    row_re = re.compile(
        rf"^(?:(?P<name>\S.*?)\.{{3,}} )?(?P<mjd>\d\d \d\d\d)(?P<star> ⋆)? (?P<type>MO|O) (?P<morph>[MFTV]) "
        rf"(?P<feat>LP|B, P|B|P|–) (?P<fpeak>{num}) (?P<lpeak>{num}) (?P<dur>[0-9.]+) "
        rf"(?P<t1>{num}) (?P<t2>{num}) (?P<t3>{num}) (?P<t4>{num}) (?P<t5>{num}) (?P<t6>{num})")
    rows, current = [], None
    for line in body.splitlines():
        line = line.strip()
        m = row_re.match(line)
        if not m:
            continue
        if m.group("name"):
            current = _norm(m.group("name"))
        if m.group("star"):
            continue
        rec = {"source": current, "paper": "Saraswati et al. 2025",
               "instrument": "RXTE/ASM or MAXI/GSC 2-12 keV",
               "t_peak_mjd": float(m.group("mjd").replace(" ", "")),
               "type": m.group("type"), "morphology": m.group("morph"), "features": m.group("feat"),
               "duration_d": float(m.group("dur"))}
        rec["f_peak_crab"], rec["f_peak_err"] = _pm(m.group("fpeak"))
        # Saraswati column order: rise 10-50, 50-90, 10-90; decay 10-50, 50-90, 10-90
        order = ["tau_rise_10_50", "tau_rise_50_90", "tau_rise_10_90",
                 "tau_decay_10_50", "tau_decay_50_90", "tau_decay_10_90"]
        for col, key in zip(order, ["t1", "t2", "t3", "t4", "t5", "t6"]):
            rec[col], rec[col + "_err"] = _pm(m.group(key))
        rec["porb_h_paper"] = SARASWATI_PORB_H.get(current, np.nan)
        rows.append(rec)
    return pd.DataFrame(rows)


def main():
    yy, sa = yan_yu(), saraswati()
    lit = pd.concat([yy, sa], ignore_index=True)
    # Same outburst in both papers: same source, peak dates within 15 d.
    lit["dup_group"] = ""
    for i, a in lit[lit.paper == "Saraswati et al. 2025"].iterrows():
        m = lit[(lit.paper == "Yan & Yu 2015") & (lit.source == a.source)
                & ((lit.t_peak_mjd - a.t_peak_mjd).abs() <= 15)]
        for j in m.index:
            tag = f"{a.source}@{int(a.t_peak_mjd)}"
            lit.loc[[i, j], "dup_group"] = tag
    lit["flag"] = ""
    # GS 1354-64 at MJD 58524: no outburst in Swift/BAT (median 0.003 Crab in Feb 2019),
    # while MAXI J1348-630 (1.82 deg away) peaked at MJD 58523.5. Treated as source confusion.
    bad = (lit.source == "GS 1354-64") & (lit.t_peak_mjd == 58524)
    lit.loc[bad, "flag"] = "confusion: MAXI J1348-630 (this work, BAT check)"
    cols = ["source", "paper", "instrument", "t_peak_mjd", "type", "morphology", "features",
            "f_peak_crab", "f_peak_err", "duration_d"] + \
           [c for t in TAU_COLS for c in (t, t + "_err")] + ["porb_h_paper", "dup_group", "flag"]
    lit = lit.reindex(columns=cols)
    out = config.DATA / "literature_timescales.csv"
    lit.to_csv(out, index=False)
    print(f"wrote {out}: {len(yy)} Yan & Yu BH outbursts, {len(sa)} Saraswati rows, "
          f"{(lit.dup_group != '').sum() // 2} duplicate pairs")
    return lit


if __name__ == "__main__":
    main()
