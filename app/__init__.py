"""Batch Inference Engine.

A learning build of a dynamic request-batching inference service: individual
synchronous HTTP requests are aggregated into batches, run through a GPU backend
(a small causal LM on a local RTX 4090, or a deterministic simulator), and the
results are routed back to each original caller.

This package holds the *service* code. It must never import test-only or
scratch code, and — outside the real GPU backend module — it must never import
``torch``. See CLAUDE.md for the full architecture and build roadmap.
"""

__version__ = "0.0.0"
