# CPU (Central Processing Unit)

**Module:** Stage 0 — Computer & Digital Foundation
**Topic:** How Computers Work

This lesson explains what a CPU is, why computers need it, how it executes instructions, and why it remains important in Data Engineering and AI Engineering.

---

## 1. What Is a CPU?

The **CPU (Central Processing Unit)** is the computer component responsible for executing program instructions. It processes information by performing operations such as addition, comparisons, and decisions.

A CPU is only one component of a computer. The complete computer also includes the motherboard, memory, storage, GPU, and other components that work together.

A program is a sequence of instructions. The CPU carries out those instructions to produce results.

---

## 2. Why Does a Computer Need a CPU?

Software contains instructions, but instructions cannot execute themselves. The CPU reads and carries out them.

Its main responsibilities are:

- **Computation:** Performing mathematical operations, such as `2 + 3`.
- **Decision-making:** Comparing values and choosing what happens next.
- **Control:** Managing the order of instructions, including repetitions and jumps.
- **Instruction execution:** Carrying out the instructions that make a program work.

This allows a general-purpose computer to run different applications without requiring new hardware for every program.

---

## 3. How Does a CPU Work Internally?

The CPU follows a simplified instruction-execution cycle:

1. **Fetch:** Obtains the next instruction.
2. **Decode:** Determines what the instruction requires.
3. **Execute:** Performs the operation and produces a result or changes what happens next.
4. **Repeat:** Continues with subsequent instructions.

For example, to calculate `5 + 3`, the CPU obtains the instruction, identifies the addition operation, performs it, and produces `8`.

Modern CPUs can overlap multiple instructions, use pipelines, and execute operations internally out of order while preserving the required program behavior. The basic cycle is a conceptual model, not a complete description of modern CPU implementation.

---

## 4. Two Important Parts of a CPU

- **Arithmetic Logic Unit (ALU):** Performs arithmetic operations and logical comparisons, such as addition and checking whether `10 > 5`.
- **Control Unit:** Coordinates instruction execution, identifies what needs to happen, and directs the appropriate CPU resources.

Modern CPUs may implement these responsibilities using multiple interacting structures rather than two physically separate blocks.

---

## 5. Why Does the CPU Matter in AI Engineering?

Even when an AI model runs on a GPU, the CPU remains important for:

- Running application logic and handling user requests.
- Preparing, cleaning, and reshaping data.
- Coordinating work between components and accelerators.
- Handling networking and API requests.
- Managing model-serving infrastructure, queues, and resources.
- Coordinating system operations and communication with the operating system.

A slow or overloaded CPU can become a bottleneck even when a powerful GPU is available.

---

## 6. Practical Linux Commands in WSL2

The lesson introduces safe, read-only commands for examining CPU information:

| Command | Purpose |
|---|---|
| `lscpu` | Displays CPU model, architecture, cores, threads, and other information. |
| `nproc` | Shows processing units available to the current process. |
| `cat /proc/cpuinfo` | Displays CPU information exposed by the Linux kernel. |
| `uname -m` | Shows the system's processor architecture. |
| `command -v lscpu` or `which lscpu` | Checks whether a command is available. |

> **WSL2 note:** Because Linux runs in a virtualized environment managed by Windows, reported CPU information may differ from the physical machine's specifications. Repeated entries in `/proc/cpuinfo` and unexpected `nproc` values can be normal.

---

## 7. Common Mistakes and Troubleshooting

Remember that:

- The CPU is not the entire computer.
- The CPU executes instructions; it is not permanent storage.
- Python source code is not directly executed as machine instructions. Its execution involves a runtime or interpreter and machine-level instructions.
- The CPU performs logical and control operations, not just arithmetic.
- Higher clock frequency (GHz) does not automatically mean better performance.
- More cores do not automatically make every program proportionally faster; the workload must be able to use them.

Actual CPU performance depends on clock frequency, architecture, instructions completed per cycle (IPC), available processing resources, workload characteristics, memory access, and software efficiency.

---

## 8. Exercises, Review, and Learning Roadmap

The module includes recognition, understanding, practical command, debugging, and integration exercises. These ask you to explain CPU concepts, inspect your system, interpret WSL2 output, trace `5 + 3` through the execution cycle, and explain why AI applications still depend on CPUs. The separate answer key should be consulted after attempting the questions.

The expected result is that you can explain the CPU's purpose, its instruction cycle, the ALU and control unit, basic CPU inspection commands, and performance limitations in your own words.

The review questions reinforce these concepts and encourage architectural reasoning, including why predictable instruction execution matters and why the "CPU is the brain" analogy is incomplete.

The next lessons cover cores, registers, cache, RAM, GPU, data movement, and performance. Instructions and machine code, compilation and interpretation, processes, and full program execution are also covered later.

---

## Main Takeaway

The CPU executes instructions, but a computer's overall performance depends on how the CPU works with the rest of the system. For AI Engineering, understanding this relationship helps you identify performance bottlenecks instead of assuming every slowdown requires a faster processor.
