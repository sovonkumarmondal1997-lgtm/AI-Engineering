# CPU Scheduling — Simple Summary

CPU scheduling is how the operating system decides which runnable process or thread gets to use the CPU, when, and for how long. The kernel component making these decisions is called the **scheduler**.

---

## 1. Why scheduling is necessary

A CPU has limited execution capacity. If a computer has 2 CPU cores but 6 runnable threads, only 2 can execute simultaneously. The others must wait for their turn.

- **Runnable:** Ready to execute, waiting for CPU time.
- **Running:** Currently executing on a CPU.
- **Waiting/blocked:** Waiting for something such as a file, network response, or database operation.
- **Preemption:** The OS interrupts a running task and gives CPU time to another task.

---

## 2. Why it matters to AI engineers

Python AI services share CPU resources with other applications and background jobs. CPU scheduling affects API latency, throughput, worker performance, preprocessing, and GPU utilization. Even GPU-based applications need CPU time for data preparation, memory transfers, and orchestration.

---

## 3. How scheduling works

The scheduler repeatedly:

1. Identifies runnable tasks.
2. Selects a task according to its scheduling policy.
3. Allows the CPU to execute it.
4. Makes another decision when the task waits, finishes, yields, or is interrupted.

Policies may consider priority, fairness, CPU availability, workload behavior, and latency. Real schedulers do not simply select the oldest task or give every task exactly equal time.

**Context switching** means saving one task's execution state and restoring another's so it can continue. It happens between processes or threads, including threads in the same process. It has overhead, so excessive switching wastes CPU time.

---

## 4. Important performance concepts

- **Concurrency:** Multiple tasks make progress over time by sharing CPU time.
- **Parallelism:** Multiple tasks execute simultaneously on separate hardware execution resources.
- **CPU-bound:** Work dominated by computation, such as data transformation.
- **I/O-bound:** Work dominated by waiting, such as network or database requests.
- **Fairness:** Runnable tasks receive meaningful opportunities to execute.
- **Starvation:** A task waits excessively because other tasks keep getting selected.
- **Throughput:** Total work completed per unit of time.
- **Latency:** Time taken for an individual operation. Batch inference often prioritizes throughput; online inference prioritizes low latency.

---

## 5. Python and Linux

The OS scheduler schedules OS-managed threads and processes, not Python functions. Python's GIL is separate: traditional GIL-enabled CPython restricts Python bytecode execution to one thread at a time per interpreter. Free-threaded Python builds can disable the GIL.

The lesson demonstrates CPU scheduling using `nproc`, `lscpu`, `ps`, and `top`. Its WSL2 environment reported 8 logical CPUs. Two bounded CPU-heavy Python processes each reached approximately 100% CPU, demonstrating parallel execution. `htop` was unavailable, but the other tools were sufficient.

---

## 6. Misconceptions and troubleshooting

The lesson corrects 19 misconceptions, including that every process gets a core, waiting processes continuously consume CPU, more workers always improve performance, and high CPU automatically means a bug.

Seven debugging scenarios cover high CPU, API latency during background jobs, worker contention, low CPU usage, Python threading without speedup, inconsistent CPU measurements, and apparently stuck tasks. The key is distinguishing active computation, normal waiting, and abnormal blocking.

---

## 7. Exercises, outcomes, and production relevance

The file includes 37 exercises across five levels: recognition, understanding, practical commands, debugging, and production integration. Review questions test scheduling, states, concurrency, fairness, Python, AI workloads, and troubleshooting.

The expected outcome is being able to explain scheduling, inspect CPU usage, interpret task states, and reason about performance trade-offs.

**Production takeaway:** Correct code does not automatically mean a fast service. CPU capacity, scheduling, worker contention, and workload type also determine production performance.

**Next:** Virtual Memory (Concept 06), followed by filesystems, permissions, environment variables, signals, I/O, pipes, shell, and process lifecycle. Advanced scheduler algorithms, NUMA, CPU affinity, synchronization internals, container CPU limits, Kubernetes scheduling, and GPU scheduling are outside this lesson's scope.
