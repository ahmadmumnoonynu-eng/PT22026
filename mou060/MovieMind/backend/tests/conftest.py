"""Shared pytest fixtures.

Uses an in-memory-backed test settings profile so tests never touch the
configured production/development database.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
