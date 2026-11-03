"""Step 1 — asyncio basics: make the event loop's concurrency visible.

We run the same fake "inference" workload two ways and time each:

    serial     : await the calls one after another   -> ~N * 0.5s
    concurrent : schedule them all, then await all    -> ~0.5s

The gap between the two numbers *is* the event loop overlapping waits on a
single thread. Nothing here touches a GPU or the network — the point is purely
to see cooperative concurrency behave.

Run it:   .venv/bin/python scratch/lesson1.py
"""

import asyncio
import time

# How many concurrent "requests" to simulate, and how long each one "waits".
N = 10
INFER_SECONDS = 0.5


async def fake_infer(prompt: str) -> str:
    """Pretend to run one inference.

    `await asyncio.sleep(...)` is a *non-blocking* wait: it SUSPENDS this
    coroutine and hands control back to the event loop, which is then free to
    run other ready coroutines. Contrast with `time.sleep(0.5)`, which would
    block the single thread and freeze every other task — the trap we study in
    Step 2. Returning the prompt in the result lets us prove, later, that each
    answer maps back to its own input.
    """
    await asyncio.sleep(INFER_SECONDS)
    return f"result:{prompt}"


async def run_serial(prompts: list[str]) -> list[str]:
    """Await each call before starting the next → no overlap.

    Each `await` here waits for THIS call to finish before the loop moves on,
    because we don't hand it the next coroutine until the current one returns.
    Total time ≈ N * INFER_SECONDS.
    """
    results: list[str] = []
    for p in prompts:
        results.append(await fake_infer(p))
    return results


async def run_concurrent(prompts: list[str]) -> list[str]:
    """Schedule all calls, then await them together → full overlap.

    `asyncio.gather` wraps each coroutine in a Task (scheduling it on the loop
    to run concurrently) and waits for all of them. While any one call is parked
    inside its `await asyncio.sleep`, the others are making progress on the same
    thread. Total time ≈ one INFER_SECONDS, not N of them.

    Key detail for later: gather returns results in the ORDER THE COROUTINES
    WERE PASSED, regardless of which finished first. That stable ordering is how
    we'll keep each caller matched to its own result (Step 6).
    """
    return await asyncio.gather(*(fake_infer(p) for p in prompts))


async def _timed(label: str, coro) -> list[str]:
    """Await `coro`, printing how long it took in wall-clock seconds."""
    start = time.perf_counter()
    results = await coro
    elapsed = time.perf_counter() - start
    print(f"{label:<12} {elapsed:6.3f}s  for {len(results)} calls")
    return results


async def main() -> None:
    prompts = [f"p{i}" for i in range(N)]

    print(f"Running {N} fake inferences of {INFER_SECONDS}s each.\n")

    serial_results = await _timed("serial", run_serial(prompts))
    concurrent_results = await _timed("concurrent", run_concurrent(prompts))

    # Correctness: same answers both ways, and each result maps to its prompt.
    assert serial_results == concurrent_results
    assert concurrent_results[3] == "result:p3"

    speedup = N  # ideal: serial is ~N× the concurrent time
    print(
        f"\nSerial does the waits back-to-back (~{N * INFER_SECONDS:.1f}s); "
        f"concurrent overlaps them (~{INFER_SECONDS:.1f}s) — up to ~{speedup}x,\n"
        "all on ONE thread. That overlap is the whole reason the front door is async."
    )
    print(f"\nSample result for 'p3': {concurrent_results[3]!r} (ordered, not by finish time)")


if __name__ == "__main__":
    # asyncio.run creates the event loop, runs main() to completion, closes it.
    asyncio.run(main())
