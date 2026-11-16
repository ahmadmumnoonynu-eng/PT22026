import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { RequireAuth } from "@/features/auth/RequireAuth";
import { AuthPage } from "@/pages/AuthPage";
import { HomePage } from "@/pages/HomePage";
import { DiscoverPage } from "@/pages/DiscoverPage";
import { MovieDetailsPage } from "@/pages/MovieDetailsPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";
import { ProfilePage } from "@/pages/ProfilePage";
import { RatingsPage } from "@/pages/RatingsPage";
import { RecommendationsPage } from "@/pages/RecommendationsPage";
import { SearchPage } from "@/pages/SearchPage";
import { WatchlistPage } from "@/pages/WatchlistPage";

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: "discover",
        element: <DiscoverPage />,
      },
      {
        path: "search",
        element: <SearchPage />,
      },
      {
        path: "movies/:movieId",
        element: <MovieDetailsPage />,
      },
      {
        path: "watchlist",
        element: <RequireAuth><WatchlistPage /></RequireAuth>,
      },
      {
        path: "ratings",
        element: <RequireAuth><RatingsPage /></RequireAuth>,
      },
      {
        path: "profile",
        element: <RequireAuth><ProfilePage /></RequireAuth>,
      },
      {
        path: "settings",
        element: <RequireAuth><PlaceholderPage title="Settings" description="Only supported account settings will be added here." /></RequireAuth>,
      },
      {
        path: "recommendations",
        element: <RequireAuth><RecommendationsPage /></RequireAuth>,
      },
    ],
  },
  { path: "login", element: <AuthPage mode="login" /> },
  { path: "register", element: <AuthPage mode="register" /> },
  { path: "*", element: <NotFoundPage /> },
]);
