"""Check saved-run completeness, pairing, IDs and metric separation."""
import argparse
import json
from pathlib import Path
from experiment import load_rows, shortlist, select_final


def audit(folder):
    meta = json.loads((folder / "metadata.json").read_text())
    cfg = meta["config"]
    rows = load_rows(folder / "raw.csv")
    candidates, _ = shortlist(rows, cfg)
    chosen, _ = select_final(rows, cfg, candidates)
    plans = {"tune": (cfg["tuning_sizes"], [("hybrid", s) for s in cfg["thresholds"]]),
             "confirm": ([cfg["confirmation_n"]], [("hybrid", s) for s in candidates]),
             "scale": (cfg["sizes"], [("hybrid", cfg["fixed_s"])]),
             "final": ([cfg["final_n"]], [("original", 1), ("hybrid", chosen)])}
    expected = {f"{stage}:{n}:{repeat}:{algorithm}:{s}:{mode}"
                for stage, (sizes, algorithms) in plans.items() for n in sizes
                for repeat in range(cfg["repeats"]) for algorithm, s in algorithms for mode in cfg["modes"]}
    assert {r["case_id"] for r in rows} == expected, "Missing/unexpected cases"
    grouped = {}
    for row in rows:
        assert row["config_hash"] == meta["config_hash"]
        for key in ("length_ok", "order_ok", "integrity_ok"): assert row[key] == "True"
        if row["measurement_mode"] == "counted":
            assert row["cpu_seconds"] == row["wall_seconds"] == ""
            assert int(row["comparisons"]) >= 0
        else:
            assert row["comparisons"] == ""
            assert float(row["cpu_seconds"]) >= 0
            assert abs(float(row["cpu_seconds"]) * int(row["sort_batch_size"]) - float(row["cpu_total_seconds"])) < 1e-8
        key = row["stage"], row["n"], row["repeat"]
        grouped.setdefault(key, []).append(row)
    for group in grouped.values():
        assert len({r["seed"] for r in group}) == 1
        assert len({r["dataset_sha256"] for r in group}) == 1
        assert len({r["output_sha256"] for r in group}) == 1
    final_seeds = {r["seed"] for r in rows if r["stage"] == "final"}
    tuning_seeds = {r["seed"] for r in rows if r["stage"] in ("tune", "confirm")}
    assert final_seeds.isdisjoint(tuning_seeds)
    report = {"status": "PASS", "measurement_rows": len(rows), "paired_datasets": len(grouped),
              "selected_s": chosen, "all_expected_cases_present": True,
              "all_outputs_validated": True, "fresh_final_seeds": True,
              "checks": "IDs, configuration, completion, pairing hashes, mode separation, length/order/integrity flags"}
    (folder / "audit.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    print(json.dumps(audit(parser.parse_args().folder), indent=2))
