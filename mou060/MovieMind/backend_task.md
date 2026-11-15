# MovieMind Backend — Implementation Task Plan

**Status:** Draft for owner review — do not implement until approved.
**Source spec:** `backend_spec.md` (v1, 2026-11)
**Backend language:** Python · **API:** FastAPI · **ML:** PyTorch · **DB:** Neon PostgreSQL · **ORM:** SQLAlchemy 2.x + Alembic
**Dev OS:** Windows 11 (PowerShell) · **Frontend:** React + TypeScript + Vite (separate app)

---

## 0. Repository inspection findings (as of task planning)

The repository already contains partial scaffolding and the real model artifacts:

```
MovieMind/
├── backend/
│   ├── app/
│   │   ├── main.py                 (empty)
│   │   ├── api/                    (empty dir)
│   │   ├── core/config.py          (empty)
│   │   ├── ml/model_architecture.py (contains MovieMindNCF class — matches notebook)
│   │   ├── services/model_service.py (empty)
│   │   └── ...
│   └── artifacts/                  (real model bundle, present locally)
├── frontend/                       (separate React app — out of scope here)
├── ML/notebooks/MovieMind.ipynb    (training notebook)
└── .gitignore                      (partial — see Phase 1 gap)
```

### Actual artifact bundle (must be treated as source of truth, not the spec's "expected" names)

| Spec expected | Actual present | Notes |
| --- | --- | --- |
| `config.json` | `model_config.json` | Loader must read the **actual** name. Contains `num_users=610`, `num_movies=9724`, `embedding_dim=32`, `mlp_hidden_dims=[128,64,32]`, `dropout=0.1`, `rating_min=0.5`, `rating_max=5.0`, `model_version="1.0.0"`. |
| `moviemind_ncf.pt` | `moviemind_ncf.pt` | **state_dict-only** checkpoint (raw tensor keys, no wrapper dict, no extra metadata). |
| `user_mapping.json` | `user_mapping.json` | `{raw MovieLens user ID: index}` — e.g. `{"1": 0, "2": 1, ...}`. |
| `movie_mapping.json` | `movie_mapping.json` | `{raw MovieLens movie ID: index}` — indices up to `9723`. |
| `movies.json` | `movies.json` | List of `{movieId, title, genres}`. `genres` is a **`|`-separated string**. No overview / year / poster. |
| `training_metrics.json` | **MISSING** | Loader must tolerate absence; report metrics unavailable until provided. |
| `model_architecture.py` (in artifacts) | MISSING (class lives in `app/ml/`) | Use the notebook reference to verify parity. |
| `inference_example.py` / README | MISSING | Derive inference contract from notebook (Phase 3). |

### Key implications already factored into the plan
1. **Model architecture** is the GMF+MLP NCF already reproduced in `app/ml/model_architecture.py` (2×GMF embeddings, 2×MLP embeddings, MLP `128→64→32` with ReLU+Dropout, final concat `[gmf; mlp_vector]` → Linear(64,1)). It must be re-verified against the notebook's `MovieMindNCF` (notebook lines ~694 and ~1525).
2. The checkpoint is a **state_dict**, so loading is `model.load_state_dict(torch.load(..., map_location="cpu", weights_only=True))`.
3. **Config filename mismatch** and the missing `training_metrics.json` must be handled explicitly (no hardcoded `config.json`).
4. `movies.json` has no posters/overviews — those fields are nullable and require an approved provider (open decision #4).
5. `.gitignore` currently ignores `*.pt`/`*.pth`/`*.ckpt` and `.env`, but **not** `backend/artifacts/*.json` or the whole `artifacts/` dir — must be fixed to prevent committing model artifacts/dataset.

---

## 1. How to read this plan

- Tasks are **ordered**; each states **Purpose**, **Files/modules**, **Implementation details**, **Dependencies**, and **Acceptance criteria**.
- Priority labels: **[Must have]** = required for first release, **[Should have]** = expected but deferrable, **[Later]** = post-release.
- Every checkbox is independently verifiable. Check it only when the acceptance criteria actually pass.
- Open decisions that need owner sign-off are collected in §4 and are **not** silently decided in the tasks.

---

## 2. Phase overview

| Phase | Name | Priority |
| --- | --- | --- |
| P1 | Repository, environment & artifact audit | Must have |
| P2 | Backend foundation (config, logging, errors, app shell) | Must have |
| P3 | Model artifact validation & NCF inference | Must have |
| P4 | Database foundation (SQLAlchemy + Alembic + schema) | Must have |
| P5 | Movie catalogue & data import | Must have |
| P6 | Authentication & users | Must have |
| P7 | Ratings & watchlist | Must have |
| P8 | Recommendation services (NCF demo → popularity → content-based) | Must have (staged) |
| P9 | API hardening (CORS, errors, rate limits, ops endpoints) | Must have |
| P10 | Testing & quality (unit/integration/contract/model) | Must have |
| P11 | Docker & deployment preparation | Should have |
| P12 | Documentation & handover | Must have |

**Definition of done (overall)** — see §5.

---

## 3. Task list

### Phase 1 — Repository, environment & artifact audit

- [x] **T1.1 Record the environment** **[Must have]**
  - **Purpose:** Lock the Python/PyTorch baseline before writing code.
  - **Details:** Run `py --version` and `py -3.11 -m venv .venv` to confirm a Python version compatible with the chosen PyTorch CPU wheel. Pin Python (3.11 recommended) and document the exact PyTorch version selected via the official selector.
  - **Files:** `backend/README.md` (env section), `backend/requirements.txt` or `pyproject.toml`.
  - **Dependencies:** none.
  - **Acceptance:** `python -c "import sys, torch; print(sys.version, torch.__version__)"` prints a consistent version; the choice is recorded in the README.

- [x] **T1.2 Audit the real artifact bundle and notebook** **[Must have]**
  - **Purpose:** Replace spec assumptions with facts before any loading code is written.
  - **Details:** Enumerate every file in `backend/artifacts/`; record exact filenames, JSON shapes, mapping direction (`raw ID → index`), tensor keys (via `torch.load(..., map_location="cpu", weights_only=True)` on `moviemind_ncf.pt`), and the notebook's save format. Confirm the architecture in `app/ml/model_architecture.py` matches the notebook's `MovieMindNCF` (two definitions: notebook lines ~694 and ~1525).
  - **Files:** a written `backend/ARTIFACTS.md` (or section of README) capturing the findings table from §0.
  - **Dependencies:** T1.1.
  - **Acceptance:** `ARTIFACTS.md` lists every artifact, its real name, shape, and any discrepancy from the spec (config filename, missing `training_metrics.json`); a sample state-dict key is recorded.

- [x] **T1.3 Fix `.gitignore`** **[Must have]**
  - **Purpose:** Keep model weights, dataset exports, secrets, and venvs out of Git.
  - **Details:** Ignore `backend/artifacts/` (entire dir), `.env`, `*.pt`/`*.pth`/`*.ckpt`, `__pycache__/`, `.venv/`, `venv/`, and `ml/data/`. Keep the existing rules.
  - **Files:** `.gitignore`.
  - **Dependencies:** none.
  - **Acceptance:** `git status` after staging shows no `.pt`, no `artifacts/*.json`, no `.env` tracked.

- [x] **T1.4 Create virtual environment & dependency manifest** **[Must have]**
  - **Purpose:** Reproducible Windows-local environment.
  - **Details:** Add `requirements.txt` (or `pyproject.toml`) pinning `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `sqlalchemy>=2.0`, `alembic`, `psycopg[binary]` (or `asyncpg` — decide and record), `python-jose` or `pyjwt`, `pwdlib[argon2]` (or `argon2-cffi`), `python-multipart`, `httpx`, `pytest`, `ruff`, and the chosen `torch` CPU wheel.
  - **Files:** `backend/requirements.txt`.
  - **Dependencies:** T1.1.
  - **Acceptance:** `pip install -r requirements.txt` completes in a fresh `.venv`; `python -c "import fastapi, sqlalchemy, torch"` succeeds.

---

### Phase 2 — Backend foundation

- [x] **T2.1 Typed settings** **[Must have]**
  - **Purpose:** Central, validated configuration with safe defaults and production fail-fast.
  - **Details:** `BaseSettings` (pydantic-settings) reading `.env`. At minimum: `APP_NAME`, `APP_ENV`, `API_V1_PREFIX` (default `/api/v1`), `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL`, `CORS_ORIGINS` (list), `MODEL_ARTIFACT_DIR`, `MODEL_DEVICE` (default `cpu`), `ENABLE_DEMO_ENDPOINTS`, `LOG_LEVEL`. Production must raise if `SECRET_KEY`/`DATABASE_URL` are missing or `SECRET_KEY` is a placeholder.
  - **Files:** `backend/app/core/config.py`, `backend/.env.example`.
  - **Dependencies:** T1.4.
  - **Acceptance:** `Settings()` parses `.env`; `APP_ENV=production` with a dummy `SECRET_KEY` fails fast; `.env.example` has placeholder values + comments only.

- [x] **T2.2 Structured logging & request correlation** **[Must have]**
  - **Purpose:** Consistent logs that never leak secrets/tokens.
  - **Details:** Configure stdlib `logging` (or `loguru` if approved) to stdout with JSON or key-value format; add a middleware that attaches a `request_id` and logs method/path/status/duration.
  - **Files:** `backend/app/core/logging.py`, middleware in `backend/app/main.py`.
  - **Dependencies:** T2.1.
  - **Acceptance:** A request produces a log line with correlation id and no password/token/header body.

- [x] **T2.3 Consistent error handling & exception model** **[Must have]**
  - **Purpose:** Uniform error bodies and no stack-trace leakage.
  - **Details:** Define `ApiError`/custom exceptions and global handlers mapping to `{"detail": ...}` (and optional `code`/`request_id`). Distinguish 400/401/403/404/409/422/500/503. Map DB-unavailable and model-unavailable to distinct 503 semantics.
  - **Files:** `backend/app/core/errors.py`, handlers registered in `main.py`.
  - **Dependencies:** T2.2.
  - **Acceptance:** Unhandled exceptions return a generic 500 with a logged (not returned) traceback.

- [x] **T2.4 App shell, routers, health & readiness** **[Must have]**
  - **Purpose:** Bootable FastAPI app with operational endpoints.
  - **Details:** `main.py` creates the app, mounts `/api/v1` router, registers CORS (explicit origins, no wildcard-with-credentials), includes `GET /` (service identity), `GET /api/v1/health` (liveness), `GET /api/v1/ready` (DB + model readiness). Readiness must be a 503 with a clear diagnostic when the model artifacts are missing/incompatible or the DB is unreachable.
  - **Files:** `backend/app/main.py`, `backend/app/api/v1/router.py`, `backend/app/api/v1/endpoints/health.py`.
  - **Dependencies:** T2.1–T2.3; readiness's model check depends on Phase 3 (stub until then).
  - **Acceptance:** `uvicorn app.main:app --reload` serves `/docs`; `/api/v1/health` returns 200; `/api/v1/ready` returns 503 with a non-secret reason when artifacts absent.

---

### Phase 3 — Model artifact validation & NCF inference

> **Critical compatibility checks (must all pass before any model-backed endpoint ships):**
> - [x] Architecture is byte-for-byte equivalent to the notebook `MovieMindNCF` (layer structure, embedding dims, concat order, activations, dropout, output layer).
> - [x] Checkpoint loads via `torch.load(path, map_location="cpu", weights_only=True)` with **no pickle trust**.
> - [x] `state_dict` keys match the constructed model's `state_dict().keys()` exactly (no `module.` prefix mismatch).
> - [x] `num_users`/`num_movies` from `model_config.json` ≥ max mapping index + 1, and mapping indices are within embedding range.
> - [x] `model.eval()` + `torch.inference_mode()` used for all inference; model loaded **once** at startup, on CPU by default.
> - [x] Sample inference returns a finite score in `[0.5, 5.0]`.
> - [x] Unknown MovieLens user/movie IDs raise controlled 404/422, never `IndexError`.

- [x] **T3.1 Model loader** **[Must have]**
  - **Purpose:** Load config, mappings, and checkpoint once at startup; fail clearly if anything is wrong.
  - **Details:** Read `model_config.json` (actual name), `user_mapping.json`, `movie_mapping.json`, and `moviemind_ncf.pt`. Construct `MovieMindNCF` from config. Validate mapping index bounds and config fields. Attach a `model_version`/artifact version and expose it via diagnostics. Use `weights_only=True`.
  - **Files:** `backend/app/ml/model_loader.py`.
  - **Dependencies:** T1.2, T2.1.
  - **Acceptance:** Loader returns a `LoadedModel` dataclass (model, config, mappings, version); missing/incompatible artifacts raise a descriptive error that surfaces in `/ready`.

- [x] **T3.2 Model architecture parity** **[Must have]**
  - **Purpose:** Guarantee inference reproduces training.
  - **Details:** Keep `MovieMindNCF` in `app/ml/model_architecture.py`; verify its forward path against the notebook (GMF element-wise product, MLP concat, final concat `[gmf; mlp_vector]`, `squeeze(1)`). Add a unit test asserting the module's parameter names/shapes match the checkpoint.
  - **Files:** `backend/app/ml/model_architecture.py`, test in `tests/unit/test_model_architecture.py`.
  - **Dependencies:** T3.1.
  - **Acceptance:** `model.state_dict().keys()` equals checkpoint keys; a shape test passes without loading weights.

- [x] **T3.3 NCF inference wrapper** **[Must have]**
  - **Purpose:** Batch, CPU-friendly rating prediction for known MovieLens IDs only.
  - **Details:** `predict(user_id, movie_id)` and `predict_batch(pairs)` translating raw IDs via mappings; returns float ratings. Reject unknown IDs explicitly. Use `torch.inference_mode()`.
  - **Files:** `backend/app/ml/recommenders/ncf_recommender.py` (or `app/ml/inference.py`).
  - **Dependencies:** T3.1, T3.2.
  - **Acceptance:** A known sample (from notebook) returns a finite score in range; unknown IDs raise a typed error.

- [x] **T3.4 Model smoke test & `/model/info`** **[Must have]**
  - **Purpose:** Deterministic proof the real bundle works; diagnosable model state.
  - **Details:** Add `GET /api/v1/model/info` returning version/type/loaded-status/supported features (no secrets). Add a smoke test that loads the real `backend/artifacts/` bundle and asserts finite predictions in `[0.5, 5.0]`.
  - **Files:** `backend/app/api/v1/endpoints/model.py`, `tests/model/test_artifact_smoke.py`.
  - **Dependencies:** T3.3.
  - **Acceptance:** `/model/info` shows version `1.0.0`; smoke test passes against real artifacts and is skipped (not failed) with a clear message only when artifacts are absent.

---

### Phase 4 — Database foundation

- [x] **T4.1 SQLAlchemy engine & session** **[Must have]**
  - **Purpose:** Typed DB access with a test-friendly session factory.
  - **Details:** `engine`, `SessionLocal`, and a FastAPI dependency yielding a session per request; enable UTC handling. Use parameterized queries only.
  - **Files:** `backend/app/db/session.py`, `backend/app/db/base.py`.
  - **Dependencies:** T2.1.
  - **Acceptance:** A session can connect to the configured PostgreSQL; a failing connection surfaces via `/ready`.

- [x] **T4.2 Base model & enums** **[Must have]**
  - **Purpose:** Shared `DeclarativeBase`, UUID/`datetime(UTC)` conventions, role enum.
  - **Files:** `backend/app/db/base.py`, `backend/app/db/models/`.
  - **Dependencies:** T4.1.
  - **Acceptance:** Models import cleanly and register on the metadata.

- [x] **T4.3 Schema migration** **[Must have]**
  - **Purpose:** Versioned, reproducible schema for User, Movie, Rating, WatchlistItem (+ optional Genre/MovieGenre, RefreshToken if approved).
  - **Details:** One Alembic initial migration creating all tables with FKs, unique constraints (`(user_id, movie_id)` on rating & watchlist), indexes on search/foreign-key columns, and explicit `ondelete` behavior. Decide genres as **normalized relation vs JSONB** — record the decision (recommend normalized `Genre`/`MovieGenre`; see open decision).
  - **Files:** `backend/alembic/versions/xxxx_initial.py`, `backend/alembic/env.py`.
  - **Dependencies:** T4.2.
  - **Acceptance:** `alembic upgrade head` on an empty DB creates all tables; `alembic downgrade base` drops them.

- [x] **T4.4 UTC timestamps, indexes & constraints audit** **[Must have]**
  - **Purpose:** Guarantee the invariants the API relies on (uniqueness, ordering, deletion).
  - **Details:** Ensure `created_at`/`updated_at` default to UTC; verify unique + FK indexes exist; confirm ratings/watchlist uniqueness is enforced at DB level.
  - **Files:** models + migration.
  - **Dependencies:** T4.3.
  - **Acceptance:** Duplicate `(user_id, movie_id)` insert raises `IntegrityError`.

---

### Phase 5 — Movie catalogue & data import

- [x] **T5.1 Movie model & schemas** **[Must have]**
  - **Purpose:** Internal movie record with validated `movielens_id` mapping.
  - **Details:** `Movie` with `id` (UUID), `movielens_id` (nullable unique int), `title`, `genres` (per chosen approach), `overview`, `release_year`, `poster_url` (all nullable), cached `average_rating`/`ratings_count`, timestamps. Pydantic response schemas (never raw ORM objects).
  - **Files:** `backend/app/db/models/movie.py`, `backend/app/schemas/movie.py`.
  - **Dependencies:** T4.3.
  - **Acceptance:** A movie can be created and serialized with `movielens_id` preserved.

- [x] **T5.2 Idempotent MovieLens import script** **[Must have]**
  - **Purpose:** Load `movies.csv` (and optionally `ratings.csv`) without duplication and without treating MovieLens ratings as user ratings.
  - **Details:** CLI script (`scripts/import_movielens.py`) reading `movies.csv`; upsert by `movielens_id`; split the `|`-separated genres; report imported/updated/skipped/failed counts; tolerate malformed rows; **never** import ratings into `Rating`. Document dataset download + license.
  - **Files:** `backend/scripts/import_movielens.py`.
  - **Dependencies:** T5.1.
  - **Acceptance:** Running twice yields zero new records the second time; output reports counts; `ratings.csv` import (if added) does not touch `Rating`.

- [x] **T5.3 Movie browse/search/filter API** **[Must have]**
  - **Purpose:** Paginated, searchable, filterable catalogue.
  - **Details:** `GET /api/v1/movies` with `limit`/`offset` (safe max), `q` (parameterized ILIKE), `genre`, `year`, `sort`/`direction` (allow-listed). `GET /api/v1/movies/{movie_id}` (decide and document whether UUID or MovieLens ID; recommend internal UUID with an optional `movielens_id` lookup). `GET /api/v1/movies/genres`. `GET /api/v1/movies/popular` (name it "popular", not "trending", until a real ranking rule exists).
  - **Files:** `backend/app/api/v1/endpoints/movies.py`, repository/service in `app/repositories`/`app/services`.
  - **Dependencies:** T5.1, T5.2.
  - **Acceptance:** Search is case-insensitive and injection-safe; invalid sort/genre/year return 422; ordering is deterministic.

---

### Phase 6 — Authentication & users

- [x] **T6.1 User model & password hashing** **[Must have]**
  - **Purpose:** Secure account records.
  - **Details:** `User` with UUID `id`, normalized unique `email`, unique `username`, `password_hash`, `display_name`, `role`, `is_active`, timestamps. Hash with Argon2id (`pwdlib[argon2]` or `argon2-cffi`). Never store plaintext.
  - **Files:** `backend/app/db/models/user.py`, `backend/app/core/security.py`.
  - **Dependencies:** T4.3.
  - **Acceptance:** Hash is verifiable and non-reversible; duplicate email/username rejected.

- [x] **T6.2 JWT creation & validation** **[Must have]**
  - **Purpose:** Short-lived access tokens with correct claims.
  - **Details:** HS256 (or approved) tokens with `sub` = user UUID, `exp`, `iat`, `type=access`. Validate signature + expiry + type. `get_current_user` dependency derives identity **only** from the token (never a client-supplied ID).
  - **Files:** `backend/app/core/security.py`, `backend/app/api/dependencies.py`.
  - **Dependencies:** T6.1.
  - **Acceptance:** Expired/forged tokens rejected; valid token resolves the correct user.

- [x] **T6.3 Register / login / logout / refresh** **[Must have]**
  - **Purpose:** Account lifecycle endpoints.
  - **Details:** `POST /auth/register` (normalize+validate email, hash password, return tokens — or 201 + login, per approved flow), `POST /auth/login` (avoid account-enumeration: same generic message on unknown email vs bad password), `POST /auth/refresh` and `POST /auth/logout` (only if refresh tokens approved; otherwise 501/stub). If refresh tokens are built, store **hashed** token identifiers with rotation + reuse detection.
  - **Files:** `backend/app/api/v1/endpoints/auth.py`, `backend/app/schemas/auth.py`.
  - **Dependencies:** T6.2.
  - **Acceptance:** Register→login→`GET /users/me` works; login failures don't reveal whether the account exists.

- [x] **T6.4 Profile endpoints & authorization** **[Must have]**
  - **Purpose:** Current-user profile read/update.
  - **Details:** `GET /users/me`, `PATCH /users/me` (allow-listed fields only). `DELETE /users/me` deferred until a deletion/retention policy is defined (open decision #7/#14) — return 501 until approved.
  - **Files:** `backend/app/api/v1/endpoints/users.py`.
  - **Dependencies:** T6.3.
  - **Acceptance:** Users can only read/update their own profile; `role=admin` gate is stubbed but enforced consistently.

---

### Phase 7 — Ratings & watchlist

- [x] **T7.1 Rating create/update (upsert)** **[Must have]**
  - **Purpose:** One rating per user per movie, transaction-safe.
  - **Details:** `POST /api/v1/ratings` upserts on `(user_id, movie_id)`. Validate score on `0.5–5.0` in `0.5` steps (pending owner approval of scale). Return saved rating + timestamps.
  - **Files:** `backend/app/api/v1/endpoints/ratings.py`, `backend/app/schemas/rating.py`.
  - **Dependencies:** T6.2, T5.1.
  - **Acceptance:** Re-rating the same movie updates (not duplicates); invalid scores/steps → 422.

- [x] **T7.2 Rating read/delete + ownership** **[Must have]**
  - **Purpose:** List/get/remove own ratings; strict ownership.
  - **Details:** `GET /ratings/me`, `GET /ratings/me/{movie_id}`, `DELETE /ratings/me/{movie_id}`. All derive user from token; enforce `user_id == current_user`.
  - **Files:** ratings endpoint.
  - **Dependencies:** T7.1.
  - **Acceptance:** User A cannot read/delete User B's rating (404 or 403, consistent).

- [x] **T7.3 Watchlist add/list/remove** **[Must have]**
  - **Purpose:** Personal watchlist with duplicates blocked at DB level.
  - **Details:** `POST /watchlist/{movie_id}`, `GET /watchlist` (paginated), `DELETE /watchlist/{movie_id}`. Unique `(user_id, movie_id)`; ownership enforced.
  - **Files:** `backend/app/api/v1/endpoints/watchlist.py`, watchlist model/schema.
  - **Dependencies:** T6.2, T5.1.
  - **Acceptance:** Duplicate add is idempotent or 409; users can't see others' watchlists.

---

### Phase 8 — Recommendation services (staged)

> The recommendation service sits **behind an interface** so strategies can evolve without changing routes. HTTP handlers never contain tensor logic or raw SQL.

- [ ] **T8.1 Service interface & candidate filter** **[Must have]**
  - **Purpose:** Strategy abstraction and shared filtering.
  - **Details:** `RecommendationService` orchestrator + `CandidateFilter` (exclude rated / watchlisted / already-selected, configurable). Strategies return `{movie, score, source, reason}` items.
  - **Files:** `backend/app/services/recommendation_service.py`, `backend/app/ml/recommenders/`.
  - **Dependencies:** T5.1, T7.1.
  - **Acceptance:** Filtering logic is unit-testable without a model or DB.

- [ ] **T8.2 NCF demo recommender (Stage A)** **[Must have — demo]**
  - **Purpose:** Model validation for known MovieLens users only.
  - **Details:** `GET /api/v1/recommendations/demo/movielens/{user_id}` and `GET /api/v1/predictions/demo/movielens?user_id=&movie_id=`. Score mapped MovieLens movies via NCF, exclude caller-provided IDs, batch predictions, sort by score desc with deterministic tie-break, return resolved catalogue entries + score/source (`ncf`). Gate behind `ENABLE_DEMO_ENDPOINTS` + admin/development protection. Unknown IDs → 404/422.
  - **Files:** `backend/app/api/v1/endpoints/recommendations.py`, `NCFRecommender`.
  - **Dependencies:** T3.3, T8.1.
  - **Acceptance:** Demo endpoint returns finite, sorted, `ncf`-labeled results; disabled when `ENABLE_DEMO_ENDPOINTS=false`; unknown MovieLens IDs error cleanly.

- [ ] **T8.3 Popularity fallback** **[Must have]**
  - **Purpose:** Honest fallback for cold-start users.
  - **Details:** `PopularityRecommender` ranks by `ratings_count`/`average_rating` (or import-time popularity) deterministically. Return `source="popularity"` and `is_fallback=true` metadata.
  - **Files:** `backend/app/ml/recommenders/popularity_recommender.py`.
  - **Dependencies:** T5.1, T8.1.
  - **Acceptance:** Deterministic ranking; no fabricated explanation.

- [ ] **T8.4 `/recommendations/me` orchestration** **[Must have]**
  - **Purpose:** Personalized endpoint that never treats account ID as a MovieLens ID.
  - **Details:** For a MovieMind user: if insufficient onboarding ratings → popularity fallback with `strategy` + `is_fallback` metadata. If enough ratings → content-based (or approved) strategy. Never map account ID into NCF user embeddings. Support `limit` with safe max; exclude already-rated by default (configurable).
  - **Files:** recommendations endpoint + `RecommendationService`.
  - **Dependencies:** T8.1–T8.3.
  - **Acceptance:** A new user gets `source="popularity"`, `is_fallback=true`, and a truthful reason; response never contains an NCF score keyed to a MovieMind account.

- [ ] **T8.5 Content-based recommender (Stage B)** **[Should have]**
  - **Purpose:** First real personalization from application ratings.
  - **Details:** Build a genre-based preference vector from the user's ratings (weighted by score, positive/negative), rank unrated movies by similarity, fall back to popularity when insufficient data. Clearly report `source="content_based"` and a truthful reason. Exact onboarding/min-rating/mix rules are **approval items** (open decisions #8–#11).
  - **Files:** `backend/app/ml/recommenders/content_based_recommender.py`.
  - **Dependencies:** T8.4.
  - **Acceptance:** Users with ratings get genre-relevant recommendations; no NCF personalization claimed for new accounts.

- [ ] **T8.6 Explanations metadata** **[Should have]**
  - **Purpose:** Optional, truthful explainability.
  - **Details:** `GET /recommendations/me/explanations` (or `reason` field) returns only real signals (e.g., "Matches genres you rated highly"); omit/return generic reason when no method exists — never fabricate.
  - **Files:** recommendations endpoint/schema.
  - **Dependencies:** T8.4/T8.5.
  - **Acceptance:** No invented explanations; reason is always traceable to an actual signal.

---

### Phase 9 — API hardening

- [ ] **T9.1 CORS & trusted proxy** **[Must have]**
  - **Purpose:** Correct browser access for the React frontend.
  - **Details:** Configure explicit `CORS_ORIGINS` from settings (no wildcard-with-credentials); honor trusted proxy/HTTPS in deployment.
  - **Files:** `backend/app/main.py`.
  - **Dependencies:** T2.4.
  - **Acceptance:** A request from an allowed origin includes correct CORS headers; a non-allowed origin is rejected.

- [ ] **T9.2 Rate limiting (login/register)** **[Should have]**
  - **Purpose:** Abuse protection before public deployment.
  - **Details:** Apply a simple in-process rate limit (e.g., slowapi) to `register`/`login` (and demo endpoints if exposed). Document limits.
  - **Files:** `backend/app/api/dependencies.py` or middleware.
  - **Dependencies:** T6.3.
  - **Acceptance:** Repeated failed logins from one client are throttled; limits documented.

- [ ] **T9.3 Request/body & pagination limits** **[Must have]**
  - **Purpose:** Bound resource use.
  - **Details:** Enforce max `limit` on list endpoints and max body size; reject oversized inputs with 413/422.
  - **Files:** endpoint schemas + validation.
  - **Dependencies:** T5.3, T6.4, T7.x.
  - **Acceptance:** `limit=100000` rejected or clamped; oversized body returns a controlled error.

- [ ] **T9.4 Inference off the event loop** **[Should have]**
  - **Purpose:** Keep latency-bound CPU inference from blocking the loop.
  - **Details:** Run NCF inference in a threadpool (`run_in_executor` / `anyio.to_thread`) or document why sync is acceptable at measured load. Keep CPU default.
  - **Files:** NCF recommender / service.
  - **Dependencies:** T3.3.
  - **Acceptance:** A benchmark note shows inference does not starve health checks (documented, not just asserted).

---

### Phase 10 — Testing & quality

- [ ] **T10.1 Unit tests** **[Must have]**
  - **Purpose:** Core logic correctness.
  - **Details:** Cover password hashing, token create/validate/expiry, Pydantic validation, rating scale/steps, MovieLens ID mapping + unknown-ID handling, model output shape/finite/range, recommendation filtering/sorting/fallback/tie-break.
  - **Files:** `backend/tests/unit/*`.
  - **Dependencies:** respective phases.
  - **Acceptance:** `pytest tests/unit` green.

- [ ] **T10.2 Integration tests (DB)** **[Must have]**
  - **Purpose:** Real DB behavior with isolated data.
  - **Details:** Use a dedicated test DB or transactional fixtures. Cover registration/duplicate email, login success/failure, cross-user isolation (A cannot touch B's ratings/watchlist), rating CRUD, watchlist CRUD+duplicate, movie search/filter/pagination, migration upgrade from empty DB, recommendation endpoint with controlled data.
  - **Files:** `backend/tests/integration/*`, `backend/tests/conftest.py`.
  - **Dependencies:** T4–T8.
  - **Acceptance:** `pytest tests/integration` green against a test database; never against production.

- [ ] **T10.3 Contract tests & OpenAPI** **[Must have]**
  - **Purpose:** Lock the API surface.
  - **Details:** Verify status codes, response schemas, auth requirements, pagination/validation errors, and OpenAPI generation via TestClient/httpx.
  - **Files:** `backend/tests/contract/*`.
  - **Dependencies:** T2.4, T5–T8.
  - **Acceptance:** OpenAPI JSON generated; contract assertions pass.

- [ ] **T10.4 Model artifact tests** **[Must have]**
  - **Purpose:** Prove real bundle loads and matches.
  - **Details:** Real artifact load; architecture↔checkpoint shape match; mappings within embedding bounds; known sample inference finite; unknown IDs → controlled error; load failure → readiness fails clearly.
  - **Files:** `backend/tests/model/*`.
  - **Dependencies:** Phase 3.
  - **Acceptance:** All pass when `backend/artifacts/` present; graceful skip message when absent.

- [ ] **T10.5 Lint & type checks** **[Must have]**
  - **Purpose:** Enforce conventions.
  - **Details:** Configure `ruff` (lint + format); optional `mypy` with strict-ish config. Add `pytest`, `ruff check .`, `ruff format --check .` to README.
  - **Files:** `backend/pyproject.toml`/`ruff.toml`, `backend/.gitignore`.
  - **Dependencies:** T1.4.
  - **Acceptance:** `ruff check .` and `ruff format --check .` clean.

---

### Phase 11 — Docker & deployment preparation

- [ ] **T11.1 Dockerfile** **[Should have]**
  - **Purpose:** Reproducible container for the API.
  - **Details:** Multi-stage (or slim) build; CPU torch; non-root user; runs `uvicorn app.main:app`.
  - **Files:** `backend/Dockerfile`.
  - **Dependencies:** T2.4, Phase 3.
  - **Acceptance:** Image builds and serves `/api/v1/health`.

- [ ] **T11.2 Compose for local API + Postgres** **[Should have]**
  - **Purpose:** One-command local services.
  - **Details:** `compose.yaml` with `db` (Postgres) and `api` services; env via `.env`; health checks; volume for artifacts (not baked into image).
  - **Files:** `backend/compose.yaml`.
  - **Dependencies:** T11.1.
  - **Acceptance:** `docker compose up -d db` starts Postgres; `docker compose up` runs the API; migrations can run via a documented step.

- [ ] **T11.3 Deployment config & docs** **[Should have]**
  - **Purpose:** Provider-agnostic release readiness.
  - **Details:** Document DB URL injection, HTTPS via reverse proxy, CORS for production origin, migration as a release step, backup/restore expectations, and CPU-inference performance measurement. No provider/budget selection without owner approval (open decision #12).
  - **Files:** README/`docs/deployment.md`.
  - **Dependencies:** T11.2.
  - **Acceptance:** A reader can run local + understand production constraints without inventing a provider.

---

### Phase 12 — Documentation & handover

- [ ] **T12.1 README** **[Must have]**
  - **Purpose:** Complete onboarding.
  - **Details:** Purpose, architecture, prerequisites, Windows PowerShell setup, env vars, DB setup, migrations, model artifact setup, run/test commands, API docs, troubleshooting.
  - **Files:** `backend/README.md`.
  - **Dependencies:** all phases.
  - **Acceptance:** A fresh developer follows it end-to-end on Windows 11.

- [ ] **T12.2 `.env.example` + schema diagram + model note** **[Must have]**
  - **Purpose:** Config template, ER overview, model integration note.
  - **Details:** `.env.example` (placeholders only); Mermaid ER diagram; model note (artifact files, compatibility, limitations, versioning/replacement).
  - **Files:** `backend/.env.example`, README or `docs/`.
  - **Dependencies:** T2.1, T4, Phase 3.
  - **Acceptance:** No real secrets; diagram matches migrations; model note reflects the real `model_config.json` naming.

- [ ] **T12.3 Dataset & licensing notes** **[Must have]**
  - **Purpose:** Compliant data usage.
  - **Details:** Document MovieLens download URL, terms/license, and that dataset files are not committed.
  - **Files:** README/`docs/data.md`.
  - **Dependencies:** T5.2.
  - **Acceptance:** License + download steps recorded.

- [ ] **T12.4 Final acceptance checklist** **[Must have]**
  - **Purpose:** Verify overall definition of done (§5).
  - **Details:** Run migrations on clean DB, import twice (idempotent), load artifacts + smoke test, exercise auth/user flows, verify recommendation honesty, run full `pytest` + `ruff`, confirm secrets/artifacts excluded from Git.
  - **Files:** this checklist (`backend_task.md` §5).
  - **Dependencies:** all.
  - **Acceptance:** Every §5 item checked with evidence recorded in README/report.

---

## 4. Open decisions for the project owner

The following are **not** decided by this plan. Recommended defaults are labeled but require confirmation.

1. **Python version** — recommend 3.11 (verify against the chosen CPU PyTorch wheel). *(T1.1)*
2. **PostgreSQL for local dev** — recommend Docker Desktop via `compose.yaml`; must also run from a native Windows venv. *(T4.1, T11.2)*
3. **Model artifact location** — local `backend/artifacts/` for dev; production source (volume vs secure download) undecided. *(Phase 3, T11.3)*
4. **Poster/metadata provider** — none approved yet; `poster_url`/`overview` stay nullable until a provider + license is approved. *(T5.1)*
5. **Application rating scale** — recommend `0.5–5.0` in `0.5` steps to match the model. *(T7.1)*
6. **Auth approach** — access token only for the first prototype, or access + rotating refresh tokens? *(T6.3)*
7. **Email verification / password reset** — required for first release? *(T6.4, optional entities)*
8. **Onboarding flow** — rate movies, choose genres, or both? *(T8.5)*
9. **Minimum ratings before personalization** — threshold count. *(T8.4/T8.5)*
10. **Exclusion rules** — exclude rated and/or watchlisted movies from recommendations? *(T8.1)*
11. **Cold-start fallback** — popularity only, content-based after onboarding, or both? *(T8.3/T8.5)*
12. **Deployment provider & budget** — none selected. *(T11.3)*
13. **Demo MovieLens endpoints** — development only, or also a controlled demo environment? *(T8.2)*
14. **Account deletion & retention policy** — define before implementing `DELETE /users/me`. *(T6.4)*

---

## 5. Definition of done

### Per-phase (summary)
- **P1:** Env pinned; artifacts audited and documented; `.gitignore` prevents committing weights/secrets; venv installs cleanly.
- **P2:** App boots with settings/logging/errors/health+readiness; readiness reports model/DB state honestly.
- **P3:** Real bundle loads; architecture matches checkpoint; smoke test passes; unknown IDs error cleanly; `/model/info` works.
- **P4:** Migrations build a clean schema with all constraints/indexes.
- **P5:** MovieLens import is idempotent; browse/search APIs work and are injection-safe.
- **P6:** Register/login/profile secure; no account enumeration; ownership enforced.
- **P7:** Ratings/watchlist CRUD with DB-level uniqueness and cross-user isolation.
- **P8:** Demo NCF works for MovieLens IDs; `/me` never confuses account IDs with MovieLens IDs; cold-start fallback is honest.
- **P9:** CORS/limits/ops endpoints correct; no secrets leaked.
- **P10:** Unit/integration/contract/model tests pass; lint/format clean.
- **P11:** Dockerfile + compose run locally; deployment docs complete (no provider assumed).
- **P12:** README/.env.example/ER/model/data docs complete; acceptance checklist verified.

### Overall (first integrated release)
The backend is done when all of the following hold:
- [ ] Starts on Windows 11 using the documented PowerShell workflow.
- [ ] Schema builds from Alembic on a clean PostgreSQL database.
- [ ] Movie metadata imports repeatedly without duplicates.
- [ ] The real NCF artifacts load and a smoke test validates inference.
- [ ] Authentication/authorization protect user-specific resources.
- [ ] Users can browse movies, save ratings, and manage a watchlist.
- [ ] Recommendation endpoints return valid, documented responses and never confuse MovieMind IDs with MovieLens IDs.
- [ ] New users receive an honest fallback rather than fabricated NCF personalization.
- [ ] Automated tests cover core services, DB behavior, model loading, and API contracts.
- [ ] Secrets and model artifacts are excluded from Git.
- [ ] Docker/local run instructions and README are complete.
- [ ] The API exposes usable OpenAPI docs.
- [ ] All known limitations and open product decisions are documented.

---

## 6. Windows 11 PowerShell workflow (reference)

```powershell
# From the backend directory
py --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# If activation is blocked:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

python -m pip install --upgrade pip
pip install -r requirements.txt

# Configuration
Copy-Item .env.example .env

# Database (Docker Desktop recommended)
docker compose up -d db
docker compose ps

# Migrations + run
alembic upgrade head
uvicorn app.main:app --reload

# Import data (idempotent)
python scripts/import_movielens.py

# Tests + quality
pytest
ruff check .
ruff format --check .

# Stop
deactivate
```

API docs: `http://127.0.0.1:8000/docs` and `http://127.0.0.1:8000/redoc`.

---

*This file is the implementation checklist. No backend code should be written until the owner reviews this plan and resolves the open decisions in §4.*
