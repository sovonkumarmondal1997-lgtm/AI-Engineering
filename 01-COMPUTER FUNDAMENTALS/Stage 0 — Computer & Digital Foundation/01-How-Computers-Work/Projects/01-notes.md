# Project 0.1.1 — Program Execution and GPU Audit

**Module:** Stage 0 — Module 0.1: How Computers Work

---

## 1. Purpose of the Project

This hands-on project teaches you two important concepts:

1. **Program execution:** What happens from typing a Python command in a terminal to seeing its output.
2. **GPU parallelism:** Why GPUs are useful for AI workloads involving large amounts of mathematical computation, such as tensor operations in neural networks.

These concepts help AI engineers understand slow programs, memory issues, CPU usage, and when GPU acceleration is worthwhile.

---

## 2. Prerequisites and Tools

You should understand the basics of CPUs, cores, registers, machine instructions, compilation and interpretation, cache, RAM, storage, GPUs, files, input/output, processes, and program startup.

Required tools:

- A terminal using Bash, Linux, macOS, WSL2, or PowerShell.
- Python 3.
- A text or Markdown editor.

You do not need a GPU, CUDA, Docker, or a cloud account. Work inside a dedicated practice folder and avoid unnecessary deletion commands or administrator privileges.

---

## 3. Practical Python Execution Audit

Create `execution_audit.py`, a small Python program that:

- Displays the interpreter path and Python version.
- Prints its process ID (PID) and working directory.
- Performs a repetitive calculation to create observable CPU activity.
- Writes a timestamp and PID to an output file.

Run it and investigate:

- **Interpreter:** Which Python executable runs your script?
- **Process:** What is its PID, and how does the operating system manage it?
- **CPU:** Why does CPU usage rise during the calculation and fall afterward?
- **RAM:** How much memory does the process use?
- **Working directory:** Where does the program create its output file?
- **Input/output:** How does terminal output differ from data saved to disk?

Use commands such as `pwd`, `python3 --version`, `which python3`, `ps`, `top`, `free` or system process-monitoring tools. Record actual observations in `findings.md`.

---

## 4. Compilation and Interpretation

Python source code is not directly executed by the CPU as written. The Python interpreter processes the source into an internal representation, such as bytecode in CPython, and executes it through the runtime. Python may cache compiled forms in `__pycache__`.

Explain this process in your own words and investigate what happens when you run the script again.

---

## 5. Why GPUs Help AI

A **tensor** is a structured collection of numbers, such as a list, matrix, or higher-dimensional array. Neural networks perform many repeated operations on these numbers.

- **CPU:** Has relatively few powerful, flexible cores, suited to branching, coordination, and sequential logic.
- **GPU:** Has many execution units suited to performing similar operations on different data elements in parallel.

The project uses a thought experiment involving 1,000 multiplication tasks to demonstrate why independent calculations can be split across many workers. GPUs can accelerate suitable AI training and inference workloads, but they are not automatically faster for every task.

---

## 6. Troubleshooting and Interview Preparation

The project covers common problems, including Python not being found, output files appearing in unexpected directories, processes finishing before inspection, and write-permission errors. Investigate one cause at a time.

Practise answering five interview questions about program execution, compilation versus interpretation, GPU acceleration, monitoring processes, and terminal output versus file output.

---

## 7. Final Deliverables and Completion Criteria

Your practice folder should contain:

- `execution_audit.py` — the annotated Python script.
- `findings.md` — your observations, explanations, and conclusions.
- Completed self-checklists and completion criteria.

Use the engineering workflow throughout:

```
Goal → Assumptions → Smallest experiment → Observe → Explain → Verify → Document
```

You finish when you have run the script yourself, verified its real process and resource activity, explained Python execution and GPU parallelism without notes, and answered all five interview questions aloud.

---

## Final Takeaway

This project connects computer fundamentals to practical AI engineering by teaching you to observe how software executes, investigate resource usage, and explain why GPUs suit parallel numerical workloads. It completes the audit evidence for Module 0.1 and prepares you to continue with the rest of Stage 0.
