import { apiClient } from "@/lib/api/client";
import type { RegisterResponse, TokenResponse, User } from "@/types/api";

export type LoginPayload = { email: string; password: string };
export type RegisterPayload = { display_name?: string; email: string; password: string; username?: string };

export async function login(payload: LoginPayload) {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
  return data;
}

export async function register(payload: RegisterPayload) {
  const { data } = await apiClient.post<RegisterResponse>("/auth/register", payload);
  return data;
}

export async function fetchCurrentUser(signal?: AbortSignal) {
  const { data } = await apiClient.get<User>("/users/me", { signal });
  return data;
}

export async function updateCurrentUser(payload: { display_name?: string; username?: string }) {
  const { data } = await apiClient.patch<User>("/users/me", payload);
  return data;
}
