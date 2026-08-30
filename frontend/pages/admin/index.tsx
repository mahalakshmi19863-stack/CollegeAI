import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Layout } from "../../components/layout/Layout";
import { StatCard } from "../../components/admin/StatCard";
import { DocumentUploadModal } from "../../components/admin/DocumentUploadModal";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { Badge } from "../../components/common/Badge";
import { api } from "../../services/api";
import { AdminDashboardData, CollegeDocument } from "../../types";
import {
  FileText,
  Users,
  MessageSquare,
  ThumbsUp,
  UploadCloud,
  ArrowRight,
  Shield,
  Clock,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

export default function AdminDashboardPage() {
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const fetchDashboard = async () => {
    setIsLoading(true);
    try {
      const res = await api.admin.getDashboard();
      setData(res);
    } catch (err) {
      console.error("Failed to load admin dashboard", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleUploadSuccess = (newDoc: CollegeDocument) => {
    fetchDashboard();
  };

  return (
    <Layout title="Admin Overview - CollegeAI" requireAuth requireAdmin>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-brand-600" />
              <h1 className="text-2xl font-bold text-slate-900">Admin Control Center</h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Manage the official college knowledge base, verify chunking, and monitor RAG usage.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchDashboard}
              className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition"
              title="Refresh metrics"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-sm transition"
            >
              <UploadCloud className="w-4 h-4" />
              Upload Document
            </button>
          </div>
        </div>

        {isLoading || !data ? (
          <div className="py-24 text-center text-slate-400">
            <LoadingSpinner size="lg" />
            <p className="text-xs mt-3">Loading system metrics...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Stat Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              <StatCard
                title="Total Documents"
                value={data.total_documents}
                subtitle={`${data.processed_documents} active in RAG index`}
                icon={<FileText className="w-5 h-5" />}
                variant="blue"
              />
              <StatCard
                title="Registered Students"
                value={data.total_students}
                subtitle="Active user accounts"
                icon={<Users className="w-5 h-5" />}
                variant="indigo"
              />
              <StatCard
                title="Questions Answered"
                value={data.total_questions}
                subtitle="Grounded responses generated"
                icon={<MessageSquare className="w-5 h-5" />}
                variant="purple"
              />
              <StatCard
                title="Satisfaction Rate"
                value={`${data.feedback_stats.satisfaction_rate_percent}%`}
                subtitle={`${data.feedback_stats.helpful} thumbs up / ${data.feedback_stats.total} ratings`}
                icon={<ThumbsUp className="w-5 h-5" />}
                variant="green"
              />
            </div>

            {/* Quick Actions & Recent Uploads */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Recent Uploads Table */}
              <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle">
                <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                  <h3 className="text-sm font-bold text-slate-900">
                    Recent Knowledge Base Documents
                  </h3>
                  <Link
                    href="/admin/documents"
                    className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
                  >
                    <span>View All Documents</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                {data.recent_uploads.length === 0 ? (
                  <div className="py-12 text-center text-slate-400 text-xs">
                    No documents uploaded yet. Click "Upload Document" to begin.
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {data.recent_uploads.map((doc) => (
                      <div
                        key={doc.id}
                        className="py-3 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="p-2 rounded-xl bg-brand-50 text-brand-600 font-bold uppercase text-[10px]">
                            {doc.file_type}
                          </div>
                          <div className="min-w-0">
                            <div className="font-semibold text-slate-900 truncate">
                              {doc.name}
                            </div>
                            <div className="text-[11px] text-slate-400">
                              {doc.category} • {doc.chunk_count} Chunks • v{doc.version}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-3">
                          <Badge status={doc.status} />
                          <span className="text-[11px] text-slate-400 hidden sm:inline">
                            {new Date(doc.uploaded_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* RAG Engine Status Card */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 mb-4">
                    RAG Pipeline Health
                  </h3>

                  <div className="space-y-3.5 text-xs">
                    <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-emerald-600" />
                        <span className="font-semibold">Vector Search Engine</span>
                      </div>
                      <span className="text-[11px] font-bold">ACTIVE</span>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 text-slate-700 border border-slate-200">
                      <span className="font-medium">Processed Documents</span>
                      <span className="font-bold text-slate-900">
                        {data.processed_documents} / {data.total_documents}
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 text-slate-700 border border-slate-200">
                      <span className="font-medium">Failed Documents</span>
                      <span className={`font-bold ${data.failed_documents > 0 ? "text-rose-600" : "text-slate-900"}`}>
                        {data.failed_documents}
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 text-slate-700 border border-slate-200">
                      <span className="font-medium">Feedback Collected</span>
                      <span className="font-bold text-slate-900">
                        {data.feedback_stats.total}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100">
                  <Link
                    href="/admin/analytics"
                    className="w-full py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition flex items-center justify-center gap-2"
                  >
                    <span>View Category & Department Analytics</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Modal */}
        <DocumentUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onSuccess={handleUploadSuccess}
        />
      </div>
    </Layout>
  );
}
