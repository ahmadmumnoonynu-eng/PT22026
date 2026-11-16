import { createBrowserRouter } from "react-router-dom";
import { lazy, Suspense, type ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { RouteFallback } from "@/app/RouteFallback";
import { RequireAuth } from "@/features/auth/RequireAuth";

const AuthPage = lazy(async () => ({ default: (await import("@/pages/AuthPage")).AuthPage }));
const DiscoverPage = lazy(async () => ({ default: (await import("@/pages/DiscoverPage")).DiscoverPage }));
const HomePage = lazy(async () => ({ default: (await import("@/pages/HomePage")).HomePage }));
const MovieDetailsPage = lazy(async () => ({ default: (await import("@/pages/MovieDetailsPage")).MovieDetailsPage }));
const MoviePreferencesPage = lazy(async () => ({ default: (await import("@/pages/MoviePreferencesPage")).MoviePreferencesPage }));
const NotFoundPage = lazy(async () => ({ default: (await import("@/pages/NotFoundPage")).NotFoundPage }));
const PlaceholderPage = lazy(async () => ({ default: (await import("@/pages/PlaceholderPage")).PlaceholderPage }));
const ProfilePage = lazy(async () => ({ default: (await import("@/pages/ProfilePage")).ProfilePage }));
const RatingsPage = lazy(async () => ({ default: (await import("@/pages/RatingsPage")).RatingsPage }));
const RecommendationsPage = lazy(async () => ({ default: (await import("@/pages/RecommendationsPage")).RecommendationsPage }));
const SearchPage = lazy(async () => ({ default: (await import("@/pages/SearchPage")).SearchPage }));
const WatchlistPage = lazy(async () => ({ default: (await import("@/pages/WatchlistPage")).WatchlistPage }));

function page(element: ReactNode) {
  return <Suspense fallback={<RouteFallback />}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { index: true, element: page(<HomePage />) },
      {
        path: "discover",
        element: page(<DiscoverPage />),
      },
      {
        path: "search",
        element: page(<SearchPage />),
      },
      {
        path: "movies/:movieId",
        element: page(<MovieDetailsPage />),
      },
      {
        path: "watchlist",
        element: page(<RequireAuth><WatchlistPage /></RequireAuth>),
      },
      {
        path: "ratings",
        element: page(<RequireAuth><RatingsPage /></RequireAuth>),
      },
      {
        path: "preferences",
        element: page(<RequireAuth><MoviePreferencesPage /></RequireAuth>),
      },
      {
        path: "profile",
        element: page(<RequireAuth><ProfilePage /></RequireAuth>),
      },
      {
        path: "settings",
        element: page(<RequireAuth><PlaceholderPage title="Settings" description="Only supported account settings will be added here." /></RequireAuth>),
      },
      {
        path: "recommendations",
        element: page(<RequireAuth><RecommendationsPage /></RequireAuth>),
      },
    ],
  },
  { path: "login", element: page(<AuthPage mode="login" />) },
  { path: "register", element: page(<AuthPage mode="register" />) },
  { path: "*", element: page(<NotFoundPage />) },
]);
