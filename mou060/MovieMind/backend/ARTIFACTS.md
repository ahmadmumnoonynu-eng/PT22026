# MovieMind Model Artifacts — Audit Record

**Audited:** 2026-11-14 · **Location:** `backend/artifacts/` (local only, excluded from Git)

This document records the **actual** artifact bundle produced by the training notebook
(`ML/notebooks/MovieMind.ipynb`). The loader (`app/ml/model_loader.py`) must follow these
real names and shapes — not the names listed in `backend_spec.md` §3.2.

## 1. Files present

| File | Role | Status vs spec |
| --- | --- | --- |
| `model_config.json` | Architecture + training configuration | Spec called it `config.json` — **name differs** |
| `moviemind_ncf.pt` | Model weights | Present, matches spec |
| `user_mapping.json` | raw MovieLens user ID → embedding index | Present, matches spec |
| `movie_mapping.json` | raw MovieLens movie ID → embedding index | Present, matches spec |
| `movies.json` | Movie catalogue used by the model/demo | Present; fields differ (see §4) |
| `training_metrics.json` | Recorded evaluation metrics | **MISSING** — loader must tolerate absence |
| `model_architecture.py` | Reference architecture copy | **MISSING in artifacts** — canonical copy lives in `app/ml/model_architecture.py` |
| `inference_example.py` / README | Reference inference notes | **MISSING** — contract derived from notebook instead |

## 2. `model_config.json` (actual contents)

```json
{
  "model_name": "MovieMindNCF",
  "model_version": "1.0.0",
  "framework": "PyTorch",
  "num_users": 610,
  "num_movies": 9724,
  "embedding_dim": 32,
  "mlp_hidden_dims": [128, 64, 32],
  "dropout": 0.1,
  "rating_min": 0.5,
  "rating_max": 5.0,
  "dataset": "MovieLens Latest Small",
  "seed": 42
}
```

## 3. `moviemind_ncf.pt` — checkpoint format

- Saved by the notebook as a **pure state_dict** (no wrapper dict, no epoch/metrics keys):
  `torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, ...)`.
- Loading pattern: `model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))`.
- **Expected tensor keys** (derived from the architecture; asserted by the loader test):

| Key | Shape |
| --- | --- |
| `user_gmf.weight` | (610, 32) |
| `movie_gmf.weight` | (9724, 32) |
| `user_mlp.weight` | (610, 32) |
| `movie_mlp.weight` | (9724, 32) |
| `mlp.0.weight` / `mlp.0.bias` | (128, 64) / (128,) |
| `mlp.3.weight` / `mlp.3.bias` | (64, 128) / (64,) |
| `mlp.6.weight` / `mlp.6.bias` | (32, 64) / (32,) |
| `output.weight` / `output.bias` | (1, 64) / (1,) |

Hidden block indices are `0, 3, 6` because each block is `Linear → ReLU → Dropout`.

## 4. Mappings and catalogue

- **Direction (both mappings):** `{"<raw MovieLens ID>": <embedding index>}`.
  - `user_mapping.json`: `{"1": 0, "2": 1, ...}` — 610 entries, contiguous `0..609`.
  - `movie_mapping.json`: raw IDs are sparse (e.g. `1, 2, 3, ..., 193609`), indices contiguous `0..9723`.
- **`movies.json` fields:** list of `{movieId, title, genres}` only.
  - `genres` is a single `|`-separated string (e.g. `"Adventure|Animation|Children|Comedy|Fantasy"`).
  - **No** `overview`, `release_year`, or `poster_url`. Those DB columns stay `NULL`
    until an approved metadata provider supplies them (open decision #4).
- Titles include the year suffix, e.g. `"Toy Story (1995)"` — release year can be parsed
  from the title during import.

## 5. Architecture parity

The notebook exports two identical definitions of `MovieMindNCF`
(training cell ~line 694, and the `model_architecture_source` string ~line 1525).
The file `backend/app/ml/model_architecture.py` is **byte-identical in behavior**:

- GMF: element-wise product of user/movie embeddings (dim 32).
- MLP: concat `[user_mlp; movie_mlp]` (dim 64) → `128 → 64 → 32` with `ReLU` + `Dropout(0.1)`.
- Head: `Linear(embedding_dim + last_mlp_dim = 32 + 32 = 64, 1)` over concat `[gmf; mlp_vector]`, `.squeeze(1)`.
- Output is a raw regression score — clamp/round to the `[0.5, 5.0]` scale happens at the API layer if desired (decision recorded in loader/endpoint docs).

## 6. Training context (from the notebook)

- Dataset: **MovieLens Latest Small** (`ratings.csv`, `movies.csv`), 610 users × 9,724 movies.
- Split: `train_test_split` train/val/test; best state restored via `copy.deepcopy(model.state_dict())`.
- Reported held-out metrics (owner-reported, **not independently verified**): RMSE **0.8738**, MAE **0.6735**.
- Because `training_metrics.json` is absent, the backend cannot self-report these —
  `/model/info` must say "metrics unavailable" until the owner provides the file.

## 7. Compatibility constraints (binding for implementation)

1. Construct the model from `model_config.json` fields — never hardcode sizes.
2. `num_users`/`num_movies` must be ≥ max mapping index + 1.
3. Only raw MovieLens IDs from the mappings may enter embedding lookups; a MovieMind
   account ID must **never** be passed as `user_indices`.
4. Load once at startup on CPU (`map_location="cpu"`, `weights_only=True`), then `model.eval()`.
5. Inference always under `torch.inference_mode()`; batch predictions where practical.
6. Any artifact change requires re-running the smoke test and bumping
   `model_version` in diagnostics.
