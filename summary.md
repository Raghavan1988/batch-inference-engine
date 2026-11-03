# Progress summary — batch-inference-engine

A running log of what we've built and learned, step by step. See `CLAUDE.md`
(and `AGENTS.md`) for the full roadmap and the **Teach → Build → Test** workflow
we build by.

**Where we are:** Step 0 done. Next up: **Step 1 — asyncio basics** (say
`GO for Step 1`).

---

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
.venv/                local virtualenv (git-ignored)
```

## Next

**Step 1 — asyncio basics:** build `scratch/lesson1.py` — run N `fake_infer`
coroutines concurrently with `gather` and show 10×0.5s "inferences" finish in
≈0.5s, not 5s. Concepts: the event loop, `await` as a yield point, cooperative
scheduling — and the one blocking line that would wreck it (the seed of why the
real GPU call must be offloaded, Step 2).
