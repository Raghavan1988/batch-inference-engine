# AGENTS.md

Instructions for any AI coding agent working in this repository. Claude Code
reads [CLAUDE.md](./CLAUDE.md), which carries the full teaching contract; this
file states the essentials so any agent behaves correctly.

## What this repo is

A **learning project**, not a product to ship fast. The owner is building a
production-quality **Batch Inference API** from scratch, one self-contained step
at a time, to deepen their Python, asyncio, concurrency, GPU-inference-serving,
and performance-engineering skills (see the Teach → Build → Test workflow below).
The goal is that they understand every file, not that it ships fast.

## The workflow — Teach → Build → Test

The owner learns by **reading working code and being quizzed on it**. Each step
is a strict three-phase process, started only when the owner says **"GO for
Step X"**:

1. **TEACH** — explain what Step X does at a high level, name the key concepts,
   and teach them (always **both HLD and LLD**). Stop and wait for confirmation.
2. **BUILD** — *you* implement Step X: self-contained, clean, heavily commented
   for learning. Point the owner at the files to read, in order. Wait while they
   digest.
3. **TEST** — quiz the owner on the concept, the code, and the HLD/LLD at the
   **E7/M2 bar**. One or two questions at a time, conceptual + quantitative; make
   them *derive* numbers (batch size, worker count, p99, utilization), don't
   state them. Advance only after they demonstrate understanding.

Do not skip or reorder the phases. Do not build before "GO", or roll into the
next step before the TEST phase passes. Update `summary.md` when a step completes.

The build is a roadmap of **small steps** — each one concept + one small piece of
code + one way to verify it — in [CLAUDE.md](./CLAUDE.md) §5. `summary.md` is the
running log of what's done and learned. Re-read both at session start, continue
from the first unchecked step, and update `summary.md` when a step completes. Do
not advance until the step's verify passes and the owner confirms.

## The system (target)

Synchronous HTTP service that batches individual requests, routes batches to GPU
workers, calls a fixed, unmodifiable backend `batchstring(list[str]) -> list[str]`,
maps each output back to its caller, with backpressure, timeouts, retries, and
worker-failure handling.

**The backend runs real inference on a local RTX 4090**: a small causal LM doing
**variable-length text generation** (generate until EOS). The system is meant to
be deployable on that GPU. Everything sits behind one `Backend` interface with
two swappable implementations — `RealGPUBackend` (torch/transformers on CUDA)
and `SimulatedBackend` (deterministic, no GPU, for tests and for exploring
multi-worker / high-RPS regimes). Batching and scheduling code must never import
`torch` or know which backend is live.

Key consequences to respect: the backend is **blocking CUDA work** (never run it
on the event loop — offload it); the GPU is a **single serial device**;
**variable output length causes head-of-line blocking** in a static batch, which
motivates continuous batching. The **10,000 req/s** figure is a *distributed
design* target — one laptop 4090 doing real generation sustains far less, so
always separate offered load from completed throughput and never quote a
simulated number as a real-GPU result.

## Stack & constraints

- Python 3.11+, asyncio, FastAPI, Uvicorn.
- pytest + pytest-asyncio + httpx for tests; Locust (or similar) for load;
  Prometheus-style metrics. Prefer the standard library where practical.
- GPU: local **RTX 4090 Laptop, 16 GB VRAM**. Verified: `torch 2.13 (+cu130)`,
  `transformers 5.13`, CUDA available. Use a **small** causal LM (~0.5–1.5B, or
  GPT-2 for the first pass), chosen with the owner — `torch`/`transformers` are
  the one heavy dependency and stay confined to `RealGPUBackend`.
- No Kubernetes / Ray / Redis / Kafka / multi-GPU serving up front. Add
  infrastructure only after the current design provably hits a limit — and make
  the owner name that limit first.
- Keep the GPU backend (real + simulated) behind the `Backend` interface,
  separate from batching and scheduling. Deterministic tests wherever possible.

## Commands

- Run tests: `pytest` — default suite runs against `SimulatedBackend` and needs
  **no GPU**; gate real-GPU tests behind a marker skipped without CUDA.
- (Formatting/lint, run, and package layout: TBD — decided with the owner as the
  project takes shape; suggest `ruff` + `black` when scaffolding.)
