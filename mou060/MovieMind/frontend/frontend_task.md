# MovieMind Frontend — Build Task Plan

## Purpose

This is the implementation backlog for the MovieMind web frontend. Build it as a responsive React single-page application in the existing repository under `MovieMind/frontend/`. The FastAPI backend is the source of truth for data, authorization, ratings, saved movies, and recommendations.

**Important implementation rule:** before creating any endpoint function, inspect the backend's OpenAPI document (`/openapi.json` or `/docs`) and its Pydantic schemas. Do not invent endpoint paths, request bodies, response fields, authentication behavior, pagination, or recommendation metadata.

## Scope and boundaries

- [ ] Build the frontend with React, TypeScript, Vite, Tailwind CSS, React Router, Axios, TanStack Query, and Lucide React.
- [ ] Add React Hook Form and Zod when implementing authenticated forms.
- [ ] Add Vitest, React Testing Library, and Playwright when their corresponding test work begins.
- [ ] Deploy the frontend separately on Vercel, rooted at `frontend/`.
- [ ] Keep all database access, recommendation logic, authorization, and persistence in FastAPI.
- [ ] Keep secrets, database URLs, tokens, private keys, and real `.env` files out of the browser bundle and Git.
- [ ] Do not build streaming, purchase/rental, social, chat, public-profile, ML-training, or admin-dashboard features unless later requested.

## Definition of done

A task is complete only when the implementation is integrated with the actual backend contract where applicable, works at the required viewport sizes, has appropriate loading/empty/error handling, is accessible by keyboard, and is verified by the relevant tests/build checks.

## Phase 0 — Repository and API discovery

### Repository preflight

- [x] Inspect the existing `MovieMind/` structure, Git status, branch conventions, and teacher-required layout before changing files.
- [x] Locate any existing backend, API documentation, environment examples, and project README files.
- [x] Preserve existing backend and ML code; create only one frontend project at `MovieMind/frontend/`.
- [x] Confirm the Node.js/npm version available for development and choose compatible current stable package versions.
- [x] Record assumptions and blockers rather than changing backend code without approval.

### API contract inventory — required before integration

- [x] Open the FastAPI `/openapi.json` or `/docs` and save a concise contract inventory in project documentation.
- [x] Identify the public movie-list endpoint, query parameters, response shape, and pagination convention.
- [x] Identify search support, including whether search is server-side, its parameter name, debounce suitability, and returned result count.
- [x] Identify the movie-detail endpoint and every actual movie field available to the UI.
- [x] Identify poster/image URL behavior and fallback requirements.
- [x] Identify authentication endpoints, accepted login/registration fields, token/cookie strategy, logout support, and unauthorized response shape.
- [x] Identify profile/current-user endpoint support, if any.
- [x] Identify rating read/create/update endpoints, allowed rating values, and whether a user's rating is included in movie data.
- [x] Identify watchlist and/or favorites endpoints, request/response schemas, and whether the two concepts are distinct.
- [x] Identify recommendation endpoint, required inputs, recommendation metadata, cold-start/insufficient-data responses, and error behavior.
- [x] Identify server error payloads and validation-error shape for user-safe error mapping.
- [x] Identify CORS requirements for local Vite, production Vercel, and any intentional preview-deployment workflow.
- [x] Define TypeScript types from the real schemas (or generate types from OpenAPI and review them); do not use `any` to bypass unknown contracts.

## Phase 1 — Application foundation

### Project setup

- [x] Initialize or configure the Vite React + TypeScript project in `MovieMind/frontend/` without creating a separate repository.
- [x] Configure Tailwind CSS and a maintainable global styling entry point.
- [x] Declare only the initial dependencies needed for the shell: React Router, Axios, TanStack Query, and Lucide React. Dependency installation is pending the local package-registry approval/usage-limit blocker.
- [x] Configure TypeScript strictness, import aliases, and Vite development/production settings.
- [x] Create a safe `.env.example` containing only `VITE_API_BASE_URL=http://127.0.0.1:8000`.
- [x] Configure `.gitignore` for `node_modules/`, `dist/`, `.env`, `.env.*`, coverage output, Playwright output, and test results while preserving `.env.example`.
- [x] Add package scripts for development, build, and type checking. Test scripts will be added with the testing phase.
- [ ] Confirm `npm run build` succeeds before feature implementation. Blocked: dependencies cannot be installed while the approval service is unavailable.

### Application structure

- [x] Add `src/main.tsx` as the application entry point.
- [x] Add `src/app/providers.tsx` for QueryClient, router, and future shared providers.
- [x] Add `src/app/router.tsx` for route definitions; lazy loading can be added once feature pages have meaningful bundle weight.
- [x] Keep `src/app/App.tsx` limited to top-level composition rather than feature business logic.
- [x] Create focused shared folders needed for the foundation: `components/ui/`, `components/layout/`, `pages/`, and `styles/`. Feature/API folders will be added as their implementations begin.
- [x] Do not create empty feature modules in advance; add each module when its implementation starts.
- [x] Keep shared layout and UI components focused and independent of feature/API logic.

### Design system and shared UI

- [x] Implement dark cinematic theme tokens: background, surfaces, text, accent, border, success, and error colors.
- [x] Define high-contrast text, control, and focus-indicator conventions; visual browser review remains pending installed dependencies.
- [x] Define reusable type, radius, shadow, and motion conventions.
- [x] Add a responsive application shell and mobile navigation.
- [x] Build initial accessible primitives: button, text input, status panel, and empty-state panel. Forms, dialogs, and skeletons will be added with their feature work.
- [x] Define inline-feedback conventions through the `StatusPanel`; mutation feedback will be connected with API features.
- [x] Respect `prefers-reduced-motion` and keep transitions subtle.

### Navigation and routes

- [x] Build responsive header/navigation with MovieMind branding, Discover, search entry point, and guest authentication actions.
- [x] Implement keyboard-accessible mobile bottom navigation with 44px-or-larger touch targets; authenticated navigation evolves in the authentication phase.
- [x] Add routes: `/`, `/search`, `/movies/:movieId`, `/login`, `/register`, `/watchlist`, `/recommendations`, and a catch-all 404 route.
- [x] Create a branded Not Found page that links back to Home.
- [ ] Implement a protected-route UI guard for authenticated pages while leaving enforcement to the backend.

## Phase 2 — Shared API and state infrastructure

### Axios client and errors

- [ ] Create one Axios client in `src/lib/api/client.ts` using `VITE_API_BASE_URL`, JSON requests, and a sensible timeout.
- [ ] Implement the authentication behavior that matches the discovered backend contract: bearer header or credentialed cookies, never an assumed hybrid.
- [ ] Add request/response handling for network failures, validation errors, unauthorized, forbidden, not found, rate limiting, and server errors.
- [ ] Map API failures to safe, useful user-facing messages; do not expose raw server errors, SQL details, stack traces, or secrets.
- [ ] Handle an expired/invalid session according to the real API response and clear user-specific cached state on logout.

### TanStack Query conventions

- [ ] Create stable query-key conventions for movies, movie details, search results, current user, ratings, saved movies, and recommendations.
- [ ] Set sensible stale times for static movie data without hiding data freshness problems.
- [ ] Define mutation invalidation/update behavior for ratings and saved-movie changes.
- [ ] Ensure stale searches do not overwrite newer search results.
- [ ] Ensure stale data from a prior account is not displayed after logout/account changes.

## Phase 3 — Discovery, search, and movie details

### Reusable movie presentation

- [ ] Define a real `Movie` UI type from the discovered API schema.
- [ ] Build a reusable movie poster component with fixed 2:3 aspect ratio, image loading behavior, meaningful alt text, and a graceful missing-poster fallback.
- [ ] Build an accessible movie card showing only API-provided title, year, rating, and genre information.
- [ ] Make card navigation keyboard accessible and avoid nesting a separate action button inside an inaccessible full-card click target.
- [ ] Build responsive movie-grid/list presentation that adapts cleanly across mobile, tablet, and desktop.
- [ ] Add skeleton cards, empty states, and retryable error states.

### Discover page — `/`

- [ ] Create a hero with the MovieMind value proposition and a prominent movie search form.
- [ ] Fetch and render the real public movie list if the backend exposes it.
- [ ] Implement API-supported filters only after confirming their schemas.
- [ ] Implement pagination or Load more using the backend's actual page/cursor protocol.
- [ ] Display a signed-in recommendation preview only when a suitable backend endpoint and data are available.
- [ ] For visitors, show a neutral discovery prompt instead of personalized recommendation claims.

### Search page — `/search`

- [ ] Sync the query with URL search parameters so results can be refreshed and shared.
- [ ] Submit search via Enter and a visible submit control.
- [ ] Reflect the current query and result count only when returned by the backend.
- [ ] Implement debounced live search only if the backend supports it and it is demonstrably useful; otherwise submit-on-search.
- [ ] Support the actual search pagination protocol.
- [ ] Add loading, no-results, API-error, and retry states.

### Movie detail page — `/movies/:movieId`

- [ ] Retrieve the individual movie using the actual detail endpoint.
- [ ] Render only confirmed fields (such as title, poster, description, date, genres, runtime, and clearly sourced rating).
- [ ] Add loading, invalid-ID/not-found, and server-error states.
- [ ] Provide signed-in rating and saved-movie actions only after their backend endpoints are implemented.
- [ ] Keep recommendation-related actions off the page unless backed by a real endpoint.

## Phase 4 — Authentication

### Auth foundation

- [ ] Add the form dependencies: React Hook Form and Zod.
- [ ] Create the auth feature module with actual request/response types and validation schemas that mirror—but never replace—backend validation.
- [ ] Implement an authentication provider/context suitable for the discovered cookie or token model.
- [ ] Restore session/current-user state only through backend-supported behavior.
- [ ] Add login/logout-driven navigation and cache clearing.
- [ ] Ensure password values and access tokens are never logged, rendered in errors, or committed to files.

### Login — `/login`

- [ ] Build labeled login fields exactly matching the backend schema.
- [ ] Add required/basic format validation and clear inline errors.
- [ ] Disable duplicate submission during the request.
- [ ] Connect to the real login endpoint and show safe authentication errors.
- [ ] Navigate after successful login according to the expected product flow.

### Registration — `/register`

- [ ] Build only fields accepted by the real registration endpoint.
- [ ] Validate inputs client-side where practical and preserve input on recoverable errors.
- [ ] Connect to the real registration endpoint.
- [ ] Show the backend-supported success/next-step result; do not assume automatic login or email verification.

### Authenticated UI behavior

- [ ] Change header actions to signed-in account/navigation actions when authenticated.
- [ ] Restrict `/watchlist` and `/recommendations` at the UI level as required by the API.
- [ ] Provide a clear sign-in/re-authentication path after 401 responses.
- [ ] Verify the UI does not treat hidden controls as authorization.

## Phase 5 — Ratings and saved movies

### Ratings

- [ ] Confirm rating scale, permitted values, create/update semantics, and current-user rating source.
- [ ] Build an accessible rating control with visible labels, keyboard support, and clear pending/success/error feedback.
- [ ] Display a user's rating only when it comes from the authenticated API response.
- [ ] Submit/create/update ratings through the actual endpoint.
- [ ] Prevent duplicate mutations and preserve/recover UI state after an error.
- [ ] Invalidate/update relevant movie, detail, recommendation, and user queries after successful rating changes.

### Watchlist/favorites

- [ ] Confirm whether the backend exposes watchlist, favorites, or both, and model the exact supported behavior.
- [ ] Implement add/remove controls with clear accessible labels and pending state.
- [ ] Create `/watchlist` using the authenticated user's real saved-movie endpoint.
- [ ] Display saved movies in an adaptive grid/list.
- [ ] Add useful empty state copy and a route back to discovery.
- [ ] Update cached saved-movie state after mutations and verify persistence after refresh.

## Phase 6 — Recommendations

- [ ] Confirm recommendation endpoint, eligibility requirements, response schema, recommendation type metadata, and cold-start/error responses.
- [ ] Create a recommendations feature API module and query hook using the confirmed contract.
- [ ] Build `/recommendations` with returned movie cards and all loading, empty, error, and retry states.
- [ ] Display recommendation method/type only when reliable backend metadata explicitly provides it.
- [ ] Render the backend's cold-start or insufficient-rating message when available; otherwise use neutral API-consistent guidance.
- [ ] Never hardcode recommendations, expose model artifacts, run model training, or implement the recommendation algorithm in the browser.

## Phase 7 — Responsive design, accessibility, and performance pass

### Responsive verification

- [ ] Verify layouts at approximately 320–767 px, 768–1023 px, and 1024 px and above.
- [ ] Confirm there is no horizontal overflow at common viewport sizes.
- [ ] Ensure navigation, dialogs, forms, grids, controls, and empty/error states work on small screens.
- [ ] Ensure poster dimensions/aspect ratios prevent layout shift.
- [ ] Use suitable touch-target sizes.

### Accessibility verification

- [ ] Use semantic landmarks, headings, buttons, links, lists, form labels, and image alternatives correctly.
- [ ] Verify complete keyboard navigation and visible focus indicators.
- [ ] Verify dialogs trap/manage focus and can be dismissed safely.
- [ ] Make asynchronous status, success, and error feedback perceptible to assistive technology where appropriate.
- [ ] Do not convey state with color alone.
- [ ] Verify sensible heading order and reduced-motion behavior.

### Performance work

- [ ] Lazy-load route-level pages where it meaningfully reduces initial load.
- [ ] Lazy-load below-the-fold poster images.
- [ ] Use backend search and pagination; do not download the entire catalogue.
- [ ] Avoid duplicate API calls through TanStack Query caching.
- [ ] Keep large ML/model assets out of the frontend bundle.
- [ ] Inspect the production build output and address unexpectedly large dependencies/chunks.

## Phase 8 — Testing

### Test infrastructure

- [ ] Configure Vitest and React Testing Library.
- [ ] Add API mocking for component/integration tests (for example, MSW if appropriate).
- [ ] Configure Playwright when critical user flows are functional and a safe test environment/account exists.

### Unit and component tests

- [ ] Test movie card rendering with complete data and missing poster data.
- [ ] Test loading, empty, error, and retry UI states.
- [ ] Test search input and URL/query behavior.
- [ ] Test form validation and duplicate-submit prevention.
- [ ] Test authentication-dependent navigation/UI.
- [ ] Test rating and saved-movie controls, including pending/error states.

### API integration tests

- [ ] Verify endpoint functions use correct discovered URLs, parameters, bodies, and authentication behavior.
- [ ] Verify client error mapping for validation, unauthorized, not found, and server failures.
- [ ] Verify relevant cached data is invalidated/updated after rating and saved-movie mutations.
- [ ] Verify logout removes protected cached data.

### End-to-end tests

- [ ] Test visitor discovery and movie detail navigation.
- [ ] Test navigation to login.
- [ ] Test login with a non-production test account.
- [ ] Test adding/removing a saved movie when supported.
- [ ] Test submitting/updating a rating when supported.
- [ ] Test recommendations and logout when supported.
- [ ] Do not run destructive automated tests against production user data.

## Phase 9 — Documentation, deployment, and release

### Documentation

- [ ] Write `MovieMind/frontend/README.md` covering purpose, stack, prerequisites, installation, local development, environment variables, FastAPI integration, tests, build, Vercel deployment, screenshots, and known limitations.
- [ ] Document confirmed API-contract assumptions and any unsupported specification features.
- [ ] Keep broad system architecture and ML methodology in the main project documentation rather than duplicating it excessively in the frontend README.

### Vercel deployment

- [ ] Push frontend changes to the teacher-required branch using small, meaningful commits.
- [ ] Create/import a separate Vercel frontend project with Root Directory set to `frontend/`.
- [ ] Verify Vercel uses the Vite build settings (`npm install`, `npm run build`, output `dist` unless configuration says otherwise).
- [ ] Set production `VITE_API_BASE_URL` to the real deployed HTTPS FastAPI URL.
- [ ] Coordinate exact production frontend origin(s) with the backend CORS allowlist.
- [ ] Configure credentials, `SameSite`, `Secure`, and CSRF handling according to the real auth deployment model.
- [ ] Add `frontend/vercel.json` SPA rewrite only if direct refresh of client routes returns 404.
- [ ] Test direct refresh on a nested route such as `/movies/:movieId` after deployment.
- [ ] Intentionally decide whether preview deployment origins/cookies are supported; do not open production CORS to arbitrary origins.

### Final verification and handoff

- [ ] Run configured lint/type-check command(s).
- [ ] Run `npm run test`.
- [ ] Run `npm run build`.
- [ ] Manually verify desktop, tablet, and mobile layouts.
- [ ] Manually verify API connectivity, authentication, ratings, saved movies, recommendations, error states, and logout based on implemented backend support.
- [ ] Review Git diff for secrets, generated files, debug logs, and accidental backend changes.
- [ ] Document deployment URL, test results, known limitations, and outstanding backend dependencies.
- [ ] Open a pull request against the teacher-required target branch when the repository workflow requires it.

## Final acceptance checklist

### Product

- [ ] React + TypeScript + Vite application runs locally.
- [ ] The layout is responsive and accessible.
- [ ] Navigation and all implemented routes work.
- [ ] Movie list, search, and detail data come from FastAPI—not mock data.
- [ ] Authentication exactly matches the backend contract.
- [ ] Ratings and saved movies persist through FastAPI when supported.
- [ ] Recommendations come from the backend model service when supported.
- [ ] Every API-driven view has loading, empty, error, and appropriate unauthorized states.
- [ ] No database connection, secrets, or recommendation logic exists in frontend code.

### Engineering and release

- [ ] TypeScript models represent confirmed API schemas without unnecessary `any`.
- [ ] Components are modular and API calls are feature-scoped and centralized.
- [ ] Critical components and workflows have suitable automated tests.
- [ ] Production build succeeds without major browser-console errors.
- [ ] Vercel uses `frontend/` and has the correct production API base URL.
- [ ] Backend CORS is limited to intentional frontend origins.
- [ ] Nested routes survive a direct browser refresh.
- [ ] No `.env`, test credential, or generated build artifact is committed.

## Suggested implementation order

1. Complete Phase 0 and confirm the actual FastAPI contract.
2. Complete the foundation and shared API client.
3. Deliver the public vertical slice: discovery, search, and movie details using real data.
4. Add authentication, then ratings/saved movies.
5. Add recommendations after eligibility/error contract is known.
6. Finish tests, responsive/accessibility work, deployment, and documentation.

This order deliberately produces a usable real-data application before implementing authenticated and model-dependent features.
