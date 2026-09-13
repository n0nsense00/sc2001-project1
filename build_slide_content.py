"""Create measured slide content and speaker notes using Python, without sorting."""
import json
import math
from pathlib import Path
import pandas as pd
from theory import comparison_model

ROOT = Path(__file__).resolve().parent


def series(name, x, y, color=0):
    return {"name": name, "x": list(map(float, x)), "y": list(map(float, y)), "color": color}


def chart(title, xlabel, ylabel, entries, **kwargs):
    return {"title": title, "xlabel": xlabel, "ylabel": ylabel, "series": entries, **kwargs}


def main():
    findings = json.loads((ROOT / "plots/full/findings.json").read_text())
    raw = pd.read_csv(ROOT / "results/full/raw.csv")
    cfg = json.loads((ROOT / "results/full/config.json").read_text())
    selected = findings["selected_s"]
    counts = raw[raw.measurement_mode == "counted"]
    times = raw[raw.measurement_mode == "timed"]
    slides = []
    def add(title, layout, **options):
        slides.append(dict(title=title, layout=layout, **options))
    add("Integration of Merge Sort\n& Insertion Sort", "cover", seconds=35,
        subtitle="SC2001 Project 1",
        body="Handwritten Python algorithms\nMeasured inputs from 1,000 to 10,000,000 integers",
        notes="0:00-0:35. State the question: can insertion sort at small recursive leaves reduce Python CPU time? We implemented both algorithms, counted key comparisons and measured CPU separately. Explain that S is a leaf-size threshold, and that we chose it from experiments. Requirements: Project1.pdf p.1. Presentation format: info.pdf p.1-2. No student names or contributions are assumed.")
    add("The hybrid algorithm", "example", seconds=75,
        left_title="Stop splitting when the range has at most S items",
        pseudocode="hybrid(A, lo, hi, S)\n  if hi-lo <= S:\n    insertion(A, lo, hi)\n    return\n  mid = lo + (hi-lo)//2\n  hybrid(A, lo, mid, S)\n  hybrid(A, mid, hi, S)\n  merge(A, lo, mid, hi)",
        right_title="Worked example: S=3",
        right="Input: [5, 2, 4, 1, 3, 6]\n\nLeaves: [5, 2, 4] and [1, 3, 6]\nInsertion: [2, 4, 5] and [1, 3, 6]\n\nMerge: [1, 2, 3, 4, 5, 6]\n\n3 + 2 + 5 = 10 key comparisons",
        notes="0:35-1:50, including about 25 seconds of live demo. Explain [lo,hi): lo is included, hi excluded. Trace the left leaf: 5>2 true, 5>4 true, 2>4 false. Right leaf has two false comparisons. Merge needs five ordering checks then copies 6. Run python demo.py from the preopened terminal. Both algorithms happen to make 10 comparisons on this input. This example explains mechanics, not typical speed. If the terminal fails, use these precomputed values. Source: algorithms.py and demo.py. Lecture 01_Sorting.pdf p.12/14.")
    add("Correctness, counting and fair timing", "columns", seconds=65,
        left_title="Correctness and counting",
        left="Insertion maintains a sorted prefix.\nMerge emits the smallest remaining head.\nInduction gives a sorted, stable result.\n\nCount each evaluated data comparison:\nmerge <= and insertion >.\nInclude terminating false comparisons.",
        right_title="Experiment protocol",
        right="Uniform integers in [1, 1,000,000].\nThree seeds per case, paired inputs.\nSeparate counted and uncounted runs.\nCPU clock: time.process_time().\n\nExclude RNG, copies, buffer allocation,\nvalidation and I/O. Run sequentially.\nVerify order, length and exact histogram.",
        notes="1:50-2:55. Explain stability: left on ties, shift only greater values. Index checks, copying and validation do not count. Tests include exhaustive ternary arrays through length 6 and S=1 equality with original counts. Large runs check exact frequency histograms and sorted order, not just checksums. Warmup is one deterministic small sort per case. Seeded shuffled order and 3 input seeds reduce systematic order bias. Timed tiny inputs use independent pre-timer batches. Metadata captures CPython/Windows/hardware. sources: tests/, experiment.py, results/full/metadata.json. Timer semantics: https://docs.python.org/3/library/time.html#time.process_time. RNG: https://docs.python.org/3/library/random.html#random.randint.")
    scale = findings["scale_rows"]
    ns = [r["n"] for r in scale]
    c1 = chart("(c)(i): fixed S=16", "log10(n integers)", "log10(key comparisons)", [
        series("Measured median", [math.log10(n) for n in ns], [math.log10(r["median"]) for r in scale]),
        series("Distinct model", [math.log10(n) for n in ns], [math.log10(comparison_model(n,16)) for n in ns], 1)], xmin=3, xmax=7)
    add("Fixed S retains n log n growth", "chart_side", seconds=75, charts=[c1],
        side="Original\nT(n) = 2T(n/2) + Theta(n)\nTime: Theta(n log n)\nBuffer: Theta(n)\n\nHybrid\nAbout log2(n/S) merge levels\nRandom leaf work: Theta(nS)\nFixed S: Theta(n log n)",
        footnote="Both axes show log10 values. Analytical counts use actual rounded splits with no fitted scale factor.",
        notes="2:55-4:10. Explain the original recurrence for even n; the exact code uses floor/ceiling lengths. Merge work is linear at each of logarithmically many levels. Hybrid replaces lower merge levels with insertion leaves. With constant S it retains n log n growth. The plotted coordinates are log10(n) and log10(count), so 3 to 7 covers 1,000 through 10,000,000. The full notebook uses conventional log axes plus min-max ranges and the worst bound. The analytical random-distinct expectation is an approximation to repeated integers, not a fitted line. Similar shape does not prove complexity; the recurrence does. Source: theory.py, docs/theory.md, raw stage=scale.")
    fixed = findings["fixed_rows"]
    thresholds = [r["S"] for r in fixed]
    c2 = chart("(c)(ii): n=100,000", "Threshold S", "Key comparisons (millions)", [
        series("Measured median", thresholds, [r["median"]/1e6 for r in fixed]),
        series("Distinct model", thresholds, [comparison_model(100000,s)/1e6 for s in thresholds], 1)])
    add("Increasing S changes the leaf work", "chart_side", seconds=60, charts=[c2],
        side="Fewer merge levels\nLarger insertion leaves\n\nRandom insertion: Theta(S^2) per leaf\nAbout n/S leaves\nTotal leaf work: Theta(nS)\n\nSome S values share the same leaves.\nPlateaus are expected.",
        footnote="S=1 is included. Medians of three seeds. Full plots also show ranges and the worst-case bound.",
        notes="4:10-5:10. Fixed n separates the threshold effect from input-size growth. Merge levels shrink only when S crosses an actual recursive subarray length. Larger leaves increase insertion comparisons. Our analytical recurrence uses the real rounded leaf sizes, explaining plateaus. Both true and terminating false comparisons are included in the distinct insertion expectation m(m-1)/4+m-H_m. The curve is an approximation with ties. Source: theory.py and raw stage=tune,n=100000.")
    tuning_series = []
    for i,n in enumerate(cfg["tuning_sizes"]):
        values = times[(times.stage=="tune") & (times.n==n)].groupby("S").cpu_seconds.median()
        tuning_series.append(series(f"n={n:,}", values.index, values/values.loc[1], i))
    confirm_series = []
    candidates = sorted(times[times.stage=="confirm"].S.unique())
    for repeat in range(3):
        values = times[(times.stage=="confirm") & (times.repeat==repeat)].set_index("S").loc[candidates]
        confirm_series.append(series(f"Seed {repeat+1}", candidates, values.cpu_seconds, repeat))
    medians = times[times.stage=="confirm"].groupby("S").cpu_seconds.median()
    tied = list(map(int, medians[medians == medians.min()].index))
    candidate_text = ", ".join(str(int(s)) for s in candidates)
    median_text = "; ".join(f"S={int(s)}: {v:.5f} s" for s,v in medians.items())
    decision_text = (f"S={', '.join(map(str,tied))} tied at {medians.min():.5f} s median. The rule chooses smaller S."
                     if len(tied)>1 else f"S={selected} had the lowest confirmation median, {medians.min():.5f} s.")
    title = f"CPU tuning selected S={selected}" + (" by the tie-break rule" if len(tied)>1 else " among tested values")
    add(title, "two_charts", seconds=75,
        charts=[chart("(c)(iii): CPU ratios across n", "Threshold S", "CPU / S=1 median", tuning_series),
                chart("Confirmation at n=1,000,000", "Threshold S", "CPU seconds", confirm_series)],
        footnote=decision_text + " Three seeds per case.",
        notes=f"5:10-6:25. CPU is the predeclared primary criterion. Shortlist the three thresholds with the lowest geometric mean of CPU ratios across the tuning sizes. Candidates: {candidate_text}. Confirm on fresh one-million inputs. Confirmation medians: {median_text}. {decision_text} These overlapping/noisy results do not establish a universal optimum. The chart shows each confirmation seed, and notebook charts show ranges. Report count winners separately from CPU winners. Source: shortlist.json, selection.json and raw tune/confirm. A threshold is best only within the tested search and criterion.")
    d_series_t, d_series_c = [], []
    for repeat in range(3):
        t = times[(times.stage=="final") & (times.repeat==repeat)].set_index("algorithm")
        c = counts[(counts.stage=="final") & (counts.repeat==repeat)].set_index("algorithm")
        d_series_t.append(series(f"Seed {repeat+1}", [0,1], t.loc[["original","hybrid"],"cpu_seconds"], repeat))
        d_series_c.append(series(f"Seed {repeat+1}", [0,1], c.loc[["original","hybrid"],"comparisons"]/1e6, repeat))
    add("Original and hybrid on 10 million integers", "two_charts", seconds=65,
        charts=[chart("(d): uncounted CPU time", "Algorithm", "CPU seconds", d_series_t, categories=["Original",f"Hybrid S={selected}"], ymin=0),
                chart("Separate counted runs", "Algorithm", "Comparisons (millions)", d_series_c, categories=["Original",f"Hybrid S={selected}"], ymin=0)],
        footnote=f"Median CPU: {findings['original_median_cpu_seconds']:.3f} s original, {findings['hybrid_median_cpu_seconds']:.3f} s hybrid. Median paired speedup {findings['median_paired_speedup']:.3f}x.",
        notes=f"6:25-7:30. These are real full-size runs on three fresh seeds. Each line pairs the same unsorted dataset. Speedup is original CPU divided by hybrid CPU for each seed; then take the median. Median paired speedup is {findings['median_paired_speedup']:.3f}x, observed range {findings['paired_speedup_min']:.3f}-{findings['paired_speedup_max']:.3f}x. The ratio of medians is {findings['ratio_of_median_cpu_times']:.3f}x, a different statistic. Median comparisons are {findings['original_median_comparisons']:,} original and {findings['hybrid_median_comparisons']:,} hybrid, a {findings['comparison_change_percent']:+.2f}% change. Counts exclude timer/counter overhead as explained. The appendix has raw values. Sources: results/full/raw.csv stage=final, plots/full/final_paired_cpu.csv and final_paired_comparisons.csv.")
    add("Conclusions and questions", "closing", seconds=30,
        body=f"Hybrid was slower in {findings['hybrid_slower_pairs']} of 3 final CPU pairs.\nMedian paired speedup: {findings['median_paired_speedup']:.3f}x.\n\nCPU time and key comparisons measure different costs.\n\nS={selected} follows a finite, noisy search and an explicit tie-break.\n\nOne interpreter, one machine, uniform integer inputs.",
        subtitle="2 minutes of Q&A",
        notes="7:30-8:00. State the observed finding without promising it on other machines/distributions. Three repeats describe variability, not statistical significance. Python overhead, copies and recursion explain why count and CPU rankings can differ, but we did not profile causality. Stop at 8:00 and allow Q&A until 10:00. Every member should be ready to answer all topics. Use the appendices only when asked. Source: measured findings and info.pdf.")
    add("Appendix: exact comparison models", "columns", seconds=0,
        left_title="Merge sort",
        left="Worst comparisons:\nn ceil(log2 n) - 2^ceil(log2 n) + 1\n\nRandom distinct merge of lengths a,b:\na+b - a/(b+1) - b/(a+1)\n\nInsertion expectation for m items:\nm(m-1)/4 + m - H_m\nH_m = 1 + 1/2 + ... + 1/m",
        right_title="Hybrid regimes",
        right="Worst/average (random distinct):\nTheta(n log(n/S) + nS), for S<=n\n\nFixed S: Theta(n log n)\nS=log n: Theta(n log n)\nS=n^alpha: Theta(n^(1+alpha))\nS>=n: insertion only\n\nBuffer O(n), recursion O(log n)",
        notes="Appendix, not in the 8-minute script. Explain the expected trailing run in merge: its expectation is a/(b+1)+b/(a+1), subtracted from total length. Expected insertion inversions omit false comparisons; add m-H_m. Exact discrete ties change the expectation. Public hybrid allocates a buffer even when S>=n, though insertion itself is O(1) extra space. The full expression uses B=min(S,n) to avoid negative log values. Source: docs/theory.md and theory.py.")
    values = [["Seed", "Algorithm", "S", "CPU seconds", "Key comparisons"]]
    for repeat in range(3):
        for algorithm in ("original", "hybrid"):
            t = times[(times.stage=="final") & (times.repeat==repeat) & (times.algorithm==algorithm)].iloc[0]
            c = counts[(counts.stage=="final") & (counts.repeat==repeat) & (counts.algorithm==algorithm)].iloc[0]
            values.append([str(int(t.seed)), algorithm, str(int(t.S)), f"{t.cpu_seconds:.6f}", f"{int(c.comparisons):,}"])
    add("Appendix: raw final measurements", "table", seconds=0, table=values,
        footnote="Each CPU value is from an uncounted run. Counts come from a separate run on identical unsorted data.",
        notes="Appendix. CPU and count are intentionally different modes. All final runs use batch size 1 and n=10,000,000. The three seeds are fresh relative to tuning. Check the raw CSV for wall time and integrity checks. Source: results/full/raw.csv. Speedup per row pair is original CPU/hybrid CPU.")
    winner_rows = [["Input n", "Lowest median CPU S", "Fewest median comparisons S"]]
    for row in findings["tuning"]:
        winner_rows.append([f"{row['n']:,}", str(row["cpu_best_s"]), str(row["comparison_best_s"])])
    add("Appendix: different criteria, different winners", "table", seconds=0, table=winner_rows,
        footnote="Ties use the smaller S. These are per-size descriptive winners, before shortlist confirmation.",
        notes="Appendix. Distinguish raw comparison minimization from practical CPU performance. Finite thresholds, three seeds, one machine. Do not use the tiny smoke run as evidence. The observed min-max CPU bars in the notebook help interpret near ties. Source: plots/full/findings.json and raw tune rows.")
    out = ROOT / "presentation"
    out.mkdir(exist_ok=True)
    (out / "content.json").write_text(json.dumps({"slides": slides, "main_seconds": sum(s["seconds"] for s in slides),
                                                  "source_config_hash": json.loads((ROOT / "results/full/metadata.json").read_text())["config_hash"]}, indent=2), encoding="utf-8")
    markdown = ["# SC2001 presentation and speaker notes\n\n8 main slides: 480 seconds. Q&A: 120 seconds. Appendices are optional during questions.\n"]
    for i, slide in enumerate(slides, 1):
        markdown.append(f"## Slide {i}: {slide['title'].replace(chr(10),' ')}\n\nTime: {slide['seconds']} seconds\n")
        for field in ("subtitle","body","left_title","left","pseudocode","right_title","right","side","footnote"):
            if field in slide:
                if field == "pseudocode":
                    markdown.append("```text\n" + slide[field] + "\n```\n")
                else:
                    markdown.append(slide[field].replace("\n", "  \n") + "\n")
        for item in slide.get("charts", []):
            markdown.append(f"Chart: {item['title']}. X: {item['xlabel']}. Y: {item['ylabel']}. Full editable series in content.json.\n")
            for entry in item["series"]:
                markdown.append(f"{entry['name']}: " + ", ".join(f"({x:g}, {y:.6g})" for x,y in zip(entry["x"],entry["y"])) + "\n")
        if "table" in slide:
            table = slide["table"]
            markdown.extend(["| " + " | ".join(table[0]) + " |", "| " + " | ".join(["---"]*len(table[0])) + " |"])
            markdown.extend("| " + " | ".join(row) + " |" for row in table[1:])
        markdown.append("\nSpeaker notes: " + slide["notes"] + "\n")
    (out / "presentation.md").write_text("\n".join(markdown), encoding="utf-8")
    print(f"Wrote {len(slides)} slides, {sum(s['seconds'] for s in slides)} main-script seconds")


if __name__ == "__main__": main()
