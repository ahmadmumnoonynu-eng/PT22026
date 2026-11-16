type SessionListener = (accessToken: string | null) => void;

let accessToken: string | null = null;
const listeners = new Set<SessionListener>();

function notify() {
  listeners.forEach((listener) => listener(accessToken));
}

/**
 * Temporary in-memory session state for the bearer-token backend contract.
 *
 * Tokens intentionally are not persisted to localStorage. The authentication
 * feature will use this module after login/registration and will require the
 * user to sign in again after a browser refresh until the backend supports a
 * safer renewal mechanism.
 */
export const authSession = {
  clear() {
    if (accessToken === null) return;
    accessToken = null;
    notify();
  },

  getToken() {
    return accessToken;
  },

  setToken(token: string) {
    accessToken = token;
    notify();
  },

  subscribe(listener: SessionListener) {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
};
