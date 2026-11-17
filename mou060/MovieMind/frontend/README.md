# MovieMind Frontend

MovieMind is a responsive React single-page application for discovering movies,
searching the catalogue, viewing movie details, signing in, rating films, saving
a watchlist, and viewing backend-generated recommendations.

The FastAPI service in [`../backend/`](../backend/) is the source of truth for
movie data, authentication, authorization, ratings, saved movies, and
recommendations. This project contains no database access, recommendation
algorithm, model artifacts, or backend secrets.

| Item | Value |
| --- | --- |
| Application root | `MovieMind/frontend/` |
| API base URL | `VITE_API_BASE_URL` + `/api/v1` |
| Default local API | `http://localhost:8000/api/v1` |
| Frontend dev server | `http://localhost:5173` (Vite default) |
| Production output | `dist/` |
| Deployment target | Vercel, rooted at `frontend/` |

## Stack

- **Runtime:** React 19, React DOM 19, TypeScript (strict), Vite 6.
- **Styling:** Tailwind CSS 4 through `@tailwindcss/vite`, with CSS custom
  properties for the cinematic dark theme.
- **Routing:** React Router 7.
- **Data:** Axios and TanStack Query 5.
- **UI:** Lucide React icons; accessible shared primitives live in
  `src/components/ui/`.
- **Auth forms:** React Hook Form and Zod are installed for future form reuse;
  the current small login/registration forms use native controlled inputs.
- **Testing:** Vitest 5, React Testing Library, MSW 2, Playwright 1.65.

## Project structure

```text
frontend/
├── e2e/
│   ├── mocked/              # Playwright critical flows with a mocked contract
│   ├── live/                # Gated live-backend smoke tests
│   └── support/             # Stateful mock FastAPI implementation
├── src/
│   ├── app/                 # Entry composition, providers, router
│   ├── components/          # Shared layout, movie, and UI primitives
│   ├── features/            # Feature-scoped API modules, hooks, components
│   ├── lib/                 # Axios client, error mapping, query keys, session
│   ├── pages/               # Route-level pages
│   ├── styles/              # Global theme and motion rules
│   ├── test/                # Vitest setup, fixtures, MSW handlers, helpers
│   └── types/               # Types derived from the FastAPI Pydantic schemas
├── playwright.config.ts     # Mocked E2E project
├── playwright.live.config.ts
├── vitest.config.ts
└── vite.config.ts
```

## Prerequisites

- Node.js 20 or newer. The project was verified with Node.js 24.18.0.
- npm 10 or newer. The project was verified with npm 11.16.0.
- A running MovieMind FastAPI backend for real-data local development.
- The backend CORS allowlist must include the exact frontend origin. The backend
  default permits `http://localhost:5173` and `http://127.0.0.1:5173`.

## Installation

```bash
cd MovieMind/frontend
npm install
```

Create a local environment file from the example. Vite loads `.env.local`
automatically.

```powershell
Copy-Item .env.example .env.local
```

```bash
cp .env.example .env.local
```

Start the API separately, then start the frontend:

```bash
npm run dev
```

Open `http://localhost:5173`.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Recommended | Public origin of the FastAPI service, without a trailing slash and without `/api/v1`. The client appends `/api/v1`. |

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Rules:

- If unset, the client falls back to `http://localhost:8000`.
- For local cookie persistence, keep the frontend and API on the same hostname
  (`localhost` in the default configuration); `localhost` and `127.0.0.1` are
  different cookie sites even though they may resolve to the same machine.
- Only `VITE_*` values are exposed to the browser. Never put database URLs,
  access tokens, private keys, or other secrets in a `VITE_*` variable.
- Do not commit `.env` or `.env.*`; only `.env.example` belongs in Git.
- Production must use the deployed HTTPS FastAPI origin.

## Movie poster data

The static MovieLens-to-TMDB poster map is
`src/data/movie-posters.json`. The frontend looks posters up by MovieLens
`movieId` (`movielens_id` in the API response); it never calls TMDB at runtime.
Missing or failed images use the shared cinematic placeholder.

To collect or refresh the catalogue, download the official MovieLens Latest
Small dataset and run the backend script from the repository root:

```powershell
$env:TMDB_API_KEY = "your-local-tmdb-api-key"
python backend/scripts/collect_movie_posters.py `
  --movies-csv "C:\path\to\ml-latest-small\movies.csv" `
  --links-csv "C:\path\to\ml-latest-small\links.csv"
```

The script writes the JSON map to `frontend/src/data/movie-posters.json` and
keeps its resumable TMDB lookup cache in the ignored
`backend/artifacts/tmdb_poster_cache.json`. It records every `movies.csv`
movie, uses `links.csv` TMDB IDs, and leaves `posterUrl` null if there is no
TMDB ID or the API confirms there is no poster. Transient lookup failures are
reported and are not cached, so rerunning retries them. Keep the API key in a
local environment variable; never add it to frontend configuration or Git.

If you need to initialize or check the complete MovieLens ID manifest before
setting up TMDB credentials, add `--catalog-only` to the command. That mode
writes null URLs without checking TMDB; it is not a completed poster
collection. Rerun without the flag once `TMDB_API_KEY` is configured.
To publish URLs already collected in the local cache without making API
requests, use `--cache-only`; uncached entries remain null until a regular run
completes them.

TMDB requires the approved logo and this prominent notice in an About/Credits
section: “This product uses the TMDB API but is not endorsed or certified by
TMDB.” The app displays both in its shared Credits footer. Non-commercial API
use requires attribution; commercial use requires a separate license. See
[TMDB's logo and attribution requirements](https://www.themoviedb.org/about/logos-attribution)
and [API FAQ](https://developer.themoviedb.org/docs/faq).

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Start the Vite development server. |
| `npm run typecheck` | Run the strict TypeScript project build check. |
| `npm test` | Run the Vitest suite once. |
| `npm run test:watch` | Run Vitest in watch mode. |
| `npm run test:coverage` | Write coverage to `coverage/`. |
| `npm run test:e2e` | Run mocked Playwright critical flows. Requires a Playwright browser. |
| `npm run test:e2e:live` | Run gated live-backend smoke tests. Skips without credentials. |
| `npm run build` | Type-check and build the production bundle into `dist/`. |
| `npm run preview` | Preview the production build locally. |

## FastAPI integration

All requests go through one Axios client in `src/lib/api/client.ts`:

- Base URL: `${VITE_API_BASE_URL}/api/v1`
- JSON `Accept` and `Content-Type` headers
- 12-second request timeout
- Credentials included for refresh-cookie requests
- Access and CSRF tokens held in memory; refresh token is only an HttpOnly cookie
- Concurrent `401` responses share one refresh request and retry once
- Protected query data is cleared when the session is revoked or signed out
- Failures are mapped to safe user-facing messages; raw server details, SQL
  errors, stack traces, and secrets are never rendered

Types in `src/types/api.ts` are derived from the confirmed Pydantic response
schemas. UI components render only fields that the API actually returns.

### Confirmed API contract

| Area | Endpoint | Notes |
| --- | --- | --- |
| Login | `POST /auth/login` | `{ email, password }` returns an access token, user, CSRF token, token type, and expiry; sets a rotating HttpOnly refresh cookie. |
| Register | `POST /auth/register` | Accepts `email`, `password` (8–128 characters), optional `username`, and optional `display_name`; returns the user and tokens. |
| CSRF token | `GET /auth/csrf` | Returns a CSRF token associated with the refresh cookie; returns `null` when no session cookie exists. |
| Refresh | `POST /auth/refresh` | Validates CSRF, rotates the refresh cookie, and returns a new short-lived access token. |
| Logout | `POST /auth/logout` | Validates CSRF, revokes the refresh-token family, and clears both cookies. |
| Current user | `GET /users/me` | Loaded after startup refresh to restore the authenticated user before protected routes render. |
| Profile update | `PATCH /users/me` | Only `username` and `display_name` are editable. |
| Movie list | `GET /movies` | Offset pagination with `limit` (1–100), `offset`, `q`, `genre`, `year`, `sort`, and `direction`. |
| Movie detail | `GET /movies/{movie_id}` | Returns one movie or `404`. |
| Genres | `GET /movies/genres` | Returns `{ id, name }[]`. |
| Popular | `GET /movies/popular?limit=1..100` | Ordered by rating count, average rating, then title. |
| My rating | `GET /ratings/me/{movie_id}` | Returns the current user's rating or `404`. |
| My ratings | `GET /ratings/me` | Offset-paginated rating list with embedded movies. |
| Upsert rating | `POST /ratings` | `{ movie_id, score }`; scores are `0.5`–`5.0` in half steps. |
| Delete rating | `DELETE /ratings/me/{movie_id}` | `204`, or `404` when absent. |
| Watchlist | `GET /watchlist` | Offset-paginated saved movies with embedded movie data. |
| Add saved movie | `POST /watchlist/{movie_id}` | Idempotent: `201` for new, `200` when already saved. |
| Remove saved movie | `DELETE /watchlist/{movie_id}` | `204`, or `404` when absent. |
| Recommendations | `GET /recommendations/me?limit=1..50` | Returns `items`, `source`, `is_fallback`, and `limit`. Each item includes a movie, score, source, and human-readable reason. |

Contract assumptions and behavior:

- Authentication uses `Authorization: Bearer <access_token>`. Access tokens
  expire after the backend-configured interval (default 30 minutes).
- Refresh tokens are opaque, stored server-side only as hashes, rotated on
  refresh, and sent in an HttpOnly cookie. Refresh and logout require the
  matching CSRF cookie and `X-CSRF-Token` header.
- The frontend attempts session restoration before deciding whether protected
  routes should redirect. A missing refresh cookie is treated as a normal
  signed-out state; transient restoration failures show a retry state.
- The `refresh_sessions` table requires the Alembic migration described in the
  backend README. It is not created automatically at application startup.
- Errors use `{ "detail": string, "code": string }` with codes such as
  `unauthorized`, `forbidden`, `not_found`, `conflict`, `validation_error`,
  `rate_limited`, `database_unavailable`, `model_unavailable`, and
  `internal_error`.
- Validation responses expose only a generic message; the UI does not rely on
  field-level FastAPI validation details.
- Login and registration are rate-limited. The client exposes retry timing from
  `Retry-After` when present.
- Recommendations are popularity-based until the user has at least five
  ratings, then become content-based. The UI labels the fallback using
  `is_fallback` and `source`; it never generates recommendations itself.
- Pagination is offset-based. No endpoint returns the whole catalogue.
- Movie data is limited to `id`, `movielens_id`, `title`, `genres`, `overview`,
  `release_year`, `poster_url`, `average_rating`, and `ratings_count`.
  `poster_url` can be null and has a graceful fallback.

### Unsupported specification features

The current backend does not support these features, so the frontend does not
build or imply them:

- Backdrops, runtime, cast, crew, trailers, or streaming availability
- Favorites as a separate concept from the watchlist
- Notifications, premium/payment flows, social features, chat, or public profiles
- Settings beyond the current placeholder route
- Client-side recommendation logic, model training, or ML artifact access
- Email verification

## Routes

| Route | Access | Description |
| --- | --- | --- |
| `/` | Public | Hero, global search, popular movies, and recommendation preview. |
| `/discover` | Public | Catalogue browsing with confirmed filters and pagination. |
| `/search` | Public | Explicit submitted search with URL-synced query and pagination. |
| `/movies/:movieId` | Public | Movie details plus signed-in rating and watchlist actions. |
| `/login` | Public | Email/password login. |
| `/register` | Public | Registration with optional username and display name. |
| `/watchlist` | Signed in | The current user's saved movies. |
| `/ratings` | Signed in | The current user's ratings. |
| `/recommendations` | Signed in | Backend recommendations and fallback guidance. |
| `/profile` | Signed in | Editable display name and username. |
| `/settings` | Signed in | Placeholder; no unsupported settings are invented. |
| `*` | Public | Branded not-found page. |

Protected routes use a UI guard for navigation only. FastAPI remains the
authorization authority for every protected request.

## Responsive and accessibility behavior

- Mobile bottom navigation with a 44px minimum target and desktop sidebar
  navigation.
- Adaptive movie grids across mobile, tablet, and desktop viewports.
- Fixed 2:3 poster aspect ratios with lazy loading below the fold and eager
  loading for priority posters.
- Semantic landmarks, heading order, labeled form controls, native selects,
  and keyboard-visible focus styles.
- Skip-to-main-content link and live regions for status and error feedback.
- Numeric/text labels accompany color-coded ratings and status.
- `prefers-reduced-motion` is respected.

## Testing

### Vitest and React Testing Library

```bash
npm test
```

The suite contains 76 tests across 19 files and covers:

- Movie card and poster fallbacks
- Loading, empty, error, and retry states
- Search input, URL synchronization, and no-results behavior
- Login/registration validation, duplicate-submit prevention, and safe errors
- Authentication-dependent navigation and header UI
- Rating and watchlist controls, including pending and error states
- Endpoint URLs, query parameters, request bodies, bearer authentication, and
  auth-cookie/CSRF contracts
- Session restoration, destination-preserving redirects, single-flight refresh,
  and `401` retry behavior
- Cache invalidation after rating/watchlist mutations
- Logout removal of protected cached data

MSW handlers in `src/test/msw/handlers.ts` mirror the verified FastAPI contract.
Use `server.use(...)` inside a test to override a response.

Useful commands:

```bash
npm run test:watch
npm run test:coverage
```

### Playwright

Two projects are configured:

- `npm run test:e2e` runs mocked critical flows from `e2e/mocked/` against a
  Vite server whose API base URL points at the same origin. This does not need a
  backend.
- `npm run test:e2e:live` runs `e2e/live/` only when a safe non-production
  environment and dedicated test account are provided.

Install a browser once before running mocked E2E tests:

```bash
npx playwright install chromium
```

Then run:

```bash
npm run test:e2e
```

Live smoke tests require:

```dotenv
E2E_BASE_URL=https://your-preview-frontend.example.com
E2E_EMAIL=qa-user@example.com
E2E_PASSWORD=replace-with-test-account-password
```

Without `E2E_EMAIL` and `E2E_PASSWORD`, live tests are skipped. They mutate the
dedicated account's watchlist and rating, so never point them at production user
data or a shared account.

**Current status:** the mocked Playwright suite was attempted but could not
launch because the local Chromium executable is unavailable. Chromium was not
installed for this task. Component and API integration tests pass locally.

## Build

```bash
npm run build
```

This runs `tsc -b` and `vite build`, then writes static assets to `dist/`.
Route-level pages are lazy-loaded into separate chunks. The current main bundle
is approximately 441.7 kB (about 142.6 kB gzipped).

Preview the production build locally:

```bash
npm run preview
```

## Vercel deployment

The frontend is intended to deploy as a separate Vercel project; it is not yet
deployed, so no production URL is recorded here.

1. Import the repository into Vercel and create a separate frontend project.
2. Set **Root Directory** to `frontend/`.
3. Use the Vite preset:
   - Install command: `npm install`
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add the production environment variable:
   - `VITE_API_BASE_URL=https://your-deployed-api.example.com`
5. Add the exact production frontend origin to the backend `CORS_ORIGINS`
   allowlist. Wildcards are rejected.
6. Deploy. Verify a direct refresh of a nested route such as
   `/movies/:movieId`.
7. Add `frontend/vercel.json` with an SPA rewrite only if direct route refreshes
   return `404`; no rewrite file is committed pre-emptively.
8. Decide deliberately whether preview deployment origins are supported. Do not
   open production CORS to arbitrary preview domains.
9. Apply the backend Alembic migration for `refresh_sessions` before deploying
   the backend changes. Configure explicit `CORS_ORIGINS` and, for a cross-site
   frontend/API deployment, set `REFRESH_COOKIE_SAME_SITE=none`; production
   automatically enforces `Secure`. Third-party-cookie restrictions may require
   a same-site custom domain or same-origin API proxy.

## Screenshots

Local Phase 7 responsive captures were produced at a 375×812 mobile viewport:

| File | Description |
| --- | --- |
| `mobile.png` | Mobile home capture |
| `mobile-phase7.png` | Responsive verification capture |
| `mobile-phase7-scale1.png` | Scale-1 verification capture |
| `mobile-phase7-settled.png` | Settled-layout verification capture |

These files are intentionally excluded by `.gitignore` as local audit captures.
Add final committed desktop, tablet, and mobile screenshots (for example under a
future `docs/screenshots/` directory) after deployment.

## Known limitations

- Browser restoration depends on the backend `refresh_sessions` migration and
  correctly configured production cookies/CORS. The access token remains
  memory-only; the persistent credential is an HttpOnly refresh cookie.
- Registration immediately signs the user in; there is no email verification.
- Favorites are not supported; only the watchlist exists.
- Recommendations use backend fallback behavior until five ratings exist.
- Movie metadata is limited to the confirmed schema; the UI does not invent
  unsupported fields or actions.
- The live backend integration environment has not been available for a full
  manual acceptance pass. UI behavior is covered with MSW contract mocks.
- Playwright E2E execution is pending installation of its Chromium runtime.
  Live E2E tests are gated and have not been run.
- Vercel deployment, production CORS configuration, and post-deployment route
  refresh checks remain outstanding.
- No ESLint or Prettier configuration exists yet; `npm run typecheck` and the
  test/build checks are the current static gates.
- `/settings` is a placeholder because no supported settings API exists.

## Related documentation

- [Backend README](../backend/README.md) — backend setup and architecture.
- [Backend plan](../backend_task.md) — backend phases and requirements.
- [Model artifact audit](../backend/ARTIFACTS.md) — ML artifact handling.

Broad system architecture and ML methodology are documented in the backend and
project-level documentation rather than duplicated here. A local, gitignored
`API_CONTRACT.md` contains the original API discovery inventory; the contract
summary above is the committed frontend reference.
