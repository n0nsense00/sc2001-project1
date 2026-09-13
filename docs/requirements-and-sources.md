# Requirements and source decisions

Read in full: `sources/Project1.pdf` (1 page) and `sources/info.pdf` (2 pages).
These are copies of the user's files in `C:/Users/daboi/Downloads`.
Their text and every page were inspected; no attachment was missing.

## Assignment requirements (the PDFs are the authority)

- (a) Switch from merge sort to insertion sort when the current range has at most S items.
- (b) Random integer arrays from n=1,000 through n=10,000,000, values in [1,x].
- (c)(i) Fixed S: key comparisons against n and theory.
- (c)(ii) Fixed n: key comparisons against S and theory.
- (c)(iii) Investigate a suitable S across different n.
- (d) Original lecture merge sort versus the hybrid on 10 million integers: key comparisons and CPU time, using a tuned S.
- Presentation: 10 minutes total, including 2 minutes of Q&A; every member understands all parts.
- Grading: correctness/implementation 40%, theoretical/empirical analysis 40%, presentation/clarity 20%.
- Teams of 3-4 are assigned by the lab TA. Suggested work allocation here does not form a new team.
- No submission is required for Projects 1 and 2. The repository and slides serve collaboration and demonstration.
- `info.pdf` also addresses attendance, absence with MC/LOA, participation and completion before the lab. Those are course instructions to students; no messages, invitations or submissions are sent by this project.

## Additional user requirements

Python only for algorithms and experiments; explicit counted/uncounted implementations;
focused tests; reproducible seeds/configurations; at least three measured repeats where
practical; CPU-time primary threshold selection; sequential fair timing; validation,
resume, notebook, plots, documentation, presentation and learning materials.
These details are requested by the user and are not claimed to appear in the PDFs.

## Design choices

- CPython 3.13, integer lists, one reusable list buffer; range [lo,hi).
- x=1,000,000, uniform `random.Random(seed).randint(1,x)`.
- Seven input sizes, exploratory fixed S=16 (not an optimality assumption).
- Nine tuning thresholds; three repeats at three sizes; confirm the three strongest
  CPU candidates at n=1,000,000. Use new seeds for the final n=10,000,000 comparison.
- Median CPU time is primary. The shortlist uses a geometric mean of per-size CPU
  ratios relative to S=1, weighting sizes equally. Confirmation chooses its lowest
  median, ties resolved by smaller S. No claim of global optimality.
- Timed small inputs use batches to reduce CPU clock quantization. Data resetting
  and buffer allocation stay outside timing. All full-run cases retain three repeats.
- Exact histograms validate these bounded integers; no giant reference sort needed.

## Lecture implementation that was actually available

`C:/Users/daboi/Downloads/01_Sorting.pdf`: pages 12, 14 and 15 were read and the
algorithm pages visually checked. Page 12 specifies top-down recursion, floor midpoint
and half-open ranges. Page 14 merges by iterating right-hand values and comparing
the current left item using <=, taking left ties first. Its line 7 says B[j],
interpreted as B_r[j] from context.

Our two-pointer merge makes the same sequence of data-order decisions: a true <=
takes left, a false <= takes right, and the exhausted side produces no more key
comparisons. For memory efficiency, our merge writes into a single shared buffer
then copies back by index, instead of allocating B_l and B_r at every merge.
Both baseline and hybrid share that exact merge routine. This is an explicitly
documented storage/control-flow adaptation of the available lecture algorithm;
the timing is of this Python implementation, not a literal execution of the slides.
Existing course examples in `../code/python/sorting` are preserved.

A copy of the available lecture is included as `sources/01_Sorting.pdf` so team
members can inspect the cited pages without depending on the original Downloads path.

## Source fingerprints

| File | SHA-256 |
|---|---|
| Project 1.pdf | `1a9b296c79ca2c2d0fcef643b1cbed78d3e394976c0b1348bb03c1580f796f3d` |
| info.pdf | `ae96f8bea5292c96a7b2f2eff1a346dcecfb83ea4f80775873c01f1c193949d2` |
| 01_Sorting.pdf | `cf5875f86a551fdcb7007091ad0faa0061cbe9937bd99f2fe58090b700cfa42f` |

The mathematical derivations in this project are provided directly. External
technical references checked for API semantics (not assignment authority):

- [Python time documentation](https://docs.python.org/3/library/time.html#time.process_time): process CPU time excludes sleep, and perf_counter records elapsed wall time.
- [Python random documentation](https://docs.python.org/3/library/random.html#random.randint): randint(a,b) includes both endpoints.

The full interpreter version is recorded with the experiment. Live documentation
may describe a newer Python release, so actual runtime metadata remains authoritative
for the interpreter used to obtain these results.
