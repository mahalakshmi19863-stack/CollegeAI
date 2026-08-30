import React, { useState } from "react";
import { FileText, ChevronDown, ChevronUp, ExternalLink, Bookmark } from "lucide-react";
import { SourceItem } from "../../types";

interface SourceCardProps {
  source: SourceItem;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const percentage = Math.round(source.relevance_score * 100);

  return (
    <div className="rounded-xl border border-slate-200 bg-white/90 shadow-sm transition hover:border-brand-300 hover:shadow overflow-hidden text-xs">
      <div
        className="p-3 cursor-pointer flex items-center justify-between gap-3 select-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="p-1.5 rounded-lg bg-brand-50 text-brand-700 flex-shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="font-semibold text-slate-800 truncate" title={source.document_name}>
              {source.document_name}
            </div>
            <div className="flex items-center gap-2 text-[11px] text-slate-500 mt-0.5">
              {source.page_number && (
                <span className="font-medium text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                  Page {source.page_number}
                </span>
              )}
              {source.category && (
                <span className="text-slate-500">{source.category}</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="flex items-center gap-1 bg-emerald-50 text-emerald-700 font-semibold px-2 py-0.5 rounded-full text-[11px] border border-emerald-200">
            <span>{percentage}% match</span>
          </div>
          <button className="text-slate-400 hover:text-slate-600">
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {isExpanded && source.snippet && (
        <div className="px-3 pb-3 pt-1 border-t border-slate-100 bg-slate-50/70 text-slate-600 font-normal leading-relaxed text-[11px]">
          <div className="text-[10px] uppercase font-bold text-slate-400 mb-1 flex items-center gap-1">
            <Bookmark className="w-3 h-3" />
            Retrieved Context Extract
          </div>
          <p className="italic bg-white p-2 rounded border border-slate-200">"{source.snippet}"</p>
        </div>
      )}
    </div>
  );
};
