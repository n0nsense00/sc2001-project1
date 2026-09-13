# Project 1: Integration of Merge Sort & Insertion Sort

Handwritten Python algorithms, reproducible experiments, saved results, and
presentation material for NTU SC2001. This is a standalone project repository;
the original local copy lives inside the course-notes folder. Read [assignment/source decisions](docs/requirements-and-sources.md)
to distinguish PDF requirements from requested deliverables and design choices.

## Start here

- [Team GitHub repository](https://github.com/n0nsense00/sc2001-project1) (private;
  accept the owner's collaborator invitation before cloning).
- [Team access and editing instructions](docs/github-collaboration.md).
- [Executed notebook](analysis.ipynb) or [portable HTML analysis](analysis.html).
- [Measured findings](plots/full/findings.md), [raw CSV](results/full/raw.csv),
  [environment and protocol](results/full/metadata.json), [audit](results/full/audit.json).
- [Google Slides presentation](https://docs.google.com/presentation/d/1xcD_j9SiE7MKP3iQ7dYprbrnjnh-WGXluFaTKWdEfbY/edit),
  [PDF copy](presentation/SC2001-Project1.pdf), and
  [PowerPoint with native editable charts](presentation/SC2001-Project1-final.pptx).
  [Speaker notes](presentation/presentation.md) and [editing/export details](presentation/google-slides.md).
- [Beginner walkthrough and TA Q&A](docs/walkthrough-and-qa.md).
- [Collaboration guide](docs/collaboration.md).
- [Completed requirements checklist](docs/run-and-delivery-checklist.md).

All 234 full measurement rows and 108 separate smoke rows completed. Twelve test
methods passed; full and smoke result audits passed. The selected S=12 tied with
S=32 on confirmation median CPU time; the predeclared rule chooses smaller S.
On the three fresh 10-million-element datasets, hybrid was slower in all three
pairs. Median CPU was 92.093750 seconds for original and 94.078125 for hybrid;
median **paired** speedup was 0.929x. These are observed results on one machine,
not a claim that hybrid sort is always slower. See the findings for ranges and counts.

## Setup

Tested with 64-bit CPython 3.13.6 on Windows. The measured sorting uses only the
Python standard library. The runner uses psutil for hardware/memory metadata;
analysis uses pandas, NumPy (analysis only), Matplotlib, and Jupyter tooling.
`requirements.txt` lists tested direct dependencies, while `requirements-lock.txt`
records the complete environment. The lock includes Windows-only pywinpty, so use
the direct dependency file for macOS/Linux.

Clone the private repository once, after receiving access (Git must be installed):

```bash
git clone https://github.com/n0nsense00/sc2001-project1.git
cd sc2001-project1
```

Already using the original local copy? Open
`C:\Users\daboi\Documents\ChatGPT\SC2001\project1` instead. All subsequent
commands run from the folder containing `algorithms.py` and `requirements.txt`.

Windows PowerShell, from this project root:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Optional activation: `.venv\Scripts\Activate.ps1`. If PowerShell blocks activation,
use the explicit executable paths shown here; changing execution policy is unnecessary.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

All commands below use `python` for an activated environment. On Windows without
activation, replace `python` with `.venv\Scripts\python.exe`.

## Tests and live demo

```bash
python -m unittest discover -s tests -v
python demo.py
```

Small correctness tests use `sorted()` as a reference only. They cover empty and
single items, duplicates, all-equal, sorted/reverse inputs, odd lengths, exhaustive
ternary arrays up to length 6, random small arrays, invalid S, S=1/n/>n, stability,
subarray boundaries, known counts and instrumented/plain equivalence.
The live demo uses six deterministic integers, prints before/after and 10 comparisons.

## Reproduce experiments

Saved full/smoke results ship with this project. A fresh run needs a NEW output
directory. Do not overwrite the supplied evidence just to try the commands.

```bash
python pilot.py
python experiment.py --config configs/smoke.json --out results/my-smoke
python audit_results.py results/my-smoke
python experiment.py --config configs/full.json --out results/my-full
python audit_results.py results/my-full
```

The full job includes 10-million-element sorts and takes substantially longer than
smoke. The pilot contains estimates clearly distinguished from measurements.
Keep at least about 1 GB of RAM available for the Python process and allow for
other applications. The pilot pointer/object estimate is about 520 MB before
histograms, interpreter, allocator slack and other overhead. Large runs may be
slower than n log n extrapolation because the pilot does not model the full machine.

Resume the supplied full configuration (completed cases are skipped):

```bash
python experiment.py --config configs/full.json --out results/full --resume
```

Resume your own interrupted run:

```bash
python experiment.py --config configs/full.json --out results/my-full --resume
```

Stages can be run sequentially with `--stage tune`, `--stage confirm`,
`--stage scale`, and `--stage final`; add `--resume` after the first stage.
Confirmation requires completed tuning; final requires tuning and confirmation.
`--stage all` is the default. No large experiment starts from opening the notebook.

Every verified case appends and flushes one CSV row. An OS file lock prevents two
writers to the same result folder and releases on exit/crash. Config and algorithm/
runner SHA-256 hashes prevent incompatible appends. Python/platform changes are
rejected on resume. Use a new folder for another machine or environment.
If a power loss leaves an incomplete last CSV row, the runner stops: back up the
file and remove only that incomplete final row, then resume. Never discard valid rows.

## Configurations and protocol

`configs/full.json` explicitly includes n=1,000 and n=10,000,000, seven increasing
sizes, x=1,000,000, three measured repeats, S=1 in the threshold grid, and distinct
seed ranges for tuning, confirmation, scaling and final testing. Modify a copied
config and use a new output folder to change n, S, x, seeds or repeats.

Measured algorithms are handwritten top-down merge/insertion/hybrid sorts, with
the same reusable merge buffer and no recursive slices, skip-merge or built-in
sorting shortcut. Both algorithms receive identical unsorted data per seed.
Counted and timed modes run separately; absent metrics are blank, never zero.

CPU time uses `time.process_time()` on the uncounted sort. Wall time uses
`time.perf_counter()` and is labelled separately. RNG, input copies, buffer
allocation, warmup, validation, plotting and I/O are excluded. GC is collected
before and disabled during each sort. Timed small cases use preallocated independent
copies, sort a batch without resets inside timing, and divide by batch size. CSV
columns retain raw batch totals and per-sort means. Three repeats mean three seeds,
not three batch copies. Cases execute sequentially in seeded shuffled order.

The primary criterion is CPU time. The predeclared shortlist scores each threshold
by geometric mean of its median CPU ratios to S=1 across tuning sizes, then confirms
the three lowest at n=1,000,000. The lowest confirmation median wins; a tie chooses
smaller S. Part (d) uses fresh seeds. Report it as best among tested candidates.

The tuning denominator is the **hybrid implementation at S=1**, not the separately
implemented original baseline. They have equal key counts but can differ in CPU
overhead. Part (d) directly compares against the original implementation.

Large-run validation checks order, length and exact frequency counts over the
bounded value range, plus sums, squared sums and XOR. SHA-256 records input order
and output agreement. For custom x beyond `exact_histogram_max_x`, the runner falls
back to collision-prone multiset fingerprints and explicitly labels that limitation.

## Recreate plots and notebook

```bash
python analyze.py --results results/full --out plots/full
python build_notebook.py
python -m jupyterlab analysis.ipynb
```

`analyze.py` refuses incomplete results. It writes PNG/SVG figures, summary CSVs,
paired final results and findings. `build_notebook.py` loads existing results and
plots, executes the lightweight cells, and exports self-contained HTML with images.
For a new run, use `python analyze.py --results results/my-full --out plots/my-full`
to keep its figures separate. The supplied notebook deliberately targets `results/full`.

## Presentation

Use 8 main slides in 8 minutes, then 2 minutes of Q&A. Appendices hold detailed
derivations and raw results. Speaker notes contain timings, claim explanations,
source references and a 25-second small demo plan. Never run the full benchmark live.
The local presentation content is generated by `python build_slide_content.py`
from the saved results. The PowerPoint contains native charts with editable data.
Google's conversion retained editable text, two tables and speaker notes, but
converted its six charts to images. Use the PowerPoint for chart-data editing or
regenerate the Python plots and replace a chart image in Google Slides. The PDF
was exported from the actual Google deck and all 11 pages were visually inspected.
See [editing and export details](presentation/google-slides.md).

## Assignment mapping

| Part | Implementation or evidence |
|---|---|
| (a) Hybrid | `algorithms.py`: `_hybrid`, `_insert`, `_merge` and counted versions |
| (b) Inputs | `experiment.py`, `configs/full.json`, recorded x/n/seeds in raw CSV |
| (c)(i) Fixed S, vary n | raw `stage=scale`; `plots/full/c1_comparisons_vs_n.png`, `c1_normalized.png` |
| (c)(ii) Fixed n, vary S | raw `stage=tune,n=100000`; `c2_comparisons_vs_s.png` |
| (c)(iii) Tune S across n | raw `tune/confirm`; `shortlist.json`, `selection.json`, `c3_threshold_tuning.png`, `c3_confirmation.png` |
| (d) Original vs hybrid | raw `stage=final,n=10000000`; `d_final_comparison.png`, paired result CSVs |
| Theory | `docs/theory.md`, `theory.py`, notebook |
| Correctness | `tests/`, exact large-input validation, `results/full/audit.json` |
| Presentation | `presentation/`, `docs/walkthrough-and-qa.md`, collaboration checklist |

## Repository hygiene

Commit source, configs, compact CSV/JSON results, notebook, plots and presentation.
Do not commit `.venv`, `.build`, caches or huge input datasets. Input arrays are
regenerated from seeds. Source PDFs remain private collaboration references.
The owner authorized uploading this project to a private GitHub repository on
2026-09-14. No teammate invitation, external message, public publication or course
submission has been performed. Google Slides access is managed separately.
