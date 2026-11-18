# Made with ChatGPT.
"""Threaded reception of delayed request/response records over HTTP.
"""

from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import random
import time

import sys
from pathlib import Path

# Share the project-wide sampler across workloads.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from memory_usage import MemorySampler


def receive_packets(num_requests=100, concurrency=1, measure_memory=False):
    """Receive records and return (result, seconds, peak_memory_bytes, seconds_until_sort)."""
    def receive_section():
        packets = []
        client = http.client.HTTPConnection("127.0.0.1", 5000)
        for _ in range(num_requests // concurrency):
            client.request("GET", "/packet")
            response = client.getresponse()
            data = response.read()
            packet = json.loads(data)
            packets.append(packet)
        client.close()
        for packet in packets:
            packet["type"] = {"tcp": 1, "udp": 0}[packet["type"]]
        return packets

    if measure_memory:
        memory = MemorySampler(interval=0.001)
        memory.start()
    else:
        start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(receive_section) for _ in range(concurrency)]
        parts = [future.result() for future in futures]
    result = [packet for part in parts for packet in part]
    seconds_until_sort = time.perf_counter() - start if not measure_memory else None
    numbers = [random.random() for _ in range(1000)]
    sorted_numbers = sorted(numbers)

    if measure_memory:
        peak_memory_bytes = memory.stop()
        elapsed_seconds = None
    else:
        elapsed_seconds = time.perf_counter() - start
        peak_memory_bytes = None

    return result, elapsed_seconds, peak_memory_bytes, seconds_until_sort
