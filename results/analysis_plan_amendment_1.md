# Analysis plan v1 — Amendment 1 (integrity record)

Date: 2026-11-25. Written by the AI pilot agent (Claude) after an audit of the plan fingerprint.
`results/analysis_plan_v1.md` and `results/analysis_plan_v1.sha256` were **not edited** for this amendment.
All clock times below are local (UTC+8) on 2026-11-22 unless stated; 05:54:19 local = 2026-11-21T21:54:19Z.

## 1. The problem

`results/analysis_plan_v1.sha256` lists SHA-256 hashes of 11 files and the line
`frozen 2026-11-21T21:54:19Z`. On 2026-11-25 eight of the eleven files (all `src/` files listed)
still match. Three do not:

| File | Recorded hash (first 12) | Hash on 2026-11-25 (first 12) | Last modified |
|---|---|---|---|
| results/analysis_plan_v1.md | ce141469bd07 | f8152349259e | 05:56:06 |
| data/outburst_windows.yaml | 0bdad753ea99 | ed658d1e72bf | 07:59:18 |
| data/sample.csv | a9ae63fb0cb4 | 7ab071603e95 | 08:03:29 |

There was no git history for these files before the single commit `ba38f87` (2026-11-24 15:17),
which already contains the modified versions.

## 2. What changed (established by exact reconstruction)

For each file I removed the suspected later additions and re-hashed. In all three cases the
recorded hash is reproduced exactly, so the frozen content is known byte for byte.

1. **results/analysis_plan_v1.md.** The file truncated just before the heading
   `## Implementation clarifications (added before the first H1 result; no rule changed)`
   (3509 bytes, ending in one newline) has the recorded hash `ce141469…`.
   So the only change is that this section (two clarifications) was appended.
2. **data/outburst_windows.yaml.** The file without the single line
   `58560: "confusion: tail of the MAXI J1348-630 window above (re-flare split off by the detection); added 2026-11-22 after referee check"`
   has the recorded hash `0bdad753…`. So the only change is one added confusion flag for the
   GS 1354−64 re-flare window at MJD 58560.
3. **data/sample.csv.** The recorded hash `a9ae63fb…` is reproduced by the current file with
   (a) LF instead of CRLF line endings (the file was later rewritten by a CSV writer),
   (b) the GRS 1716−249 row without the remark "(K2 from Halpha FWHM correlation; not a full RV solution)" in
   `status_ref` and with the note ending at "old 2.4 kpc distance superseded",
   (c) the MAXI J1659−152 row with `in_tau_porb_test = False` and the note
   "validation only: 2010 outburst seen by both RXTE/ASM and MAXI (Yan & Yu peak MJD 55476)".
   No number (period, distance, mass) and no `bh_status`, `maxi_id` or `bat_name` value changed.

How to repeat: apply the three reversals above to copies of the files and run `shasum -a 256`.

## 3. When, relative to the H1 runs (from file-system timestamps)

| Time | Event (source: creation/modification times of the files) |
|---|---|
| 05:53:12 | validation written (`results/method_check.md`) |
| 05:54:19 | plan and `.sha256` created (matches the `frozen` line) |
| 05:55:25 | `src/tau_vs_porb.py` and `data/literature_porb.csv` created — **after** the fingerprint |
| 05:56:06 | plan modified (the two clarifications appended) |
| 05:56:13 | `results/h1_run.log` first created (start of the first logged H1 run) |
| 05:57:41–05:57:43 | first `h1_robustness.csv`, `h1_results.json`, `fig_tau_porb.png` (first result) |
| 07:59:18 | `outburst_windows.yaml` modified (58560 flag); timescale tables regenerated 07:59:24–31 |
| 08:02:13 | `src/tau_vs_porb.py` and `src/hierarchical.py` modified |
| 08:03:29 | `data/sample.csv` modified |
| 08:04:27 | final H1 run finished (the files now in `results/`) |

So: the plan clarifications were appended 7 s before the first logged run started and about 1.5 min
before the first result existed. The yaml and sample.csv changes were made about two hours **after**
the first result, and before the final run whose numbers are in the paper.

## 4. Could the changes have affected the H1 result?

**sample.csv — no.** The analysis code reads only `source`, `maxi_id`, `bat_name`, `bh_status`,
`porb_d` and `porb_method` from this file (`src/tau_vs_porb.py`, `src/outbursts.py`,
`src/catalogue.py`); `in_tau_porb_test`, `status_ref` and `notes` are never read. MAXI J1659−152
was already in the test in the first run through plan rule 4 (its period comes from
`data/literature_porb.csv`); only its label in sample.csv was out of date.

**outburst_windows.yaml — not the primary result; one robustness row changed.** I re-ran the
pipeline (`src.outbursts --raw`, `src.outbursts`, `src.tau_vs_porb`) on a copy of the repository
with the reconstructed frozen `sample.csv` and `outburst_windows.yaml`:

- `timescales_maxi.csv`: identical in every timescale; only the flag of the GS 1354−64 window at MJD 58560.5 differs.
- `h1_outbursts_primary.csv`, `h1_sources_primary.csv`, `h1_results.json`: **byte-identical** to the committed files.
  Primary result unchanged: B = 0.17, 95% interval [−0.17, 0.52].
- `h1_robustness.csv`: one row differs, "+ re-flares":
  frozen inputs 13 systems / 28 outbursts, B = 0.05 [−0.36, 0.47], Kendall τ = 0.15, p = 0.50;
  current inputs 13 / 27, B = 0.17 [−0.18, 0.51], τ = 0.28, p = 0.19.
  Both are consistent with zero. The flagged window is the tail of the MAXI J1348−630 contamination
  (see `notes/confusion_check.md`), so flagging it is justified, but it was done after the first
  result was seen, and the paper must say so and give both values.

**Plan clarifications — they define the sample, so they could matter in principle; measured effect is small.**
Both clarifications decide which literature outbursts enter. `src/amendment_checks.py`
(`results/amendment_1_checks.json`) refits the primary model with each undone:

| Variant | N systems / outbursts | B median [95%] | Outbursts added |
|---|---|---|---|
| A: as run | 13 / 26 | 0.169 [−0.169, 0.521] | — |
| B: clarification 1 undone (±20 d peak matching) | 13 / 28 | 0.177 [−0.159, 0.519] | GX 339−4 2021 and MAXI J1820+070 2018 literature values (double-counted) |
| C: clarification 2 undone (literature flux only) | 13 / 28 | 0.147 [−0.176, 0.485] | GX 339−4 2013 and 2017–18 (Saraswati et al.) |
| D: both undone | 13 / 30 | 0.149 [−0.177, 0.487] | all four |

The H1 decision (95% interval includes zero) is the same in all four.

## 5. What is not known

1. **The timestamps are local file-system metadata.** They are not independent evidence: nothing
   was committed, tagged or deposited externally before the results existed (the first commit
   containing these files is from 2026-11-24). The ordering in Section 3 cannot be verified by a
   third party.
2. **The analysis code was not covered by the fingerprint.** `src/tau_vs_porb.py` was created after
   the fingerprint and modified at 08:02:13, after the first result. `paper/notes.md` says the
   change was seeding the random numbers (and that the first, unseeded run gave power 84%/41%
   instead of 84%/39%). No earlier copy exists, so I cannot verify that nothing else changed.
3. **The first-run numbers were overwritten.** The 05:57 outputs do not survive. Apart from the
   power values quoted in `paper/notes.md`, I cannot show what the first run gave. The frozen-input
   re-run in Section 4 uses the *current* code.
4. **What was known when the clarifications were written.** The clarifications name specific
   outbursts (MAXI J1820+070 2018, GX 339−4 2021, GX 339−4 2013 and 2017–18), so the sample list
   had been inspected. The timestamps suggest no complete H1 run could have preceded them
   (the script existed for 41 s; a run took about 90 s), but an unlogged partial run cannot be
   excluded.
5. `data/literature_porb.csv` (periods of eight literature systems) was created after the
   fingerprint and is not in the hash list.

## 6. Consequences

- All three hash mismatches are explained, and none changes the primary H1 result.
- The plan was **documented before the first run but not verifiably frozen**: the fingerprint is
  local, the code and the period table were outside it, two clarifications were appended after it,
  and one flag was changed after the first result. The paper therefore does **not** describe the
  analysis as pre-registered. It describes the plan as written before the test, states these facts,
  and reports the "+ re-flares" row both ways.
- Task T3.8 (commit and tag the plan before the result) can no longer be done as intended. The
  tag `analysis-plan-v1` should not be created retroactively as if it predated the result.
- For any future confirmatory analysis in this project: commit and push the plan, the code and the
  input tables (or deposit them, e.g. OSF/Zenodo) **before** the first run, and keep first-run outputs.
