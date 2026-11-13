"""Run every benchmark with: python3 run_benchmarks.py Developed code using ChatGPT."""

import asyncio
import csv
import importlib
import multiprocessing
from pathlib import Path
import sys

FRAMEWORKS = Path(__file__).resolve().parent / "frameworks"
MATRIX_SIZES = {"small": 128, "medium": 512, "large": 2048}
RANDOM_SEED = 42
CONCURRENCY_LEVELS = [1, 2, 4]
RESULTS = Path(__file__).resolve().parent / "results" / "matrix_multiplication_benchmarks.csv"


def run_benchmark(filename, size, concurrency, measure_memory, connection):
    """Run one framework function inside a spawned process."""
    sys.path.insert(0, str(FRAMEWORKS))
    module = importlib.import_module(filename.removesuffix(".py"))
    multiply = module.matrix_multiply

    # Import after the framework sets the BLAS thread limits.
    import numpy as np

    rng = np.random.default_rng(RANDOM_SEED)
    dimension = MATRIX_SIZES[size]
    matrix_a = rng.random((dimension, dimension))
    matrix_b = rng.random((dimension, dimension))

    if filename == "async_framework.py":
        _, seconds, memory_bytes = asyncio.run(
            multiply(matrix_a, matrix_b, measure_memory=measure_memory)
        )
    elif filename == "baseline_framework.py":
        _, seconds, memory_bytes = multiply(matrix_a, matrix_b, measure_memory=measure_memory)
    else:
        _, seconds, memory_bytes = multiply(
            matrix_a,
            matrix_b,
            concurrency=concurrency,
            measure_memory=measure_memory,
        )

    connection.send(memory_bytes if measure_memory else seconds)
    connection.close()


def measure(filename, size, concurrency, measure_memory):
    """Run one measurement in a fresh process and return its result."""
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(
        target=run_benchmark,
        args=(filename, size, concurrency, measure_memory, sender),
    )
    process.start()
    sender.close()
    process.join()

    if process.exitcode != 0:
        receiver.close()
        raise SystemExit(f"Benchmark failed: {filename}, {size}")

    result = receiver.recv()
    receiver.close()
    process.close()
    return result


def main():
    RESULTS.parent.mkdir(exist_ok=True)
    fieldnames = ["framework", "concurrency", "matrix_size", "seconds", "peak_memory_mib"]
    results = []

    for filename in ["baseline_framework.py", "async_framework.py", "thread_framework.py", "multiprocessing_framework.py"]:
        levels = [None] if filename in ["baseline_framework.py", "async_framework.py"] else CONCURRENCY_LEVELS
        for concurrency in levels:
            for size in MATRIX_SIZES:
                seconds = measure(filename, size, concurrency, measure_memory=False)
                memory = measure(filename, size, concurrency, measure_memory=True) / 1024 ** 2
                row = {
                    "framework": filename,
                    "concurrency": concurrency or "",
                    "matrix_size": MATRIX_SIZES[size],  # N for both N x N inputs.
                    "seconds": seconds,
                    "peak_memory_mib": memory,
                }

                results.append(row)
                with RESULTS.open("w", newline="") as output:
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)


if __name__ == "__main__":
    main()
