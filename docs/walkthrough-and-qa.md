# Beginner walkthrough

Start in the project folder. Run `python demo.py`. It shows six values before and
after sorting and the key-comparison count. S=3 means a recursive range containing
3 or fewer items is sorted with insertion sort. It does not mean 3 recursion levels
or 3 comparisons.

1. Split [5,2,4,1,3,6] into [5,2,4] and [1,3,6]. Both leaves have length 3.
2. Left insertion: 5>2 is true; 5>4 is true; 2>4 is false. Result [2,4,5], 3 checks.
3. Right insertion: 1>3 is false; 3>6 is false. Result [1,3,6], 2 checks.
4. Merge heads: 2<=1 false, 2<=3 true, 4<=3 false, 4<=6 true, 5<=6 true.
   Left is exhausted; copy 6 without another key comparison. Total 3+2+5=10.
5. The baseline happens to need 10 checks on this example too. Never use one tiny
   example to claim one algorithm is generally faster.

Read `algorithms.py` in this order: `_insert`, `_merge`, `_original`, `_hybrid`.
Then inspect the counted counterparts. A count increments immediately before a
data-order check, never just because a loop is entered. Follow the index boundaries
on paper: mid belongs to the right half because hi is exclusive.

Next read `configs/full.json`, then `docs/theory.md`, then `analysis.html`. For each
chart say what stays fixed, what changes, what the units are, and how variation is
shown. Finally read `plots/full/findings.md` for the actual conclusions and limits.

# Likely TA questions and answers

**What does S mean?** The maximum size of a current recursive subarray that uses
insertion sort. Splitting continues only while its size exceeds S.

**Why combine the algorithms?** Insertion handles small ranges with short loops
and no recursive subdivision. It may save recursion and merge-copy work at the
cost of more comparisons/shifts. Whether that saves CPU is measured, not assumed.

**How do you prove correctness?** Insertion maintains a sorted prefix and preserves
the elements. Merge chooses the smallest remaining head and preserves both sorted
halves' multiset. Induction on subarray length proves hybrid correctness. Empty
and single-item base cases are already sorted.

**Is it stable?** Yes. Merge chooses left on equality (<=); insertion shifts only
strictly greater items (>). Equal keys keep their initial relative order. Tests use
tagged equal-key objects to verify this, although measured inputs are integers.

**Does a false comparison count?** Yes if evaluated. In insertion [1,2] makes one
false 1>2 comparison. In [2,1], the true 2>1 comparison is followed by a failed
index check; there is no second key comparison because the index is out of range.

**Why no comparisons when copying the remainder?** After a side is exhausted,
the other side is already sorted, so no ordering decision between keys is needed.

**Does S=1 match merge sort?** It matches output, partitions and key counts exactly.
The hybrid helper still incurs some extra call/threshold overhead, so timing may
differ. Our tests explicitly check count agreement on exhaustive small inputs.

**What if S>=n?** The algorithm makes one insertion-sort call. Best time is linear;
average/worst is quadratic under the stated assumptions. Our public merge/hybrid
API still provides an O(n) buffer, though it is unused in that case. Insertion's
own auxiliary space is O(1).

**What are the recurrences?** Original: T(n)=T(floor(n/2))+T(ceil(n/2))+Theta(n).
Hybrid stops at n<=S and incurs insertion work there. For 1<=S<=n its worst/average
random-distinct order is O(n log(n/S)+nS). Fixed S gives Theta(n log n).

**Why is the original's worst input not necessarily reverse sorted?** Merge work
depends on interleaving sorted halves. Reverse input can exhaust a half early.
Alternating values across halves can force a+b-1 comparisons.

**What is the average insertion count?** For random distinct permutations it is
m(m-1)/4+m-H_m, including terminating false comparisons. Just m(m-1)/4 counts expected
inversions/shifts and omits those false comparisons. Ties reduce shifts.

**Why is the comparison fair?** All candidates share original data from the same
recorded seed, the same merge logic/buffer convention, one interpreter and sequential
execution. Data resetting is outside timing; each sort starts unsorted. Timed runs
omit counters, while counted runs collect only counts. Order is deterministically
shuffled, and all full cases have three measured repeats.

**Why separate CPU and wall time?** CPU measures processor time charged to this
process. Wall time includes scheduling waits. The assignment requests CPU time, so
CPU is primary and wall is separately labelled. Neither includes RNG/checks/I/O.

**Why batch tiny sorts?** Windows CPU accounting is too coarse for an individual
millisecond-scale run. Prepare independent copies before the timer, sort all, then
divide total CPU by batch size. No reset occurs inside timing. Batch repetitions
are not additional independent seeds. Three seed repeats remain the variation unit.

**How was S selected?** Predeclare CPU as primary; test the saved threshold grid at
three n values; shortlist three by geometric mean of median CPU ratios to S=1;
confirm at one million values; choose the lowest median, ties choosing smaller S.
Use fresh final seeds. Consult `selection.json` for the actual selected value and
`c3_confirmation.png` for overlaps/ties. Do not call it a universal optimum.

**Why can several S have identical counts?** Midpoint splits only create certain
subarray lengths. If two thresholds stop the recursion at the same leaves, the
algorithm makes the same comparisons on the same data. CPU differences on such
plateaus may be noise; do not invent an algorithmic explanation.

**Can fewer comparisons be slower?** Yes. Python CPU also pays for function calls,
index checks, pointer assignments, copying and shifts. Counting overhead itself
adds work, which is why counters are excluded from timing.

**How was ten-million correctness checked?** Verify length and sorted order, then
compare an exact frequency table over [1,1,000,000], plus sum, squared sum and XOR.
SHA-256 verifies paired input identity and output agreement. Sum-based checks can
collide; the exact histogram is what guarantees multiset preservation here.

**What is the memory use?** O(n) merge buffer plus O(log n) recursion. The harness
also stores one base dataset and one working copy. These are pointer lists sharing
integer objects, not three independent sets of newly generated integers. Consult
metadata for actual sampled RSS; it is not a precise peak measurement.

**Why not NumPy/Timsort/Numba?** They would measure different implementations or
algorithms. Our measured sorts are handwritten Python loops. NumPy/pandas/Matplotlib
are used only for plotting/analysis, never measured sorting.

**Do the theoretical lines prove your timing result?** No. The recurrence proves
asymptotic order. Count curves describe a particular operation model; the distinct
expectation approximates repeated-integer input. CPU evidence is specific to the
machine, interpreter, data and tested grid. Observed ranges are not confidence intervals.

**What would you investigate next?** More seeds on the CPU plateau, different x
and distributions, nearly sorted/adversarial data, and another interpreter/machine.
Those are proposed follow-ups, not experiments claimed to have been run.

**How can n be larger than x?** The inputs are random integer arrays, not random
permutations. With n=10,000,000 and x=1,000,000, duplicates necessarily occur.
The distinct-permutation model is therefore labelled as an approximation. We did
not sweep x, so we do not claim to have experimentally isolated the effect of ties.

**Why might the tuned hybrid lose to original merge sort?** The selection ranks
hybrid candidates on the confirmation input size and the measured CPU medians.
It does not guarantee a win against the original at a larger n. Different actual
leaf lengths, Python execution costs and noisy timing all limit transfer of the
selection. We report every final pair, including regressions, and do not retune
using the test seeds. Profiling and additional repetitions would be needed to
identify the cause of a timing difference.

# Live-demo plan (about 25 seconds within slide 2)

Have the terminal already open in `project1` with the virtual environment active.
Run `python demo.py`; point to S=3 and the ten comparisons. Keep the same output
in the speaker notes/PDF as backup. Do not edit code during the presentation.
All ten-million results are precomputed. If the terminal fails, trace the six-item
example from the slide and continue within the allotted time.
