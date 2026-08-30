import { create } from "zustand";
import { api } from "../services/api";
import { User, UserRole } from "../types";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string, role?: UserRole) => Promise<User>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isLoading: true,
  error: null,

  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (typeof window !== "undefined") {
      if (token) localStorage.setItem("college_ai_token", token);
      else localStorage.removeItem("college_ai_token");
    }
    set({ token });
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.auth.login({ email, password });
      if (typeof window !== "undefined") {
        localStorage.setItem("college_ai_token", data.access_token);
      }
      set({ user: data.user, token: data.access_token, isLoading: false });
      return data.user;
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
      throw err;
    }
  },

  register: async (name, email, password, role = "STUDENT") => {
    set({ isLoading: true, error: null });
    try {
      const user = await api.auth.register({ name, email, password, role });
      // After registration, automatically login
      const loginData = await api.auth.login({ email, password });
      if (typeof window !== "undefined") {
        localStorage.setItem("college_ai_token", loginData.access_token);
      }
      set({ user: loginData.user, token: loginData.access_token, isLoading: false });
      return loginData.user;
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
      throw err;
    }
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("college_ai_token");
    }
    set({ user: null, token: null, error: null });
  },

  checkAuth: async () => {
    if (typeof window === "undefined") {
      set({ isLoading: false });
      return;
    }

    const token = localStorage.getItem("college_ai_token");
    if (!token) {
      set({ user: null, token: null, isLoading: false });
      return;
    }

    set({ token, isLoading: true });
    try {
      const user = await api.auth.getMe();
      set({ user, isLoading: false });
    } catch (err) {
      localStorage.removeItem("college_ai_token");
      set({ user: null, token: null, isLoading: false });
    }
  },
}));
