"""Merge sort, insertion sort, and hybrid sort written for learning.

All functions sort the supplied list directly.
Use merge_sort() or hybrid_sort() for sorting without a counter.
Use a function ending in _counted() to sort and return the comparison count.

Index names used throughout:
    lo: the first index to include
    hi: the first index to exclude
    mid: the start of the right half
For example, lo=0 and hi=3 means indices 0, 1, 2. The size is hi - lo.

Names beginning with _ are helpers used by the public sorting functions.
Read _insert, _merge, _original, and _hybrid to learn the main algorithms.
"""


# Input checks and temporary storage.
def _check_threshold(threshold):
    # Python treats True and False as integers, but neither is a valid S here.
    if isinstance(threshold, bool):
        raise TypeError("threshold must be an integer, not bool")
    if not isinstance(threshold, int):
        raise TypeError("threshold must be an integer, not bool")
    if threshold < 1:
        raise ValueError("threshold must be at least 1")


def _check_range(values, lo, hi):
    if lo < 0:
        raise ValueError("expected 0 <= lo <= hi <= len(values)")
    if lo > hi:
        raise ValueError("expected 0 <= lo <= hi <= len(values)")
    if hi > len(values):
        raise ValueError("expected 0 <= lo <= hi <= len(values)")


def _get_buffer(values, buffer):
    if buffer is None:
        # Make one empty slot for each item. Every merge reuses this buffer.
        buffer = [None] * len(values)
    else:
        if buffer is values:
            raise ValueError("buffer must be distinct and have the same length")
        if len(buffer) != len(values):
            raise ValueError("buffer must be distinct and have the same length")
    return buffer


# Insertion sort: put each next item into the sorted section before it.
def _insert(values, lo, hi):
    # The first item is already a sorted section of size one.
    for position in range(lo + 1, hi):
        key = values[position]
        previous = position - 1

        # Move larger items one place right to make room for key.
        while previous >= lo:
            if values[previous] > key:
                values[previous + 1] = values[previous]
                previous = previous - 1
            else:
                # Stop at a value <= key. Equal items keep their order.
                break

        values[previous + 1] = key


def _insert_counted(values, lo, hi):
    comparisons = 0
    for position in range(lo + 1, hi):
        key = values[position]
        previous = position - 1

        while previous >= lo:
            # Count the next data comparison, whether true or false.
            comparisons = comparisons + 1
            if values[previous] > key:
                values[previous + 1] = values[previous]
                previous = previous - 1
            else:
                break

        values[previous + 1] = key

    return comparisons


def insertion_sort(values, lo=0, hi=None):
    """Sort the specified section, or the whole list if no indices are given."""
    if hi is None:
        hi = len(values)

    _check_range(values, lo, hi)
    _insert(values, lo, hi)


def insertion_sort_counted(values, lo=0, hi=None):
    """Insertion-sort the section and return its number of key comparisons."""
    if hi is None:
        hi = len(values)

    _check_range(values, lo, hi)
    comparisons = _insert_counted(values, lo, hi)
    return comparisons


# Merge assumes that the left and right halves are ALREADY sorted.
def _merge(values, buffer, lo, mid, hi):
    left = lo
    right = mid
    output = lo

    # Compare the next unused item from each half.
    while left < mid and right < hi:
        if values[left] <= values[right]:
            # Take the left item on a tie to preserve equal-item order.
            buffer[output] = values[left]
            left = left + 1
        else:
            buffer[output] = values[right]
            right = right + 1
        output = output + 1

    # One half is exhausted. Copy any leftovers without data comparisons.
    while left < mid:
        buffer[output] = values[left]
        left = left + 1
        output = output + 1

    while right < hi:
        buffer[output] = values[right]
        right = right + 1
        output = output + 1

    # Put the completed merged section back into the original list.
    for output in range(lo, hi):
        values[output] = buffer[output]


def _merge_counted(values, buffer, lo, mid, hi):
    comparisons = 0
    left = lo
    right = mid
    output = lo

    while left < mid and right < hi:
        # Index checks and copying do not count as key comparisons.
        comparisons = comparisons + 1
        if values[left] <= values[right]:
            buffer[output] = values[left]
            left = left + 1
        else:
            buffer[output] = values[right]
            right = right + 1
        output = output + 1

    while left < mid:
        buffer[output] = values[left]
        left = left + 1
        output = output + 1

    while right < hi:
        buffer[output] = values[right]
        right = right + 1
        output = output + 1

    for output in range(lo, hi):
        values[output] = buffer[output]

    return comparisons


# Original merge sort: split down to sections of size zero or one.
def _original(values, buffer, lo, hi):
    size = hi - lo
    if size <= 1:
        return

    mid = lo + size // 2

    # Each recursive call finishes sorting its half before we merge.
    _original(values, buffer, lo, mid)
    _original(values, buffer, mid, hi)
    _merge(values, buffer, lo, mid, hi)


def _original_counted(values, buffer, lo, hi):
    size = hi - lo
    if size <= 1:
        return 0

    mid = lo + size // 2
    left_comparisons = _original_counted(values, buffer, lo, mid)
    right_comparisons = _original_counted(values, buffer, mid, hi)
    merge_comparisons = _merge_counted(values, buffer, lo, mid, hi)

    comparisons = left_comparisons + right_comparisons + merge_comparisons
    return comparisons


# Hybrid sort: stop splitting once the CURRENT section has at most S items.
def _hybrid(values, buffer, lo, hi, threshold):
    size = hi - lo
    if size <= threshold:
        _insert(values, lo, hi)
        return

    mid = lo + size // 2
    _hybrid(values, buffer, lo, mid, threshold)
    _hybrid(values, buffer, mid, hi, threshold)
    _merge(values, buffer, lo, mid, hi)


def _hybrid_counted(values, buffer, lo, hi, threshold):
    size = hi - lo
    if size <= threshold:
        comparisons = _insert_counted(values, lo, hi)
        return comparisons

    mid = lo + size // 2
    left_comparisons = _hybrid_counted(values, buffer, lo, mid, threshold)
    right_comparisons = _hybrid_counted(values, buffer, mid, hi, threshold)
    merge_comparisons = _merge_counted(values, buffer, lo, mid, hi)

    comparisons = left_comparisons + right_comparisons + merge_comparisons
    return comparisons


# Public functions: these prepare the inputs and start the recursive helpers.
# No timing happens in this file. experiment.py supplies a buffer before timing.
def merge_sort(values, buffer=None):
    """Sort values using original merge sort; the supplied list is changed."""
    buffer = _get_buffer(values, buffer)
    lo = 0
    hi = len(values)
    _original(values, buffer, lo, hi)


def merge_sort_counted(values, buffer=None):
    """Sort values using original merge sort and return the comparison count."""
    buffer = _get_buffer(values, buffer)
    lo = 0
    hi = len(values)
    comparisons = _original_counted(values, buffer, lo, hi)
    return comparisons


def hybrid_sort(values, threshold, buffer=None):
    """Sort values using the hybrid; threshold is the insertion cutoff S."""
    _check_threshold(threshold)
    buffer = _get_buffer(values, buffer)
    lo = 0
    hi = len(values)
    _hybrid(values, buffer, lo, hi, threshold)


def hybrid_sort_counted(values, threshold, buffer=None):
    """Hybrid-sort values and return the number of evaluated key comparisons."""
    _check_threshold(threshold)
    buffer = _get_buffer(values, buffer)
    lo = 0
    hi = len(values)
    comparisons = _hybrid_counted(values, buffer, lo, hi, threshold)
    return comparisons
