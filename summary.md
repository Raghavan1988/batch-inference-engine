# Progress summary — batch-inference-engine

A running log of what we've built and learned, step by step. See `CLAUDE.md`
(and `AGENTS.md`) for the full roadmap and the rules we build by.

**Where we are:** Nothing built yet. Warming up on **Step 1 — asyncio basics**
(the `fake_infer` + `gather` exercise). **Step 0 — Setup is still pending** — we
jumped into the concurrency warm-up first; we'll lay down the venv + `app/`
package before the service skeleton (Step 4/5).

---

<!--
Fill one ✅ section per completed step, in this shape:

## ✅ Step N — Title (`path/touched.py`)

One or two lines on what we built and how we verified it.

**Ideas learned:**
- key idea, with the "why" and the alternative we rejected
- ...

**Design decisions made explicit:**
- decision → reason

Keep the "Where we are" line at the top current, and tick the box in CLAUDE.md §5.
-->

## ⏳ Step 1 — asyncio basics (in progress)

Exercise: `scratch/lesson1.py` — run 10 `fake_infer` coroutines concurrently and
show the 10 overlapping 0.5 s "inferences" finish in ≈0.5 s, not 5 s.

*To capture once done:* why one thread beats synchronous here (the event loop
runs other ready tasks during each `await`); and the one blocking line that would
kill the benefit (a sync call with no `await` — the seed of why the real GPU
backend must be offloaded, Step 2).

## Files so far

```
CLAUDE.md    the build rules + roadmap (source of truth)
AGENTS.md    agent-agnostic companion
summary.md   this file — the running log
README.md    project intro (stub)
```

## Next

**Step 0 — Setup** (venv + `app/` + `tests/` layout), then continue the
fundamentals warm-up (Steps 2–3) before the service skeleton.
