"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { TokenResponse, User } from "@/types";
import { loginUser, registerUser } from "@/lib/api";

interface AuthContextType {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedEmail = localStorage.getItem("email");
    if (storedToken) {
      setToken(storedToken);
      if (storedEmail) setUser({ id: "", email: storedEmail });
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const tokenResponse: TokenResponse = await loginUser(email, password);
    localStorage.setItem("token", tokenResponse.access_token);
    localStorage.setItem("email", email);
    setToken(tokenResponse.access_token);
    setUser({ id: "", email });
  };

  const register = async (email: string, password: string, fullName?: string) => {
    await registerUser(email, password, fullName);
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}