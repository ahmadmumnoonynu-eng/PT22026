import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, type PropsWithChildren, useContext, useEffect, useMemo, useState } from "react";

import { fetchCurrentUser, login, register, type LoginPayload, type RegisterPayload } from "@/features/auth/api";
import { authSession } from "@/lib/auth/session";
import { queryKeys } from "@/lib/query/keys";
import type { User } from "@/types/api";

export type AuthContextValue = {
  isAuthenticated: boolean;
  isLoading: boolean;
  signIn: (payload: LoginPayload) => Promise<User>;
  signOut: () => void;
  signUp: (payload: RegisterPayload) => Promise<User>;
  user: User | null;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState(() => authSession.getToken());
  const me = useQuery({
    queryKey: queryKeys.user.me(),
    queryFn: ({ signal }) => fetchCurrentUser(signal),
    enabled: Boolean(token),
    staleTime: 60_000,
    retry: false,
  });

  useEffect(() => authSession.subscribe(setToken), []);

  async function signIn(payload: LoginPayload) {
    const response = await login(payload);
    authSession.setToken(response.access_token);
    try {
      return await queryClient.fetchQuery({
        queryKey: queryKeys.user.me(),
        queryFn: () => fetchCurrentUser(),
        staleTime: 60_000,
      });
    } catch (error) {
      authSession.clear();
      throw error;
    }
  }

  async function signUp(payload: RegisterPayload) {
    const response = await register(payload);
    authSession.setToken(response.access_token);
    queryClient.setQueryData(queryKeys.user.me(), response.user);
    return response.user;
  }

  function signOut() {
    authSession.clear();
    queryClient.removeQueries({ queryKey: queryKeys.user.me() });
  }

  const value = useMemo<AuthContextValue>(() => ({
    isAuthenticated: Boolean(token) && Boolean(me.data),
    isLoading: Boolean(token) && me.isLoading,
    signIn,
    signOut,
    signUp,
    user: me.data ?? null,
  }), [me.data, me.isLoading, token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
