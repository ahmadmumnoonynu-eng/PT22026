import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { AuthPlaceholderPage } from "@/pages/AuthPlaceholderPage";
import { HomePage } from "@/pages/HomePage";
import { DiscoverPage } from "@/pages/DiscoverPage";
import { MovieDetailsPage } from "@/pages/MovieDetailsPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";
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
        element: <PlaceholderPage title="My List" description="Your saved movies will appear here after authentication is connected." />,
      },
      {
        path: "ratings",
        element: <PlaceholderPage title="My Ratings" description="Your ratings will appear here after the ratings feature is connected." />,
      },
      {
        path: "profile",
        element: <PlaceholderPage title="My Profile" description="Profile information will be available after authentication is connected." />,
      },
      {
        path: "settings",
        element: <PlaceholderPage title="Settings" description="Only supported account settings will be added here." />,
      },
      {
        path: "recommendations",
        element: <PlaceholderPage title="Recommended for You" description="Personalized recommendations will be connected after ratings and authentication are ready." />,
      },
    ],
  },
  { path: "login", element: <AuthPlaceholderPage mode="login" /> },
  { path: "register", element: <AuthPlaceholderPage mode="register" /> },
  { path: "*", element: <NotFoundPage /> },
]);
