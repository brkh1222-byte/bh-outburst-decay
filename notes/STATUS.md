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

### In progress
- Replica run of the H1 pipeline with the reconstructed frozen inputs (in the session scratchpad, not in the repo) to show the H1 numbers are unchanged. Timescale tables already identical except the one new flag; primary sample files identical byte for byte.
- Helper agents: (1) references.bib verification against Crossref/arXiv/ADS; (2) T1.1 novelty search.

### Next
- Write results/analysis_plan_amendment_1.md; T2.2 light-curve script + figures; T3.3 decay-shape fits (lmfit then emcee); re-verify the GS 1354-64 / MAXI J1348-630 confusion claim (notes/confusion_check.md); number audit table in paper/notes.md; revise paper/main.tex.

### Needs the researcher
- T2.4 MAXI on-demand 2-12 keV light curves (manual web tool).
- Authorship and AI-use statement.

### How to resume
- Long jobs are run with `nice` one at a time; each script writes its outputs to results/ and can simply be rerun.
