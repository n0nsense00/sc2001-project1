"""Small reference tests; built-in sorted is used ONLY for test expectations."""
import ast
import inspect
import itertools
import random
import unittest

import algorithms as a


class SortingTests(unittest.TestCase):
    def assert_sorts(self, values):
        expected = sorted(values)
        for fn in (a.merge_sort, a.merge_sort_counted,
                   a.insertion_sort, a.insertion_sort_counted):
            actual = values.copy()
            fn(actual)
            self.assertEqual(actual, expected)
        baseline = a.merge_sort_counted(values.copy())
        for threshold in {1, 2, 3, 8, max(1, len(values)), len(values) + 7}:
            counted, plain = values.copy(), values.copy()
            count = a.hybrid_sort_counted(counted, threshold)
            a.hybrid_sort(plain, threshold)
            self.assertEqual(counted, expected)
            self.assertEqual(plain, counted)
            if threshold == 1:
                self.assertEqual(count, baseline)

    def test_edge_cases(self):
        for values in ([], [4], [2, 1], [7] * 17, list(range(19)),
                       list(range(20, -1, -1)), [3, 1, 3, 2, 1, 2, 1]):
            with self.subTest(values=values):
                self.assert_sorts(values)

    def test_exhaustive_ternary_arrays(self):
        for length in range(7):
            for values in itertools.product(range(3), repeat=length):
                self.assert_sorts(list(values))

    def test_random_small(self):
        rng = random.Random(2001)
        for _ in range(100):
            self.assert_sorts([rng.randint(1, 17) for _ in range(rng.randrange(101))])

    def test_known_counts(self):
        # [3,1,2]: insertion compares 3>1, 3>2, 1>2 (false).
        for values, insertion, merge in (([], 0, 0), ([1], 0, 0),
                ([3, 1, 2], 3, 3), ([1, 2, 3, 4], 3, 4),
                ([4, 3, 2, 1], 6, 4), ([2, 2, 2, 2], 3, 4)):
            self.assertEqual(a.insertion_sort_counted(values.copy()), insertion)
            self.assertEqual(a.merge_sort_counted(values.copy()), merge)
            self.assertEqual(a.hybrid_sort_counted(values.copy(), max(1, len(values))), insertion)
        self.assertEqual(a.hybrid_sort_counted([5, 2, 4, 1, 3, 6], 3), 10)

    def test_subarray_and_buffer(self):
        for fn in (a.insertion_sort, a.insertion_sort_counted):
            values = [99, 3, 1, 2, -99]
            fn(values, 1, 4)
            self.assertEqual(values, [99, 1, 2, 3, -99])
            with self.assertRaises(ValueError):
                fn(values, -1, 4)
        buffer = [None] * 7
        for threshold in (1, 8, 3):
            values = [4, 2, 1, 3, 7, 6, 5]
            a.hybrid_sort(values, threshold, buffer)
            self.assertEqual(values, list(range(1, 8)))
        with self.assertRaises(ValueError):
            a.merge_sort(values, values)
        with self.assertRaises(ValueError):
            a.merge_sort(values, [])

    def test_invalid_thresholds(self):
        for fn in (a.hybrid_sort, a.hybrid_sort_counted):
            for threshold in (0, -1, -10):
                with self.assertRaises(ValueError):
                    fn([], threshold)
            for threshold in (True, False, 1.5, "3", None):
                with self.assertRaises(TypeError):
                    fn([], threshold)

    def test_stability(self):
        class Item:
            def __init__(self, key, tag): self.key, self.tag = key, tag
            def __le__(self, other): return self.key <= other.key
            def __gt__(self, other): return self.key > other.key
        original = [Item(k, i) for i, k in enumerate([2, 1, 2, 1, 2, 1])]
        for fn in (a.merge_sort, a.merge_sort_counted,
                   lambda v: a.hybrid_sort(v, 3),
                   lambda v: a.hybrid_sort_counted(v, 3)):
            values = original.copy()
            fn(values)
            self.assertEqual([v.tag for v in values], [1, 3, 5, 0, 2, 4])

    def test_lecture_merge_comparison_equivalence(self):
        # Unmeasured reference: lecture p.14 copies halves and iterates right.
        # This verifies the shared-buffer adaptation preserves key decisions.
        def lecture(values):
            if len(values) <= 1: return 0
            mid = len(values) // 2
            left, right = values[:mid], values[mid:]
            count = lecture(left) + lecture(right)
            i = output = 0
            for key in right:
                while i < len(left):
                    count += 1
                    if left[i] <= key:
                        values[output] = left[i]
                        i += 1
                        output += 1
                    else:
                        break
                values[output] = key
                output += 1
            while i < len(left):
                values[output] = left[i]
                i += 1
                output += 1
            return count
        for length in range(7):
            for items in itertools.product(range(3), repeat=length):
                ref, actual = list(items), list(items)
                self.assertEqual(lecture(ref), a.merge_sort_counted(actual))
                self.assertEqual(actual, ref)

    def test_instrumentation_logic_matches(self):
        # Mechanically check loop/branch equivalence after removing accounting.
        class RemoveCounts(ast.NodeTransformer):
            def visit_Assign(self, node):
                if any(isinstance(t, ast.Name) and t.id == "comparisons" for t in node.targets):
                    return None
                return self.generic_visit(node)
            def visit_AugAssign(self, node):
                if isinstance(node.target, ast.Name) and node.target.id == "comparisons":
                    return None
                return self.generic_visit(node)
            def visit_Return(self, node):
                return None
        for plain, counted in ((a._insert, a._insert_counted), (a._merge, a._merge_counted)):
            trees = [RemoveCounts().visit(ast.parse(inspect.getsource(fn))) for fn in (plain, counted)]
            for tree in trees:
                tree.body[0].name = "same"
            self.assertEqual(ast.dump(trees[0]), ast.dump(trees[1]))


if __name__ == "__main__":
    unittest.main()
