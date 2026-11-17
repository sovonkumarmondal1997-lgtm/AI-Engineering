# Cache

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 9

---

## 1. What Is CPU Cache?

**CPU cache** is a small, very fast hardware memory located inside or close to the CPU. It temporarily stores recently or frequently needed data and instructions so the CPU does not have to wait as long for data from RAM.

Cache is different from a browser or application cache, which is managed by software.

---

## 2. Why Does Cache Exist?

The CPU executes instructions extremely quickly, but accessing RAM takes longer. If the CPU had to retrieve everything directly from RAM, it would spend more time waiting.

Cache reduces this delay by keeping useful data closer to the CPU.

A simplified memory hierarchy is:

```
Registers → L1 Cache → L2 Cache → L3 Cache → RAM → Persistent Storage
```

- **L1:** Generally the smallest and fastest cache.
- **L2:** Generally larger and slower than L1.
- **L3:** Generally larger and slower than L2.
- **RAM:** Much larger than cache but slower to access.

This hierarchy is a simplified model; not every CPU has exactly these three cache levels.

---

## 3. Cache Hits and Cache Misses

- **Cache hit:** The requested data is found in the cache being checked.
- **Cache miss:** The requested data is not found there, so the CPU looks at another cache level or RAM.

A cache miss is normal. It does not mean the program crashed, the data was lost, or something failed.

Cache is temporary, volatile memory. It can store both data and CPU instructions. Hardware primarily manages its contents; ordinary programs generally do not choose which cache level stores each value.

---

## 4. Locality: Why Cache Is Useful

Cache works effectively when programs access data in patterns that make reuse likely.

- **Temporal locality:** The same data is used repeatedly within a short period. Example: incrementing a counter several times.
- **Spatial locality:** Nearby memory locations are accessed close together. Example: processing `array[0]`, `array[1]`, `array[2]`, and `array[3]`.

Predictable, repeated access gives cache more opportunities to help than scattered, unpredictable access.

---

## 5. Practical Linux/WSL2 Commands

Use these read-only commands to inspect reported cache information:

```bash
uname -m
which lscpu
lscpu
lscpu | grep -i cache
ls -R /sys/devices/system/cpu/cpu0/cache/
```

To inspect cache levels, types, and sizes:

```bash
for d in /sys/devices/system/cpu/cpu0/cache/index*; do
    echo "== $d =="
    cat "$d/level"
    cat "$d/type"
    cat "$d/size"
done
```

> WSL2 may report information differently from the physical Windows host. These commands do not show live cache hits, misses, or actual program performance.

---

## 6. Common Mistakes and Troubleshooting

Remember that:

- Cache is not the same as RAM or permanent storage.
- L1 is generally faster than L2 and L3.
- More cache does not automatically make every program faster.
- Cache does not increase CPU clock speed or eliminate RAM access.
- A cache miss is routine, not a failure.
- If `lscpu | grep -i cache` shows nothing, try inspecting the `/sys/devices/system/cpu/cpu0/cache/` directory.

---

## 7. Exercises and Applied AI Relevance

The module includes exercises on recognition, understanding, applying cache hierarchy concepts, identifying locality, debugging misconceptions, and analyzing AI preprocessing and WSL2 observations.

The practical task is to inspect and record cache levels, sizes, and types in your own notes. Do not modify repository projects or attempt advanced cache benchmarking.

For Applied AI Engineers, cache concepts matter in numerical computation, array processing, data pipelines, preprocessing, and model inference. A workload may be **memory-bound** (limited by data access) rather than **compute-bound** (limited by computational capacity). Actual optimization and performance measurement are later topics.

---

## Next Concept

**Concept 10 — RAM**
