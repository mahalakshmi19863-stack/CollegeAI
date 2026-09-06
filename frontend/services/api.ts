import axios, { AxiosError } from "axios";
import {
  AdminAnalyticsData,
  AdminDashboardData,
  ChatResponseData,
  CollegeDocument,
  Conversation,
  Message,
  User,
} from "../types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:8002" : "");

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token from localStorage to every outgoing request
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("college_ai_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor for consistent error extracting
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: { code?: string; message?: string } }>) => {
    const errorMsg =
      error.response?.data?.error?.message ||
      error.message ||
      "An unexpected network error occurred.";
    return Promise.reject(new Error(errorMsg));
  }
);

export const api = {
  // Authentication
  auth: {
    async register(data: { name: string; email: string; password: string; role?: string }) {
      const res = await apiClient.post<{ success: boolean; data: User }>("/auth/register", data);
      return res.data.data;
    },
    async login(data: { email: string; password: string }) {
      const res = await apiClient.post<{
        success: boolean;
        data: { access_token: string; token_type: string; user: User };
      }>("/auth/login", data);
      return res.data.data;
    },
    async logout() {
      const res = await apiClient.post<{ success: boolean; data: any }>("/auth/logout");
      return res.data.data;
    },
    async getMe() {
      const res = await apiClient.get<{ success: boolean; data: User }>("/auth/me");
      return res.data.data;
    },
  },

  // Document Management
  documents: {
    async upload(formData: FormData) {
      const res = await apiClient.post<{ success: boolean; data: CollegeDocument }>(
        "/documents",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      return res.data.data;
    },
    async list(params?: {
      search?: string;
      category?: string;
      department?: string;
      status?: string;
      is_active?: boolean;
    }) {
      const res = await apiClient.get<{ success: boolean; data: CollegeDocument[] }>(
        "/documents",
        { params }
      );
      return res.data.data;
    },
    async getById(id: string) {
      const res = await apiClient.get<{ success: boolean; data: CollegeDocument }>(
        `/documents/${id}`
      );
      return res.data.data;
    },
    async update(id: string, updates: Partial<CollegeDocument>) {
      const res = await apiClient.patch<{ success: boolean; data: CollegeDocument }>(
        `/documents/${id}`,
        updates
      );
      return res.data.data;
    },
    async delete(id: string) {
      const res = await apiClient.delete<{ success: boolean; data: any }>(
        `/documents/${id}`
      );
      return res.data.data;
    },
    async reprocess(id: string) {
      const res = await apiClient.post<{ success: boolean; data: CollegeDocument }>(
        `/documents/${id}/reprocess`
      );
      return res.data.data;
    },
    async replace(id: string, file: File) {
      const formData = new FormData();
      formData.append("file", file);
      const res = await apiClient.post<{ success: boolean; data: CollegeDocument }>(
        `/documents/${id}/replace`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      return res.data.data;
    },
  },

  // Chat & Conversations
  chat: {
    async sendMessage(question: string, conversation_id?: string) {
      const res = await apiClient.post<{ success: boolean; data: ChatResponseData }>(
        "/chat",
        { question, conversation_id }
      );
      return res.data.data;
    },
    async listConversations() {
      const res = await apiClient.get<{ success: boolean; data: Conversation[] }>(
        "/conversations"
      );
      return res.data.data;
    },
    async getConversation(id: string) {
      const res = await apiClient.get<{
        success: boolean;
        data: { conversation: Conversation; messages: Message[] };
      }>(`/conversations/${id}`);
      return res.data.data;
    },
    async updateConversation(id: string, title: string) {
      const res = await apiClient.patch<{ success: boolean; data: Conversation }>(
        `/conversations/${id}`,
        { title }
      );
      return res.data.data;
    },
    async deleteConversation(id: string) {
      const res = await apiClient.delete<{ success: boolean; data: any }>(
        `/conversations/${id}`
      );
      return res.data.data;
    },
  },

  // Feedback
  feedback: {
    async submit(data: { message_id: string; rating: "helpful" | "not_helpful"; comment?: string }) {
      const res = await apiClient.post<{ success: boolean; data: any }>("/feedback", data);
      return res.data.data;
    },
  },

  // Admin Dashboard & Analytics
  admin: {
    async getDashboard() {
      const res = await apiClient.get<{ success: boolean; data: AdminDashboardData }>(
        "/admin/dashboard"
      );
      return res.data.data;
    },
    async getAnalytics() {
      const res = await apiClient.get<{ success: boolean; data: AdminAnalyticsData }>(
        "/admin/analytics"
      );
      return res.data.data;
    },
  },

  // Health
  health: {
    async check() {
      const res = await apiClient.get<{ success: boolean; data: any }>("/health");
      return res.data.data;
    },
  },
};
