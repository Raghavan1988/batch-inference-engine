"""Shared pytest configuration.

The whole test suite must run **without a GPU** by default, so that tests stay
fast, deterministic, and runnable in CI. Tests that genuinely need CUDA are
marked ``@pytest.mark.gpu`` (the marker is declared in pyproject.toml). This
hook auto-skips those marked tests whenever CUDA is unavailable, instead of
letting them error out.

On this machine CUDA *is* available, so the gpu-marked tests will actually run;
on a CPU-only box (or CI) they are skipped with a clear reason.
"""

import pytest


def _cuda_available() -> bool:
    # Import torch lazily and defensively: on a box without torch at all, the
    # import itself would raise, and "no CUDA" is the correct conclusion.
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if _cuda_available():
        return  # GPU present: let gpu-marked tests run normally.
    skip_gpu = pytest.mark.skip(reason="no CUDA GPU available")
    for item in items:
        if "gpu" in item.keywords:
            item.add_marker(skip_gpu)
