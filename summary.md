# Progress summary — batch-inference-engine

A running log of what we've built and learned, step by step. See `CLAUDE.md`
(and `AGENTS.md`) for the full roadmap and the **Teach → Build → Test** workflow
we build by.

**Where we are:** Steps 0–1 done. Next up: **Step 2 — the blocking trap +
executors** (say `GO for Step 2`).

---

## ✅ Step 1 — asyncio basics (`scratch/lesson1.py`)

Ran the same 10×0.5s fake-inference workload two ways and timed it: **serial
5.01s vs concurrent (`gather`) 0.50s** — ~10× overlap on one thread.

**Ideas learned:**
- **Concurrency ≠ parallelism.** asyncio overlaps *waiting* on one thread; it
  helps I/O-bound work, does nothing for CPU-bound work (no extra cores).
- **`await` is the only yield point.** Cooperative scheduling: a task runs until
  it awaits. Swapping `await asyncio.sleep(0.5)` → `time.sleep(0.5)` blocks the
  loop's thread (no suspension point) → concurrency gone, back to ~5s. This is
  exactly why a synchronous GPU call must be offloaded (Step 2).
- **`gather` returns results in submission order, not finish order** — the
  **correlation invariant**: `results[i]` belongs to `inputs[i]`. Relying on
  finish order instead would misroute answers to the wrong caller (cross-talk),
  i.e. cross-tenant data leakage. Protected properly via index→`Future` in Step 6.
  Counterpart tool: `asyncio.as_completed` yields in *completion* order (right for
  "handle whichever finishes first", wrong for correlation).

## ✅ Step 0 — Setup

Project skeleton + isolated environment, verified by a green smoke suite.

- **Env (option A):** `.venv` created with `--system-site-packages` so it
  **inherits the base Anaconda `torch 2.13+cu130` + CUDA** (confirmed from inside
  the venv) — no multi-GB torch reinstall. Installed only the light deps
  (fastapi, uvicorn, pytest, pytest-asyncio, httpx) *into* the venv. Base
  `numpy` stayed 1.24.3 (<2), untouched.
- **Layout:** `app/` (service package), `tests/` (+ `conftest.py`), `scratch/`,
  `pyproject.toml`, `requirements.txt` / `requirements-dev.txt`, `.gitignore`.
- **Verify:** `pip install -e .` + `pytest` → **4 passed** (package import, async
  test wiring, a concurrency-overlap preview, and the real-4090 GPU check).

**Ideas learned:**
- **`--system-site-packages` = shadowing.** The venv's own site-packages wins
  over the inherited base ones; installs into the venv never touch base. *Danger:*
  the env is **not hermetic** — it inherits base's state, so an unrelated base
  change (e.g. numpy→2) can silently break torch here. Fine for a solo learning
  laptop; in prod you'd use a clean, fully-pinned container image instead.
- **Runtime vs dev deps** (`requirements.txt` vs `-dev.txt`). Shipping dev/test
  deps to prod = bigger **attack surface** (httpx/pip/locust are "living off the
  land" tools post-RCE) + **resolver instability** (a dev tool bumps a shared lib
  your service uses) + **slower cold starts** (hurts autoscale during overload).
- **GPU-free by default:** `conftest.py` auto-skips `@pytest.mark.gpu` tests when
  CUDA is absent, so the suite stays fast/CI-friendly; torch stays out of `app`
  except (later) the real GPU backend module.

## Files so far

```
CLAUDE.md             build rules + roadmap + Teach→Build→Test workflow (source of truth)
AGENTS.md             agent-agnostic companion
summary.md            this file — the running log
pyproject.toml        metadata + pytest(asyncio=auto, gpu marker) + ruff config
requirements.txt      runtime deps (fastapi, uvicorn); torch/transformers inherited from base
requirements-dev.txt  dev deps (pytest, pytest-asyncio, httpx)
.gitignore
app/__init__.py       the service package (no torch here)
tests/__init__.py
tests/conftest.py     auto-skip gpu tests without CUDA
tests/test_smoke.py   4 toolchain smoke tests
scratch/README.md     throwaway experiments go here
scratch/lesson1.py    Step 1 — serial vs concurrent asyncio demo
.venv/                local virtualenv (git-ignored)
```

## Next

**Step 2 — the blocking trap + executors:** demonstrate that a synchronous
`time.sleep`/CPU call freezes the event loop (kills the concurrency we just
measured), then fix it with `asyncio.to_thread` / `run_in_executor` so the loop's
thread stays free. This is the pattern the real blocking GPU `generate()` call
will need. Concepts: blocking vs awaitable, thread-pool offload, the GIL caveat.
