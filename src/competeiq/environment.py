"""Runtime environment detection (Colab / Jupyter / plain Python)."""

from __future__ import annotations

import sys


def is_colab() -> bool:
    """Return True if executing inside Google Colab."""
    return "google.colab" in sys.modules


def is_jupyter() -> bool:
    """Return True if running under a Jupyter/IPython kernel."""
    try:
        from IPython import get_ipython  # type: ignore[import-not-found]
    except ImportError:
        return False
    ip = get_ipython()
    if ip is None:
        return False
    return ip.__class__.__name__ in {"ZMQInteractiveShell", "Shell"}


def is_local() -> bool:
    """Return True if running as a normal (non-Colab) Python process."""
    return not is_colab()


IN_COLAB: bool = is_colab()
IN_JUPYTER: bool = is_jupyter()
