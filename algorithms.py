"""Stable, in-place-interface sorting with half-open ranges [lo, hi).

The algorithms rearrange the supplied list and return None (uncounted) or an
integer count (counted). One caller-owned merge buffer is reused throughout.
No slicing, skip-merge optimization, sentinel values, or built-in sorting.
"""


def _check_threshold(threshold):
    if isinstance(threshold, bool) or not isinstance(threshold, int):
        raise TypeError("threshold must be an integer, not bool")
    if threshold < 1:
        raise ValueError("threshold must be at least 1")


def _check_range(values, lo, hi):
    if not 0 <= lo <= hi <= len(values):
        raise ValueError("expected 0 <= lo <= hi <= len(values)")


def _get_buffer(values, buffer):
    if buffer is None:
        return [None] * len(values)
    if buffer is values or len(buffer) != len(values):
        raise ValueError("buffer must be distinct and have the same length")
    return buffer


def _insert(values, lo, hi):
    for position in range(lo + 1, hi):
        key = values[position]
        previous = position - 1
        while previous >= lo:
            if values[previous] > key:
                values[previous + 1] = values[previous]
                previous -= 1
            else:
                break
        values[previous + 1] = key


def _insert_counted(values, lo, hi):
    comparisons = 0
    for position in range(lo + 1, hi):
        key = values[position]
        previous = position - 1
        while previous >= lo:
            comparisons += 1  # Includes an evaluated false comparison.
            if values[previous] > key:
                values[previous + 1] = values[previous]
                previous -= 1
            else:
                break
        values[previous + 1] = key
    return comparisons


def insertion_sort(values, lo=0, hi=None):
    """Sort just [lo, hi); equal items do not move past one another."""
    hi = len(values) if hi is None else hi
    _check_range(values, lo, hi)
    _insert(values, lo, hi)


def insertion_sort_counted(values, lo=0, hi=None):
    """Sort [lo, hi) and count only evaluated values[previous] > key."""
    hi = len(values) if hi is None else hi
    _check_range(values, lo, hi)
    return _insert_counted(values, lo, hi)


def _merge(values, buffer, lo, mid, hi):
    left, right, output = lo, mid, lo
    while left < mid and right < hi:
        if values[left] <= values[right]:
            buffer[output] = values[left]
            left += 1
        else:
            buffer[output] = values[right]
            right += 1
        output += 1
    while left < mid:
        buffer[output] = values[left]
        left += 1
        output += 1
    while right < hi:
        buffer[output] = values[right]
        right += 1
        output += 1
    for output in range(lo, hi):
        values[output] = buffer[output]


def _merge_counted(values, buffer, lo, mid, hi):
    comparisons = 0
    left, right, output = lo, mid, lo
    while left < mid and right < hi:
        comparisons += 1  # One ordering decision; bounds/copying are excluded.
        if values[left] <= values[right]:
            buffer[output] = values[left]
            left += 1
        else:
            buffer[output] = values[right]
            right += 1
        output += 1
    while left < mid:
        buffer[output] = values[left]
        left += 1
        output += 1
    while right < hi:
        buffer[output] = values[right]
        right += 1
        output += 1
    for output in range(lo, hi):
        values[output] = buffer[output]
    return comparisons


def _original(values, buffer, lo, hi):
    if hi - lo <= 1:
        return
    mid = lo + (hi - lo) // 2
    _original(values, buffer, lo, mid)
    _original(values, buffer, mid, hi)
    _merge(values, buffer, lo, mid, hi)


def _original_counted(values, buffer, lo, hi):
    if hi - lo <= 1:
        return 0
    mid = lo + (hi - lo) // 2
    comparisons = _original_counted(values, buffer, lo, mid)
    comparisons += _original_counted(values, buffer, mid, hi)
    comparisons += _merge_counted(values, buffer, lo, mid, hi)
    return comparisons


def _hybrid(values, buffer, lo, hi, threshold):
    if hi - lo <= threshold:
        _insert(values, lo, hi)
        return
    mid = lo + (hi - lo) // 2
    _hybrid(values, buffer, lo, mid, threshold)
    _hybrid(values, buffer, mid, hi, threshold)
    _merge(values, buffer, lo, mid, hi)


def _hybrid_counted(values, buffer, lo, hi, threshold):
    if hi - lo <= threshold:
        return _insert_counted(values, lo, hi)
    mid = lo + (hi - lo) // 2
    comparisons = _hybrid_counted(values, buffer, lo, mid, threshold)
    comparisons += _hybrid_counted(values, buffer, mid, hi, threshold)
    comparisons += _merge_counted(values, buffer, lo, mid, hi)
    return comparisons


def merge_sort(values, buffer=None):
    """Original top-down merge sort; optional buffer allocation is not timed."""
    _original(values, _get_buffer(values, buffer), 0, len(values))


def merge_sort_counted(values, buffer=None):
    """Original merge sort returning its number of key comparisons."""
    return _original_counted(values, _get_buffer(values, buffer), 0, len(values))


def hybrid_sort(values, threshold, buffer=None):
    """Use insertion sort once the CURRENT subarray size is <= threshold."""
    _check_threshold(threshold)
    _hybrid(values, _get_buffer(values, buffer), 0, len(values), threshold)


def hybrid_sort_counted(values, threshold, buffer=None):
    """Count merge <= and insertion > comparisons, including evaluated false."""
    _check_threshold(threshold)
    return _hybrid_counted(values, _get_buffer(values, buffer), 0, len(values), threshold)
