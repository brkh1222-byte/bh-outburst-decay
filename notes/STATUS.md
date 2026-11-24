# STATUS (kept current by the pilot agent; newest first)

Branch: `research-plan` (from `main` at ba38f87, which already contains the 22 Nov analysis as one commit "progress").
Policy: Claude runs the project and drafts the paper; the researcher edits later. Authorship and AI-use statement are placeholders.

## 2026-11-25 session log

### Done
- Read all project files. Found that the 22 Nov work IS already committed and pushed on `main` (commit ba38f87, 24 Nov, "progress"), so there is no uncommitted backlog; new work goes on `research-plan`.
- Hash mismatches (results/analysis_plan_v1.sha256) fully explained by exact reconstruction (details go in results/analysis_plan_amendment_1.md):
  - analysis_plan_v1.md: file minus the appended "Implementation clarifications" section hashes to the recorded value.
  - data/outburst_windows.yaml: file minus the single `58560:` line (GS 1354-64 re-flare flag "added 2026-11-22 after referee check") hashes to the recorded value.
  - data/sample.csv: recorded hash reproduced with LF line endings (now CRLF) + GRS 1716-249 row without two status remarks + MAXI J1659-152 row with `in_tau_porb_test=False` and note "validation only: ...". None of these fields is read by the analysis code.
- CLAUDE.md / TASKS.md updated to the new roles policy.

- Amendment written: results/analysis_plan_amendment_1.md (+ src/amendment_checks.py, results/amendment_1_checks.json). Frozen-input re-run: primary H1 byte-identical; only "+ re-flares" row differs (B 0.05 vs 0.17).
- references.bib verified by helper against Crossref (44 entries; 3 titles corrected; Tominaga et al. 2020 added and verified).
- T2.2 done: src/plot_lightcurves.py -> results/lightcurves/*.png (24 sources + overview).
- GS 1354-64 / MAXI J1348-630 confusion re-checked: notes/confusion_check.md (claim softened to "most likely contamination").
- src/audit_numbers.py -> results/paper_numbers.json (every derived number in the paper).
- paper/main.tex revision 2 in progress (placeholders for authors/AI statement, plan paragraph, limitations, confusion section done).

### In progress
- T3.3 decay fits running: `nice .venv/bin/python -m src.fit_decay --steps 4000 > results/decay_fits.log` (rerun the same command if interrupted; it rewrites results/decay_fits.csv at the end).
- Helper agent: T1.1 novelty search (result to be written to notes/novelty.md).

### Next
- Add decay-fit subsection to the paper; audit table in paper/notes.md; novelty notes; tick TASKS.md; final commit.

### Needs the researcher
- T2.4 MAXI on-demand 2-12 keV light curves (manual web tool).
- Authorship and AI-use statement.

### How to resume
- Long jobs are run with `nice` one at a time; each script writes its outputs to results/ and can simply be rerun.
