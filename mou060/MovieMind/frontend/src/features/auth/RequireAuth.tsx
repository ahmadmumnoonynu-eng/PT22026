import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";

import { StatusPanel } from "@/components/ui/StatusPanel";
import { useAuth } from "@/features/auth/AuthProvider";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  if (isLoading) return <StatusPanel>Restoring your MovieMind session…</StatusPanel>;
  if (!isAuthenticated) return <Navigate replace state={{ from: location }} to="/login" />;
  return <>{children}</>;
}
