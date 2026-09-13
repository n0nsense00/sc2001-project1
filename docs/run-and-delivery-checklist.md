# Assignment and delivery checklist

Completed: all 234 full measurement rows, all 108 separate smoke rows, twelve
passing test methods, passing result audits, and all requested local deliverables.
The Google Slides deck and its PDF export are available. Google converted six
charts to images; the supplied original PowerPoint retains editable chart data.
The separate collaboration checklist contains human rehearsal activities.

| Requirement | Evidence / verification |
|---|---|
| Read both assignment PDFs fully | `docs/requirements-and-sources.md`, local source copies |
| Inspect existing work and AGENTS.md | Existing sorting examples/notes reviewed; no applicable AGENTS.md found; originals preserved |
| (a) Hybrid threshold <=S | `algorithms.py`, edge/exhaustive tests |
| Original and insertion sort implemented | `algorithms.py`; available lecture comparison order verified by test |
| (b) Inclusive uniform integers, 1,000 to 10,000,000 | `configs/full.json`, `raw.csv`, RNG and integrity tests |
| (c)(i) Fixed S, varying n | stage `scale`, c1 plot plus normalized diagnostic |
| (c)(ii) Fixed n, varying S including 1 | stage `tune`, c2 plot |
| (c)(iii) Several input sizes and larger confirmation | three tuning sizes, shortlist, 1-million confirmation, c3 plots |
| Distinguish count/CPU objectives | winner table, confirmation and theory notes |
| (d) Fresh 10-million datasets, both algorithms | stage `final`, 3 paired seeds, counted and uncounted modes |
| Meaningful comparison convention | evaluated data checks only; hand counts and terminating false comparisons |
| All requested correctness edge cases | `tests/test_algorithms.py` |
| Large correctness without reference sort | order/length/exact histogram and output hashes |
| Fair timing | sequential, independent copies, shared buffer convention, warmup, shuffled order, CPU clock |
| Three repeats and variation | full config, raw rows, median/min-max plots and paired seed charts |
| Honest runtime/memory pilot | `results/pilot/pilot.json`, estimates labelled |
| Resume without duplicates or incompatible config | hashes, case IDs, OS lock, smoke resume and full audit |
| Raw results and environment | `results/full/raw.csv`, `metadata.json`, snapshot config |
| Theory: merge/insertion/hybrid regimes and space | `docs/theory.md`, `theory.py`, notebook and appendix |
| Explain comparison versus Python CPU | notebook, findings, slide notes and Q&A |
| Jupyter + portable HTML | `analysis.ipynb`, `analysis.html`, lightweight executed code |
| Exported readable plots | `plots/full/*.png` and `*.svg` |
| Exact commands and assignment mapping | project README |
| Demo | `demo.py`, fixed six-item input |
| Collaboration, whole-project learning | `docs/collaboration.md`, `docs/walkthrough-and-qa.md` |
| Eight-minute main presentation + Q&A | 8 main slides, 480 seconds, 3 appendices, notes |
| Editable Google Slides and PDF | `presentation/google-slides.md`: saved private deck and 11-page PDF; chart-editing limitation disclosed |
| Visual inspection | All 11 final PDF pages checked; `presentation/qa.md` |
| Virtual environment and dependencies | `.venv` ignored; requirements and tested lock recorded |
| Sharing authorization | Private GitHub upload authorized on 2026-09-14; no public publication, teammate invitations or course submission |

Completion of measured stages is machine-checked by `python audit_results.py results/full`.
No required experiment remains unrun. Resume is demonstrated without duplicate
rows; use the README commands for an interrupted new run. Results are descriptive
evidence from one CPython/Windows machine and three seeds, not a universal optimum.
