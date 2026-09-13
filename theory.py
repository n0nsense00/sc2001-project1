"""Analytical comparison curves, not experimental measurements."""
from functools import lru_cache


@lru_cache(maxsize=None)
def comparison_model(n, threshold, kind="distinct_average"):
    """Exact recurrence for worst bound or random DISTINCT permutations.

    Merge expectation for left a/right b: a+b-a/(b+1)-b/(a+1).
    Insertion expectation: m(m-1)/4 + m-H_m, including false comparisons.
    The random-distinct curve is an approximation for our uniform integer data
    with ties. No empirical scale factor is fitted.
    """
    if n <= 1:
        return 0.0
    if n <= threshold:
        if kind == "worst": return n * (n - 1) / 2
        if kind == "best": return n - 1
        harmonic = sum(1 / i for i in range(1, n + 1))
        return n * (n - 1) / 4 + n - harmonic
    left, right = n // 2, n - n // 2
    if kind == "worst": merge = n - 1
    elif kind == "best": merge = min(left, right)
    else: merge = n - left / (right + 1) - right / (left + 1)
    return comparison_model(left, threshold, kind) + comparison_model(right, threshold, kind) + merge


@lru_cache(maxsize=None)
def leaf_sizes(n, threshold):
    """Return {actual leaf length: number of leaves} without enumerating leaves."""
    if n <= threshold:
        return {n: 1}
    result = dict(leaf_sizes(n // 2, threshold))
    for size, count in leaf_sizes(n - n // 2, threshold).items():
        result[size] = result.get(size, 0) + count
    return result
