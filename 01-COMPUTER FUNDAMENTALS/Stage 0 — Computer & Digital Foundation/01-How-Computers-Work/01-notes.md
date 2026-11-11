# Motherboard and Buses

**Module:** Stage 0 — Computer & Digital Foundation
**Topic:** How Computers Work

This lesson explains how computer hardware components connect and communicate with each other, and why this matters for future Data Engineering and AI Engineering work.

---

## 1. What Are a Motherboard and Buses?

- **Hardware:** The physical parts of a computer that you can touch, such as chips, cables, and memory sticks.
- **Component:** An individual hardware part that performs a specific job, such as a processor, memory stick, or storage drive.
- **Motherboard:** The main printed circuit board (PCB) that holds and connects important computer components. It contains tiny copper pathways that carry electrical signals.
- **Bus:** A communication pathway, along with the rules that allow components to exchange data and coordination signals.

The motherboard is the physical foundation, while buses and other interconnects provide the communication pathways between components.

---

## 2. Why Do They Exist?

Computer components cannot work together effectively in isolation. For example, a storage drive can store data, but that data must reach the processor or memory when a program needs it.

Components need:

- **Connection:** A physical pathway between components.
- **Communication:** The exchange of meaningful signals.
- **Data movement:** The transfer of information from one location to another.
- **Control:** Signals that coordinate when and how operations happen.

Without communication pathways, the components would remain separate parts rather than functioning as one computer.

---

## 3. How Do They Work?

The motherboard contains sockets, slots, connectors, and electrical traces.

- **Socket:** Holds a specific chip, such as a processor.
- **Slot:** Accepts a card-shaped component, such as a memory stick or expansion card.
- **Connector:** Provides a general attachment point for a cable or component.
- **Chipset and controllers:** Help coordinate communication and input/output operations.

Traditionally, computer architecture used three categories of bus signals:

- **Data bus:** Carries the actual data.
- **Address bus:** Identifies the relevant memory location or resource.
- **Control bus:** Carries signals such as read, write, and timing instructions.

Modern computers also use dedicated point-to-point links and advanced interconnects. For example, PCI Express (PCIe) connects devices such as GPUs, NVMe SSDs, and network adapters to the rest of the system. These connections can use multiple lanes to increase data capacity.

---

## 4. Bandwidth vs. Latency

- **Bandwidth:** How much data a connection can transfer per unit of time.
- **Latency:** How long it takes data to travel from its source to its destination.

Think of a highway: bandwidth is how many cars can pass per minute, while latency is how long one car takes to reach its destination. High bandwidth does not automatically mean low latency.

---

## 5. Why This Matters for Data and AI Engineering

AI workloads often move large datasets, model weights, and input batches between storage, memory, CPUs, and GPUs.

Slow communication pathways can cause:

- GPUs to wait for data.
- Large datasets or models to load slowly.
- Multiple GPUs to spend time exchanging data rather than processing it.

Overall performance depends on the entire system, not just processor speed or motherboard quality. Data movement can be a major bottleneck, depending on the workload.

---

## 6. Practical Linux Commands in WSL2

The lesson introduces safe, read-only commands to inspect system information:

| Command | Purpose |
|---|---|
| `uname -a` | Shows Linux kernel and system information. |
| `lscpu` | Displays CPU information. |
| `lsmem` | Displays memory information. |
| `lsblk` | Lists storage devices and partitions. |
| `lspci` | Lists visible PCI/PCIe devices. |
| `command -v lspci` | Checks whether `lspci` is installed. |

> **Important:** WSL2 runs Linux in a virtualized environment managed by Windows. Therefore, some hardware details may be limited, virtualized, or different from native Linux. If `lspci` is missing, the `pciutils` package may need to be installed.

---

## 7. Common Mistakes and Troubleshooting

Remember these key points:

- The motherboard is not the CPU; it connects the CPU and other components.
- A bus is more than a single cable.
- The motherboard connects components but does not perform their main computations.
- Modern computers do not rely on one shared bus for everything.
- Bandwidth and latency are different measurements.
- Overall performance depends on several components working together.
- Differences between Windows and WSL2 hardware information are often expected because of virtualization.

The practical exercises ask you to identify hardware components, explain communication concepts, run Linux commands, investigate WSL2 hardware visibility, and reason about possible AI performance bottlenecks.

---

## 8. Connection to the Rest of the Roadmap

This is the first concept in Module 0.1, so it has no prerequisites. The next concepts introduce the CPU, cores, registers, cache, RAM, storage, and GPU. Later lessons build on these foundations to explain program execution.

By the end, you should be able to explain what a motherboard and buses do, how data and control signals travel, why bandwidth and latency differ, why hardware communication matters for AI workloads, and why WSL2 may not expose every physical hardware detail.

---

## Main Takeaway

A computer works as a complete system because its components can communicate. For Data Engineering and AI Engineering, understanding how data moves between hardware components is an important first step toward understanding performance bottlenecks in real-world systems.
