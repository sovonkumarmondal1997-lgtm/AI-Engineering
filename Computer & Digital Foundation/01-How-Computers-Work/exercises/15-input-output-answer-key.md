# Concept 15 — Input/Output — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../15-input-output.md`](../15-input-output.md), Section 14. Attempt every question yourself
> first, with your own worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. What is input?** Data entering a system or program.

**2. What is output?** Data leaving a system or program.

**3. What is I/O?** The general term for the movement of data between a computing system and an
external source or destination — input and output together.

**4. Example of device input.** A keyboard providing keystrokes (or mouse, microphone, camera).

**5. Example of device output.** A display showing an image (or speakers, a printer).

**6. Example of file input.** A program reading a dataset file (e.g., `input.csv`).

**7. Example of file output.** A program writing results to a file (e.g., `summary.txt`).

**8. Example of network input.** A server receiving a request from a client.

**9. Example of network output.** A server sending a response back to a client.

**10. What is stdin?** Standard input — the default source a program reads input from unless told
otherwise.

**11. What is stdout?** Standard output — the default destination a program writes its normal
output to.

**12. What is stderr?** Standard error — a separate default destination a program writes
error/diagnostic information to.

**13. What is a stream?** Data thought of as arriving or leaving over time, rather than all at
once as one complete block.

**14. What does "compute-bound" mean?** A workload whose overall speed is primarily limited by
CPU/GPU computation speed, not by I/O.

**15. What does "I/O-bound" mean?** A workload whose overall speed is primarily limited by how
long I/O operations take (waiting), not by computation.

---

## Level 2 — Understanding

**16. Why is input/output relative to a system boundary, rather than universal?** Because the
same piece of data is simultaneously "leaving" one component and "arriving" at another — whether
it's called input or output depends entirely on which component you're currently observing
(Section 2's keyboard→OS→application chain, and Section 9's client/server example, both
demonstrate this directly).

**17. Why is I/O different from computation?** Computation (the CPU executing instructions,
Concept 2) transforms data already available to it; I/O is the separate activity of moving data
across a system boundary, into or out of the system, so that computation has something to work
with in the first place, or so results can be delivered somewhere (Section 6).

**18. Why is I/O different from storage?** Storage (Concept 11) is a place persistent data
resides; I/O is the act of moving data into or out of a system boundary — reading from or writing
to storage happens *through* I/O operations, but storage itself is not I/O (Section 6's comparison
table).

**19. Why is I/O different from RAM?** RAM (Concept 10) is active, volatile working memory where
data is held during processing; I/O is the movement of data across a system boundary — data may
pass through RAM as part of an I/O operation, but RAM itself is a place, not an act of movement
(Section 6's comparison table).

**20. Why are stdout and stderr kept as separate streams?** So a program's normal results and its
error/diagnostic messages don't get mixed together indiscriminately — a tool consuming a program's
output can focus on stdout while error information remains separately available on stderr
(Section 10).

**21. Why can I/O become a bottleneck even when the CPU is fast?** Because I/O often involves
waiting for something external (a device, network, or slower storage) that is slower than the
CPU's execution speed — if a program spends a large proportion of its time waiting on I/O, the
CPU's raw speed doesn't matter as much to overall performance (Section 12).

**22. Why is "output" not the same as "something shown on the screen"?** Because output simply
means data leaving the system/component being observed — writing to a file, sending a network
response, or producing sound are all equally valid examples of output; the screen is only one
possible destination among many (Section 4's explicit correction).

**23. Why does synchronous I/O mean the program waits?** Because, by definition, synchronous I/O
means the program does not continue in the relevant execution flow until the I/O operation
completes — it blocks until the result (or completion) is available (Section 11).

**24. Why is asynchronous I/O generally more complex to reason about?** Because it requires
additional coordination mechanisms (this lesson does not teach them) to track what's happening
while other work continues, and to handle the eventual completion/notification — rather than the
simpler, linear "wait, then continue" flow of synchronous I/O (Section 11).

**25. Why do most real programs need both computation and I/O?** Because a program needs data to
compute with (input) and needs to deliver its results somewhere (output) — computation alone,
without any way to receive information or report results, would be useless in isolation (Section
1, Section 6).

---

## Level 3 — Application

**26. Exercise A — File-processing scenario (`input.csv` → total → `summary.txt`).**

- Reading `input.csv`: **file input** (Section 3, Section 7).
- Computing the total: **computation**, not I/O (Section 6) — this is the CPU processing data
  already available to it.
- Writing to `summary.txt`: **file output** (Section 4, Section 7).

**27. Exercise B — Terminal command reading piped text and printing a count.**

Two streams are involved: **stdin** (the piped text arriving as the command's input, Section 10)
and **stdout** (the count being printed as the command's normal output, Section 10). This directly
mirrors Section 13, Step 5's genuinely observed `printf ... | wc -l` example.

**28. Exercise C — User types a query, sees results on screen.**

Input: the typed query is **human input**, specifically **device input** via the keyboard (Section
3). Output: the displayed results are **screen/display output** (Section 4).

**29. Exercise D — Mobile app request/response, system-boundary reasoning.**

The request data is **output** from the mobile app's perspective (it is leaving the app) and
simultaneously **input** to the server's perspective (it is arriving at the server) — the same
underlying data, described differently depending on which component (app or server) is being
observed, exactly as Section 2 and Section 9 establish. There is no single, "correct," universal
label for this data independent of perspective.

**30. Exercise E — AI workload: dataset load, CPU/GPU processing, log write.**

- Loading the dataset from storage: **file input** (Section 7, Concept 11).
- CPU/GPU processing: **computation**, not I/O (Section 6, Concept 2, Concept 13).
- Writing evaluation results to a log file: **file output** (Section 7, Concept 14).

---

## Level 4 — Debugging

**31. A program is supposed to receive input from a file but appears to receive no data.**
At least two possible explanations: (1) the file path is wrong or the file doesn't exist at the
expected location (recalling Concept 14's path-reasoning exercises), so there's genuinely nothing
to read; (2) the file exists but is empty (zero bytes) — the program is correctly reading it, but
there's simply no data present. Both are plausible, distinct explanations that require checking
the actual file (e.g., with `ls`, `stat`, or `cat`, per Concept 14 and this lesson's Section 13)
rather than assuming the program's I/O logic itself is broken.

**32. A program's output appears in a file when the user expected to see it printed on the
screen.** This is a classic sign that the program's normal output (stdout) was **redirected** to a
file rather than displayed — as Section 13, Step 7 demonstrated genuinely (`echo ... > output.txt`),
redirecting stdout to a file is a deliberate, common operation; the program itself likely behaved
exactly as intended, it's simply that its output destination was a file rather than the screen.

**33. One user says a command "printed an error," another insists it "printed nothing unusual" —
how can both be describing the same event?** Because stdout and stderr are separate streams
(Section 10) — if the two users viewed the command's output differently (one seeing only stdout,
perhaps because stderr was redirected elsewhere or not visible to them; the other seeing the
combined terminal output including stderr), they could genuinely be looking at different pieces of
the same underlying event. Section 13, Step 4's genuinely observed example showed exactly how
stdout and stderr output can appear together but originate from distinct streams.

**34. A program appears to "hang" after starting — a plausible I/O-related explanation, without
assuming it's broken.** The program may be performing **synchronous I/O** (Section 11) and is
simply *waiting* for an I/O operation to complete — for example, waiting for user input via stdin
that hasn't been provided yet, or waiting on a slow file read or network response (Section 6, Section
12). This is not necessarily a malfunction; it may be entirely expected behavior for a program that
is blocked on I/O it hasn't yet received.

**35. A file read returns garbled-looking data instead of the expected neatly formatted data —
what should be checked first?** Using Concept 14's file-type reasoning: check whether the file
actually contains the expected format at all — for example, using `file` (Concept 14, this
lesson's Section 13) to verify its actual type, since a mismatched extension or an actually-binary
file being read as text would produce exactly this kind of garbled output (Concept 14,
Misconception 9's identical point).

**36. `output.txt` is empty after running a program meant to write results to it.** At least two
possible explanations: (1) the program encountered an error before reaching the write step (and
the error, if reported via stderr rather than causing a visible crash, might have gone unnoticed);
(2) the program's write logic ran but wrote zero bytes because the data it intended to write was
itself empty (e.g., an empty result from earlier processing) — the write operation succeeded, but
there was nothing meaningful to write.

**37. A learner assumes reading from a file must be "device I/O."** This is imprecise: file I/O
(Section 7) and device I/O (Section 8) are related but distinct categories in this lesson's
vocabulary — a file is a logical object managed by the filesystem (Concept 14), not itself a
hardware device. While the file's underlying data ultimately resides on a storage device (Concept
11, Concept 12), "file I/O" and "device I/O" are named as separate conceptual categories
specifically because interacting with a file (through the filesystem) is a different pattern than
interacting directly with a device like a keyboard or microphone.

**38. A learner classifies a heavy, CPU-only mathematical simulation with no file/network/device
interaction as "I/O-bound."** This is incorrect: I/O-bound specifically means a workload's overall
speed is primarily limited by I/O operation time (Section 12) — a workload with no file, network,
or device interaction at all has essentially no I/O to be limited by; its speed is determined
entirely by computation, making it a clear example of **compute-bound**, the opposite
classification.

---

## Level 5 — Integration / AI Engineering Reasoning

### Scenario A — End-to-end AI data movement

**39.** Tracing the full scenario:

```text
1. Read dataset file from storage       → file input (Section 7; Concept 11, Concept 12)
2. Load relevant data into RAM           → data becomes active working memory (Concept 10)
3. CPU + GPU computation                  → computation, not I/O (Concept 2, Concept 13; Section 6)
4. Write result to a log file              → file output (Section 7; Concept 14)
5. Send response over network               → network output (Section 9)
   (and, from the client's perspective, that same response is network input)
```

Every input/output step is explicitly identified above; the computation step (step 3) is
deliberately *not* I/O, per Section 6's explicit distinction — this is exactly the kind of
end-to-end reasoning Section 15's AI-relevance diagrams were built to support.

### Scenario B — Compute-bound or I/O-bound? (training script)

**40.** This scenario is **compute-bound**: the vast majority of running time is spent on matrix
computations already loaded into RAM (i.e., no repeated waiting on external I/O), with only a
brief file read at the start. Since the overall time is dominated by computation rather than
waiting on I/O, this matches Section 12's compute-bound definition directly.

### Scenario C — Compute-bound or I/O-bound? (contrast case)

**41.** This scenario is **I/O-bound**: the vast majority of running time is spent waiting to read
a very large dataset from a slow storage device, with only a small amount of computation once data
arrives — the overall speed is limited by I/O (waiting), not computation, matching Section 12's
I/O-bound definition directly. For this classification to flip, the workload's *shape* would need
to change — for example, if the dataset were much smaller (or already cached in fast memory) so
the read took negligible time, while the computation performed on it became substantially heavier,
shifting the dominant cost from waiting to computing.

### Scenario D — Model checkpoint loading

**42.**

- Reading the checkpoint file from storage: **file input** (Section 7), depending on Concept 11
  (persistent storage) and Concept 12 (the specific storage device's characteristics, e.g., HDD vs.
  SSD affecting how long this read takes).
- Loading into RAM: depends on Concept 10 (RAM as active working memory) — the checkpoint's data
  becomes available for use.
- GPU inference: **computation**, not I/O (Section 6), depending on Concept 13 (GPU architecture
  and its suitability for this kind of numerical work).
- Sending the inference result as a network response: **network output** (Section 9).

---

_This answer key covers Concept 15 (Input/Output) only. It does not contain, reference, or
anticipate answers for Concept 16 (Processes) or any later concept._
