"""Model service layer.

Phase 2 stub: exposes model status for the readiness endpoint so the app can
report an honest, distinguishable state before the real loader (Phase 3) exists.
"""

from __future__ import annotations

from typing import Any


def get_model_status() -> dict[str, Any]:
    """Report the current state of the recommendation model.

    Returns a dict with at least:
    - ``status``: ``not_configured`` | ``loaded`` | ``unavailable``
    - ``loaded``: bool
    - ``version``: artifact/model version when known
    - ``reason``: short human-readable diagnostic when not loaded
    """
    return {
        "status": "not_configured",
        "loaded": False,
        "version": None,
        "reason": "Model loader is implemented in Phase 3 (see backend_task.md)",
    }
