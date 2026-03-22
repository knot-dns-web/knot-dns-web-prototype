"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/lib/auth/storage";
import { decodeJwtPayload } from "@/lib/auth/jwtPayload";

export type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  /** true после чтения localStorage на клиенте */
  isReady: boolean;
  /** Никнейм из JWT (sub) */
  username: string | null;
  role: string | null;
  isAdmin: boolean;
  login: (accessToken: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    try {
      const stored = getAccessToken();
      if (stored) setTokenState(stored);
    } finally {
      setIsReady(true);
    }
  }, []);

  const login = useCallback((accessToken: string) => {
    setAccessToken(accessToken);
    setTokenState(accessToken);
  }, []);

  const logout = useCallback(() => {
    clearAccessToken();
    setTokenState(null);
  }, []);

  const claims = useMemo(() => decodeJwtPayload(token), [token]);
  const username = claims?.sub ?? null;
  const role = claims?.role ?? null;
  const isAdmin = role === "admin";

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      isReady,
      username,
      role,
      isAdmin,
      login,
      logout,
    }),
    [token, isReady, username, role, isAdmin, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth должен использоваться внутри AuthProvider");
  }
  return ctx;
}
