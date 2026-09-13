"""Build and execute a lightweight results notebook and portable HTML export."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parent


def main():
    md = nbformat.v4.new_markdown_cell
    code = nbformat.v4.new_code_cell
    cells = [md("""# SC2001 Project 1: Integration of Merge Sort & Insertion Sort

This notebook explains the implementation and reads **saved full-run results**.
It does not generate large inputs or run benchmarks. Start with the small demo in
the terminal if you want to see the algorithm operate.

The assignment asks for hybrid implementation, integer inputs from 1,000 to
10,000,000, three threshold/size studies, and an original-versus-hybrid comparison
on 10 million integers. Presentation time is 8 minutes plus 2 minutes of Q&A.
Requirements come from `sources/Project1.pdf` and `sources/info.pdf`.
"""), md("""## Algorithm and correctness

Use half-open ranges [lo,hi), split at lo+(hi-lo)//2, and stop when hi-lo <= S.
Insertion establishes a sorted prefix; merge repeatedly emits the smallest
remaining head. By induction, sorted children yield a sorted parent. Each step
preserves the multiset. Taking the left value on <= and shifting only on > makes
the sort stable. Empty/single-item ranges are already sorted.

```text
hybrid(A, lo, hi, S):
    if hi-lo <= S: insertion(A, lo, hi); return
    mid = lo + floor((hi-lo)/2)
    hybrid(A, lo, mid, S)
    hybrid(A, mid, hi, S)
    merge(A, lo, mid, hi, shared_buffer)
```

Worked example, S=3: [5,2,4 | 1,3,6] becomes [2,4,5 | 1,3,6].
Insertion counts are 3+2; merging counts are 5; total 10.
The original algorithm also makes 10 comparisons on this particular input.
This illustrates mechanics, not a general speed claim.

Reusable code is in `algorithms.py`. Focused tests compare to `sorted` only on
small cases, test all ternary arrays of lengths 0 through 6, cover the requested
edge cases, and check stability and counted/uncounted equivalence. An AST test
checks the merge and insertion loops differ only in accounting.
"""), md((ROOT / "docs/theory.md").read_text(encoding="utf-8")),
    md("""## Reproducible experiment protocol

Uniform `randint(1,x)` with x=1,000,000; recorded seeds; independent seed per repeat.
Candidates use identical unsorted data. Counted and uncounted runs are separate.
`time.process_time()` records only sorting CPU; wall time is a separate column.
Input copies, RNG, buffer allocation, warmup, checks, plotting and I/O are excluded.
Small sorts are batched from independent pre-timer copies; per-sort times and raw
batch totals are recorded. GC is collected before timing, disabled during sorting,
then restored. One small deterministic warmup precedes each case; order is shuffled
with a recorded seed; all comparative sorting is sequential.

Three measured seeds per full case; plots show median and observed min-max where
visible. These bars are not confidence intervals. CPU is the primary selection
criterion, and counts are reported independently. The configuration and source
hashes prevent incompatible resume; the CSV saves each verified completed case.

Large output checks: exact length, nondecreasing order, sum, squared sum, XOR,
and exact frequency histogram for this bounded range. SHA-256 identifies paired
input order and cross-checks counted/uncounted outputs. Checksums alone can collide;
the histogram establishes exact multiset preservation without a reference sort.
"""), code("""from pathlib import Path
import json
import pandas as pd
from IPython.display import display, Image

ROOT = Path.cwd()
if not (ROOT / 'results/full/raw.csv').exists():
    ROOT = ROOT / 'project1'
raw = pd.read_csv(ROOT / 'results/full/raw.csv')
metadata = json.loads((ROOT / 'results/full/metadata.json').read_text())
findings = json.loads((ROOT / 'plots/full/findings.json').read_text())
display(pd.Series(metadata['config'], name='Configuration'))
display(pd.Series(metadata['environment'], name='Environment'))
display(raw.head(8))
"""), md("## (c)(i): fix S=16 and vary n"),
    code("display(Image(filename=str(ROOT / 'plots/full/c1_comparisons_vs_n.png')))\ndisplay(Image(filename=str(ROOT / 'plots/full/c1_normalized.png')))"),
    md("""The analytical curves have no fitted scale factor. The random-distinct curve
approximates these samples with ties. The worst curve is a bound, not a prediction
for random inputs. Normalization by n log2(n) tests consistency with fixed-S growth.
"""), md("## (c)(ii): fix n=100,000 and vary S"),
    code("display(Image(filename=str(ROOT / 'plots/full/c2_comparisons_vs_s.png')))\ndisplay(pd.Series(findings['actual_leaves_at_fixed_n'], name='Actual leaf sizes and counts'))"),
    md("## (c)(iii): compare thresholds across input sizes"),
    code("display(Image(filename=str(ROOT / 'plots/full/c3_threshold_tuning.png')))\ndisplay(pd.DataFrame(findings['tuning']))\ndisplay(Image(filename=str(ROOT / 'plots/full/c3_confirmation.png')))\ndisplay(pd.DataFrame(findings['confirmation']))"),
    md("""The CPU chart normalizes each size by its S=1 median; lower is faster. That
normalization compares curve shapes without allowing the largest n to dominate.
Shortlisting uses the geometric mean of these ratios. The larger confirmation set
then selects its lowest median CPU, ties choosing smaller S. This finite search
does not establish a universal optimum. Repeated values and split rounding create
plateaus. Show uncertainty rather than claiming that every small difference matters.
"""), md("## (d): original versus hybrid on 10,000,000 integers"),
    code("display(Image(filename=str(ROOT / 'plots/full/d_final_comparison.png')))\ndisplay(pd.read_csv(ROOT / 'plots/full/final_paired_cpu.csv'))\ndisplay(pd.read_csv(ROOT / 'plots/full/final_paired_comparisons.csv'))"),
    md((ROOT / "plots/full/findings.md").read_text(encoding="utf-8")),
    md("## Sources and requirement distinctions\n\n" + (ROOT / "docs/requirements-and-sources.md").read_text(encoding="utf-8"))]
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
    NotebookClient(notebook, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
    nbformat.write(notebook, ROOT / "analysis.ipynb")
    exporter = HTMLExporter()
    exporter.embed_images = True
    html, _ = exporter.from_notebook_node(notebook)
    (ROOT / "analysis.html").write_text(html, encoding="utf-8")
    print("Wrote executed analysis.ipynb and portable analysis.html; no sorting was run")


if __name__ == "__main__": main()
