# Updated code slides 2-7

These notes match the Google Slides refresh on 2026-09-14, including the shorter merge indices left, right and output. The suggested times total 160 seconds, including the optional small demo. Rehearse the full team-edited deck separately to stay within 8 minutes plus 2 minutes of Q&A.

## Slide 2

Suggested time: 25 seconds. Read merge_sort first: prepare one reusable buffer, set lo=0 and hi=len(values), then call _original. The range [lo, hi) includes lo but excludes hi. _original stops at size 0 or 1, recursively sorts both halves, and merges them. In _merge, left and right are the indices of the next unused items in each half. output is the index of the next buffer slot to fill. Taking the left item when values are equal keeps the sort stable. Copying leftovers needs no ordering comparisons. Code source: current algorithms.py, using left, right and output. Historical full benchmark results were measured before the readability rewrite (commit 25fc591).

## Slide 3

Suggested time: 20 seconds. The counted version makes the same sorting decisions as the uncounted version. A key comparison compares data values for ordering. In _merge_counted, increment comparisons immediately before evaluating values[left] <= values[right]. Count either outcome, true or false. left and right index the two halves, and output indexes the buffer. Do not count index checks, copying, or the stopping condition. _original_counted adds left_comparisons, right_comparisons and merge_comparisons. The base case returns zero. Timing uses the separate uncounted version so the counter does not distort sorting CPU time. Code source: current algorithms.py with the shorter index names.

## Slide 4

Suggested time: 25 seconds. If hi is None, no end index was supplied, so set hi to len(values). _check_range verifies 0 <= lo <= hi <= len(values). _insert starts at the second item because the first item alone is already sorted. Save the current item as key, shift earlier values that are larger than key one place right, then insert key into the gap. The prefix remains sorted after each pass. Strict > means an equal item is not moved past another equal item, preserving stability. Explicit assignments such as previous = previous - 1 replace shorthand. These panels use the current beginner-friendly algorithms.py (422d067), with comments/docstrings omitted.

## Slide 5

Suggested time: 20 seconds. Count one comparison whenever values[previous] > key is evaluated, including the false result that stops shifting. If previous falls below lo, the while condition stops before another data comparison; add no extra comparison. Example [5, 2, 4]: 5 > 2 is true; then 5 > 4 is true and 2 > 4 is false, giving three comparisons. [1, 3, 6] needs two false comparisons. Index checks and assignments do not count. The public counted function sorts the supplied list and returns comparisons. Source: current algorithms.py (422d067).

## Slide 6

Suggested time: 35 seconds, including the worked example. S is the cutoff for the CURRENT subarray, whose size is hi - lo. If size <= threshold, use insertion sort and return; otherwise split, recursively sort both halves, and merge. The public wrapper validates S and prepares one reusable buffer. For [5, 2, 4, 1, 3, 6] with S=3, insertion sort sorts each length-three half, then merge combines the sorted halves. Source: current algorithms.py (422d067). Suggested live demo: run python demo.py on the next slide; do not start large benchmarks during the presentation.

## Slide 7

Suggested time: 35 seconds, including an optional 20-second live demo using python demo.py. A leaf returns its insertion-sort comparison count. An internal call adds the counts from the left half, right half and merge. For S=3 on [5, 2, 4, 1, 3, 6], insertion needs 3 comparisons on the left and 2 on the right. Merge compares five pairs and copies the remaining 6, giving 3 + 2 + 5 = 10 comparisons. S=1 agrees with original merge sort under this implementation; S>=n uses insertion sort on the whole list. This tiny example explains the mechanism, not a performance advantage. Panels use current algorithms.py (422d067), with equivalent wrapping of long lines. The full benchmark results were measured with the earlier implementation (25fc591); the readability rewrite has correctness tests and its own smoke run.
