"""Step 0 smoke tests — prove the toolchain works end to end.

These assert nothing about the *service* (there is none yet); they only verify
that the environment, the package layout, async tests, and the GPU are all
wired correctly. If these pass, every later step starts from solid ground.
"""

import asyncio

import pytest

import app


def test_app_package_importable():
    """The editable install makes ``app`` importable from anywhere."""
    assert app.__name__ == "app"
    assert app.__version__ == "0.0.0"


async def test_async_test_runs():
    """``asyncio_mode = "auto"`` (pyproject.toml) runs this coroutine as a test
    without any decorator — the mechanism nearly every later test relies on."""
    await asyncio.sleep(0)
    assert True


async def test_concurrency_actually_overlaps():
    """A tiny preview of Step 1: two 0.1s sleeps run *concurrently* via gather,
    so the pair finishes in ~0.1s, not ~0.2s. Proves the event loop overlaps
    waits rather than running them back to back."""
    start = asyncio.get_event_loop().time()
    await asyncio.gather(asyncio.sleep(0.1), asyncio.sleep(0.1))
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed < 0.18, f"expected overlap (~0.1s), got {elapsed:.3f}s"


@pytest.mark.gpu
def test_cuda_backend_reachable():
    """Confirms the inherited torch/CUDA stack is reachable from inside the venv.
    Marked ``gpu`` → skipped automatically on a CPU-only machine (see conftest)."""
    import torch

    assert torch.cuda.is_available()
    assert "4090" in torch.cuda.get_device_name(0)
