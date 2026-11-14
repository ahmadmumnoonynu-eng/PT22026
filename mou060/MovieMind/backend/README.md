# MovieMind Backend

AI movie recommendation backend — FastAPI + PyTorch (NCF) + PostgreSQL.

Implementation plan: see [`backend_task.md`](../backend_task.md).
Model artifact audit: see [`ARTIFACTS.md`](ARTIFACTS.md).

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
