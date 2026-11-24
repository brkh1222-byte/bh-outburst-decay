# Check of literature orbital periods against the original papers (T5.4)

Date: 2026-11-25. Done by a helper agent (arXiv abstracts and LaTeX sources, Crossref, journal pages);
summarised by the pilot agent. ADS pages could not be read. `data/literature_porb.csv` was **not changed**;
the differences below are too small to matter (largest: 0.8% = 0.003 dex) and changing an input after
the result needs a decision by the researcher. A refit with the corrected XTE J1650−500 period is in
`results/amendment_1_checks.json` if the key `porb_1650_corrected` is present.

| System | Used (h) | Original value | In hours | Method | Reference | Verdict |
|---|---|---|---|---|---|---|
| XTE J1118+480 (not in H1 primary) | 4.07 | 0.1699339(2) d | 4.0784 | RV spectroscopy | Torres et al. 2004, ApJ 612, 1026 (text, not abstract) | rounding: should be 4.08 |
| XTE J1550−564 | 37.0 | 1.5420333(24) d | 37.009 | RV + light curves | Orosz et al. 2011, ApJ 730, 75 (abstract) | match |
| GRO J1655−40 | 62.92 | 2.62168(14) d | 62.920 | photometry | van der Hooft et al. 1998 (arXiv:astro-ph/9709151, abstract); Greene et al. 2001 give 2.62191(20) d | match |
| GS 2023+338 = V404 Cyg (not in H1 primary) | 155.30 | 6.471170(2) d | 155.308 | RV spectroscopy | Casares et al. 2019, MNRAS 488, 1356 (table) | rounding: 155.31 |
| SAX J1819.3−2525 = V4641 Sgr (not in H1 primary) | 67.61 | 2.81730(1) d | 67.615 | photometry | Orosz et al. 2001, ApJ 555, 489 (abstract) | rounding: 67.62 |
| XTE J1650−500 | 7.63 | 0.3205(7) d, "(i.e. 7.63 hr)" | 7.692 | photometry + spectra | Orosz et al. 2004, ApJ 616, 376 (abstract) | **the abstract's hours do not equal its days; 0.3205 d = 7.69 h. Used value is 0.8% low** |
| MAXI J1659−152 | 2.41 | 2.414(5) h | 2.414 | X-ray dips | Kuulkers et al. 2013, A&A 552, A32 (abstract) | match |
| XTE J1859+226 | 6.58 | 6.58(5) h; newer 0.276(3) d = 6.62 h | 6.58 | photometry + RV | Corral-Santana et al. 2011, MNRAS 413, L15; Yanes-Rizo et al. 2022, MNRAS 517, 1476 | match (2011) |
| 4U 1543−47 (data/sample.csv) | 26.79377(7) | 1.116407(3) d | 26.79377 | RV | Orosz 2003, IAU Symp. 212 (arXiv:astro-ph/0209041), Table 1 | match, but that table cites "Orosz et al. 2002b, in preparation": **no published measurement paper was found for this value**. Orosz et al. 1998 give 1.123(8) d |
| GS 1354−64 (data/sample.csv) | 61.068(2) | 2.54451 d | 61.068 | RV spectroscopy | Casares et al. 2009, ApJS 181, 238 (abstract + text fragment) | value matches; the quoted uncertainty could not be read |

Not verified: Casares & Charles 1994 for V404 Cyg (paywalled); full texts in general (mostly abstracts).

Consequences for the paper: Table 1's period references for the five "compilation" systems can now
cite the original papers (XTE J1550−564: Orosz et al. 2011; GRO J1655−40: van der Hooft et al. 1998;
XTE J1650−500: Orosz et al. 2004; XTE J1859+226: Corral-Santana et al. 2011; MAXI J1659−152:
Kuulkers et al. 2013), once each bib entry is added and verified. Until then the paper keeps the
compilation citations and says that the values were compared with the original abstracts.
