# Virtual Memory — Simple Summary

---

## 1. What is virtual memory?

**Virtual memory** is a system managed by the operating system and CPU hardware that gives every process its own private address space. A program uses virtual addresses, which are translated into actual physical addresses in RAM.

- **Virtual address:** Address used by a process.
- **Physical address:** Actual location in RAM.
- **Virtual address space:** Private range of addresses available to a process.
- **RAM:** Real physical working memory.

---

## 2. Why does virtual memory exist?

It provides:

- **Process isolation:** One process cannot normally access another process's private memory.
- **Memory protection:** Controls whether memory can be read, written, or executed.
- **Controlled allocation:** Memory can be assigned incrementally.
- **Efficient memory usage:** Physical memory can be shared or allocated flexibly.
- **Partial residency:** A process does not need all its mapped memory in RAM simultaneously.

---

## 3. Pages and page tables

Memory is divided into fixed-size chunks:

- **Page:** Chunk of virtual memory.
- **Page frame:** Corresponding-sized chunk of physical memory.
- **Page table:** Records which virtual pages map to which physical frames.
- **Page-table entry:** One mapping record.
- **Memory mapping:** Association between virtual addresses and physical resources.

A virtual address conceptually contains a page number and an offset. The page table identifies the physical frame; the offset identifies the exact location inside it. Hardware can cache recent translations using the **TLB**.

---

## 4. Page faults, swap, and protection

A **page fault** occurs when memory access requires OS intervention. It does not automatically mean a crash.

- **Normal page fault:** OS supplies or establishes the required mapping; execution continues.
- **Invalid access:** Address is unmapped or violates protection rules; the process may terminate.
- **Heavy memory pressure:** Frequent movement between RAM and swap can cause severe slowdowns.

**Swap** uses storage to hold pages not currently in RAM. It increases capacity but is much slower than RAM. Excessive swapping is called **thrashing**.

Memory protection provides:

- **Readable:** permission to read.
- **Writable:** permission to modify.
- **Executable:** permission to run instructions.

---

## 5. Processes, threads, and Python

Separate processes generally have separate virtual address spaces. Threads within one process share that process's address space, which explains why shared-memory race conditions can occur.

Python objects also consume memory overhead. A list's memory usage is not simply its element count multiplied by the size of one primitive value.

---

## 6. Practical Linux observations

The lesson demonstrates:

- `free -h`: RAM and swap overview.
- `/proc/meminfo`: Kernel memory statistics.
- `ps`: Process memory information.
- `/proc/<PID>/status`: Detailed process memory values.
- `/proc/<PID>/maps`: Memory regions and permissions.
- `top`: Live memory and CPU information.
- `htop`: Not installed in the lesson environment.

Important measurements:

- **VSZ/VIRT:** Virtual memory size.
- **RSS/RES:** Memory currently resident in physical RAM.

The example showed VSZ of 83,856 KB versus RSS of 8,020 KB. A large virtual size does not automatically mean high RAM usage.

---

## 7. Misconceptions and troubleshooting

The file addresses 10 misconceptions and five debugging scenarios: growing memory usage, large VSZ but smaller RSS, severe slowdown from swap, invalid memory access, and multiple inference workers loading separate model copies.

It includes 37 exercises across five levels, expected results, and review questions covering definitions, mechanisms, Linux commands, Python memory, and AI engineering.

---

## 8. Production relevance

Virtual memory helps engineers understand:

- Model-serving memory requirements.
- Why multiple worker processes multiply model memory demand.
- Out-of-memory failures.
- Memory leaks versus legitimate memory growth.
- Swap-related performance degradation.
- Process isolation and reliability.
- Capacity planning for AI services.

**Key takeaway:** Virtual memory is not RAM. It is the addressing and protection system that manages how processes use memory. Understanding virtual memory, resident memory, and swap is essential for diagnosing production AI service performance and memory problems.

**Next:** Filesystems (Concept 07), followed by permissions, environment variables, signals, standard I/O, pipes, shell, and process lifecycle. Advanced kernel internals, TLB architecture, NUMA, huge pages, container/Kubernetes memory management, and GPU memory architecture are outside this lesson's scope.
