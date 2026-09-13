# Theory and counting conventions

## What counts

A **key comparison** compares two stored data values for ordering. Merge evaluates
`values[left] <= values[right]` once while both halves have remaining values.
Both true and false outcomes count. Once a half is exhausted, copying the remainder
uses no key comparisons. Merging nonempty halves of lengths a and b takes between
min(a,b) and a+b-1 key comparisons.

Insertion compares `values[previous] > key` whenever `previous >= lo`. A true
comparison shifts the earlier value. A false comparison stops shifting and DOES
count. If the index falls below lo, the key comparison is never evaluated and does
NOT count. Index checks, recursion/threshold checks, moving values and validation
are excluded. For [3,1,2], insertion's comparisons are 3>1 (true), 3>2 (true),
1>2 (false): exactly 3.

## Original merge sort

For n>1, split into a=floor(n/2) and b=ceil(n/2):

`T(n) = T(a) + T(b) + Theta(n)`, with `T(0), T(1) = Theta(1)`.

The linear merge work includes copying, so running time is Theta(n log n) in best,
average and worst cases for n>=2. Comparisons also have Theta(n log n) growth for
balanced splits. For powers of two the best comparison count is (n/2)log2(n).
The worst count for any n>=1 is
`n*ceil(log2(n)) - 2**ceil(log2(n)) + 1`.
For n=4 this is 5, although already sorted and reverse-sorted inputs each need 4.
Worst case is not synonymous with reverse order for merge sort.

The shared buffer has n slots, hence Theta(n) auxiliary storage. The recursion
stack is O(log n). Input/base copies belong to the experiment's memory use and
are distinct from the algorithm's auxiliary-space analysis.

## Insertion sort

On m>=1 already sorted or all-equal values: m-1 comparisons, Theta(m) time.
On strictly decreasing values: m(m-1)/2 comparisons and shifts, Theta(m^2) time.
On a uniformly random permutation of m distinct values, the expected number of
inversions (and shifts) is m(m-1)/4. There are also terminating false comparisons.
At insertion position i (zero based), one is absent precisely when the new item
is a strict prefix minimum, probability 1/(i+1). Summing gives:

`E[C_insert(m)] = m(m-1)/4 + m - H_m`, where `H_m = sum(1/i, i=1..m)`.

The average time is Theta(m^2) under that random-permutation assumption.
For IID uniform integers in [1,x], ties are possible and do not shift: expected
inversions are `m(m-1)(x-1)/(4x)`. Thus the distinct model is an approximation
to our data, not an exact expected count for all x. At x=1, all data are equal and
insertion is linear. Insertion itself uses O(1) extra space.

## Hybrid merge levels and leaf work

Let B=min(S,n), for n>=1 and S>=1. Splits stop at lengths <=S, NOT after S levels.
For n>S, there are about n/S leaves, each of size approximately S (between
roughly S/2 and S), and about log2(n/S) merging levels. Each merge level touches
O(n) values. Integer midpoint rounding changes actual leaves in steps.

For power-of-two n and S dividing n into power-of-two leaves:

- Number of leaves = n/S; merge levels = log2(n/S).
- Worst insertion-leaf comparisons = (n/S)*S(S-1)/2 = n(S-1)/2.
- Random-distinct insertion-leaf expectation = (n/S)*[S(S-1)/4 + S-H_S].
- Merge comparison upper bound = n log2(n/S) - n/S + 1.

Combining gives worst time `Theta(n*(1 + log2(n/B)) + n*B)`; for random distinct
input, expected time has the same asymptotic order. A convenient big-O form is
`O(n log(n/S) + nS)` for 1<=S<=n, with the constant/edge cases understood.
Best time is `Theta(n*(1 + log2(n/B)))` because each insertion leaf is linear.

- Fixed S: Theta(n log n) expected/worst growth; S affects constant factors.
- S=1: same partitions, merges, output and key counts as original merge sort.
  Our hybrid still calls the empty/single-item insertion helper, so CPU need not
  match the baseline exactly; comparisons must match.
- Growing S: use the full expression. S=log n still gives Theta(n log n).
  S=n^alpha (0<alpha<=1) gives Theta(n^(1+alpha)) worst/average leaf work.
- S>=n: one insertion sort, no merges, average/worst Theta(n^2), best Theta(n).
  The current public hybrid API still allocates/provides an n-slot buffer, even
  though this extreme case does not use it, so its implemented auxiliary storage
  remains O(n). A dedicated insertion-only call uses O(1).

## Analytical curves used in the plots

`theory.py` recurses over actual rounded subproblem lengths. A merge of sorted
random DISTINCT halves of sizes a,b has expected comparisons
`a+b-a/(b+1)-b/(a+1)`: merging omits the final trailing run, whose expected length
is a/(b+1)+b/(a+1). Combine this with the insertion expectation above. This is exact
for uniform distinct permutations and serves as an approximation for our tied
integer samples. The worst curve uses insertion m(m-1)/2 and merge a+b-1.
No fitted constant or scaling is applied to either analytical count curve.
The normalized c(i) plot divides measured C by n log2(n); it is a diagnostic ratio,
not another measured comparison count.

For fixed n, increasing S removes merging levels in steps but increases insertion
work. Different S values can yield exactly the same recursion tree and counts.
The plots use actual leaf lengths to explain plateaus; no smooth optimum is assumed.

## Why comparisons and CPU time can disagree

Comparisons omit function calls, loop/index operations, pointer assignments,
buffer copying and integer-counter updates. Fewer recursive calls can save CPU
even if insertion increases comparisons. Python executes all measured loops;
no built-in sort or compiled/JIT replacement performs the measured sorting.
Counted runs increment Python integers; their CPU times are intentionally absent
from the timed results. Both versions share structure, verified by tests.

Random seeds vary arrangement; equal keys affect early exhaustion and insertion
shifts. OS scheduling, clock quantization and machine load can affect repeated
timings. CPU seconds measure this process's CPU use, whereas wall seconds include
waiting. Three seeds support descriptive median/min/max comparisons, not a strong
claim about every workload or hardware platform. Cache/thermal explanations are
possible hypotheses, not measured causal findings here.

In this run, recorded CPU totals commonly fell on 0.015625-second increments.
The clock metadata reports a nominal resolution of 1e-7 seconds via GetProcessTimes,
which does not guarantee that a tiny experiment receives CPU charges at that
granularity. Small-case batching addresses the observed quantization. It does
not remove all scheduling or workload noise. Smoke batches are deliberately short
and unsuitable for drawing performance conclusions.
