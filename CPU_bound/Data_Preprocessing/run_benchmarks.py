"""Run every benchmark with: python3 run_benchmarks.py Developed code using ChatGPT."""

import asyncio
import csv
import importlib
import multiprocessing
from pathlib import Path
import sys

FRAMEWORKS = Path(__file__).resolve().parent / "frameworks"
DATASETS = ["boston", "quake", "diamonds"]
CONCURRENCY_LEVELS = [1, 2, 4]
RESULTS = Path(__file__).resolve().parent / "results" / "preprocessing_benchmarks.csv"


def run_benchmark(filename, dataset, concurrency, measure_memory, connection):
    """Run one framework function inside a spawned process."""
    sys.path.insert(0, str(FRAMEWORKS))
    module = importlib.import_module(filename.removesuffix(".py"))
    preprocess = getattr(module, "preprocess_" + dataset)

    if filename == "async_framework.py":
        _, seconds, memory_bytes = asyncio.run(preprocess(measure_memory=measure_memory))
    else:
        _, seconds, memory_bytes = preprocess(
            concurrency=concurrency,
            measure_memory=measure_memory,
        )

    connection.send(memory_bytes if measure_memory else seconds)
    connection.close()


def measure(filename, dataset, concurrency, measure_memory):
    """Run one measurement in a fresh process and return its result."""
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(
        target=run_benchmark,
        args=(filename, dataset, concurrency, measure_memory, sender),
    )
    process.start()
    sender.close()
    process.join()

    if process.exitcode != 0:
        receiver.close()
        raise SystemExit(f"Benchmark failed: {filename}, {dataset}")

    result = receiver.recv()
    receiver.close()
    process.close()
    return result


def main():
    RESULTS.parent.mkdir(exist_ok=True)
    fieldnames = ["framework", "concurrency"] + [
        f"{dataset}_{metric}"
        for dataset in DATASETS
        for metric in ("seconds", "peak_memory_mib")
    ]
    results = []

    for filename in ["async_framework.py", "thread_framework.py", "multiprocessing_framework.py"]:
        levels = [None] if filename == "async_framework.py" else CONCURRENCY_LEVELS
        for concurrency in levels:
            row = {"framework": filename, "concurrency": concurrency or ""}
            for dataset in DATASETS:
                seconds = measure(filename, dataset, concurrency, measure_memory=False)
                memory = measure(filename, dataset, concurrency, measure_memory=True) / 1024 ** 2
                row[f"{dataset}_seconds"] = seconds
                row[f"{dataset}_peak_memory_mib"] = memory

            results.append(row)
            with RESULTS.open("w", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)


if __name__ == "__main__":
    main()
