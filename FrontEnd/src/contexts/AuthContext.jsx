import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
const TOKEN_STORAGE_KEY = "nn_access_token";
const USER_STORAGE_KEY = "nn_current_user";

const AuthContext = createContext({
  user: null,
  token: null,
  loading: true,
  isAuthenticated: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  refreshProfile: async () => {},
  getAuthHeaders: () => ({}),
});

export const useAuth = () => useContext(AuthContext);

const parseStoredUser = (value) => {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch (error) {
    console.warn("Failed to parse stored user", error);
    return null;
  }
};

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [user, setUser] = useState(() => parseStoredUser(localStorage.getItem(USER_STORAGE_KEY)));
  const [loading, setLoading] = useState(true);

  const persistAuthState = useCallback((nextToken, nextUser) => {
    setToken(nextToken);
    setUser(nextUser);
    if (nextToken) {
      localStorage.setItem(TOKEN_STORAGE_KEY, nextToken);
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    }

    if (nextUser) {
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(nextUser));
    } else {
      localStorage.removeItem(USER_STORAGE_KEY);
    }
  }, []);

  const logout = useCallback(() => {
    persistAuthState(null, null);
  }, [persistAuthState]);

  const refreshProfile = useCallback(async () => {
    if (!token) return null;
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        if (response.status === 401) {
          logout();
        }
        return null;
      }
      const profile = await response.json();
      persistAuthState(token, profile);
      return profile;
    } catch (error) {
      console.error("Failed to refresh profile", error);
      return null;
    }
  }, [token, logout, persistAuthState]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      await refreshProfile();
      if (mounted) setLoading(false);
    })();
    return () => {
      mounted = false;
    };
  }, [token, refreshProfile]);

  const login = useCallback(
    async (email, password) => {
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);
      params.append("grant_type", "password");

      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: params,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data?.detail ?? "Unable to sign in");
      }

      const data = await response.json();
      persistAuthState(data.access_token, data.user);
      return data.user;
    },
    [persistAuthState]
  );

  const register = useCallback(
    async (name, email, password) => {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data?.detail ?? "Unable to create account");
      }

      const data = await response.json();
      persistAuthState(data.access_token, data.user);
      return data.user;
    },
    [persistAuthState]
  );

  const getAuthHeaders = useCallback(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
      refreshProfile,
      getAuthHeaders,
    }),
    [user, token, loading, login, register, logout, refreshProfile, getAuthHeaders]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
