# SC2001 presentation and speaker notes

8 main slides: 480 seconds. Q&A: 120 seconds. Appendices are optional during questions.

## Slide 1: Integration of Merge Sort & Insertion Sort

Time: 35 seconds

SC2001 Project 1

Handwritten Python algorithms  
Measured inputs from 1,000 to 10,000,000 integers


Speaker notes: 0:00-0:35. State the question: can insertion sort at small recursive leaves reduce Python CPU time? We implemented both algorithms, counted key comparisons and measured CPU separately. Explain that S is a leaf-size threshold, and that we chose it from experiments. Requirements: Project1.pdf p.1. Presentation format: info.pdf p.1-2. No student names or contributions are assumed.

## Slide 2: The hybrid algorithm

Time: 75 seconds

Stop splitting when the range has at most S items

```text
hybrid(A, lo, hi, S)
  if hi-lo <= S:
    insertion(A, lo, hi)
    return
  mid = lo + (hi-lo)//2
  hybrid(A, lo, mid, S)
  hybrid(A, mid, hi, S)
  merge(A, lo, mid, hi)
```

Worked example: S=3

Input: [5, 2, 4, 1, 3, 6]  
  
Leaves: [5, 2, 4] and [1, 3, 6]  
Insertion: [2, 4, 5] and [1, 3, 6]  
  
Merge: [1, 2, 3, 4, 5, 6]  
  
3 + 2 + 5 = 10 key comparisons


Speaker notes: 0:35-1:50, including about 25 seconds of live demo. Explain [lo,hi): lo is included, hi excluded. Trace the left leaf: 5>2 true, 5>4 true, 2>4 false. Right leaf has two false comparisons. Merge needs five ordering checks then copies 6. Run python demo.py from the preopened terminal. Both algorithms happen to make 10 comparisons on this input. This example explains mechanics, not typical speed. If the terminal fails, use these precomputed values. Source: algorithms.py and demo.py. Lecture 01_Sorting.pdf p.12/14.

## Slide 3: Correctness, counting and fair timing

Time: 65 seconds

Correctness and counting

Insertion maintains a sorted prefix.  
Merge emits the smallest remaining head.  
Induction gives a sorted, stable result.  
  
Count each evaluated data comparison:  
merge <= and insertion >.  
Include terminating false comparisons.

Experiment protocol

Uniform integers in [1, 1,000,000].  
Three seeds per case, paired inputs.  
Separate counted and uncounted runs.  
CPU clock: time.process_time().  
  
Exclude RNG, copies, buffer allocation,  
validation and I/O. Run sequentially.  
Verify order, length and exact histogram.


Speaker notes: 1:50-2:55. Explain stability: left on ties, shift only greater values. Index checks, copying and validation do not count. Tests include exhaustive ternary arrays through length 6 and S=1 equality with original counts. Large runs check exact frequency histograms and sorted order, not just checksums. Warmup is one deterministic small sort per case. Seeded shuffled order and 3 input seeds reduce systematic order bias. Timed tiny inputs use independent pre-timer batches. Metadata captures CPython/Windows/hardware. sources: tests/, experiment.py, results/full/metadata.json. Timer semantics: https://docs.python.org/3/library/time.html#time.process_time. RNG: https://docs.python.org/3/library/random.html#random.randint.

## Slide 4: Fixed S retains n log n growth

Time: 75 seconds

Original  
T(n) = 2T(n/2) + Theta(n)  
Time: Theta(n log n)  
Buffer: Theta(n)  
  
Hybrid  
About log2(n/S) merge levels  
Random leaf work: Theta(nS)  
Fixed S: Theta(n log n)

Both axes show log10 values. Analytical counts use actual rounded splits with no fitted scale factor.

Chart: (c)(i): fixed S=16. X: log10(n integers). Y: log10(key comparisons). Full editable series in content.json.

Measured median: (3, 4.01649), (4, 5.10439), (5, 6.2147), (5.47712, 6.72089), (6, 7.30581), (6.47712, 7.80314), (7, 8.35491)

Distinct model: (3, 4.01386), (4, 5.10403), (5, 6.21469), (5.47712, 6.72084), (6, 7.30586), (6.47712, 7.80312), (7, 8.35491)


Speaker notes: 2:55-4:10. Explain the original recurrence for even n; the exact code uses floor/ceiling lengths. Merge work is linear at each of logarithmically many levels. Hybrid replaces lower merge levels with insertion leaves. With constant S it retains n log n growth. The plotted coordinates are log10(n) and log10(count), so 3 to 7 covers 1,000 through 10,000,000. The full notebook uses conventional log axes plus min-max ranges and the worst bound. The analytical random-distinct expectation is an approximation to repeated integers, not a fitted line. Similar shape does not prove complexity; the recurrence does. Source: theory.py, docs/theory.md, raw stage=scale.

## Slide 5: Increasing S changes the leaf work

Time: 60 seconds

Fewer merge levels  
Larger insertion leaves  
  
Random insertion: Theta(S^2) per leaf  
About n/S leaves  
Total leaf work: Theta(nS)  
  
Some S values share the same leaves.  
Plateaus are expected.

S=1 is included. Medians of three seeds. Full plots also show ranges and the worst-case bound.

Chart: (c)(ii): n=100,000. X: Threshold S. Y: Key comparisons (millions). Full editable series in content.json.

Measured median: (1, 1.53637), (4, 1.53681), (8, 1.55808), (12, 1.62021), (16, 1.63993), (24, 1.76553), (32, 1.86288), (48, 1.94985), (64, 2.38466)

Distinct model: (1, 1.53637), (4, 1.53679), (8, 1.55792), (12, 1.61971), (16, 1.6394), (24, 1.76487), (32, 1.86209), (48, 1.94833), (64, 2.38257)


Speaker notes: 4:10-5:10. Fixed n separates the threshold effect from input-size growth. Merge levels shrink only when S crosses an actual recursive subarray length. Larger leaves increase insertion comparisons. Our analytical recurrence uses the real rounded leaf sizes, explaining plateaus. Both true and terminating false comparisons are included in the distinct insertion expectation m(m-1)/4+m-H_m. The curve is an approximation with ties. Source: theory.py and raw stage=tune,n=100000.

## Slide 6: CPU tuning selected S=12 by the tie-break rule

Time: 75 seconds

S=12, 32 tied at 2.78125 s median. The rule chooses smaller S. Three seeds per case.

Chart: (c)(iii): CPU ratios across n. X: Threshold S. Y: CPU / S=1 median. Full editable series in content.json.

n=1,000: (1, 1), (4, 0.771084), (8, 0.638554), (12, 0.650602), (16, 0.626506), (24, 0.710843), (32, 0.722892), (48, 0.819277), (64, 1.07229)

n=10,000: (1, 1), (4, 0.827586), (8, 0.784483), (12, 0.75), (16, 0.793103), (24, 0.810345), (32, 0.715517), (48, 0.887931), (64, 0.801724)

n=100,000: (1, 1), (4, 1.11921), (8, 1), (12, 0.940397), (16, 0.993377), (24, 0.940397), (32, 0.821192), (48, 1.07947), (64, 1.09272)

Chart: Confirmation at n=1,000,000. X: Threshold S. Y: CPU seconds. Full editable series in content.json.

Seed 1: (12, 2.54688), (16, 4.53125), (32, 2.57812)

Seed 2: (12, 2.82812), (16, 2.82812), (32, 2.78125)

Seed 3: (12, 2.78125), (16, 2.5), (32, 2.84375)


Speaker notes: 5:10-6:25. CPU is the predeclared primary criterion. Shortlist the three thresholds with the lowest geometric mean of CPU ratios across the tuning sizes. Candidates: 12, 16, 32. Confirm on fresh one-million inputs. Confirmation medians: S=12: 2.78125 s; S=16: 2.82812 s; S=32: 2.78125 s. S=12, 32 tied at 2.78125 s median. The rule chooses smaller S. These overlapping/noisy results do not establish a universal optimum. The chart shows each confirmation seed, and notebook charts show ranges. Report count winners separately from CPU winners. Source: shortlist.json, selection.json and raw tune/confirm. A threshold is best only within the tested search and criterion.

## Slide 7: Original and hybrid on 10 million integers

Time: 65 seconds

Median CPU: 92.094 s original, 94.078 s hybrid. Median paired speedup 0.929x.

Chart: (d): uncounted CPU time. X: Algorithm. Y: CPU seconds. Full editable series in content.json.

Seed 1: (0, 78.9688), (1, 85)

Seed 2: (0, 92.0938), (1, 99.9062)

Seed 3: (0, 92.5156), (1, 94.0781)

Chart: Separate counted runs. X: Algorithm. Y: Comparisons (millions). Full editable series in content.json.

Seed 1: (0, 220.096), (1, 226.418)

Seed 2: (0, 220.1), (1, 226.425)

Seed 3: (0, 220.101), (1, 226.418)


Speaker notes: 6:25-7:30. These are real full-size runs on three fresh seeds. Each line pairs the same unsorted dataset. Speedup is original CPU divided by hybrid CPU for each seed; then take the median. Median paired speedup is 0.929x, observed range 0.922-0.983x. The ratio of medians is 0.979x, a different statistic. Median comparisons are 220,099,689 original and 226,418,149 hybrid, a +2.87% change. Counts exclude timer/counter overhead as explained. The appendix has raw values. Sources: results/full/raw.csv stage=final, plots/full/final_paired_cpu.csv and final_paired_comparisons.csv.

## Slide 8: Conclusions and questions

Time: 30 seconds

2 minutes of Q&A

Hybrid was slower in 3 of 3 final CPU pairs.  
Median paired speedup: 0.929x.  
  
CPU time and key comparisons measure different costs.  
  
S=12 follows a finite, noisy search and an explicit tie-break.  
  
One interpreter, one machine, uniform integer inputs.


Speaker notes: 7:30-8:00. State the observed finding without promising it on other machines/distributions. Three repeats describe variability, not statistical significance. Python overhead, copies and recursion explain why count and CPU rankings can differ, but we did not profile causality. Stop at 8:00 and allow Q&A until 10:00. Every member should be ready to answer all topics. Use the appendices only when asked. Source: measured findings and info.pdf.

## Slide 9: Appendix: exact comparison models

Time: 0 seconds

Merge sort

Worst comparisons:  
n ceil(log2 n) - 2^ceil(log2 n) + 1  
  
Random distinct merge of lengths a,b:  
a+b - a/(b+1) - b/(a+1)  
  
Insertion expectation for m items:  
m(m-1)/4 + m - H_m  
H_m = 1 + 1/2 + ... + 1/m

Hybrid regimes

Worst/average (random distinct):  
Theta(n log(n/S) + nS), for S<=n  
  
Fixed S: Theta(n log n)  
S=log n: Theta(n log n)  
S=n^alpha: Theta(n^(1+alpha))  
S>=n: insertion only  
  
Buffer O(n), recursion O(log n)


Speaker notes: Appendix, not in the 8-minute script. Explain the expected trailing run in merge: its expectation is a/(b+1)+b/(a+1), subtracted from total length. Expected insertion inversions omit false comparisons; add m-H_m. Exact discrete ties change the expectation. Public hybrid allocates a buffer even when S>=n, though insertion itself is O(1) extra space. The full expression uses B=min(S,n) to avoid negative log values. Source: docs/theory.md and theory.py.

## Slide 10: Appendix: raw final measurements

Time: 0 seconds

Each CPU value is from an uncounted run. Counts come from a separate run on identical unsorted data.

| Seed | Algorithm | S | CPU seconds | Key comparisons |
| --- | --- | --- | --- | --- |
| 100900100 | original | 1 | 78.968750 | 220,095,927 |
| 100900100 | hybrid | 12 | 85.000000 | 226,418,149 |
| 100900101 | original | 1 | 92.093750 | 220,099,689 |
| 100900101 | hybrid | 12 | 99.906250 | 226,424,963 |
| 100900102 | original | 1 | 92.515625 | 220,101,452 |
| 100900102 | hybrid | 12 | 94.078125 | 226,417,959 |

Speaker notes: Appendix. CPU and count are intentionally different modes. All final runs use batch size 1 and n=10,000,000. The three seeds are fresh relative to tuning. Check the raw CSV for wall time and integrity checks. Source: results/full/raw.csv. Speedup per row pair is original CPU/hybrid CPU.

## Slide 11: Appendix: different criteria, different winners

Time: 0 seconds

Ties use the smaller S. These are per-size descriptive winners, before shortlist confirmation.

| Input n | Lowest median CPU S | Fewest median comparisons S |
| --- | --- | --- |
| 1,000 | 16 | 1 |
| 10,000 | 32 | 1 |
| 100,000 | 32 | 1 |

Speaker notes: Appendix. Distinguish raw comparison minimization from practical CPU performance. Finite thresholds, three seeds, one machine. Do not use the tiny smoke run as evidence. The observed min-max CPU bars in the notebook help interpret near ties. Source: plots/full/findings.json and raw tune rows.
