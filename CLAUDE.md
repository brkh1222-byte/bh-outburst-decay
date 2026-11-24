# CLAUDE.md

This is a research project by an independent astrophysics researcher. It builds uniform rise and decay timescales and Eddington-scaled peaks for 2016–2026 black hole X-ray transient outbursts (MAXI + Swift/BAT), and tests whether the decay timescale scales with orbital period (disc size). Read PROPOSAL.md first. A mentor who works on black holes may co-author.

- **Stack:** Python with numpy, scipy, lmfit/emcee, astropy and pandas. Public MAXI and BAT light curves; laptop-scale.
- **Parameters:** every system parameter (P_orb, distance, mass) in `data/sample.csv` must have a cited reference column. Never invent values. Mark unknowns as NaN.
- **Comparability:** use the same timescale definitions as Yan & Yu 2015 and Saraswati et al. 2025 so the samples can be merged.
- **Roles (policy since 2026-11-25):** the researcher pilots; Claude runs the project (code, analysis, checks) and drafts the paper; the researcher edits it later. Authorship is undecided: keep the placeholders `[AUTHORS — TBD]` and `[AI-USE STATEMENT — TBD]` in `paper/main.tex` until the researcher decides. The paper must carry an AI-use disclosure.
- **Integrity:** explain methods when implementing them. Verify every citation against ADS/Crossref. Every number in the paper must be traceable to a file in `results/` (see the audit table in `paper/notes.md`). Never edit `results/analysis_plan_v1.md` or its `.sha256`; changes go in dated amendment files (`results/analysis_plan_amendment_*.md`). Do not call the plan pre-registered: it was fingerprinted locally with no external timestamp (see `results/analysis_plan_amendment_1.md`).
- **Machine:** shared laptop. At most one CPU-heavy process at a time, under `nice`; no GPU work. Never commit `data/raw/` or `.venv/`.
- **Status log:** keep `notes/STATUS.md` current.
