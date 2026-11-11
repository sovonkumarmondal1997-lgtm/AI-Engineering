# Input/Output (I/O)

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 15

---

## 1. What Is Input/Output?

- **Input:** Data entering a program or system.
- **Output:** Data leaving a program or system.
- **I/O:** The movement of data between a system and an external source or destination.

Examples include typing on a keyboard, reading a file, receiving a network request, displaying results, and saving logs.

> **Important:** Input and output depend on the system boundary. A client's network request is output from the client but input to the server.

---

## 2. Types of Input and Output

**Input types:** Human input (keyboard, mouse, microphone, camera), file input, device input, sensor input, network input, and program/API input.

**Output types:** Screen display, file output, audio, printer, device, network output, and responses sent to other programs.

Output does not necessarily mean displaying something on a screen. Saving data to a file or sending a network response also counts as output.

---

## 3. How Data Flows Through a Computer

A simplified model is:

```
Input → Memory (RAM) → Processing (CPU/GPU) → Output
```

For example, a program reads a dataset, processes it, and writes the results to a file. Real systems may use additional stages, and not every operation follows this exact sequence.

- **CPU:** Executes instructions and performs computation.
- **RAM:** Holds active data while a program uses it.
- **Storage:** Keeps persistent data.
- **I/O:** Moves data across system boundaries. RAM and storage themselves are not I/O.

---

## 4. File, Device, and Network I/O

- **File I/O:** Reading, writing, or appending to files.
- **Device I/O:** Receiving data from or sending data to devices.
- **Network I/O:** Exchanging requests and responses between clients and servers.

These categories can overlap. For example, a server can receive network data and then save it to a file.

---

## 5. Streams and I/O Behavior

A **stream** represents data flowing over time.

- **stdin:** Standard input—a program's default input source.
- **stdout:** Standard output—normal program results.
- **stderr:** Standard error—diagnostic and error messages.

Keeping stdout and stderr separate helps programs process normal results without mixing them with errors.

- **Synchronous I/O:** The calling flow commonly waits for the operation to complete.
- **Asynchronous I/O:** An operation can be initiated while the program continues other work; completion is handled later.
- Blocking/non-blocking is related but not identical to synchronous/asynchronous behavior.

---

## 6. I/O Performance

- **Latency:** Delay before an operation completes or responds.
- **Throughput:** Amount of data transferred or work completed over time.
- **Bandwidth:** Data-transfer capacity of a pathway.
- **Bottleneck:** The resource or step limiting overall performance.
- **Compute-bound:** Performance is mainly limited by CPU/GPU computation.
- **I/O-bound:** Performance is mainly limited by data transfer or waiting.

A fast CPU cannot eliminate delays caused by slow storage, devices, or networks.

---

## 7. Practical Work, Exercises, and AI Relevance

The Linux/WSL2 practical section uses a temporary directory to observe stdout, stderr, stdin, file input/output, and basic commands such as `echo`, `ls`, `printf`, `wc`, `cat`, and `file`. It requires no `sudo`, internet access, or system-file changes. Example outputs may vary by environment.

The module includes 42 exercises covering definitions, comparisons, file/device/network scenarios, debugging, and AI-workload reasoning. Answers are in `exercises/15-input-output-answer-key.md`.

For AI engineering, I/O supports dataset loading, model-checkpoint loading, user requests, inference responses, and log writing. AI systems must not only compute; they must continuously receive, move, transform, and produce data.

**Scope boundaries:** Operating-system internals, process management, comprehensive command-line syntax, networking protocols, asynchronous implementation, detailed benchmarking, and ML framework internals are reserved for later topics.

---

## Next Concept

**Concept 16 — Processes**
