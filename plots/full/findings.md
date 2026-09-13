# Measured findings: full

All 234 planned measurement rows completed; 3 measured repeats per case.
Counts and times come from separate runs. Smoke data are not assignment evidence.

## Threshold selection

| Input size n | Lowest median CPU S | Fewest median comparisons S |
|---|---:|---:|
| 1,000 | 16 | 1 |
| 10,000 | 32 | 1 |
| 100,000 | 32 | 1 |

CPU ties in the displayed table use the smaller S. The saved shortlist applies
the predeclared geometric-ratio rule across these sizes. At n=1,000,000,
the lowest confirmation median selected **S=12**, best among the shortlisted
tested values. Check the min-max intervals in `c3_confirmation.png`: three seeds
do not establish a universal optimum or statistical significance.

## Final n=10,000,000 comparison

| Metric | Original | Hybrid S=12 |
|---|---:|---:|
| Median CPU seconds | 92.093750 | 94.078125 |
| CPU min-max seconds | 78.968750-92.515625 | 85.000000-99.906250 |
| Median key comparisons | 220,099,689 | 226,418,149 |

Speedup per paired seed = original CPU seconds / hybrid CPU seconds.
Median paired speedup = **0.929x**, range
0.922-0.983x. A value above 1 means the
hybrid is faster. The ratio of the two medians is 0.979x;
it is a different statistic. Hybrid median comparisons changed by
+2.87% relative to original.

Across the three paired seeds, the hybrid was faster in
**0**, slower in **3**,
and tied in **0**. These observations include every
measured regression; no repeat was discarded or replaced after seeing its result.

Raw per-repeat counts and times are in `final_paired_comparisons.csv` and
`final_paired_cpu.csv`; the original raw observations remain in the results folder.

## Connection to theory

At fixed S=16, the comparison plot and C/(n log2 n) normalization
are consistent with the derived Theta(n log n) fixed-threshold growth. The maximum
absolute relative difference from the random-distinct expectation across the
scale medians is 0.608%.
That analytical curve is unscaled and is only approximate for repeated integers.
Agreement over seven measured sizes is evidence of consistency, not a proof of
asymptotic complexity; the recurrence supplies the proof.

For fixed n, increasing S creates stepwise changes in leaf sizes. Insertion work
eventually increases faster than the saved merge comparisons. The CPU chart
measures extra costs absent from the comparison count: recursion, loop/index
operations, pointer assignments and copying. Separate instrumentation avoids
count increments distorting the timed comparison.

## Scope and limitations

One CPython interpreter and one Windows laptop, IID uniform integers with x=1,000,000,
three distinct seeds per case, and a finite threshold grid. Repeats mix input
variation and timing variation; they are not independent hardware replications.
Small-case batching repeats each seed's input, not additional independent datasets.
Timers exclude input generation/reset, merge-buffer allocation, validation and I/O.
The same machine was also used for lightweight document preparation; background
OS/browser activity was not controlled. No cache or thermal profiling was done.
Min-max bars are observed ranges, not confidence intervals.
The largest recorded post-validation RSS was 583.1 MiB;
this is a sampled process footprint, not a measured allocation peak.
Exact frequency histograms plus sorted order prove the bounded-integer multiset
was preserved. Fingerprints alone would not give that guarantee.
