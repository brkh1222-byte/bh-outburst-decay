# bh-outburst-decay

Does disc size set the decay? This repo measures outburst timescales of black hole X-ray transients in the MAXI era (2016–2026) and tests the decay-time vs orbital-period relation.

📄 **Read the research proposal:** [PROPOSAL.md](PROPOSAL.md) · **Tasks:** [TASKS.md](TASKS.md)

## Plan

Outburst sample and system parameters → MAXI + Swift/BAT light curves → rise/decay fits → Eddington-scaled peaks → τ_decay vs P_orb (combined with the RXTE-era literature)

## Status

Pipeline built and validated; H1 result: slope B = 0.17, 95% interval −0.17 to 0.52 (13 systems), so the predicted increase of decay time with orbital period is not detected. Draft paper in `paper/main.tex` (AI-drafted, not yet edited by the researcher). Current state: [notes/STATUS.md](notes/STATUS.md). Integrity record of the analysis plan: [results/analysis_plan_amendment_1.md](results/analysis_plan_amendment_1.md).

## Data credit

MAXI/GSC (RIKEN, JAXA, MAXI team); Swift/BAT Transient Monitor (NASA GSFC); BlackCAT.
