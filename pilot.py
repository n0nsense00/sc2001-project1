"""Measure a smaller run before committing to the large configuration."""
import json
import math
from pathlib import Path
import random
import sys
import time
import psutil
from algorithms import merge_sort, hybrid_sort, hybrid_sort_counted

def main():
    n = 100000
    rng = random.Random(8871)
    base = [rng.randint(1, 1000000) for _ in range(n)]
    buffer = [None] * n
    results = []
    for name, fn in (("original", lambda v: merge_sort(v, buffer)),
                     ("hybrid_s16", lambda v: hybrid_sort(v, 16, buffer)),
                     ("counted_hybrid_s16", lambda v: hybrid_sort_counted(v, 16, buffer))):
        values = base.copy()
        start = time.process_time()
        count = fn(values)
        elapsed = time.process_time() - start
        assert all(values[i-1] <= values[i] for i in range(1, n))
        results.append({"algorithm": name, "pilot_n": n, "pilot_cpu_seconds": elapsed,
                        "comparisons": count, "estimated_10m_seconds": elapsed * 100 * math.log2(10000000)/math.log2(n)})
    data = {"note": "Estimates ONLY; n log n scaling does not capture cache, memory or noise",
            "measurements": results, "available_memory_bytes": psutil.virtual_memory().available,
            "estimated_large_array_bytes": 10000000 * (sys.getsizeof(1000000) + 3 * 8),
            "memory_note": "Approximate integer objects plus base/work/buffer pointer arrays; additional interpreter/histograms/slack needed",
            "rss_bytes_after_pilot": psutil.Process().memory_info().rss}
    Path("results/pilot").mkdir(parents=True, exist_ok=True)
    Path("results/pilot/pilot.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))

if __name__ == "__main__": main()
