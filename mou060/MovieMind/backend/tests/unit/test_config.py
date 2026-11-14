"""Unit tests for app.core.config (T2.1 acceptance criteria)."""

from __future__ import annotations

import pytest

from app.core.config import Settings, get_settings


def test_defaults_are_development_safe():
    s = Settings(APP_ENV="development", _env_file=None)
    assert s.APP_ENV == "development"
    assert s.API_V1_PREFIX == "/api/v1"
    assert s.MODEL_DEVICE == "cpu"


def test_cors_origins_parsed_and_normalized():
    s = Settings(CORS_ORIGINS="http://localhost:5173, http://127.0.0.1:5173/", _env_file=None)
    assert s.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]


def test_cors_wildcard_rejected():
    with pytest.raises(ValueError):
        Settings(CORS_ORIGINS="*", _env_file=None)


def test_api_prefix_must_start_with_slash():
    with pytest.raises(ValueError):
        Settings(API_V1_PREFIX="api/v1", _env_file=None)


def test_production_fails_fast_on_dev_secret():
    s = Settings(
        APP_ENV="production",
        SECRET_KEY="dev-only-secret-change-me",
        DATABASE_URL="postgresql+psycopg://x@localhost/db",
        _env_file=None,
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        s._enforce_production_safety()


def test_production_passes_with_real_secret():
    s = Settings(
        APP_ENV="production",
        SECRET_KEY="a" * 32,
        DATABASE_URL="postgresql+psycopg://x@localhost/db",
        _env_file=None,
    )
    s._enforce_production_safety()  # must not raise


def test_get_settings_cached():
    assert get_settings() is get_settings()
