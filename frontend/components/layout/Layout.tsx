import React, { useEffect } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import { Navbar } from "./Navbar";
import { useAuthStore } from "../../store/authStore";
import { LoadingSpinner } from "../common/LoadingSpinner";

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  requireAuth?: boolean;
  requireAdmin?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  title = "CollegeAI - Grounded RAG College Information Assistant",
  requireAuth = false,
  requireAdmin = false,
}) => {
  const router = useRouter();
  const { user, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !user) {
        router.replace("/login");
      } else if (requireAdmin && user && user.role !== "ADMIN") {
        router.replace("/dashboard");
      }
    }
  }, [user, isLoading, requireAuth, requireAdmin, router]);

  if (isLoading && requireAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-slate-500 font-medium">Verifying authorization...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Head>
        <title>{title}</title>
        <meta
          name="description"
          content="Official AI-powered college information assistant grounded in verified college documents."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Navbar />

      <main className="flex-1 flex flex-col">{children}</main>
    </div>
  );
};
