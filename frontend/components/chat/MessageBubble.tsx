import React, { useState } from "react";
import { Message, SourceItem } from "../../types";
import { SourceCard } from "./SourceCard";
import { FeedbackModal } from "./FeedbackModal";
import {
  GraduationCap,
  User as UserIcon,
  ThumbsUp,
  ThumbsDown,
  Layers,
  Clock,
  Sparkles,
} from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === "USER";
  const [feedbackRating, setFeedbackRating] = useState<"helpful" | "not_helpful" | null>(null);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);

  const handleFeedbackClick = (rating: "helpful" | "not_helpful") => {
    setFeedbackRating(rating);
    setIsFeedbackModalOpen(true);
  };

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 my-4">
        <div className="max-w-2xl bg-brand-600 text-white rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-sm">
          <p className="text-sm font-normal leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0 text-xs font-bold">
          <UserIcon className="w-4 h-4" />
        </div>
      </div>
    );
  }

  // Assistant Response
  const hasSources = message.sources && message.sources.length > 0;
  const retrieval = message.retrieval_metadata;

  return (
    <div className="flex justify-start gap-3.5 my-6">
      <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
        <GraduationCap className="w-5 h-5" />
      </div>

      <div className="max-w-3xl flex-1">
        {/* Main Answer Card */}
        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm p-5 shadow-subtle">
          <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>

          {/* Source Attribution Cards */}
          {hasSources && (
            <div className="mt-5 pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-brand-600" />
                  Verified College Sources ({message.sources?.length})
                </span>
                {retrieval?.processing_time_ms && (
                  <span className="text-[11px] text-slate-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {retrieval.processing_time_ms}ms
                  </span>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {message.sources?.map((source, idx) => (
                  <SourceCard key={idx} source={source} />
                ))}
              </div>
            </div>
          )}

          {/* Feedback & Actions Footer */}
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span className="text-[11px]">Was this helpful?</span>
              <button
                onClick={() => handleFeedbackClick("helpful")}
                className={`p-1 rounded hover:bg-slate-100 transition ${
                  feedbackRating === "helpful" ? "text-emerald-600 bg-emerald-50" : "text-slate-400 hover:text-slate-600"
                }`}
                title="Helpful answer"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedbackClick("not_helpful")}
                className={`p-1 rounded hover:bg-slate-100 transition ${
                  feedbackRating === "not_helpful" ? "text-rose-600 bg-rose-50" : "text-slate-400 hover:text-slate-600"
                }`}
                title="Not helpful"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="text-[11px] text-slate-400 font-medium">
              Grounded in Knowledge Base
            </div>
          </div>
        </div>
      </div>

      {feedbackRating && (
        <FeedbackModal
          isOpen={isFeedbackModalOpen}
          onClose={() => setIsFeedbackModalOpen(false)}
          messageId={message.id}
          initialRating={feedbackRating}
        />
      )}
    </div>
  );
};
