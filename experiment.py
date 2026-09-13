"""Sequential, resumable experiments. Run --help; analysis never calls this file.

Counts and CPU times are different runs on fresh copies of the same seed data.
Buffer allocation, copies, RNG, warmup, checks and I/O are outside sort timers.
"""
import argparse
from array import array
from contextlib import contextmanager
import csv
from datetime import datetime, timezone
import gc
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time

import psutil
from algorithms import hybrid_sort, hybrid_sort_counted, merge_sort, merge_sort_counted

ROOT = Path(__file__).resolve().parent
FIELDS = ["case_id", "config_hash", "environment_id", "experiment", "stage", "algorithm",
          "n", "S", "x", "seed", "repeat", "measurement_mode", "comparisons",
          "cpu_seconds", "wall_seconds", "sort_batch_size", "cpu_total_seconds", "wall_total_seconds", "order_position", "length_ok", "order_ok",
          "integrity_method", "integrity_ok", "input_sum", "input_sum_squares",
          "input_xor", "dataset_sha256", "output_sha256", "rss_bytes_after",
          "python_version", "platform", "completed_utc"]


def write_json(path, data):
    """Atomic metadata/selection update; raw CSV rows are flushed separately."""
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(path)


@contextmanager
def result_lock(path):
    """OS releases this advisory lock on crash; no stale-lock deletion needed."""
    stream = path.open("a+b")
    stream.seek(0)
    stream.write(b"0")
    stream.flush()
    stream.seek(0)
    try:
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        stream.close()


def environment():
    hardware = {"logical_cpus": psutil.cpu_count(), "physical_cores": psutil.cpu_count(logical=False),
                "total_ram_bytes": psutil.virtual_memory().total,
                "available_ram_bytes_at_start": psutil.virtual_memory().available,
                "processor": platform.processor()}
    if sys.platform == "win32":
        try:
            hardware["cpu_details"] = json.loads(subprocess.check_output([
                "powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"], text=True))
        except (OSError, ValueError, subprocess.SubprocessError):
            hardware["cpu_details"] = "unavailable"
    return {"python_version": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "machine": platform.machine(),
            "hardware": hardware, "process_time_clock": vars(time.get_clock_info("process_time")),
            "created_utc": datetime.now(timezone.utc).isoformat()}


def signature(values, x, exact_limit, check_order=False):
    """Streaming identity checks, plus exact histogram when the range is bounded.

    SHA-256 of little-endian uint64 blocks also identifies input order. Sums,
    squared sums and XOR alone can collide and do not prove multiset equality.
    The optional histogram DOES prove equality for values in [1,x].
    """
    frequencies = array("Q", [0]) * (x + 1) if x <= exact_limit else None
    total = squares = xor = 0
    previous = None
    ordered = True
    digest = hashlib.sha256()
    block = array("Q")
    for value in values:
        if not 1 <= value <= x:
            raise AssertionError("out-of-range data")
        total += value
        squares += value * value
        xor ^= value
        if frequencies is not None:
            frequencies[value] += 1
        if check_order and previous is not None and previous > value:
            ordered = False
        previous = value
        block.append(value)
        if len(block) == 8192:
            if sys.byteorder != "little": block.byteswap()
            digest.update(block.tobytes())
            block = array("Q")
    if sys.byteorder != "little": block.byteswap()
    digest.update(block.tobytes())
    return {"length": len(values), "sum": total, "sum_squares": squares, "xor": xor,
            "histogram": frequencies, "ordered": ordered, "sha256": digest.hexdigest()}


def sort_function(algorithm, mode):
    if algorithm == "original":
        return merge_sort_counted if mode == "counted" else merge_sort
    return hybrid_sort_counted if mode == "counted" else hybrid_sort


def call_sort(fn, values, buffer, algorithm, threshold):
    return fn(values, buffer) if algorithm == "original" else fn(values, threshold, buffer)


def measure(values, buffer, algorithm, threshold, mode, warmup_n, x, batch_size):
    fn = sort_function(algorithm, mode)
    # Independent unsorted copies are prepared before the timer. Batching makes
    # small-case CPU totals longer than the OS timer quantum. No reset is timed.
    batch = [values] + [values.copy() for _ in range(batch_size - 1)]
    warm_rng = random.Random(772)
    warm = [warm_rng.randint(1, x) for _ in range(warmup_n)]
    call_sort(fn, warm, [None] * len(warm), algorithm, threshold)
    del warm
    gc.collect()
    enabled = gc.isenabled()
    gc.disable()
    try:
        if mode == "timed":
            wall_start = time.perf_counter()
            cpu_start = time.process_time()
            for data in batch:
                call_sort(fn, data, buffer, algorithm, threshold)
            cpu = time.process_time() - cpu_start
            wall = time.perf_counter() - wall_start
            # Every batch output must match; outside timer, no new reference copy.
            if any(data != values for data in batch):
                raise AssertionError("Batch outputs disagree")
            return None, cpu / batch_size, wall / batch_size
        return call_sort(fn, values, buffer, algorithm, threshold), None, None
    finally:
        if enabled: gc.enable()


def load_rows(path):
    if not path.exists(): return []
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise RuntimeError("Incomplete CSV row: preserve a backup, remove only the incomplete final row, then resume")
    ids = [r["case_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate case IDs in results")
    return rows


def append_row(path, row):
    import os
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if not exists: writer.writeheader()
        writer.writerow(row)
        stream.flush()
        os.fsync(stream.fileno())


def run_stage(stage, sizes, candidates, cfg, out, rows, config_hash, env, exp):
    completed = {r["case_id"] for r in rows}
    for n in sizes:
        for repeat in range(cfg["repeats"]):
            seed = cfg["seed_bases"][stage] + n * 10 + repeat
            jobs = [(algorithm, threshold, mode) for algorithm, threshold in candidates
                    for mode in cfg["modes"]]
            random.Random(cfg["order_seed"] + seed).shuffle(jobs)
            jobs = [(position, algorithm, threshold, mode,
                     f"{stage}:{n}:{repeat}:{algorithm}:{threshold}:{mode}")
                    for position, (algorithm, threshold, mode) in enumerate(jobs)]
            if all(job[-1] in completed for job in jobs): continue
            rng = random.Random(seed)
            base = [rng.randint(1, cfg["x"]) for _ in range(n)]
            before = signature(base, cfg["x"], cfg["exact_histogram_max_x"])
            buffer = [None] * n
            for position, algorithm, threshold, mode, case_id in jobs:
                if case_id in completed: continue
                print(f"START {case_id} seed={seed}", flush=True)
                values = base.copy()  # Every case receives the identical unsorted data.
                batch_size = max(1, cfg["timed_batch_items"] // n) if mode == "timed" else 1
                count, cpu, wall = measure(values, buffer, algorithm, threshold,
                                          mode, cfg["warmup_n"], cfg["x"], batch_size)
                after = signature(values, cfg["x"], cfg["exact_histogram_max_x"], True)
                length_ok = before["length"] == after["length"] == n
                integrity_ok = all(before[k] == after[k] for k in ("sum", "sum_squares", "xor", "histogram"))
                if not (length_ok and integrity_ok and after["ordered"]):
                    raise AssertionError(f"Validation failed: {case_id}")
                # Sorted integer output is unique: compare hashes with prior modes/candidates.
                peers = [r for r in rows if r["stage"] == stage and int(r["n"]) == n and int(r["repeat"]) == repeat]
                if any(r["output_sha256"] != after["sha256"] for r in peers):
                    raise AssertionError("Counted/uncounted or candidate output mismatch")
                row = dict(case_id=case_id, config_hash=config_hash, environment_id=env["environment_id"],
                           experiment=exp(n), stage=stage, algorithm=algorithm, n=n, S=threshold,
                           x=cfg["x"], seed=seed, repeat=repeat, measurement_mode=mode,
                           comparisons=count, cpu_seconds=cpu, wall_seconds=wall, sort_batch_size=batch_size,
                           cpu_total_seconds=None if cpu is None else cpu*batch_size,
                           wall_total_seconds=None if wall is None else wall*batch_size,
                           order_position=position, length_ok=length_ok, order_ok=after["ordered"],
                           integrity_method="exact_histogram+sum+squares+xor" if before["histogram"] is not None else "sum+squares+xor (probabilistic)",
                           integrity_ok=integrity_ok, input_sum=before["sum"], input_sum_squares=before["sum_squares"],
                           input_xor=before["xor"], dataset_sha256=before["sha256"], output_sha256=after["sha256"],
                           rss_bytes_after=psutil.Process().memory_info().rss,
                           python_version=platform.python_version(), platform=platform.platform(),
                           completed_utc=datetime.now(timezone.utc).isoformat())
                append_row(out / "raw.csv", row)
                rows.append({k: "" if v is None else str(v) for k, v in row.items()})
                completed.add(case_id)
                print(f"DONE {case_id} comparisons={count} CPU={cpu} wall={wall}; verified", flush=True)
                del values, after
            del buffer, base, before


def shortlist(rows, cfg):
    def median_cpu(n, threshold):
        values = [float(r["cpu_seconds"]) for r in rows if r["stage"] == "tune"
                  and int(r["n"]) == n and int(r["S"]) == threshold and r["measurement_mode"] == "timed"]
        if len(values) != cfg["repeats"]: raise RuntimeError("Incomplete tuning")
        return statistics.median(values)
    scores = {}
    for threshold in cfg["thresholds"]:
        ratios = [median_cpu(n, threshold) / max(median_cpu(n, 1), 1e-12) for n in cfg["tuning_sizes"]]
        scores[threshold] = math.exp(statistics.mean(math.log(max(r, 1e-12)) for r in ratios))
    chosen = sorted(scores, key=lambda threshold: (scores[threshold], threshold))[:cfg["shortlist_count"]]
    return chosen, scores


def select_final(rows, cfg, candidates):
    medians = {}
    for threshold in candidates:
        values = [float(r["cpu_seconds"]) for r in rows if r["stage"] == "confirm"
                  and int(r["S"]) == threshold and r["measurement_mode"] == "timed"]
        if len(values) != cfg["repeats"]: raise RuntimeError("Incomplete confirmation")
        medians[threshold] = statistics.median(values)
    return min(medians, key=lambda threshold: (medians[threshold], threshold)), medians


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/full.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--stage", choices=["all", "tune", "confirm", "scale", "final"], default="all")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    if cfg["repeats"] < 1 or not 1 <= cfg["x"] < 2**64: raise ValueError("Invalid config")
    if any(s < 1 for s in cfg["thresholds"]): raise ValueError("Invalid S")
    if cfg["modes"] != ["timed", "counted"]: raise ValueError("Both measurement modes are required")
    code_hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                   for name in ("algorithms.py", "experiment.py")}
    config_hash = hashlib.sha256(json.dumps({"config": cfg, "code": code_hashes}, sort_keys=True).encode()).hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    with result_lock(args.out / ".run.lock"):
        meta_path = args.out / "metadata.json"
        if meta_path.exists():
            if not args.resume: raise RuntimeError("Results exist. Use --resume or a new --out directory")
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta["config_hash"] != config_hash: raise RuntimeError("Config/code changed; choose a new --out")
            env = meta["environment"]
            if env["python_version"] != sys.version or env["platform"] != platform.platform():
                raise RuntimeError("Interpreter/platform changed; choose a new --out")
        else:
            env = environment()
            env["environment_id"] = hashlib.sha256(json.dumps(env, sort_keys=True).encode()).hexdigest()[:16]
            meta = {"config": cfg, "config_hash": config_hash, "code_sha256": code_hashes, "environment": env,
                    "protocol": {"buffer_allocation": "excluded, one reused buffer per dataset", "input_reset": "copy outside timer",
                    "gc": "collected before each sort, disabled during sort, restored afterwards", "execution": "sequential; seeded shuffled case order",
                    "cpu_timer": "time.process_time; uncounted sort only", "wall_timer": "time.perf_counter; separate column",
                    "warmup": "one deterministic small sort per case using the same implementation",
                    "batching": "timed batch size=max(1,timed_batch_items//n); independent pre-timer copies; raw totals and per-sort means saved; all outputs checked",
                    "repetition": "independent input seed per repeat, paired across candidates and modes", "missing_metrics": "empty CSV cells, never zero"}}
            write_json(meta_path, meta)
            write_json(args.out / "config.json", cfg)
        rows = load_rows(args.out / "raw.csv")
        if any(r["config_hash"] != config_hash for r in rows): raise RuntimeError("Mixed result configuration")
        stages = ["tune", "confirm", "scale", "final"] if args.stage == "all" else [args.stage]
        for stage in stages:
            if stage == "tune":
                run_stage(stage, cfg["tuning_sizes"], [("hybrid", s) for s in cfg["thresholds"]], cfg,
                          args.out, rows, config_hash, env, lambda n: "c(ii)+c(iii)" if n == cfg["fixed_n"] else "c(iii)")
            elif stage == "confirm":
                candidates, scores = shortlist(rows, cfg)
                write_json(args.out / "shortlist.json", {"thresholds": candidates, "geometric_cpu_ratios": scores})
                run_stage(stage, [cfg["confirmation_n"]], [("hybrid", s) for s in candidates], cfg,
                          args.out, rows, config_hash, env, lambda n: "c(iii)-confirmation")
                selected, medians = select_final(rows, cfg, candidates)
                write_json(args.out / "selection.json", {"selected_s": selected, "confirmation_median_cpu_seconds": medians,
                           "criterion": cfg["primary_criterion"], "scope": "best among shortlisted tested values at confirmation_n"})
            elif stage == "scale":
                run_stage(stage, cfg["sizes"], [("hybrid", cfg["fixed_s"])], cfg,
                          args.out, rows, config_hash, env, lambda n: "c(i)")
            else:
                candidates, _ = shortlist(rows, cfg)
                selected, _ = select_final(rows, cfg, candidates)
                run_stage(stage, [cfg["final_n"]], [("original", 1), ("hybrid", selected)], cfg,
                          args.out, rows, config_hash, env, lambda n: "d")
        print(f"Saved {len(rows)} completed measurements to {args.out / 'raw.csv'}", flush=True)


if __name__ == "__main__":
    main()
