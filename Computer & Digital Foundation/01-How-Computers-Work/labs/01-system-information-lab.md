# Lab 0.1.1 — System Information Lab

**Status:** Not Started
**Concepts exercised:** Motherboard & Buses, CPU, Cores, RAM, Storage, GPU

## Objective

Identify the real hardware inside the learner's own machine (or WSL2 host) using basic
inspection tools, and connect what is found to the concept files already read, without writing
any code.

## Prerequisites

- Concept files 1–3 and 9–13 read (Motherboard & Buses, CPU, Cores, Cache, RAM, Storage,
  HDD vs SSD, GPU).
- A terminal on Linux, Ubuntu, or WSL2.

## Commands/tools required

- `lscpu`
- `lsblk`
- `free -h`
- `lspci` (or Windows Device Manager, if inspecting the WSL2 host from Windows)
- `nvidia-smi` (only if a GPU with NVIDIA drivers is present — optional)

## Procedure outline

1. Run `lscpu` and locate: CPU model name, number of cores, number of threads, cache sizes.
2. Run `free -h` and locate: total RAM, used RAM, available RAM.
3. Run `lsblk` and locate: attached storage devices and their sizes.
4. Run `lspci | grep -i vga` (or equivalent) to identify the GPU, if any.
5. If an NVIDIA GPU is present, run `nvidia-smi` and note VRAM size.

## Observations to record

- CPU model, core count, thread count, cache sizes (L1/L2/L3 if shown).
- Total installed RAM.
- Storage device name(s) and capacity.
- GPU model (or confirmation that none is present/exposed to this environment).

## Expected learning outcome

The learner can point to a specific number or name from their own machine for each hardware
concept covered so far (CPU, cores, RAM, storage, GPU), replacing the abstract concept with a
concrete, personally-verified fact.

## Troubleshooting

- **WSL2 does not expose full hardware info:** note this as an observation itself (WSL2 is a
  virtualized environment) rather than treating it as a failure — this connects directly to later
  Module 0.2 concepts (kernel/user space, virtualization).
- **`nvidia-smi` not found:** acceptable — record "no NVIDIA GPU detected in this environment" as
  a valid observation.
- **Permission errors:** most of these commands do not require `sudo`; if one does, note which
  one and why (this previews Module 0.2's permissions concept).

---

_This is a lab specification prepared during repository setup. No lab has been performed yet._
