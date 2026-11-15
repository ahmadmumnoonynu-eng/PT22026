# MovieMind UI/UX Design Skill

## Cinematic Companion --- Visual System and Frontend Implementation Guide

**Purpose:** This document is the design skill for the MovieMind
frontend AI coding agent. Use it together with
`FRONTEND_SPECIFICATION.md` and the supplied visual reference image,
**`MovieMind_ Your Cinematic Companion.png`**. The image is the primary
visual direction. The frontend specification remains the source of truth
for product scope, routes, backend integration, and technical
requirements.

The goal is to reproduce the same overall visual language and
layout---not to copy the screenshot as a static picture. Build a
responsive, accessible, functional React interface using real components
and real application data.

------------------------------------------------------------------------

# 1. Design direction

MovieMind should feel like a **premium, cinematic movie-discovery and
recommendation platform**.

The reference combines: - A deep navy/near-black cinema-inspired
background. - Rich violet and electric-purple accents. - Soft gradients,
restrained glows, and translucent dark surfaces. - Large cinematic
artwork and poster imagery. - Rounded cards and pill-shaped actions. - A
spacious dashboard with a left navigation rail, central discovery feed,
and right recommendation column. - Clear, confident typography with
strong contrast and hierarchy.

The experience should feel immersive and polished, but remain easy to
scan and use. Avoid making every element glow or adding decoration that
competes with movie artwork.

## Design principles

1.  **Artwork leads.** Movie posters and the hero visual should be the
    most visually prominent elements.
2.  **Dark, not muddy.** Use layered navy surfaces and clear text
    contrast rather than one flat black background.
3.  **Purple is the action color.** Use it for primary actions, active
    navigation, selected states, and small highlights.
4.  **Hierarchy before decoration.** Section titles, movie titles,
    ratings, and actions must be immediately understandable.
5.  **Consistent components.** Reuse the same card radius, spacing,
    button styles, icon sizes, and interaction states.
6.  **Responsive by design.** Preserve the visual identity on laptop,
    tablet, and mobile; do not simply shrink the desktop layout.
7.  **Real functionality.** Every visible button, link, search field,
    and navigation item must work or be clearly represented as
    unavailable/coming soon.

------------------------------------------------------------------------

# 2. Reference layout anatomy

The reference is a desktop dashboard with three main zones:

``` text
┌──────────────────┬───────────────────────────────────────────────┬──────────────────────┐
│                  │ Search bar                         Profile    │                      │
│  Brand / logo    ├───────────────────────────────────────────────┤                      │
│                  │                                               │                      │
│  Main navigation │ Hero / welcome banner                         │                      │
│                  │                                               │ Recommendations     │
│  Upgrade card    ├───────────────────────────────────────────────┤ panel                │
│                  │ Trending Now                                  │                      │
│                  │ Horizontal movie-card row                     │                      │
│                  ├───────────────────────────────────────────────┤                      │
│                  │ Top Rated Movies                               │                      │
│                  │ Horizontal movie-card row                     │ Next movie adventure │
│                  │                                               │ promotional panel    │
└──────────────────┴───────────────────────────────────────────────┴──────────────────────┘
```

## 2.1 Left sidebar

A fixed-width vertical navigation rail anchors the desktop experience.

**Contents, top to bottom:** - MovieMind logo/icon and wordmark. - Short
tagline: "Discover. Watch. Enjoy." - Home (active in the reference). -
Discover. - My List. - Ratings. - Profile. - Settings. - A separated
upgrade-to-Pro promotional card near the bottom.

**Styling:** - Dark navy surface, subtly distinct from the page
background. - Thin right divider. - Brand icon in a purple gradient;
wordmark primarily white with a purple accent on "Mind". - Navigation
rows have consistent height, left-aligned icons, and readable labels. -
Active item uses a bright purple gradient, rounded corners, and a soft
glow. Inactive items are muted lavender/grey. - Upgrade card uses a
subtle purple border and warm gold crown/accent. It must not dominate
the navigation.

**Behavior:** - Active navigation state follows the current route. - All
navigation items must link to their corresponding supported routes. - If
a route is not implemented, do not create a dead-looking control; either
implement the route, hide the item until available, or show a clear
disabled state. - On smaller screens, convert the sidebar into a drawer
or compact navigation pattern.

## 2.2 Top bar

The main content area begins with a compact top bar: - Search field on
the left. - Notification control and user avatar/profile menu on the
right.

**Search field:** - Rounded pill/soft capsule. - Search icon on the
left. - Placeholder: "Search for movies, genres..." - Dark translucent
surface with a subtle border. - Clear focus ring and visible keyboard
focus. - Search submission should navigate to the search results page or
update the search results view.

**Profile controls:** - Circular avatar, notification icon, and dropdown
indicator. - Use the actual signed-in user when authentication/profile
data exists. - Provide accessible labels and keyboard-operable menus. -
Do not invent notifications or user data. Use a neutral empty state if
the backend does not provide them.

## 2.3 Hero banner

The hero is the visual centerpiece of the home dashboard.

**Composition:** - Wide cinematic background artwork spanning the
central content column. - Dark gradient overlay behind text so the
heading remains legible. - Small eyebrow label: "MovieMind". - Large
heading: "Your Personal Movie Companion". - Highlight "Companion" with a
violet gradient or accent. - Supporting copy: "Get AI-powered
recommendations and discover movies you'll love!" - Primary action:
"Start Exploring". - Secondary action: "Learn More". - Optional slide
indicators only if the hero is genuinely implemented as a carousel.

**Visual treatment:** - Large rounded visual region with a soft lower
fade into the page background. - Purple/blue atmospheric lighting is
acceptable, but keep text readable. - Keep the artwork visually rich
while ensuring the copy and actions remain the focal point. - Use the
supplied image as a visual reference; do not use the screenshot itself
as the hero background.

**Behavior:** - "Start Exploring" should navigate to the discovery
experience. - "Learn More" should open a real information section/page
or be omitted if no destination exists. - If multiple hero slides are
implemented, provide working controls, accessible labels, and
reduced-motion support. Otherwise use a single static hero.

## 2.4 Main content column

The center column contains stacked discovery sections. Each section
has: - A section heading with a small thematic icon/emoji. - Optional
"See All" text link aligned to the right. - A horizontal row or
responsive grid of movie cards.

Reference section examples: - "🔥 Trending Now" - "⭐ Top Rated Movies"

Use actual backend/API data when available. Do not hardcode screenshot
titles as the application's permanent dataset. For development, use
clearly identified mock data until API integration is ready.

## 2.5 Right recommendation rail

On wide screens, a narrower right-hand column contains two stacked
panels.

**Panel A --- Your Recommendations** - Heading with a small sparkle
icon. - Supporting line: "Based on your ratings and interests". -
Compact vertical list of recommended movies. - Each row includes a small
poster, title, rating, genre/category where available, and a circular
purple action control.

The action should have a clear purpose, such as opening movie details.
Do not use a play icon if the app cannot actually play films; MovieMind
is a discovery/recommendation product, not a streaming service.

**Panel B --- Next movie adventure** - Short promotional heading. -
Primary action such as "Get Recommendations". - Supporting movie-reel
artwork on the right. - Dark purple/plum gradient surface with a subtle
border.

**Responsive behavior:** - On medium screens, move this rail below the
central content or convert it into full-width sections. - On mobile,
show recommendation content as a normal section in the page flow. Never
squeeze it into a narrow side column.

------------------------------------------------------------------------

# 3. Design tokens

The values below are a practical implementation palette inferred from
the supplied reference. Treat them as the starting design system and
keep them centralized in CSS variables or the project's theme
configuration. Fine-tune against the reference during implementation.

## 3.1 Color palette

  Token                                 Suggested value Usage
  ----------------------- ----------------------------- --------------------------------------
  `--mm-bg`                                   `#080B1B` Main application background
  `--mm-bg-elevated`                          `#0D1126` Sidebar and elevated page regions
  `--mm-surface`                              `#12172F` Movie cards and panels
  `--mm-surface-strong`                       `#1A1D3B` Raised cards, search field
  `--mm-surface-glass`         `rgba(28, 24, 61, 0.78)` Translucent panels
  `--mm-primary`                              `#762BFA` Primary purple
  `--mm-primary-bright`                       `#923CFF` Hover/bright accent
  `--mm-primary-deep`                         `#4D18C9` Gradient depth
  `--mm-accent`                               `#C17BFF` Highlight text and secondary accents
  `--mm-gold`                                 `#FFBE3D` Ratings, crown, premium highlights
  `--mm-text`                                 `#F7F5FF` Main text
  `--mm-text-muted`                           `#B5B4CC` Secondary text
  `--mm-text-subtle`                          `#8586A5` Placeholder and tertiary text
  `--mm-border`             `rgba(164, 151, 220, 0.16)` Subtle borders
  `--mm-success`                              `#35C98A` Success feedback
  `--mm-danger`                               `#F06B83` Error/destructive feedback

**Important:** These are suggested tokens, not color values sampled
exactly from the screenshot. Keep them consistent and adjust visually
after rendering.

## 3.2 Gradients and effects

Use gradients selectively: - Primary button:
`linear-gradient(110deg, #6D24F5 0%, #963BFF 100%)` - Active navigation:
a similar purple gradient with a soft outer glow. - Hero overlay:
transparent-to-deep-navy gradient, strongest behind text and near the
lower edge. - Premium/recommendation panels: subtle navy-to-plum
gradient.

Suggested shadow language: - Cards: soft, low-opacity navy shadow. -
Primary actions: subtle purple glow, stronger on hover. - Focus: visible
2px purple/lavender outline with offset. - Avoid large, constant neon
glows around every component.

## 3.3 Typography

Use a modern sans-serif family such as **Inter** or **Manrope**. Prefer
one family across the product.

Hierarchy: - Hero heading: large, bold, tight line-height. - Section
headings: 20--24px, semibold/bold. - Movie titles: 14--16px, semibold. -
Body/supporting text: 14--16px. - Metadata: 12--13px. -
Buttons/navigation: 14--15px, medium/semibold.

Use consistent weights and line heights. Avoid excessive letter spacing.
Ensure text remains readable against artwork and dark surfaces.

## 3.4 Shape and spacing

-   Main cards/panels: 16--22px radius.
-   Poster images: 12--16px radius at the top corners or full card
    radius where appropriate.
-   Buttons: pill-shaped or 12--18px radius, matching the reference.
-   Search field: pill-shaped.
-   Sidebar active item: 14--18px radius.
-   Use a consistent spacing scale (4, 8, 12, 16, 20, 24, 32, 40, 48px).
-   Keep consistent gaps between sections and card rows.

------------------------------------------------------------------------

# 4. Movie card system

Movie cards are a core reusable component. Build one consistent card
component and use it in Trending, Top Rated, Search Results, and other
movie collections.

## Standard movie card anatomy

1.  Poster image with a fixed, consistent aspect ratio (prefer 2:3).
2.  Optional subtle image overlay for legibility.
3.  Movie title.
4.  Rating with a gold star icon and numeric value, when available.
5.  A small action to add/remove from the user's list, when that feature
    exists.

**Visual requirements:** - Poster image should fill its frame using
`object-fit: cover`. - Avoid stretching or distorting posters. - Keep
card widths consistent within a row. - Use a dark metadata footer. - Use
a subtle hover lift/scale (small enough not to disrupt the layout). - On
hover/focus, reveal or emphasize available actions without making them
inaccessible on touch devices. - Provide image fallback artwork when a
poster is missing. - Clamp long titles to a predictable number of lines
without hiding essential information.

**Interaction requirements:** - Clicking the poster/title opens the
movie details route. - Add/remove action updates the user's list and
reflects loading/success/error state. - Do not show an "Add" action as
successful until the API confirms it. - Prevent nested click targets
from triggering duplicate navigation. - Make icon-only actions
accessible with descriptive `aria-label` text.

## Compact recommendation row

Use a separate compact layout for the right recommendation panel: -
Small 2:3 poster thumbnail. - Movie title. - Rating and genre/category
metadata if provided. - One clear action, preferably opening details. -
Rows should align consistently and remain readable at narrow widths.

------------------------------------------------------------------------

# 5. Buttons, controls, and interaction states

Create reusable button variants: - **Primary:** purple gradient, white
text, clear hover/focus/pressed states. - **Secondary:**
dark/translucent surface, subtle border, white/lavender text. -
**Ghost:** transparent background, muted text, hover surface. - **Icon
button:** consistent square/circular hit area with tooltip or accessible
label.

Every interactive component must support: - Default. - Hover (pointer
devices). - Focus-visible (keyboard). - Active/pressed. - Disabled. -
Loading where an asynchronous action occurs. - Error/success feedback
where relevant.

Use transitions around 150--220ms for color, border, shadow, and small
transforms. Respect `prefers-reduced-motion`; do not rely on animation
to communicate state.

------------------------------------------------------------------------

# 6. Detailed page-by-page UI/UX specifications

The Home dashboard is only one part of MovieMind. Every route must feel
like the same product, using the shared design tokens and components,
while each page has a layout suited to its purpose.

Use the route names and backend capabilities defined in
`FRONTEND_SPECIFICATION.md`. If the actual repository or API uses
different route names, preserve the existing agreed routes rather than
silently creating duplicates.

## 6.1 Shared application shell

All authenticated/main application pages should reuse a consistent
shell: - Desktop: left sidebar, top header, page content, and optional
right rail where useful. - The sidebar remains visually consistent
across routes; the current route is highlighted. - The top header
contains the global search control and user actions. - The main content
begins with a page heading and optional subtitle/breadcrumb. - Use a
consistent content max-width and page padding so pages align with the
Home dashboard. - Do not force the right recommendation rail onto every
page. Use it only where it adds value; otherwise allow the main page
content to use the available width. - On mobile, use a compact header
and mobile navigation pattern; page content becomes a single column.

For pages that require authentication, show the agreed
login/unauthorized flow. Do not invent access rules that conflict with
the backend.

## 6.2 Discover page --- `/discover` (or the route already defined in the frontend specification)

**Purpose:** Let users explore movies intentionally, beyond the curated
Home dashboard.

**Desktop layout:** 1. Page heading: "Discover Movies", with a short
subtitle such as "Find your next favorite film". 2. A prominent
search/filter toolbar beneath the heading. 3. A filter row or compact
filter panel with only filters supported by available data/API, such as
genre, release year, rating, or sort order. 4. A responsive movie poster
grid as the main content. 5. Pagination or a "Load more" control if
supported by the data source.

**Visual design:** - Keep the dark navy page background. - Put filters
in a slightly raised surface with subtle borders. - Selected filters use
purple chips or purple-tinted controls. - Movie cards use the shared
standard poster-card component. - Keep the grid visually dense enough
for discovery, but leave clear gutters between cards.

**Interactions and states:** - Filters must visibly show selected values
and provide a clear reset action. - Search and filters should work
together without unexpectedly clearing one another. - Loading uses a
grid of poster-shaped skeletons. - No-results state explains that no
movies match and offers "Clear filters". - Error state offers retry
where safe. - Do not display filter options that the backend cannot
support; if a filter is frontend-only, explain its source and behavior
in code comments/documentation.

## 6.3 Search page --- `/search`

**Purpose:** Present results for the user's query and help refine the
search.

**Desktop layout:** 1. Page title "Search Results". 2. Search input near
the top, prefilled with the current query. 3. A short result summary,
such as "Results for ...", and result count only if the API provides a
reliable count. 4. Optional supported filters/sort controls. 5.
Responsive poster grid with the shared movie cards.

**Visual design:** - Make the search input more prominent than ordinary
filter controls. - Keep query and filter controls visually grouped. -
Use the same card dimensions as Discover so the product feels
consistent. - Search results should use the full main content width; the
right rail is optional and usually omitted.

**Interactions and states:** - Submit on Enter and provide a clear
search action. - Preserve the query in the URL where practical. -
Provide a clear control to remove the query. - Distinguish initial state
("Search for a movie to get started"), loading, results, no results, and
request failure. - Avoid firing an API request on every keystroke unless
debouncing is implemented. - Clicking a result opens its movie details
page.

## 6.4 Movie details page --- `/movies/:movieId`

**Purpose:** Give one movie a cinematic, information-rich page and
provide clear next actions.

**Desktop layout:** 1. A wide backdrop/hero area at the top, using the
movie's backdrop when available. 2. Dark gradient overlay to protect
text contrast. 3. Poster artwork anchored to the left side of the
information area, with rounded corners. 4. To the right: movie title,
release year, rating, genres, runtime and other metadata only when
available. 5. Overview/synopsis in a readable text width. 6. Primary
actions: "Add to My List" / "Remove from My List" and "Rate this Movie",
only where supported. 7. Below the hero: sections such as "More Like
This" or recommendations only if the backend exposes the corresponding
data. 8. Optional cast/crew or production details only if present in the
actual movie model.

**Visual design:** - Use a large cinematic image but keep it subordinate
to readable content. - Use gold for rating emphasis and purple for
primary actions. - Use compact metadata chips with consistent spacing. -
Separate lower content sections with clear headings and generous
vertical spacing. - Avoid inventing trailer playback, streaming, or
purchase actions. MovieMind is a discovery/recommendation product unless
the product specification explicitly adds streaming.

**Interactions and states:** - The movie title/poster should have a
stable loading skeleton. - Missing backdrop or poster uses a branded
fallback. - Add/remove actions show pending, success, and error states
based on API responses. - Rating controls must be keyboard accessible
and clearly show the selected value. - Invalid or missing movie IDs
should show a useful not-found state with a route back to Discover. -
Related movies link to their own details pages.

## 6.5 My List page --- `/watchlist` or the route defined in the frontend specification

**Purpose:** Let users revisit movies they have saved.

**Desktop layout:** 1. Heading: "My List", with a short explanatory
subtitle. 2. Optional summary count only if the count is available and
accurate. 3. A responsive poster grid using the standard movie card. 4.
Optional sort control if supported (for example, recently added or
title).

**Visual design:** - This page should feel calm and personal rather than
promotional. - Use the same dark surfaces and poster cards as
Discover. - Give the saved collection enough space; do not add a right
rail that squeezes the grid. - Make the remove action discoverable
without cluttering every card.

**Interactions and states:** - Removing a movie updates the list only
after the API confirms success. - Empty state: a simple film/bookmark
illustration or icon, heading "Your list is empty", short guidance, and
a "Discover Movies" action. - Loading state uses poster skeletons. -
Error state offers retry. - If the user is not authenticated, follow the
backend's actual authentication requirement and provide a clear login
route.

## 6.6 Recommendations page --- `/recommendations`

**Purpose:** Present personalized movie suggestions and explain why they
may fit the user's taste.

**Desktop layout:** 1. Heading: "Recommended for You" and a concise
subtitle. 2. A short explanation of the recommendation basis, such as
ratings/interests, only if that basis is actually supported by the
recommender. 3. A featured recommendation area for the top suggestion,
if the API returns ranked recommendations and enough metadata. 4. A
responsive grid/list of recommended movie cards. 5. Optional sections
such as "Because you liked..." or "Explore a different genre" only when
the API provides the required explanation/data.

**Visual design:** - Use purple/sparkle accents sparingly to signal
personalization. - The featured item may use a wider backdrop card, but
ordinary recommendations should remain consistent with standard movie
cards. - Show rank or match score only if the backend supplies a
meaningful value; do not fabricate percentages or "AI confidence". - A
compact reason label is preferable to long technical explanations.

**Interactions and states:** - Movie cards open details. - "Refresh
recommendations" should call a real supported endpoint; otherwise omit
it. - If the user has not rated enough movies, show an onboarding empty
state explaining that rating a few movies can improve recommendations,
with a link to Discover. - If no personalized results are available,
distinguish that from a network error. - Clearly label
general/popularity-based fallback recommendations if the backend uses
them instead of personalized results.

## 6.7 Login page --- `/login`

**Purpose:** Provide a focused, trustworthy sign-in experience.

**Layout:** - Use a full-viewport dark navy background with a restrained
purple/blue cinematic glow or blurred artwork. - Center a single focused
authentication panel; do not show the full dashboard sidebar. - Place
the MovieMind logo/wordmark above or inside the panel. - Heading:
"Welcome back" with a short supporting sentence. - Email/username and
password fields according to the actual backend contract. - Primary
full-width "Sign In" button. - Link to registration. - Optional password
visibility toggle. - Add a simple link back to Home if guest browsing is
supported.

**Visual design:** - Panel uses a raised dark surface, subtle border,
18--24px radius, and restrained shadow. - Inputs have clear labels,
consistent height, and visible focus states. - Primary action uses the
purple gradient. - Keep decorative imagery low contrast so it never
competes with the form.

**Behavior:** - Validate required fields and formats before submission
where appropriate. - Show server authentication errors in a clear,
non-technical message. - Disable duplicate submissions while loading. -
Do not invent social login, password reset, or remember-me behavior
unless implemented and supported. - Follow the backend specification for
token/session handling; never expose secrets in frontend code.

## 6.8 Registration page --- `/register`

**Purpose:** Let a new user create an account with minimal friction.

**Layout:** - Reuse the Login page background and centered panel. -
Heading: "Create your account". - Include only fields required by the
actual registration API (for example, name, email, password, and
confirmation only if the frontend validates it locally). - Primary
full-width "Create Account" button. - Link to Login for existing
users. - A short privacy/terms note only if the project has real
corresponding policies.

**Visual design and behavior:** - Match Login exactly in panel width,
field styles, spacing, typography, and button design. - Show field-level
validation and server errors. - Password requirements should be
displayed only when known. - Show a clear success/next step after
account creation, based on the backend response. - Do not assume email
verification exists unless the backend implements it.

## 6.9 Profile page --- `/profile`

**Purpose:** Show and, where supported, let the user update their
account information.

**Layout:** 1. Heading: "My Profile". 2. Profile summary card with
avatar/initials, display name, and email or username where permitted. 3.
Edit form for fields the backend actually allows users to update. 4.
Optional account statistics (ratings count, saved movies count) only
when supported and accurate. 5. Save action with clear
pending/success/error feedback.

**Visual design:** - Use a two-column layout on wide screens only if it
improves clarity: profile summary on one side and editable details on
the other. - On mobile, stack sections. - Use the same panel and form
styles as authentication. - Use a neutral avatar fallback if no profile
image exists.

**Behavior:** - Prefill fields from the authenticated user's actual
profile data. - Do not allow editing server-controlled fields such as
role or account ID. - Validate and submit only fields supported by the
API. - Show a clear unsaved-changes state if navigation could discard
edits.

## 6.10 Ratings page --- `/ratings`

**Purpose:** Let users review movies they have rated and manage their
ratings.

**Layout:** 1. Heading: "My Ratings" with a short subtitle. 2. Optional
summary such as number of rated movies, if supplied. 3. A list or
responsive grid of rated movies. 4. Each item shows poster, title,
user's rating, and an edit action. 5. Optional sort order if supported
(for example, most recently rated or highest rated).

**Visual design:** - Prefer a slightly more information-dense layout
than Discover. - Keep posters smaller than the main discovery cards if
using a list. - Use gold stars to display rating values, while ensuring
the numeric rating is also visible. - Make the user's rating visually
distinct from a public/average rating.

**Behavior:** - Editing a rating opens an accessible dialog or inline
editor. - Show the selected rating and save/cancel actions. - Confirm
successful updates from the API before changing the persisted state. -
Empty state should invite the user to discover movies and rate a few. -
Do not confuse the user's own rating with the movie's external or
average rating.

## 6.11 Settings page --- `/settings`

**Purpose:** Provide a small, understandable place for supported
application preferences and account actions.

**Layout:** - Heading: "Settings". - Group settings into clear
panels/sections, for example: - Appearance (only if theme switching is
implemented; otherwise the dark theme can remain fixed). -
Recommendation preferences (only if supported). - Account/security
actions (only if supported by backend). - Sign out. - Use labeled
controls with short explanatory text. - Keep destructive actions
visually distinct and require confirmation where appropriate.

**Visual design:** - Use simple settings rows with labels on the left
and controls on the right. - Separate groups with spacing and subtle
dividers. - Avoid building a large settings dashboard for options that
do not exist.

**Behavior:** - Persist settings only through a real supported
mechanism. - Clearly distinguish saved preferences from local-only UI
state. - Sign out must use the actual authentication flow and return the
user to an appropriate public page. - Do not create fake toggles for
unimplemented features.

## 6.12 Not Found page --- `*` / 404

**Purpose:** Help users recover from an invalid route without making the
app feel broken.

**Layout and visual design:** - Keep the shared dark MovieMind
background. - Center a compact panel with a film-themed
icon/illustration. - Large "404" label and heading such as "This scene
is missing". - Short explanation and a prominent "Back to Home" or
"Discover Movies" action. - Do not display a blank page or raw router
error.

**Behavior:** - Main action navigates to a valid route. - Preserve the
shared shell only if that is consistent with the routing structure;
otherwise use a standalone centered layout. - Ensure unknown URLs do not
crash the application.

## 6.13 Upgrade / Pro presentation

The reference includes an Upgrade to Pro card in the sidebar. Treat this
as a visual element only if a real Pro tier, pricing, or upgrade flow is
part of the agreed product scope.

-   If a Pro feature/payment flow exists, link to its real page and
    clearly describe actual benefits.
-   If no Pro plan exists in the backend/product scope, omit the upgrade
    card or replace it with a non-commercial "Improve your
    recommendations" prompt.
-   Never imply a payment, subscription, or premium entitlement exists
    when it does not.

# 7. Responsive behavior

The desktop screenshot is the main visual reference, but the application
must work at all viewport sizes.

Suggested breakpoints (adjust to the existing project conventions): -
**Large desktop:** 1280px and above --- sidebar, center content, and
right rail. - **Desktop/tablet:** 1024--1279px --- compact sidebar and
narrower content; right rail may move below. - **Tablet:** 768--1023px
--- sidebar becomes compact/drawer; one main content column. -
**Mobile:** below 768px --- mobile header/navigation, one-column page
flow, horizontally scrollable poster rails or a two-column poster grid
depending on available width.

Rules: - Never cause horizontal page overflow. - Keep poster aspect
ratios consistent. - Make touch targets comfortably large (aim for at
least 44×44 CSS pixels). - Keep primary actions visible and reachable. -
Do not hide essential controls behind hover-only behavior. - Use a
mobile navigation drawer or bottom navigation if it provides a clearer
experience. - The right recommendation rail must become normal content
on smaller screens. - Test at narrow phone widths, not only desktop
emulation.

------------------------------------------------------------------------

# 8. Accessibility and usability

Accessibility is part of the design, not a later decoration.

-   Use semantic landmarks: header, nav, main, aside, section, footer as
    appropriate.
-   Use a logical heading hierarchy.
-   Ensure text contrast is sufficient against all surfaces and image
    overlays.
-   Provide visible keyboard focus.
-   All controls must be keyboard operable.
-   Give icon-only controls accessible names.
-   Add meaningful alt text to informative poster/artwork images; use
    empty alt text for purely decorative imagery.
-   Do not communicate rating, selection, or status by color alone.
-   Respect reduced-motion preferences.
-   Ensure dialogs and dropdowns manage focus and close behavior
    correctly.
-   Forms need persistent labels and clear error associations.

------------------------------------------------------------------------

# 9. Loading, empty, and error states

The visual quality must remain consistent beyond the happy path.

**Loading** - Use skeleton cards that match the final poster/card
geometry. - Use subtle shimmer only if it does not cause distracting
motion. - Disable duplicate submissions while an action is pending.

**Empty** - Use concise, friendly copy and one relevant next action. -
Examples: "Your list is empty" or "No movies match this search." - Do
not leave large blank regions without explanation.

**Error** - Use a clear message and retry action when retry is safe. -
Do not expose stack traces, internal server details, or secrets. - Keep
the rest of the page usable if only one content section fails.

**Image failure** - Render a branded fallback tile with a film/poster
icon or neutral artwork. - Preserve the card's dimensions to prevent
layout shifts.

------------------------------------------------------------------------

# 10. Motion and micro-interactions

Use motion to make the interface feel responsive, not theatrical.

Appropriate: - Small card lift on hover. - Slight image zoom on hover. -
Smooth active navigation transition. - Button hover glow. - Short
fade/slide for menus and dialogs. - Skeleton shimmer where appropriate.

Avoid: - Constant pulsing glows. - Large parallax effects. - Long
entrance animations that delay content. - Animations that make scrolling
or reading uncomfortable.

All motion must have a reduced-motion alternative.

------------------------------------------------------------------------

# 11. Image and asset guidance

-   Use real movie poster images from a legitimate movie-data/image
    source already selected by the project, or use approved development
    placeholders.
-   Do not scrape random image URLs or invent poster paths.
-   Keep image loading resilient and use lazy loading for below-the-fold
    posters.
-   Reserve image dimensions/aspect ratios to reduce layout shift.
-   Use the supplied reference screenshot to guide layout, color,
    spacing, and mood---not as a source of individual poster assets.
-   The screenshot's robot/cinema hero is a design reference. Use a
    separate licensed/approved hero image or a suitable project-created
    asset.
-   Do not include assets or fonts with unclear licensing in the
    deployed application.

------------------------------------------------------------------------

# 12. Frontend implementation rules for the AI agent

Before coding: 1. Read `FRONTEND_SPECIFICATION.md` completely. 2. Read
the backend specification and inspect the actual FastAPI OpenAPI schema.
3. Inspect the current repository, existing folder structure, package
manager, and installed dependencies. 4. Locate and inspect the supplied
MovieMind reference image. 5. Identify existing reusable components and
styles before creating replacements. 6. Create `TASKS.md` in the
frontend project root with ordered, actionable UI implementation tasks,
dependencies, and acceptance criteria. 7. Present the proposed task
breakdown and wait for the project owner's approval before implementing.

During implementation: - Follow the product routes and API contract in
the frontend specification. Do not invent API endpoints or response
fields. - Keep design tokens centralized; do not scatter arbitrary
colors and spacing values across components. - Build reusable components
for navigation, buttons, movie cards, section headers, recommendation
rows, panels, and feedback states. - Use real API data when integration
is ready; label temporary mock data clearly. - Keep components
responsive and accessible from the beginning. - Keep API/data logic
separate from presentation components. - Avoid giant page components and
duplicated markup. - Do not use the screenshot as a single background
image or recreate the page as a non-functional static mockup. - Do not
add unrelated features or change the agreed technology stack without
approval. - Do not claim an action works unless it is connected to a
real route or API operation.

After each task: 1. Run the relevant lint, type-check, and tests
available in the project. 2. Verify the page at desktop and mobile
sizes. 3. Check keyboard focus and interactive states. 4. Update
`TASKS.md` only after the task is implemented and verified. 5. Report
changed files, what was implemented, commands/tests run, results, and
any blockers. 6. Stop at the next task boundary and wait for the project
owner's instruction if the workflow is being done step by step.

------------------------------------------------------------------------

# 13. Definition of done

The design implementation is ready for review when:

-   [ ] The desktop dashboard clearly follows the supplied three-zone
    reference composition.
-   [ ] The visual system uses consistent dark navy surfaces, purple
    accents, typography, radii, and spacing.
-   [ ] The hero has a readable overlay, clear heading, supporting copy,
    and working actions.
-   [ ] Movie cards use consistent poster ratios and display real or
    clearly identified development data.
-   [ ] Trending and Top Rated sections are visually consistent.
-   [ ] The recommendation rail is present on wide screens and reflows
    naturally on smaller screens.
-   [ ] Sidebar active states match the current route.
-   [ ] Search, profile, navigation, and movie actions have real
    behavior or honest disabled states.
-   [ ] Loading, empty, error, and missing-image states are designed.
-   [ ] Mobile/tablet layouts do not overflow or hide essential actions.
-   [ ] Keyboard focus, accessible names, labels, and reduced-motion
    behavior are supported.
-   [ ] No invented API contracts, fake successful actions, or exposed
    secrets are present.
-   [ ] Linting, type-checking, and relevant tests pass.

------------------------------------------------------------------------

# 14. Final instruction

**Treat the supplied MovieMind screenshot as the visual north star.**
Recreate its cinematic dark-purple identity, dashboard composition,
visual hierarchy, and polished movie-card experience while building a
genuinely responsive and functional React application. When the
screenshot and the written product specification appear to conflict,
preserve the product/API requirements from `FRONTEND_SPECIFICATION.md`
and use the screenshot for visual direction. Ask before making a major
design or architecture change.
