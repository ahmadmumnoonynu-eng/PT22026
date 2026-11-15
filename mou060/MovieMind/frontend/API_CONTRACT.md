# MovieMind Frontend API Contract

**Verified:** 2026-11-16  
**Sources:** `backend/app` implementation and the supplied API documentation.  
**Base path:** `/api/v1`

This is the frontend integration reference for the current backend. It records only behavior that is implemented in the local backend source.

## Authentication

- Authentication uses `Authorization: Bearer <access_token>`.
- `POST /auth/register` accepts `{ email, password, username?, display_name? }` and returns `201` with `access_token`, `token_type`, `expires_in`, and `user`.
- `POST /auth/login` accepts `{ email, password }` and returns `200` with `access_token`, `token_type`, and `expires_in`.
- After login, call `GET /users/me` to obtain the current user profile.
- Access tokens expire after the backend-configured number of seconds; the default is 30 minutes.
- `POST /auth/refresh` and `POST /auth/logout` deliberately return `501`. Sign-out must discard the token and clear user-specific frontend cache locally.
- Registration password length is 8–128 characters. Login password length is 1–128 characters.
- User-editable profile fields are only `username` and `display_name`, via `PATCH /users/me`.

## Error responses

- Controlled API errors use `{ "detail": string, "code": string }`.
- Relevant error codes include `unauthorized`, `forbidden`, `not_found`, `conflict`, `validation_error`, `rate_limited`, `database_unavailable`, `model_unavailable`, `not_implemented`, and `internal_error`.
- A `401` response includes `WWW-Authenticate: Bearer`.
- Validation responses intentionally expose only the generic message `Request validation failed`; do not rely on FastAPI field-level error details.
- Login and registration are rate-limited. Respect a `429` response and its `Retry-After: 60` header.

## Movies and discovery

### `GET /movies`

Returns `MovieListOut`:

```ts
{
  items: Movie[];
  total: number;
  limit: number;
  offset: number;
}
```

Supported query parameters:

| Parameter | Type / range | Default | Notes |
| --- | --- | --- | --- |
| `limit` | integer, 1–100 | `20` | Page size |
| `offset` | integer, >= 0 | `0` | Offset pagination |
| `q` | string, max 200 chars | — | Title search |
| `genre` | string, max 100 chars | — | Case-insensitive genre match |
| `year` | integer, 1888–2100 | — | Exact release year |
| `sort` | allowed value below | `title` | Invalid values return 422 |
| `direction` | `asc` or `desc` | `asc` | Sort direction |

Allowed `sort` values, confirmed from the backend source:

- `title`
- `release_year`
- `average_rating`
- `ratings_count`
- `created_at`

### Other public movie endpoints

- `GET /movies/genres` returns `Genre[]`.
- `GET /movies/popular?limit=1..100` returns a movie array ordered by rating count, average rating, then title.
- `GET /movies/{movie_id}` returns a single movie, or `404` when missing.

### Movie model

```ts
type Movie = {
  id: string; // UUID
  movielens_id: number | null;
  title: string;
  genres: string[];
  overview: string | null;
  release_year: number | null;
  poster_url: string | null;
  average_rating: number | null;
  ratings_count: number | null;
};
```

Do not design against unsupported fields such as a backdrop image, runtime, cast, crew, trailer, provider/streaming data, or related-movie collections.

## Ratings

- All rating endpoints require bearer authentication.
- `POST /ratings` upserts `{ movie_id: UUID, score: number }` and returns `201` with `RatingOut`.
- Scores must be from `0.5` to `5.0` in **0.5 increments**.
- `GET /ratings/me?limit=1..100&offset>=0` returns a paginated rating list.
- `GET /ratings/me/{movie_id}` returns the current user's rating or `404`.
- `DELETE /ratings/me/{movie_id}` returns `204`, or `404` if no rating exists.

`RatingOut` includes the rated `movie`, so the Ratings page does not need an extra movie request per item.

## Watchlist

- All watchlist endpoints require bearer authentication.
- `GET /watchlist?limit=1..100&offset>=0` returns a paginated watchlist.
- `POST /watchlist/{movie_id}` is idempotent: it returns `201` for a new item and `200` when the item already exists.
- `DELETE /watchlist/{movie_id}` returns `204`, or `404` if the item is absent.
- There is no supported favorites endpoint; build only watchlist behavior.

Each watchlist item contains its `movie`, so no additional movie lookup is required for the list.

## Recommendations

- `GET /recommendations/me?limit=1..50` requires bearer authentication.
- It returns `RecommendationsOut` with `items`, overall `source`, `is_fallback`, and `limit`.
- Each item has a `movie`, numeric `score`, `source`, and human-readable `reason`.
- The backend uses popularity fallback until a user has at least five ratings, then uses content-based recommendations. Use `is_fallback` and `source` to label this truthfully in the UI.
- The MovieLens demo endpoints are development/demo functionality and are not part of the main user experience.

## CORS and deployment

- Local backend CORS currently permits `http://localhost:5173` and `http://127.0.0.1:5173`.
- The backend allows `Authorization` and `Content-Type` headers and explicitly permits `GET`, `POST`, `PATCH`, `DELETE`, and `OPTIONS`.
- Production requires the Vercel frontend origin to be added explicitly to `CORS_ORIGINS`; wildcards are rejected.
- The frontend should set only the public `VITE_API_BASE_URL` environment variable. It must never contain backend secrets.

## Design-impacting decisions

- Use poster fallbacks because `poster_url` can be null.
- Build the detail page around title, poster, overview, release year, genres, average rating, and rating count only.
- Use `/movies?sort=ratings_count&direction=desc` or `/movies/popular` for a trending/popular section; `sort=average_rating` is available for top-rated content.
- Omit fake notification, premium/payment, favorite, trailer, streaming, and settings features.
- Show user initials rather than an avatar image because the profile model has no avatar field.
