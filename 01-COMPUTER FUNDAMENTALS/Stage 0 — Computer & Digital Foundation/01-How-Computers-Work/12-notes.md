# HDD vs. SSD

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 12

---

## 1. What Are HDD and SSD?

- **HDD (Hard Disk Drive):** Stores data magnetically on spinning platters. A mechanical arm moves a read/write head to access data.
- **SSD (Solid-State Drive):** Stores data electronically in non-volatile flash memory chips. It has no spinning platters or moving read/write arm.

The fundamental difference is mechanical access in HDDs versus electronic access in SSDs. Both are persistent storage devices, unlike volatile RAM.

---

## 2. How They Work

- **HDD:** Application requests data → operating system → HDD controller → mechanical positioning → magnetic data access → data returned.
- **SSD:** Application requests data → operating system → SSD controller → flash-memory access → data returned.

The absence of mechanical positioning generally gives SSDs lower access latency, especially for scattered, small-file operations.

---

## 3. Performance and Physical Differences

| Feature | HDD | SSD |
|---|---|---|
| Technology | Magnetic | Electronic flash memory |
| Moving parts | Yes | No |
| Access latency | Generally higher | Generally lower |
| Random access | Generally weaker | Generally stronger |
| Sequential access | Often suitable for large transfers | Generally strong |
| Noise | May produce mechanical noise | Usually silent |
| Shock resistance | Generally lower | Generally higher |
| Cost per capacity | Historically lower | Historically higher |
| Failure risk | Includes mechanical risks | Can fail electronically or through wear |

These are general tendencies, not guarantees. Both technologies vary by device, controller, interface, workload, and implementation. Power consumption, heat, and durability also vary.

---

## 4. Important Performance Terms

- **Random access:** Reading data from scattered locations.
- **Sequential access:** Reading data in an ordered, continuous pattern.
- **Latency:** Delay associated with an individual operation.
- **Throughput:** Amount of data transferred over time.
- **IOPS:** Number of input/output operations per second.

HDDs are particularly affected by random access because the mechanical head may need to reposition. Sequential access usually reduces this disadvantage.

More capacity does not automatically mean better performance. Capacity, latency, throughput, access pattern, and cost are separate considerations.

---

## 5. Practical Applications in AI Engineering

- **SSD:** Operating systems, Python environments, development tools, frequently accessed datasets, model loading, and repeatedly loaded checkpoints.
- **HDD:** Large archives, backups, and datasets accessed infrequently where capacity and cost matter more than responsiveness.
- **Both:** An AI workstation may combine SSD responsiveness with HDD capacity.

Datasets, model files, checkpoints, logs, and generated artifacts all require persistent storage. The best choice depends on the workload and how frequently data is accessed.

---

## 6. Common Mistakes

Do not assume that:

- SSD is faster RAM or cannot fail.
- HDDs are obsolete or only store certain file types.
- Every SSD or HDD has identical performance.
- More storage capacity guarantees faster performance.
- Sequential and random access are equivalent.
- An SSD's lack of moving parts makes its data unchangeable.
- WSL2 device information always identifies the host's physical drive.

---

## 7. Practical Linux/WSL2 Tasks

| Command | Purpose |
|---|---|
| `uname -a` | Inspect the Linux environment. |
| `lsblk` | View visible block devices. |
| `df -h` | Inspect filesystem capacity and usage. |
| `lsblk -o NAME,SIZE,TYPE,ROTA,MODEL` | Inspect device fields, including rotational status and reported model. |

> WSL2 may expose virtualized devices. `ROTA` and `MODEL` are not definitive proof of the physical host's HDD/SSD technology; `/mnt/c` identifies a Windows filesystem mount, not a storage technology.

The module includes 49 exercises, an AI-engineering decision exercise, review questions, interview/architecture questions, and a practical observation task. Use read-only commands only; do not benchmark storage or modify the `project/` directory.

**Scope boundary:** HDD/SSD internals, storage protocols, filesystem internals, cloud/distributed storage, and advanced performance engineering are deferred to later topics.

---

## Next Concept

**Concept 13 — GPU**
