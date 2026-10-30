# Parallel execution benchmark

`benchmark.py` runs the same work three ways: sequential, threads, and processes. Each task is either a CPU loop or a wait. It varies the task count and the worker count, and writes `benchmark_results.csv`.

`visualize.py` reads that CSV and saves `task_count_time.png`, `workers_throughput.png`, and `speedup_utilization.png`.

Processes can finish CPU-bound Python work sooner. Threads can finish waiting work sooner. Starting and coordinating workers has a cost. A fresh copy of this folder has neither the CSV nor the charts.
