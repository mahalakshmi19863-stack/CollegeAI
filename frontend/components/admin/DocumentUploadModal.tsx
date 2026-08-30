import React, { useState, useRef } from "react";
import { Modal } from "../common/Modal";
import { api } from "../../services/api";
import { CollegeDocument } from "../../types";
import { UploadCloud, File, AlertCircle } from "lucide-react";

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newDoc: CollegeDocument) => void;
}

const CATEGORIES = [
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

const DEPARTMENTS = ["General", "CSE", "ECE", "ISE", "ME", "CIVIL"];

export const DocumentUploadModal: React.FC<DocumentUploadModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("General");
  const [department, setDepartment] = useState("General");
  const [description, setDescription] = useState("");
  const [version, setVersion] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!name) {
        // Strip extension for clean display name
        const cleanName = selected.name.replace(/\.[^/.]+$/, "");
        setName(cleanName);
      }
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      if (!name) {
        setName(selected.name.replace(/\.[^/.]+$/, ""));
      }
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", name || file.name);
      formData.append("category", category);
      formData.append("department", department);
      formData.append("description", description);
      formData.append("version", version.toString());

      const uploadedDoc = await api.documents.upload(formData);
      onSuccess(uploadedDoc);
      // Reset form
      setFile(null);
      setName("");
      setDescription("");
      setVersion(1);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to upload document.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Upload College Document" maxWidth="max-w-xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2 text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Dropzone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition ${file
              ? "border-emerald-300 bg-emerald-50/50"
              : "border-slate-300 hover:border-brand-400 bg-slate-50/50"
            }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            className="hidden"
          />
          {file ? (
            <div className="flex items-center justify-center gap-3">
              <div className="p-3 bg-emerald-100 text-emerald-700 rounded-xl">
                <File className="w-6 h-6" />
              </div>
              <div className="text-left">
                <div className="text-sm font-semibold text-slate-800">{file.name}</div>
                <div className="text-xs text-slate-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB • Click or drag to replace
                </div>
              </div>
            </div>
          ) : (
            <div>
              <div className="mx-auto w-12 h-12 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center mb-3">
                <UploadCloud className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-slate-800">
                Click to browse or drag and drop document
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supports official PDF, DOCX, or TXT documents (Max 20MB)
              </p>
            </div>
          )}
        </div>

        {/* Document Name */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Display Document Name
          </label>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Academic Calendar 2026-2027"
            className="w-full text-sm rounded-xl border border-slate-200 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
          />
        </div>

        {/* Category & Department */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full text-sm rounded-xl border border-slate-200 px-3 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Department
            </label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full text-sm rounded-xl border border-slate-200 px-3 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Version & Description */}
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-1">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Version
            </label>
            <input
              type="number"
              min="1"
              value={version}
              onChange={(e) => setVersion(parseInt(e.target.value) || 1)}
              className="w-full text-sm rounded-xl border border-slate-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Description (Optional)
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief note about the document contents"
              className="w-full text-sm rounded-xl border border-slate-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>
        </div>

        {/* Modal Actions */}
        <div className="flex justify-end gap-2.5 pt-4 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isUploading || !file}
            className="px-6 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-sm transition disabled:opacity-50 flex items-center gap-2"
          >
            {isUploading ? "Uploading & Ingesting..." : "Upload & Process"}
          </button>
        </div>
      </form>
    </Modal>
  );
};
