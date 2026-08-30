import React, { useState } from "react";
import { CollegeDocument } from "../../types";
import { Badge } from "../common/Badge";
import {
  FileText,
  Trash2,
  RefreshCw,
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
  UploadCloud,
} from "lucide-react";
import { Modal } from "../common/Modal";

interface DocumentTableProps {
  documents: CollegeDocument[];
  onDelete: (id: string) => Promise<void>;
  onReprocess: (id: string) => Promise<void>;
  onReplace: (id: string, file: File) => Promise<void>;
  onToggleActive: (id: string, currentStatus: boolean) => Promise<void>;
}

export const DocumentTable: React.FC<DocumentTableProps> = ({
  documents,
  onDelete,
  onReprocess,
  onReplace,
  onToggleActive,
}) => {
  const [docToDelete, setDocToDelete] = useState<CollegeDocument | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [reprocessingId, setReprocessingId] = useState<string | null>(null);
  const [replacingId, setReplacingId] = useState<string | null>(null);

  const confirmDelete = async () => {
    if (!docToDelete) return;
    setIsDeleting(true);
    try {
      await onDelete(docToDelete.id);
      setDocToDelete(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleReprocess = async (id: string) => {
    setReprocessingId(id);
    try {
      await onReprocess(id);
    } finally {
      setReprocessingId(null);
    }
  };

  const handleReplace = async (id: string, file: File) => {
    setReplacingId(id);
    try {
      await onReplace(id, file);
    } finally {
      setReplacingId(null);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="py-16 text-center border border-dashed border-slate-200 rounded-2xl bg-white">
        <div className="mx-auto w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mb-3">
          <FileText className="w-6 h-6" />
        </div>
        <h4 className="text-base font-semibold text-slate-800">No documents found</h4>
        <p className="text-xs text-slate-500 mt-1">
          Upload official college documents to populate the RAG knowledge base.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-subtle">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
            <tr>
              <th className="px-5 py-3.5">Document</th>
              <th className="px-4 py-3.5">Category</th>
              <th className="px-4 py-3.5">Department</th>
              <th className="px-3 py-3.5 text-center">Version</th>
              <th className="px-4 py-3.5 text-center">Status</th>
              <th className="px-3 py-3.5 text-center">Chunks</th>
              <th className="px-4 py-3.5 text-center">Active</th>
              <th className="px-5 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-slate-50/70 transition">
                {/* Document Name & Format */}
                <td className="px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-brand-50 text-brand-600 font-bold uppercase text-[10px]">
                      {doc.file_type}
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 text-sm">
                        {doc.name}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {doc.original_filename} • {(doc.file_size / 1024).toFixed(1)} KB
                      </div>
                      {doc.processing_error && (
                        <div className="text-[10px] text-rose-600 font-medium mt-0.5">
                          Error: {doc.processing_error}
                        </div>
                      )}
                    </div>
                  </div>
                </td>

                {/* Category */}
                <td className="px-4 py-4 font-medium text-slate-800">
                  {doc.category}
                </td>

                {/* Department */}
                <td className="px-4 py-4 text-slate-600">
                  {doc.department || "General"}
                </td>

                {/* Version */}
                <td className="px-3 py-4 text-center">
                  <span className="bg-slate-100 text-slate-700 font-semibold px-2 py-0.5 rounded text-[11px]">
                    v{doc.version}
                  </span>
                </td>

                {/* Status */}
                <td className="px-4 py-4 text-center">
                  <Badge status={doc.status} />
                </td>

                {/* Chunks Count */}
                <td className="px-3 py-4 text-center font-semibold text-slate-700">
                  {doc.chunk_count}
                </td>

                {/* Active Switch */}
                <td className="px-4 py-4 text-center">
                  <button
                    onClick={() => onToggleActive(doc.id, doc.is_active)}
                    className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold transition ${doc.is_active
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : "bg-slate-100 text-slate-500 border border-slate-200"
                      }`}
                    title={doc.is_active ? "Active in RAG Index" : "Inactive (Ignored by RAG)"}
                  >
                    {doc.is_active ? "Active" : "Disabled"}
                  </button>
                </td>

                {/* Actions */}
                <td className="px-5 py-4 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    <label
                      className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-brand-50 transition cursor-pointer"
                      title="Replace with a new version"
                    >
                      <UploadCloud className={`w-4 h-4 ${replacingId === doc.id ? "animate-pulse" : ""}`} />
                      <input
                        type="file"
                        accept=".pdf,.docx,.txt"
                        className="hidden"
                        disabled={replacingId === doc.id}
                        onChange={(event) => {
                          const file = event.target.files?.[0];
                          if (file) void handleReplace(doc.id, file);
                          event.target.value = "";
                        }}
                      />
                    </label>
                    <button
                      onClick={() => handleReprocess(doc.id)}
                      disabled={reprocessingId === doc.id}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-brand-50 transition"
                      title="Reprocess Document"
                    >
                      <RefreshCw
                        className={`w-4 h-4 ${reprocessingId === doc.id ? "animate-spin text-brand-600" : ""
                          }`}
                      />
                    </button>
                    <button
                      onClick={() => setDocToDelete(doc)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                      title="Delete Document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={Boolean(docToDelete)}
        onClose={() => setDocToDelete(null)}
        title="Confirm Document Deletion"
      >
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <div>
              Deleting this document will permanently remove all indexed chunks and embeddings from MongoDB Atlas Vector Search.
            </div>
          </div>
          <p className="text-sm text-slate-700">
            Are you sure you want to delete <span className="font-semibold">{docToDelete?.name}</span>?
          </p>
          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              onClick={() => setDocToDelete(null)}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition"
            >
              Cancel
            </button>
            <button
              onClick={confirmDelete}
              disabled={isDeleting}
              className="px-5 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-sm transition disabled:opacity-50"
            >
              {isDeleting ? "Deleting..." : "Delete Permanently"}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
};
