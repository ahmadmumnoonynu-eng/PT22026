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
import { SearchPage } from "@/pages/SearchPage";

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
        element: <RequireAuth><PlaceholderPage title="My List" description="Your saved movies feature will be connected in the next authenticated feature phase." /></RequireAuth>,
      },
      {
        path: "ratings",
        element: <RequireAuth><PlaceholderPage title="My Ratings" description="Your ratings feature will be connected in the next authenticated feature phase." /></RequireAuth>,
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
        element: <RequireAuth><PlaceholderPage title="Recommended for You" description="Personalized recommendations will be connected after ratings and authentication are ready." /></RequireAuth>,
      },
    ],
  },
  { path: "login", element: <AuthPage mode="login" /> },
  { path: "register", element: <AuthPage mode="register" /> },
  { path: "*", element: <NotFoundPage /> },
]);
