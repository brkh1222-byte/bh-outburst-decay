# CLAUDE.md

This is a research project by a 17-year-old astrophysics student. It builds uniform rise and decay timescales and Eddington-scaled peaks for 2016–2026 black hole X-ray transient outbursts (MAXI + Swift/BAT), and tests whether the decay timescale scales with orbital period (disc size). Read PROPOSAL.md first. The student's mentor works on black holes and may co-author.

- **Stack:** Python with numpy, scipy, lmfit/emcee, astropy and pandas. Public MAXI and BAT light curves; laptop-scale.
- **Parameters:** every system parameter (P_orb, distance, mass) in `data/sample.csv` must have a cited reference column. Never invent values. Mark unknowns as NaN.
- **Comparability:** use the same timescale definitions as Yan & Yu 2015 and Saraswati et al. 2025 so the samples can be merged.
- **Integrity:** the student must understand and write the paper themselves. Explain methods when implementing them. Verify every citation.
