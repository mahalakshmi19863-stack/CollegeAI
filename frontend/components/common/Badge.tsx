import React from "react";
import { DocumentStatus } from "../../types";

interface BadgeProps {
  status?: DocumentStatus | string;
  variant?: "blue" | "green" | "red" | "amber" | "gray" | "purple";
  children?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ status, variant, children }) => {
  let colorClass = "bg-slate-100 text-slate-700 border-slate-200";

  const resolvedStatus = status?.toUpperCase();

  if (resolvedStatus === "PROCESSED" || variant === "green") {
    colorClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (resolvedStatus === "PROCESSING" || variant === "amber") {
    colorClass = "bg-amber-50 text-amber-700 border-amber-200 animate-pulse";
  } else if (resolvedStatus === "FAILED" || variant === "red") {
    colorClass = "bg-rose-50 text-rose-700 border-rose-200";
  } else if (resolvedStatus === "UPLOADED" || variant === "blue") {
    colorClass = "bg-blue-50 text-blue-700 border-blue-200";
  } else if (variant === "purple") {
    colorClass = "bg-indigo-50 text-indigo-700 border-indigo-200";
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70"></span>
      {children || status}
    </span>
  );
};
