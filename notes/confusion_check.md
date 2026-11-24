# Re-check of the claimed source confusion in Saraswati et al. (2025): GS 1354−64 vs MAXI J1348−630

Date: 2026-11-25 (AI pilot agent). This is a claim about another group's paper, so the evidence
and its limits are listed separately. Numbers recomputed today from `data/raw/` with
`src/lightcurves.py` (MAXI 2–10 keV standard daily product, BAT 15–50 keV daily, Crab units).

## The claim under test

Saraswati, Vierdayanti & Premadi (2025, MNRAS 537, 1146), Table 2, list for GS 1354−64 an
outburst ("O", morphology "V") peaking at MJD 58 524 with F_peak = 1.92 ± 0.04 Crab (2–12 keV),
duration 84.5 d, τ_d,10–90 = 12.4 ± 5.45 d (transcription: `data/literature_raw/saraswati2025_table2_pdftext.txt`).
Our claim: this event is contamination from MAXI J1348−630, not an outburst of GS 1354−64.

## Evidence

1. **Position.** GS 1354−64 (13h58m09.7s, −64°44′05″) and MAXI J1348−630 (13h48m12.8s, −63°16′28″)
   are 1.82° apart (astropy). The MAXI/GSC point-spread function is about 1.5° FWHM.
2. **Timing.** MAXI J1348−630 was discovered by MAXI on 2019 January 26 (ATel #12425) and reached its
   first peak about 14 d later (Tominaga et al. 2020: ~4 Crab in 2–20 keV), i.e. MJD ≈ 58523.
   In our data its 2–10 keV peak is 3.11 Crab at MJD 58523.5. The Saraswati event peaks at MJD 58524.
3. **The MAXI standard light curve of GS 1354−64 copies MAXI J1348−630.** From MJD 58495 to 58625
   the two daily light curves have Pearson r = 0.84 and Spearman ρ = 0.86 (124 common days).
   The GS 1354−64 file rises from 0.002 Crab (58505.5) to 0.41–0.44 Crab (58523.5–58527.5) in step
   with MAXI J1348−630. Before the discovery (MJD 58440–58500) its median is 0.0014 Crab.
4. **Swift/BAT sees nothing at GS 1354−64.** BAT is a coded-mask imager with ~17′ resolution, so it
   separates the two sources. For GS 1354−64 in MJD 58505–58545: 41 daily points, median 0.005 Crab,
   weighted mean 0.0056 ± 0.0015 Crab, no day above 3σ (0 of 108 days in MJD 58495–58625).
   In its real outbursts the same BAT light curve shows 0.26 Crab (2015, peak MJD 57223) and
   ~0.2 Crab (2025–26).
5. **Leak fraction varies as expected for contamination.** The ratio (GS 1354−64 file)/(MAXI J1348−630 file)
   swings between ~0.01 and ~0.16 with maxima near MJD 58527 and 58562, about 35 d apart. MAXI's
   scan geometry repeats with the ~70 d precession of the ISS orbit, so a leak that depends on scan
   direction would vary like this. (This is my interpretation, not a tested model.)
6. **No independent report.** The recorded outbursts of GS 1354−64 are 1987, 1997, 2015 and 2025–26
   (e.g. Koljonen et al. 2016; ATel #17563, #17586). A web search found no report of a 2019 outburst.
   A 1.9 Crab outburst of a known black hole would have been widely reported.
7. **Flux scale is consistent.** Saraswati et al.'s peak fluxes for GS 1354−64 are about 4 times the
   MAXI standard 2–10 keV product for both events: 2015, 0.25 vs 0.065 Crab; 2019, 1.92 vs 0.41–0.44 Crab
   (0.565 ± 0.036 on one noisy day). So their 2019 event looks like the same feature that is in the
   standard GS 1354−64 file, on their flux scale.

## Limits

- I have not seen or reproduced Saraswati et al.'s own light curve. They used 2–12 keV (ASM-like)
  MAXI data; reproducing it needs the MAXI on-demand tool (task T2.4, manual). The factor ~4 in flux
  scale between their values and the standard product is itself unexplained.
- I read their Table 2 from the PDF text only; I have not checked whether the text of their paper
  discusses this event or flags it.
- BAT (15–50 keV) could miss a purely soft outburst. Against that: GS 1354−64's known outbursts were
  hard, a 1.9 Crab soft state normally still has a detectable hard tail, and the timing coincidence
  to within a day would be needed as well.
- The literature search for a 2019 outburst was a web search, not a full ATel/ADS query.
- The authors have not been contacted.

## Conclusion

The evidence is strong that the MJD 58524 event attributed to GS 1354−64 is MAXI J1348−630 seen
through the MAXI point-spread function. It is still an inference from public monitoring data, so
the paper should say "is most likely contamination from MAXI J1348−630", give points 1–4, and
state that the original light curve was not reproduced. Courtesy step before submission: write to
the authors (needs the researcher).

The same reasoning supports our own flags on the GS 1354−64 MAXI windows at MJD 58537 and 58560
(the second peak of the leak pattern in point 5).
