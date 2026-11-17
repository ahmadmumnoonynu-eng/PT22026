# MovieMind Backend

AI movie recommendation backend — FastAPI + PyTorch (NCF) + PostgreSQL.

Implementation plan: see [`backend_task.md`](../backend_task.md).
Model artifact audit: see [`ARTIFACTS.md`](ARTIFACTS.md).

## Persistent authentication

Access tokens remain short-lived and in memory in the frontend. Refresh tokens
are opaque, rotated, and stored only as hashes in `refresh_sessions`; the raw
refresh value is sent in an HttpOnly cookie. The cookie is Secure in production.
CSRF protection is required for refresh and logout.

The refresh-session table requires a database migration. Review and apply it
explicitly during deployment with `alembic upgrade head`; application startup
does not run migrations.

Configure `CORS_ORIGINS` with the exact frontend origin(s). For a cross-site
frontend/API deployment (for example separate Vercel and API domains), set
`REFRESH_COOKIE_SAME_SITE=none`; production automatically enforces Secure
cookies. Browser third-party-cookie restrictions may still block cross-site
cookies, so a same-site custom domain or same-origin API proxy is preferable.

## Environment (pinned)

| Component | Version | Note |
| --- | --- | --- |
| Python | **3.15.1** | Only version installed on this machine; verified compatible |
| PyTorch | **2.15.0** (CPU wheel) | `pip install --dry-run torch` resolves for cp315 |

> Decision record: the spec preferred Python 3.11, but 3.15 is the only interpreter
> available here and `torch 2.15.0` resolves against it, so the environment is locked to
> **Python 3.15 + torch 2.15.0**. If a teammate runs a different Python version, adjust the
> torch pin via the official PyTorch selector.

## Status

Phase 1 (environment + artifact audit) in progress — see `backend_task.md` for the full plan.
