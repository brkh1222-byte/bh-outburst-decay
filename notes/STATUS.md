# STATUS (kept current by the pilot agent)

Last update: 2026-11-25, end of the pilot session. Branch: `research-plan` (from `main` at ba38f87; `main` already held the 22 Nov analysis as one commit, "progress", made by the researcher on 24 Nov).
Policy: Claude runs the project and drafts the paper; the researcher edits later. Authorship and the AI-use statement are placeholders in paper/main.tex.

## Main result (unchanged)
H1: slope B = 0.17, 95% interval [−0.17, 0.52], 13 systems / 26 outbursts. H1 not supported. Power 0.84 for B = 0.5, 0.39 for B = 0.3.

## Done on 2026-11-25
1. **Hash mismatches explained** (results/analysis_plan_amendment_1.md). All three recorded hashes reproduced exactly:
   plan = current file minus the appended "Implementation clarifications"; windows file = minus one flag line (GS 1354−64 MJD 58560);
   sample.csv = LF line endings + two rows' text fields. Re-run on the fingerprinted inputs: primary H1 files byte-identical; only the
   "+ re-flares" row changes (B = 0.05 [−0.36, 0.47] before the flag, 0.17 [−0.18, 0.51] after). Clarifications undone: B = 0.15–0.18.
   Not verifiable: timestamps are local; test script was outside the fingerprint and edited after the first run; first-run output not kept.
   The paper says "written before the test, not pre-registered".
2. **References**: all entries checked against Crossref; 3 titles corrected; 3 entries added (Tominaga2020, Orosz2004, Newville2014).
3. **T1.1 novelty** (notes/novelty.md): no blocking paper found via OpenAlex / Semantic Scholar / INSPIRE / arXiv. ADS could not be queried, so the by-hand ADS check stays open.
4. **T2.2** src/plot_lightcurves.py → results/lightcurves/ (24 sources + overview).
5. **T3.3** src/fit_decay.py (lmfit then emcee, 16000 steps) → results/decay_fits.csv, decay_fits_summary.md, decay_fits/*.png; src/fit_decay_porb.py → results/decay_fits_porb.json. Broken model preferred for 17 of 24 (2016–2026). Exploratory.
6. **Confusion claim re-checked** (notes/confusion_check.md): strong but inferential; paper now says "most likely contamination".
7. **Literature periods checked** (notes/porb_check.md): XTE J1650−500 is 0.8% low; input table not changed; refit gives B = 0.17 [−0.16, 0.51].
8. **Number audit** (paper/notes.md, src/audit_numbers.py → results/paper_numbers.json): all numbers traced; 5 rounding errors in Table 2 fixed.
9. **paper/main.tex revision 2**: new title, placeholders, plan paragraph, both re-flare values, new checks in Table 4, §5.8 decay fits, expanded limitations, softened claims.

## Not done / open
- T2.4 MAXI on-demand 2–12 keV light curves (manual web tool) — needs the researcher.
- T1.1 by-hand ADS citation check — needs the researcher (or an ADS API token).
- T3.4 peak L/L_Edd, T3.5 hardness transitions, H3, H4 — not started; need a choice of bolometric correction and distances/masses.
- T3.8 cannot be met retroactively (see amendment).
- main.tex has **not been compiled**: no LaTeX on this machine. Static checks pass (braces, \begin/\end, all \cite keys in the .bib, all \ref labels defined).
- Figures in paper/figures/ are unchanged from 22 Nov (no figure for §5.8 yet).
- Cited papers were checked at metadata/abstract level only, not read in full.

## Questions for the researcher
1. Authorship and AI-use statement (placeholders in main.tex).
2. Whether to write to Saraswati et al. about the GS 1354−64 event before submission.
3. Whether to correct the XTE J1650−500 period in data/literature_porb.csv (changes nothing material) and cite original period papers in Table 1.
4. Venue: full MNRAS paper vs short note, given a null result with 13 systems and a non-registered plan.

## How to rerun
`.venv/bin/python -m src.audit_numbers` (light). Heavy, one at a time under `nice`:
`python -m src.amendment_checks`, `python -m src.plot_lightcurves`, `python -m src.fit_decay --steps 16000` (about 30–60 min on a loaded machine), `python -m src.fit_decay_porb`.
