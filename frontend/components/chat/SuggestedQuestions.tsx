import React from "react";
import { Sparkles } from "lucide-react";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

export const SUGGESTED_QUESTIONS = [
  "What are the college library opening hours?",
  "What is the annual hostel fee?",
  "What are the admission requirements?",
  "When are the semester examinations?",
  "What scholarships are available?",
  "Tell me about the CSE department courses.",
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ onSelect }) => {
  return (
    <div className="w-full">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 mb-2.5">
        <Sparkles className="w-3.5 h-3.5 text-brand-600" />
        <span>Suggested Questions</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(q)}
            className="text-left text-xs bg-white hover:bg-brand-50 hover:text-brand-700 hover:border-brand-300 text-slate-700 font-medium px-3 py-2 rounded-xl border border-slate-200 shadow-sm transition-all duration-150"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
};
