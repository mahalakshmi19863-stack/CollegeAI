import React, { useEffect, useState } from "react";
import { Layout } from "../../components/layout/Layout";
import { DocumentTable } from "../../components/admin/DocumentTable";
import { DocumentUploadModal } from "../../components/admin/DocumentUploadModal";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../services/api";
import { CollegeDocument } from "../../types";
import {
  UploadCloud,
  Search,
  Filter,
  RefreshCw,
  FileText,
  Shield,
} from "lucide-react";

const CATEGORIES = [
  "All",
  "Admissions",
  "Academics",
  "Examinations",
  "Fees",
  "Hostel",
  "Library",
  "Scholarships",
  "Placements",
  "Clubs",
  "Events",
  "Policies",
  "General",
];

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<CollegeDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedStatus, setSelectedStatus] = useState("All");

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const params: any = {};
      if (selectedCategory !== "All") params.category = selectedCategory;
      if (selectedStatus !== "All") params.status = selectedStatus;
      if (searchTerm.trim()) params.search = searchTerm.trim();

      const docs = await api.documents.list(params);
      setDocuments(docs);
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [selectedCategory, selectedStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDocuments();
  };

  const handleDelete = async (id: string) => {
    await api.documents.delete(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  };

  const handleReprocess = async (id: string) => {
    await api.documents.reprocess(id);
    fetchDocuments();
  };

  const handleReplace = async (id: string, file: File) => {
    const replacement = await api.documents.replace(id, file);
    setDocuments((prev) => [replacement, ...prev]);
  };

  const handleToggleActive = async (id: string, currentStatus: boolean) => {
    const updated = await api.documents.update(id, { is_active: !currentStatus });
    setDocuments((prev) => prev.map((d) => (d.id === id ? updated : d)));
  };

  const handleUploadSuccess = (newDoc: CollegeDocument) => {
    setDocuments((prev) => [newDoc, ...prev]);
  };

  return (
    <Layout title="Manage Documents - CollegeAI Admin" requireAuth requireAdmin>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-brand-600" />
              <h1 className="text-2xl font-bold text-slate-900">
                Knowledge Base Documents
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Upload, re-index, version, and manage official college documents.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchDocuments}
              className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition"
              title="Refresh list"
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

        {/* Filter Controls */}
        <div className="bg-white rounded-2xl border border-slate-200 p-4 mb-6 shadow-subtle flex flex-col sm:flex-row items-center gap-4">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by title, original filename, or content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full text-xs rounded-xl border border-slate-200 pl-10 pr-4 py-2.5 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </form>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-xs rounded-xl border border-slate-200 px-3 py-2.5 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500 w-full sm:w-48"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  Category: {cat}
                </option>
              ))}
            </select>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="text-xs rounded-xl border border-slate-200 px-3 py-2.5 bg-white focus:outline-none focus:ring-1 focus:ring-brand-500 w-full sm:w-40"
            >
              {['All', 'UPLOADED', 'PROCESSING', 'PROCESSED', 'FAILED'].map((item) => (
                <option key={item} value={item}>
                  Status: {item}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Documents Table */}
        {isLoading ? (
          <div className="py-24 text-center text-slate-400">
            <LoadingSpinner size="lg" />
            <p className="text-xs mt-3">Loading knowledge documents...</p>
          </div>
        ) : (
          <DocumentTable
            documents={documents}
            onDelete={handleDelete}
            onReprocess={handleReprocess}
            onReplace={handleReplace}
            onToggleActive={handleToggleActive}
          />
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
