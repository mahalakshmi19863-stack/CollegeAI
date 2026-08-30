import React from "react";
import Link from "next/link";
import { Layout } from "../components/layout/Layout";
import { useAuthStore } from "../store/authStore";
import {
  GraduationCap,
  Sparkles,
  ShieldCheck,
  FileCheck,
  Search,
  ArrowRight,
  Database,
  CheckCircle2,
  Cpu,
  Layers,
  HelpCircle,
} from "lucide-react";

export default function LandingPage() {
  const { user } = useAuthStore();

  return (
    <Layout title="CollegeAI - Official RAG College Assistant">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28">
        {/* Glow background blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-400/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-indigo-400/20 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold mb-6 shadow-sm">
            <Sparkles className="w-4 h-4 text-brand-600" />
            <span>Next-Gen Retrieval-Augmented Generation (RAG)</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight sm:leading-none max-w-4xl mx-auto">
            Grounded College Knowledge.{" "}
            <span className="bg-gradient-to-r from-brand-600 to-indigo-600 bg-clip-text text-transparent">
              Zero Hallucinations.
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Ask any question about admissions, semester fees, hostel rules, exam schedules, and courses. Every answer is strictly retrieved and cited from verified college documents.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href={user ? "/dashboard" : "/register"}
              className="w-full sm:w-auto px-8 py-4 text-base font-semibold text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 rounded-2xl shadow-glow transition transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
            >
              <span>{user ? "Open Assistant" : "Get Started as Student"}</span>
              <ArrowRight className="w-5 h-5" />
            </Link>

            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-4 text-base font-semibold text-slate-700 bg-white hover:bg-slate-50 rounded-2xl border border-slate-200 shadow-sm transition flex items-center justify-center gap-2"
            >
              <span>Administrator Portal</span>
            </Link>
          </div>

          {/* Verification Badges */}
          <div className="mt-12 pt-8 border-t border-slate-200/80 flex flex-wrap items-center justify-center gap-6 text-xs font-medium text-slate-500">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>MongoDB Atlas Vector Search</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Page-by-Page Source Attribution</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Anti-Hallucination Safe Guard</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Multi-Format PDF, DOCX, TXT</span>
            </div>
          </div>
        </div>
      </section>

      {/* RAG Pipeline Breakdown */}
      <section className="py-16 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-bold uppercase tracking-wider text-brand-600 mb-2">
              Architectural Rigor
            </h2>
            <h3 className="text-2xl sm:text-3xl font-bold text-slate-900">
              How Genuine RAG Guarantees Truth
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <div className="rounded-2xl border border-slate-200 p-6 bg-slate-50/50 hover:bg-white hover:shadow-subtle transition">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-brand-600 flex items-center justify-center mb-4">
                <FileCheck className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">
                1. Official Ingestion & Chunking
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Admins upload PDF, DOCX, and TXT notices. Text is cleaned, segmented into semantic sliding-window chunks, preserving page numbers and category metadata.
              </p>
            </div>

            {/* Card 2 */}
            <div className="rounded-2xl border border-slate-200 p-6 bg-slate-50/50 hover:bg-white hover:shadow-subtle transition">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4">
                <Search className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">
                2. Semantic Vector Search
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Queries are embedded into high-dimensional vector space and matched via MongoDB Atlas Vector Search. Only chunks exceeding relevance thresholds are retrieved.
              </p>
            </div>

            {/* Card 3 */}
            <div className="rounded-2xl border border-slate-200 p-6 bg-slate-50/50 hover:bg-white hover:shadow-subtle transition">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-4">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">
                3. Grounded Synthesis & Citations
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                The LLM synthesizes an answer strictly from verified context with source cards and page numbers. If no relevant info exists, it explicitly rejects answering.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Comparison */}
      <section className="py-16 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <h3 className="text-2xl font-bold text-slate-900">
            Known Query vs. Unknown Query Handling
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            See how the system answers documented facts and rejects hallucinating missing data.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Known Query */}
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50/30 p-5">
            <div className="flex items-center gap-2 text-emerald-800 text-xs font-bold mb-3">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Documented Query (Hostel Fee)</span>
            </div>
            <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-xs text-slate-800 space-y-2">
              <p className="font-semibold text-slate-900">"What is the annual hostel fee?"</p>
              <p className="text-slate-700">"The annual hostel fee is ₹50,000 for standard accommodation."</p>
              <div className="pt-2 border-t border-slate-100 flex items-center gap-2 text-[11px] text-slate-500">
                <span className="font-semibold text-brand-600">Source:</span> Hostel Information 2026 • Page 8 • 92% match
              </div>
            </div>
          </div>

          {/* Unknown Query */}
          <div className="rounded-2xl border border-rose-200 bg-rose-50/30 p-5">
            <div className="flex items-center gap-2 text-rose-800 text-xs font-bold mb-3">
              <HelpCircle className="w-4 h-4 text-rose-600" />
              <span>Undocumented Query (Principal's Salary)</span>
            </div>
            <div className="bg-white p-3.5 rounded-xl border border-slate-200 text-xs text-slate-800 space-y-2">
              <p className="font-semibold text-slate-900">"What is the principal's monthly salary?"</p>
              <p className="text-rose-700 font-medium">
                "I couldn't find reliable information about this in the college knowledge base. Please try rephrasing your question or contact the college administration."
              </p>
              <div className="pt-2 border-t border-slate-100 text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                Zero Hallucination Guarantee Enforced
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
