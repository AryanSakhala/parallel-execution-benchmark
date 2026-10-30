import csv
import matplotlib.pyplot as plt

COLORS = {"threads": "C0", "processes": "C1"}


def load(path="benchmark_results.csv"):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in ("tasks", "workers", "duration", "seconds", "throughput", "cpu_util"):
            row[key] = float(row[key])
    return rows


def pick(rows, **match):
    return [row for row in rows if all(row[key] == value for key, value in match.items())]


def draw(axis, rows, xkey, ykey, label, color):
    rows = sorted(rows, key=lambda row: row[xkey])
    axis.plot(
        [row[xkey] for row in rows],
        [row[ykey] for row in rows],
        marker="o",
        color=color,
        label=label,
    )


def save(figure, path):
    figure.tight_layout()
    figure.savefig(path, dpi=140)
    plt.close(figure)
    print("saved", path)


def task_count_chart(rows):
    figure, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    for axis, kind in zip(axes, ("cpu", "io")):
        draw(axis, pick(rows, kind=kind, method="sequential", workers=1), "tasks", "seconds", "sequential", "C2")
        for method in ("threads", "processes"):
            draw(axis, pick(rows, kind=kind, method=method, workers=4), "tasks", "seconds", method, COLORS[method])
        axis.set_title(kind)
        axis.set_xlabel("tasks")
        axis.set_ylabel("seconds")
        axis.legend()
    figure.suptitle("Task count vs completion time")
    save(figure, "task_count_time.png")


def worker_chart(rows):
    tasks = max(row["tasks"] for row in rows)
    figure, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    for axis, kind in zip(axes, ("cpu", "io")):
        sequential = pick(rows, kind=kind, method="sequential", tasks=tasks)[0]
        axis.axhline(sequential["throughput"], color="C2", linestyle="--", label="sequential")
        for method in ("threads", "processes"):
            draw(axis, pick(rows, kind=kind, method=method, tasks=tasks), "workers", "throughput", method, COLORS[method])
        axis.set_title(kind)
        axis.set_xlabel("workers")
        axis.set_ylabel("tasks per second")
        axis.legend()
    figure.suptitle("Workers vs throughput")
    save(figure, "workers_throughput.png")


def speedup_chart(rows):
    tasks = max(row["tasks"] for row in rows)
    figure, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    for axis, kind in zip(axes, ("cpu", "io")):
        base = pick(rows, kind=kind, method="sequential", tasks=tasks)[0]["seconds"]
        util_axis = axis.twinx()
        for method in ("threads", "processes"):
            chosen = sorted(pick(rows, kind=kind, method=method, tasks=tasks), key=lambda row: row["workers"])
            workers = [row["workers"] for row in chosen]
            axis.plot(workers, [base / row["seconds"] for row in chosen], marker="o", color=COLORS[method], label=method + " speedup")
            util_axis.plot(workers, [row["cpu_util"] for row in chosen], marker="x", linestyle="--", color=COLORS[method], label=method + " cpu")
        axis.axhline(1, color="gray", linewidth=0.8)
        axis.set_title(kind)
        axis.set_xlabel("workers")
        axis.set_ylabel("speedup vs sequential")
        util_axis.set_ylabel("CPU utilization")
        handles, labels = axis.get_legend_handles_labels()
        more_handles, more_labels = util_axis.get_legend_handles_labels()
        axis.legend(handles + more_handles, labels + more_labels, fontsize=8)
    figure.suptitle("Speedup and CPU utilization vs workers")
    save(figure, "speedup_utilization.png")


def main():
    rows = load()
    task_count_chart(rows)
    worker_chart(rows)
    speedup_chart(rows)


if __name__ == "__main__":
    main()
