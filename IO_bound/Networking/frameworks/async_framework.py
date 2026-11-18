# Made with ChatGPT.
"""Async reception of delayed request/response records over HTTP.
"""

import asyncio
import random
import time

import aiohttp

import sys
from pathlib import Path

# Share the project-wide sampler across workloads.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from memory_usage import MemorySampler


async def receive_packets(num_requests=100, measure_memory=False):
    """Receive records and return (result, seconds, peak_memory_bytes, seconds_until_sort)."""
    requests_sent = asyncio.Event()
    sent_count = 0

    async def on_headers_sent(session, context, params):
        nonlocal sent_count
        sent_count += 1
        if sent_count == num_requests:
            requests_sent.set()

    async def receive_section():
        packets = []
        trace = aiohttp.TraceConfig()
        trace.on_request_headers_sent.append(on_headers_sent)
        connector = aiohttp.TCPConnector(limit=1000)
        async with aiohttp.ClientSession(connector=connector, trace_configs=[trace]) as client:
            responses = await asyncio.gather(*(
                client.get("http://127.0.0.1:5000/packet")
                for _ in range(num_requests)
            ))
            for response in responses:
                async with response:
                    packet = await response.json()
                packets.append(packet)
        for packet in packets:
            packet["type"] = {"tcp": 1, "udp": 0}[packet["type"]]
        return packets

    if measure_memory:
        memory = MemorySampler(interval=0.001)
        memory.start()
    else:
        start = time.perf_counter()

    # Wait until all requests have been sent.
    receive_task = asyncio.create_task(receive_section())
    await requests_sent.wait()
    seconds_until_sort = time.perf_counter() - start if not measure_memory else None
    numbers = [random.random() for _ in range(1000)]
    sorted_numbers = sorted(numbers)
    result = await receive_task

    if measure_memory:
        peak_memory_bytes = memory.stop()
        elapsed_seconds = None
    else:
        elapsed_seconds = time.perf_counter() - start
        peak_memory_bytes = None

    return result, elapsed_seconds, peak_memory_bytes, seconds_until_sort
