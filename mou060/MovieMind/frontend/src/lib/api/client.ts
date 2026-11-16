import axios from "axios";

import { authSession } from "@/lib/auth/session";
import { toApiClientError } from "@/lib/api/errors";

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() || "http://127.0.0.1:8000";
const apiBaseUrl = `${configuredBaseUrl.replace(/\/$/, "")}/api/v1`;

/**
 * The only shared HTTP client. Feature modules own their endpoint functions;
 * this module owns base URL, bearer auth, timeout, and common failures.
 */
export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: { Accept: "application/json", "Content-Type": "application/json" },
  timeout: 12_000,
});

apiClient.interceptors.request.use((config) => {
  const token = authSession.getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const normalized = toApiClientError(error);
    if (normalized.status === 401) authSession.clear();
    return Promise.reject(normalized);
  },
);
