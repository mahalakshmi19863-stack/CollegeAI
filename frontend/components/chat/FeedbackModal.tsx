import React, { useState } from "react";
import { Modal } from "../common/Modal";
import { api } from "../../services/api";
import { ThumbsUp, ThumbsDown, CheckCircle2 } from "lucide-react";

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  messageId: string;
  initialRating: "helpful" | "not_helpful";
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  messageId,
  initialRating,
}) => {
  const [rating, setRating] = useState<"helpful" | "not_helpful">(initialRating);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await api.feedback.submit({
        message_id: messageId,
        rating,
        comment: comment.trim() || undefined,
      });
      setIsSubmitted(true);
      setTimeout(() => {
        setIsSubmitted(false);
        setComment("");
        onClose();
      }, 1500);
    } catch (err) {
      console.error("Feedback submit error", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Provide Answer Feedback">
      {isSubmitted ? (
        <div className="py-8 text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mb-3">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h4 className="text-base font-semibold text-slate-800">Thank you!</h4>
          <p className="text-sm text-slate-500 mt-1">Your feedback helps improve CollegeAI answers.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-2">
              Was this answer helpful and accurate?
            </label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setRating("helpful")}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border font-medium text-sm transition ${
                  rating === "helpful"
                    ? "bg-emerald-50 border-emerald-500 text-emerald-700 shadow-sm"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <ThumbsUp className="w-4 h-4" />
                Helpful
              </button>
              <button
                type="button"
                onClick={() => setRating("not_helpful")}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border font-medium text-sm transition ${
                  rating === "not_helpful"
                    ? "bg-rose-50 border-rose-500 text-rose-700 shadow-sm"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <ThumbsDown className="w-4 h-4" />
                Not Helpful
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              What could be improved? (Optional)
            </label>
            <textarea
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="e.g., The fee amount was correct, but hostel room types were missing..."
              className="w-full text-sm rounded-xl border border-slate-200 p-3 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-sm transition disabled:opacity-50"
            >
              {isSubmitting ? "Submitting..." : "Submit Feedback"}
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
};
