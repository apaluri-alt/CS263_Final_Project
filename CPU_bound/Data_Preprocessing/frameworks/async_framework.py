"""Async numeric preprocessing for the three datasets. Developed code using ChatGPT."""

import csv
import asyncio
import math
from pathlib import Path
import time
from memory_usage import MemorySampler

DATASETS = Path(__file__).resolve().parent.parent / "Datasets"

async def preprocess_boston(dataset=DATASETS / "Boston-house-price-data.csv", *, measure_memory=False):
    """Standardize numeric columns in the Boston housing dataset."""
    if measure_memory:
        memory = MemorySampler(interval=0.001)
        memory.start()
    else:
        start = time.perf_counter()

    with open(dataset, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        rows = list(reader)

    numeric_columns = ["CRIM"]

    means = {}
    scales = {}
    for column in numeric_columns:
        values = [float(row[column]) for row in rows]
        means[column] = sum(values) / len(values)
        variance = sum((value - means[column]) ** 2 for value in values) / len(values)
        scales[column] = math.sqrt(variance) or 1.0

    processed = []
    for row in rows:
        processed.append([
            (float(row[column]) - means[column]) / scales[column]
            for column in numeric_columns
        ])

    if measure_memory:
        peak_memory_bytes = memory.stop()
        elapsed_seconds = None
    else:
        elapsed_seconds = time.perf_counter() - start
        peak_memory_bytes = None

    return processed, elapsed_seconds, peak_memory_bytes

async def preprocess_quake(dataset=DATASETS / "dataset_2195_quake.csv", *, measure_memory=False):
    """Standardize numeric columns in the earthquake dataset."""
    if measure_memory:
        memory = MemorySampler(interval=0.001)
        memory.start()
    else:
        start = time.perf_counter()

    with open(dataset, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        rows = list(reader)

    numeric_columns = ["focal_depth"]

    means = {}
    scales = {}
    for column in numeric_columns:
        values = [float(row[column]) for row in rows]
        means[column] = sum(values) / len(values)
        variance = sum((value - means[column]) ** 2 for value in values) / len(values)
        scales[column] = math.sqrt(variance) or 1.0

    processed = []
    for row in rows:
        processed.append([
            (float(row[column]) - means[column]) / scales[column]
            for column in numeric_columns
        ])

    if measure_memory:
        peak_memory_bytes = memory.stop()
        elapsed_seconds = None
    else:
        elapsed_seconds = time.perf_counter() - start
        peak_memory_bytes = None

    return processed, elapsed_seconds, peak_memory_bytes

async def preprocess_diamonds(dataset=DATASETS / "diamonds.csv", *, measure_memory=False):
    """Standardize numeric columns in the diamonds dataset."""
    if measure_memory:
        memory = MemorySampler(interval=0.001)
        memory.start()
    else:
        start = time.perf_counter()

    with open(dataset, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        rows = list(reader)

    numeric_columns = ["carat"]

    means = {}
    scales = {}
    for column in numeric_columns:
        values = [float(row[column]) for row in rows]
        means[column] = sum(values) / len(values)
        variance = sum((value - means[column]) ** 2 for value in values) / len(values)
        scales[column] = math.sqrt(variance) or 1.0

    processed = []
    for row in rows:
        processed.append([
            (float(row[column]) - means[column]) / scales[column]
            for column in numeric_columns
        ])

    if measure_memory:
        peak_memory_bytes = memory.stop()
        elapsed_seconds = None
    else:
        elapsed_seconds = time.perf_counter() - start
        peak_memory_bytes = None

    return processed, elapsed_seconds, peak_memory_bytes
