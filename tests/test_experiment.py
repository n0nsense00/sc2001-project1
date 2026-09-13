import random
import tempfile
from pathlib import Path
import unittest
from experiment import signature, append_row, load_rows, FIELDS
from theory import comparison_model, leaf_sizes


class ProtocolTests(unittest.TestCase):
    def test_inclusive_rng_and_integrity(self):
        rng = random.Random(71)
        data = [rng.randint(1, 3) for _ in range(100)]
        before = signature(data, 3, 10)
        self.assertEqual(set(data), {1, 2, 3})
        after = signature(sorted(data), 3, 10, True)
        self.assertTrue(after["ordered"])
        for key in ("length", "sum", "sum_squares", "xor", "histogram"):
            self.assertEqual(before[key], after[key])
        self.assertNotEqual(before["sha256"], after["sha256"])
        data[0] = 4
        with self.assertRaises(AssertionError): signature(data, 3, 10)

    def test_csv_missing_metrics_and_duplicate_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.csv"
            row = {field: "" for field in FIELDS}
            row.update(case_id="one", comparisons=None, cpu_seconds=1.2)
            append_row(path, row)
            self.assertEqual(load_rows(path)[0]["comparisons"], "")
            append_row(path, row)
            with self.assertRaises(RuntimeError): load_rows(path)

    def test_models(self):
        self.assertEqual(comparison_model(4, 1, "worst"), 5)
        self.assertEqual(comparison_model(4, 4, "worst"), 6)
        self.assertAlmostEqual(comparison_model(3, 3), 8/3)
        self.assertEqual(leaf_sizes(10, 3), {2: 2, 3: 2})


if __name__ == "__main__": unittest.main()
