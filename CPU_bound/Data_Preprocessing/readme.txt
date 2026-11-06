Notes

- The async, threading, and multiprocessing frameworks each standardize one numeric column from each of the three datasets using pure Python arithmetic.

- The selected columns are CRIM for Boston housing, focal_depth for quakes, and carat for diamonds. The standardization mean and population standard deviation are calculated from the selected column.

- Threading and multiprocessing divide the column's values into chunks. Asyncio has no awaited work, so it behaves synchronously. this is intentional as a baseline showing that asyncio does not benefit CPU-bound work without awaitable operations.

- Execution time is measured with time.perf_counter(). CSV loading, statistics calculation, worker startup, standardization, and result assembly are included in the timed function.


- Memory is measured separately using psutil. A background sampler records peak summed RSS for the measurement process and its child processes. 

- The benchmark runner tests concurrency levels 1, 2, and 4 for threading and multiprocessing. Asyncio has no concurrency setting here.


- Run python3 run_benchmarks.py from the project directory to execute all configurations. Each timing and memory measurement runs in a fresh process. Results are stored in results/preprocessing_benchmarks.csv.
