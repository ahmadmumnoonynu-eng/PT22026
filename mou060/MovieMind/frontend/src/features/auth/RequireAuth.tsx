import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";

import { PageLoader } from "@/components/ui/PageLoader";
import { useAuth } from "@/features/auth/AuthProvider";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  if (isLoading) return <PageLoader label="Restoring your MovieMind session…" />;
  if (!isAuthenticated) return <Navigate replace state={{ from: location }} to="/login" />;
  return <>{children}</>;
}
