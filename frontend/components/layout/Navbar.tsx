import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import {
  GraduationCap,
  MessageSquare,
  FileText,
  BarChart3,
  LogOut,
  User as UserIcon,
  Shield,
  Layers,
} from "lucide-react";
import { useAuthStore } from "../../store/authStore";

export const Navbar: React.FC = () => {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const isAdmin = user?.role === "ADMIN";

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-glow group-hover:scale-105 transition">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-brand-700 to-indigo-700 bg-clip-text text-transparent">
                CollegeAI
              </span>
              <span className="hidden sm:inline-block ml-2 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-brand-100 text-brand-800">
                Official RAG
              </span>
            </div>
          </Link>

          {/* Navigation Links for Authenticated Users */}
          {user && (
            <nav className="hidden md:flex items-center gap-1">
              <Link
                href="/dashboard"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${
                  router.pathname === "/dashboard"
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                Assistant
              </Link>
              <Link
                href="/conversations"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${
                  router.pathname.startsWith("/conversations") || router.pathname.startsWith("/chat")
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <Layers className="w-4 h-4" />
                History
              </Link>

              {isAdmin && (
                <>
                  <div className="h-4 w-px bg-slate-200 mx-2" />
                  <Link
                    href="/admin"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${
                      router.pathname === "/admin"
                        ? "bg-brand-50 text-brand-700"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <Shield className="w-4 h-4 text-brand-600" />
                    Admin
                  </Link>
                  <Link
                    href="/admin/documents"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${
                      router.pathname === "/admin/documents"
                        ? "bg-brand-50 text-brand-700"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <FileText className="w-4 h-4" />
                    Documents
                  </Link>
                  <Link
                    href="/admin/analytics"
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${
                      router.pathname === "/admin/analytics"
                        ? "bg-brand-50 text-brand-700"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <BarChart3 className="w-4 h-4" />
                    Analytics
                  </Link>
                </>
              )}
            </nav>
          )}
        </div>

        {/* Right Action / Profile */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-sm font-semibold text-slate-800">{user.name}</span>
                <span className="text-xs text-slate-500">{user.role}</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition"
                title="Log out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-brand-600 transition"
              >
                Log In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-sm transition"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
