# Made with ChatGPT.
"""Run every benchmark with: python3 run_benchmarks.py."""

import asyncio
import csv
import importlib
import multiprocessing
from pathlib import Path
import sys

from server import serve

FRAMEWORKS = Path(__file__).resolve().parent / "frameworks"
RESPONSE_DELAY = 0.01
CONCURRENCY_LEVELS = [1, 2, 4]
REQUEST_COUNTS = [100, 500, 1000]
RESULTS = Path(__file__).resolve().parent / "results" / "networking_benchmarks.csv"


def run_benchmark(filename, request_count, concurrency, measure_memory, connection):
    """Run one framework function inside a spawned process."""
    sys.path.insert(0, str(FRAMEWORKS))
    module = importlib.import_module(filename.removesuffix(".py"))
    receive = module.receive_packets

    if filename == "async_framework.py":
        _, seconds, memory_bytes, seconds_until_sort = asyncio.run(
            receive(num_requests=request_count, measure_memory=measure_memory)
        )
    elif filename == "baseline_framework.py":
        _, seconds, memory_bytes, seconds_until_sort = receive(num_requests=request_count, measure_memory=measure_memory)
    else:
        _, seconds, memory_bytes, seconds_until_sort = receive(
            num_requests=request_count,
            concurrency=concurrency,
            measure_memory=measure_memory,
        )

    connection.send(memory_bytes if measure_memory else (seconds, seconds_until_sort))
    connection.close()


def measure(filename, request_count, concurrency, measure_memory):
    """Run one measurement in a fresh process and return its result."""
    context = multiprocessing.get_context("spawn")
    ready, ready_sender = context.Pipe(duplex=False)
    finished = context.Event()
    server = context.Process(target=serve, args=(RESPONSE_DELAY, ready_sender, finished))
    server.start()
    ready_sender.close()

    try:
        if not ready.poll(10):
            raise RuntimeError("Local server did not start")
        ready.recv()
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(
            target=run_benchmark,
            args=(filename, request_count, concurrency, measure_memory, sender),
        )
        process.start()
        sender.close()
        process.join()

        if process.exitcode != 0:
            receiver.close()
            process.close()
            raise SystemExit(f"Benchmark failed: {filename}, {request_count}, {concurrency}")

        result = receiver.recv()
        receiver.close()
        process.close()
        return result
    finally:
        ready.close()
        finished.set()
        server.join(timeout=5)
        if server.is_alive():
            server.terminate()
            server.join()
        server.close()


def main():
    RESULTS.parent.mkdir(exist_ok=True)
    fieldnames = ["framework", "concurrency", "packet_count", "response_delay_seconds", "seconds", "seconds_until_sort", "peak_memory_mib"]
    results = []

    for filename in ["baseline_framework.py", "async_framework.py", "thread_framework.py", "multiprocessing_framework.py"]:
        levels = [None] if filename in ["baseline_framework.py", "async_framework.py"] else CONCURRENCY_LEVELS
        for concurrency in levels:
            for request_count in REQUEST_COUNTS:
                seconds, seconds_until_sort = measure(filename, request_count, concurrency, measure_memory=False)
                memory = measure(filename, request_count, concurrency, measure_memory=True) / 1024 ** 2
                row = {
                    "framework": filename,
                    "concurrency": concurrency or "",
                    "packet_count": request_count,
                    "response_delay_seconds": RESPONSE_DELAY,
                    "seconds": seconds,
                    "seconds_until_sort": seconds_until_sort,
                    "peak_memory_mib": memory,
                }

                results.append(row)
                with RESULTS.open("w", newline="") as output:
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)

if __name__ == "__main__":
    main()
