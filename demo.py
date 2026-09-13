"""Small deterministic live demo; never runs a benchmark."""
from algorithms import hybrid_sort_counted, merge_sort_counted

values = [5, 2, 4, 1, 3, 6]
print("Input:", values)
for name, threshold in (("Original", 1), ("Hybrid", 3)):
    data = values.copy()
    comparisons = (merge_sort_counted(data) if name == "Original"
                   else hybrid_sort_counted(data, threshold))
    print(f"{name}, S={threshold}: {data}; key comparisons={comparisons}")
print("S=3 sorts the two length-3 leaves by insertion, then merges them.")
