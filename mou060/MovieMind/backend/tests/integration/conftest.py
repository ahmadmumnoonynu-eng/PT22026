"""Integration test fixtures.

Tests in this directory run against a real PostgreSQL database (the dev/Neon
database configured via ``DATABASE_URL``). Every test uses a transactional
fixture that flushes but never commits, so no test data persists.

The whole directory is skipped when the database is unreachable.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_engine


def _db_available() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 — any failure means "skip"
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")


@pytest.fixture
def db() -> Session:
    """Session bound to an uncommitted connection; rolled back after each test."""
    connection = get_engine().connect()
    session = Session(bind=connection, expire_on_commit=False, autoflush=False)
    try:
        yield session
        session.rollback()
    finally:
        session.close()
        connection.close()
