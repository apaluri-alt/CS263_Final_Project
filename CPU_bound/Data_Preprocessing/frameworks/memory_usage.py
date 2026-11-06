"""Developed code using ChatGPT."""
"""Sample peak RSS for a process and its children using psutil.

RSS includes interpreter and native-library memory. Shared pages can be counted
in multiple processes, and peaks shorter than the sampling interval may be missed.
Run benchmarks one at a time, preferably in a fresh process for each measurement.
"""

from threading import Event, Thread

import psutil


class MemorySampler:
    def __init__(self, interval=0.01):
        self.process = psutil.Process()
        self.interval = interval
        self.peak_bytes = 0
        self.finished = Event()
        self.thread = Thread(target=self._sample, daemon=True)

    def _measure(self):
        total_bytes = 0
        for process in [self.process] + self.process.children(recursive=True):
            try:
                total_bytes += process.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.peak_bytes = max(self.peak_bytes, total_bytes)

    def _sample(self):
        while not self.finished.wait(self.interval):
            self._measure()

    def start(self):
        self._measure()
        self.thread.start()

    def stop(self):
        self.finished.set()
        self.thread.join()
        self._measure()
        return self.peak_bytes
