import React from "react";
import { Layout } from "../components/layout/Layout";
import { useAuthStore } from "../store/authStore";
import { User, Mail, Shield, Calendar, Database, Sparkles } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuthStore();

  return (
    <Layout title="Account Settings - CollegeAI" requireAuth>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">User Profile & Settings</h1>
        <p className="text-xs text-slate-500 mb-8">
          Manage your account credentials and view RAG assistant parameters.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Profile Card */}
          <div className="md:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-6">
            <h2 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100">
              Account Information
            </h2>

            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 font-semibold uppercase tracking-wider block mb-1">
                  Full Name
                </label>
                <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium">
                  <User className="w-4 h-4 text-slate-400" />
                  <span>{user?.name}</span>
                </div>
              </div>

              <div>
                <label className="text-slate-400 font-semibold uppercase tracking-wider block mb-1">
                  Email Address
                </label>
                <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium">
                  <Mail className="w-4 h-4 text-slate-400" />
                  <span>{user?.email}</span>
                </div>
              </div>

              <div>
                <label className="text-slate-400 font-semibold uppercase tracking-wider block mb-1">
                  Role
                </label>
                <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium">
                  <Shield className="w-4 h-4 text-slate-400" />
                  <span className="font-semibold text-brand-700">{user?.role}</span>
                </div>
              </div>
            </div>
          </div>

          {/* RAG Architecture Metadata */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle space-y-4">
            <div className="flex items-center gap-2 text-brand-600 font-bold text-sm">
              <Sparkles className="w-4 h-4" />
              <span>RAG Engine Config</span>
            </div>

            <div className="space-y-3 text-xs text-slate-600">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                <div className="font-semibold text-slate-800">Vector Search</div>
                <div className="text-[11px] text-slate-500">MongoDB Atlas Vector Search</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                <div className="font-semibold text-slate-800">Relevance Threshold</div>
                <div className="text-[11px] text-slate-500">0.70 (Cosine Similarity)</div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                <div className="font-semibold text-slate-800">Chunk Size / Overlap</div>
                <div className="text-[11px] text-slate-500">800 chars / 120 chars</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
