# Made with ChatGPT.
"""Sequential matrix multiplication using NumPy."""

import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time

import numpy as np

import sys
from pathlib import Path

# Share the project-wide sampler across workloads.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from memory_usage import MemorySampler


def matrix_multiply(matrix_a, matrix_b, *, measure_memory=False):
    """Multiply two 2-D matrices and return (result, seconds, peak_memory_bytes)."""
    if measure_memory:
        memory = MemorySampler(interval=0.001)
        memory.start()
    else:
        start = time.perf_counter()

    result = np.matmul(matrix_a, matrix_b)

    if measure_memory:
        peak_memory_bytes = memory.stop()
        elapsed_seconds = None
    else:
        elapsed_seconds = time.perf_counter() - start
        peak_memory_bytes = None

    return result, elapsed_seconds, peak_memory_bytes
