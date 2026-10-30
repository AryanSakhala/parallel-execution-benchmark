import csv
import resource
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

DURATION = 0.05
TASK_COUNTS = [4, 8, 16]
WORKERS = [1, 2, 4]
METHODS = ["sequential", "threads", "processes"]
KINDS = ["cpu", "io"]


def cpu_task(iterations):
    total = 0
    for number in range(iterations):
        total += number * number
    return total


def io_task(duration):
    time.sleep(duration)
    return duration


def iterations_for(duration):
    sample = 200_000
    started = time.perf_counter()
    cpu_task(sample)
    elapsed = time.perf_counter() - started
    return max(1, int(sample * duration / elapsed))


def cpu_used():
    own = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + kids.ru_utime + kids.ru_stime


def run(method, kind, tasks, workers, iterations):
    task = cpu_task if kind == "cpu" else io_task
    jobs = [iterations if kind == "cpu" else DURATION] * tasks
    before = cpu_used()
    started = time.perf_counter()
    if method == "sequential":
        for job in jobs:
            task(job)
    else:
        pool = ThreadPoolExecutor if method == "threads" else ProcessPoolExecutor
        with pool(max_workers=workers) as executor:
            list(executor.map(task, jobs))
    seconds = time.perf_counter() - started
    return seconds, tasks / seconds, (cpu_used() - before) / seconds


def main():
    iterations = iterations_for(DURATION)
    rows = []
    for kind in KINDS:
        for tasks in TASK_COUNTS:
            for method in METHODS:
                worker_choices = [1] if method == "sequential" else WORKERS
                for workers in worker_choices:
                    seconds, throughput, util = run(method, kind, tasks, workers, iterations)
                    rows.append([
                        method,
                        kind,
                        tasks,
                        workers,
                        DURATION,
                        round(seconds, 4),
                        round(throughput, 2),
                        round(util, 2),
                    ])

    with open("benchmark_results.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "method", "kind", "tasks", "workers", "duration",
            "seconds", "throughput", "cpu_util",
        ])
        writer.writerows(rows)

    print(len(rows), "measurements written")


if __name__ == "__main__":
    main()
