"""Load completed CSVs, audit, plot, and summarize. Never runs any sorting."""
import argparse
import json
from pathlib import Path
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from audit_results import audit
from theory import comparison_model, leaf_sizes

COLORS = ["#166A8F", "#C4532D", "#508238", "#79479B"]
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 130, "savefig.dpi": 180, "axes.titleweight": "bold"})


def aggregate(frame, keys, metric):
    return frame.groupby(keys, sort=True)[metric].agg(["median", "min", "max", "std", "count"]).reset_index()


def errors(summary):
    return np.array([summary["median"] - summary["min"], summary["max"] - summary["median"]])


def save(fig, out, name):
    fig.tight_layout()
    for extension in ("png", "svg"):
        fig.savefig(out / f"{name}.{extension}", bbox_inches="tight")
    plt.close(fig)


def make_analysis(folder, out):
    audit(folder)
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(folder / "raw.csv")
    cfg = json.loads((folder / "config.json").read_text())
    selected = json.loads((folder / "selection.json").read_text())["selected_s"]
    counted = raw[raw.measurement_mode == "counted"]
    timed = raw[raw.measurement_mode == "timed"]
    summaries = []
    for data, metric in ((counted, "comparisons"), (timed, "cpu_seconds")):
        stat = aggregate(data, ["stage", "algorithm", "n", "S"], metric)
        stat["metric"] = metric
        summaries.append(stat)
    pd.concat(summaries).to_csv(out / "summary.csv", index=False)

    scale = aggregate(counted[counted.stage == "scale"], ["n"], "comparisons")
    n_values = scale.n.to_numpy()
    predicted = [comparison_model(int(n), cfg["fixed_s"]) for n in n_values]
    worst = [comparison_model(int(n), cfg["fixed_s"], "worst") for n in n_values]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(n_values, scale["median"], yerr=errors(scale), fmt="o-", color=COLORS[0], capsize=4,
                label="Measured median (min-max, 3 seeds)")
    ax.plot(n_values, predicted, "--", color=COLORS[1], label="Random-distinct expectation (no fit)")
    ax.plot(n_values, worst, ":", color=COLORS[2], label="Worst-case comparison bound")
    ax.set(xscale="log", yscale="log", xlabel="Input size n (integers)", ylabel="Key comparisons",
           title=f"(c)(i): comparisons as n grows, fixed S={cfg['fixed_s']}")
    ax.grid(True, which="major", alpha=.2)
    ax.legend(fontsize=10)
    save(fig, out, "c1_comparisons_vs_n")

    fig, ax = plt.subplots(figsize=(10, 5))
    denominator = n_values * np.log2(n_values)
    ax.errorbar(n_values, scale["median"] / denominator, yerr=errors(scale) / denominator,
                fmt="o-", capsize=4, color=COLORS[0], label="Measured / (n log2 n)")
    ax.plot(n_values, np.array(predicted) / denominator, "--", color=COLORS[1], label="Distinct model / (n log2 n)")
    ax.set(xscale="log", xlabel="Input size n (integers)", ylabel="Comparisons / (n log2 n)",
           title="A normalization check for fixed-S growth")
    ax.grid(alpha=.2); ax.legend()
    save(fig, out, "c1_normalized")

    fixed = aggregate(counted[(counted.stage == "tune") & (counted.n == cfg["fixed_n"])], ["S"], "comparisons")
    fixed_time = aggregate(timed[(timed.stage == "tune") & (timed.n == cfg["fixed_n"])], ["S"], "cpu_seconds")
    grid = list(range(1, max(cfg["thresholds"]) + 1))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(fixed.S, fixed["median"] / 1e6, yerr=errors(fixed) / 1e6, fmt="o", capsize=4,
                color=COLORS[0], label="Measured median (min-max, 3 seeds)")
    ax.step(grid, [comparison_model(cfg["fixed_n"], s) / 1e6 for s in grid], where="mid",
            color=COLORS[1], linestyle="--", label="Random-distinct expectation (no fit)")
    ax.step(grid, [comparison_model(cfg["fixed_n"], s, "worst") / 1e6 for s in grid], where="mid",
            color=COLORS[2], linestyle=":", label="Worst-case bound")
    ax.set(xlabel="Threshold S (integers per insertion leaf, at most)", ylabel="Key comparisons (millions)",
           title=f"(c)(ii): fixed n={cfg['fixed_n']:,}")
    ax.grid(alpha=.2); ax.legend(fontsize=10)
    save(fig, out, "c2_comparisons_vs_s")

    tuning_summary = []
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for index, n in enumerate(cfg["tuning_sizes"]):
        t = aggregate(timed[(timed.stage == "tune") & (timed.n == n)], ["S"], "cpu_seconds")
        c = aggregate(counted[(counted.stage == "tune") & (counted.n == n)], ["S"], "comparisons")
        base = float(t[t.S == 1]["median"].iloc[0])
        axes[0].errorbar(t.S, t["median"] / base, yerr=errors(t) / base, fmt="o-", capsize=3,
                         color=COLORS[index], label=f"n={n:,}")
        c_base = float(c[c.S == 1]["median"].iloc[0])
        axes[1].plot(c.S, c["median"] / c_base, "o-", color=COLORS[index], label=f"n={n:,}")
        fastest = t.loc[t["median"].idxmin()]
        least = c.loc[c["median"].idxmin()]
        tuning_summary.append({"n": n, "cpu_best_s": int(fastest.S), "cpu_median_seconds": float(fastest["median"]),
                               "comparison_best_s": int(least.S), "comparison_median": int(least["median"])})
    for ax in axes:
        ax.set_xlabel("Threshold S")
        ax.grid(alpha=.2); ax.legend(fontsize=10)
    axes[0].set(ylabel="CPU time / median CPU at S=1", title="(c)(iii): CPU time (lower is better)")
    axes[1].set(ylabel="Comparisons / median count at S=1", title="Comparisons favor different thresholds")
    save(fig, out, "c3_threshold_tuning")

    confirm = aggregate(timed[timed.stage == "confirm"], ["S"], "cpu_seconds")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(confirm.S.astype(str), confirm["median"], yerr=errors(confirm), fmt="o", markersize=9,
                capsize=8, color=COLORS[0], label="Median and min-max of 3 seeds")
    for index, threshold in enumerate(confirm.S):
        vals = timed[(timed.stage == "confirm") & (timed.S == threshold)].cpu_seconds.to_numpy()
        ax.scatter([index-.08, index, index+.08], vals, color=COLORS[1], s=24, zorder=3)
    ax.set(xlabel="Shortlisted threshold S", ylabel="CPU time per sort (seconds)",
           title=f"Larger-input confirmation: n={cfg['confirmation_n']:,}; selected S={selected}")
    ax.grid(axis="y", alpha=.2); ax.legend()
    save(fig, out, "c3_confirmation")

    final_t = timed[timed.stage == "final"].pivot(index="repeat", columns="algorithm", values="cpu_seconds")
    final_c = counted[counted.stage == "final"].pivot(index="repeat", columns="algorithm", values="comparisons")
    final_t["speedup"] = final_t.original / final_t.hybrid
    final_t.to_csv(out / "final_paired_cpu.csv")
    final_c.to_csv(out / "final_paired_comparisons.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, frame, metric in ((axes[0], final_t, "CPU seconds per sort"), (axes[1], final_c / 1e6, "Key comparisons (millions)")):
        for repeat, row in frame.iterrows():
            ax.plot([0, 1], [row.original, row.hybrid], "o-", color=COLORS[int(repeat)], label=f"Seed {int(repeat)+1}")
        ax.set(xticks=[0, 1], xticklabels=["Original", f"Hybrid S={selected}"], ylabel=metric)
        ax.set_ylim(0, max(frame.original.max(), frame.hybrid.max()) * 1.12)
        ax.grid(axis="y", alpha=.2); ax.legend(fontsize=10)
    axes[0].set_title(f"(d): n={cfg['final_n']:,}, uncounted timing")
    axes[1].set_title("Separate counted runs on identical inputs")
    save(fig, out, "d_final_comparison")

    baseline_median = float(final_t.original.median())
    hybrid_median = float(final_t.hybrid.median())
    summary = {"configuration": cfg["name"], "measurement_rows": len(raw), "selected_s": selected,
               "tuning": tuning_summary, "confirmation": confirm.to_dict("records"),
               "original_median_cpu_seconds": baseline_median, "hybrid_median_cpu_seconds": hybrid_median,
               "ratio_of_median_cpu_times": baseline_median / hybrid_median,
               "median_paired_speedup": float(final_t.speedup.median()),
               "hybrid_faster_pairs": int((final_t.speedup > 1).sum()),
               "hybrid_slower_pairs": int((final_t.speedup < 1).sum()),
               "tied_cpu_pairs": int((final_t.speedup == 1).sum()),
               "paired_speedup_min": float(final_t.speedup.min()), "paired_speedup_max": float(final_t.speedup.max()),
               "original_median_comparisons": int(final_c.original.median()), "hybrid_median_comparisons": int(final_c.hybrid.median()),
               "comparison_change_percent": float((final_c.hybrid.median()/final_c.original.median()-1)*100),
               "original_cpu_range": [float(final_t.original.min()), float(final_t.original.max())],
               "hybrid_cpu_range": [float(final_t.hybrid.min()), float(final_t.hybrid.max())],
               "maximum_recorded_rss_bytes": int(raw.rss_bytes_after.max()),
               "scale_model_relative_errors_percent": [float((m/e-1)*100) for m,e in zip(scale["median"],predicted)],
               "scale_rows": scale.to_dict("records"), "fixed_rows": fixed.to_dict("records"),
               "actual_leaves_at_fixed_n": {str(s): leaf_sizes(cfg["fixed_n"], s) for s in cfg["thresholds"]}}
    (out / "findings.json").write_text(json.dumps(summary, indent=2))
    table = "\n".join(f"| {r.n:,} | {int(r.cpu_best_s)} | {int(r.comparison_best_s)} |" for r in pd.DataFrame(tuning_summary).itertuples())
    report = f'''# Measured findings: {cfg['name']}

All {len(raw)} planned measurement rows completed; 3 measured repeats per case.
Counts and times come from separate runs. Smoke data are not assignment evidence.

## Threshold selection

| Input size n | Lowest median CPU S | Fewest median comparisons S |
|---|---:|---:|
{table}

CPU ties in the displayed table use the smaller S. The saved shortlist applies
the predeclared geometric-ratio rule across these sizes. At n={cfg['confirmation_n']:,},
the lowest confirmation median selected **S={selected}**, best among the shortlisted
tested values. Check the min-max intervals in `c3_confirmation.png`: three seeds
do not establish a universal optimum or statistical significance.

## Final n={cfg['final_n']:,} comparison

| Metric | Original | Hybrid S={selected} |
|---|---:|---:|
| Median CPU seconds | {baseline_median:.6f} | {hybrid_median:.6f} |
| CPU min-max seconds | {final_t.original.min():.6f}-{final_t.original.max():.6f} | {final_t.hybrid.min():.6f}-{final_t.hybrid.max():.6f} |
| Median key comparisons | {int(final_c.original.median()):,} | {int(final_c.hybrid.median()):,} |

Speedup per paired seed = original CPU seconds / hybrid CPU seconds.
Median paired speedup = **{final_t.speedup.median():.3f}x**, range
{final_t.speedup.min():.3f}-{final_t.speedup.max():.3f}x. A value above 1 means the
hybrid is faster. The ratio of the two medians is {baseline_median/hybrid_median:.3f}x;
it is a different statistic. Hybrid median comparisons changed by
{summary['comparison_change_percent']:+.2f}% relative to original.

Across the three paired seeds, the hybrid was faster in
**{summary['hybrid_faster_pairs']}**, slower in **{summary['hybrid_slower_pairs']}**,
and tied in **{summary['tied_cpu_pairs']}**. These observations include every
measured regression; no repeat was discarded or replaced after seeing its result.

Raw per-repeat counts and times are in `final_paired_comparisons.csv` and
`final_paired_cpu.csv`; the original raw observations remain in the results folder.

## Connection to theory

At fixed S={cfg['fixed_s']}, the comparison plot and C/(n log2 n) normalization
are consistent with the derived Theta(n log n) fixed-threshold growth. The maximum
absolute relative difference from the random-distinct expectation across the
scale medians is {max(abs(x) for x in summary['scale_model_relative_errors_percent']):.3f}%.
That analytical curve is unscaled and is only approximate for repeated integers.
Agreement over seven measured sizes is evidence of consistency, not a proof of
asymptotic complexity; the recurrence supplies the proof.

For fixed n, increasing S creates stepwise changes in leaf sizes. Insertion work
eventually increases faster than the saved merge comparisons. The CPU chart
measures extra costs absent from the comparison count: recursion, loop/index
operations, pointer assignments and copying. Separate instrumentation avoids
count increments distorting the timed comparison.

## Scope and limitations

One CPython interpreter and one Windows laptop, IID uniform integers with x={cfg['x']:,},
three distinct seeds per case, and a finite threshold grid. Repeats mix input
variation and timing variation; they are not independent hardware replications.
Small-case batching repeats each seed's input, not additional independent datasets.
Timers exclude input generation/reset, merge-buffer allocation, validation and I/O.
The same machine was also used for lightweight document preparation; background
OS/browser activity was not controlled. No cache or thermal profiling was done.
Min-max bars are observed ranges, not confidence intervals.
The largest recorded post-validation RSS was {summary['maximum_recorded_rss_bytes']/2**20:.1f} MiB;
this is a sampled process footprint, not a measured allocation peak.
Exact frequency histograms plus sorted order prove the bounded-integer multiset
was preserved. Fingerprints alone would not give that guarantee.
'''
    (out / "findings.md").write_text(report, encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results/full"))
    parser.add_argument("--out", type=Path, default=Path("plots/full"))
    args = parser.parse_args()
    print(json.dumps(make_analysis(args.results, args.out), indent=2))
