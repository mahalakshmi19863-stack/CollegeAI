import React, { useEffect, useState } from "react";
import { Layout } from "../../components/layout/Layout";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { api } from "../../services/api";
import { AdminAnalyticsData } from "../../types";
import {
  BarChart3,
  PieChart,
  FolderOpen,
  Building,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
} from "lucide-react";

export default function AdminAnalyticsPage() {
  const [analytics, setAnalytics] = useState<AdminAnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      try {
        const data = await api.admin.getAnalytics();
        setAnalytics(data);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  return (
    <Layout title="Knowledge Analytics - CollegeAI Admin" requireAuth requireAdmin>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        <div className="mb-8">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-brand-600" />
            <h1 className="text-2xl font-bold text-slate-900">
              Knowledge Base & Usage Analytics
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Breakdown of knowledge coverage across college categories, departments, and user satisfaction ratings.
          </p>
        </div>

        {isLoading || !analytics ? (
          <div className="py-24 text-center text-slate-400">
            <LoadingSpinner size="lg" />
            <p className="text-xs mt-3">Compiling knowledge analytics...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Category Distribution Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Categories */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle">
                <div className="flex items-center gap-2 pb-4 border-b border-slate-100 mb-4">
                  <FolderOpen className="w-4 h-4 text-brand-600" />
                  <h3 className="text-sm font-bold text-slate-900">
                    Documents by Category
                  </h3>
                </div>

                {Object.keys(analytics.categories).length === 0 ? (
                  <p className="text-xs text-slate-400 py-6 text-center">
                    No documents uploaded yet.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(analytics.categories).map(([category, count]) => {
                      const percentage = Math.round(
                        (count / (analytics.overview.total_documents || 1)) * 100
                      );
                      return (
                        <div key={category} className="text-xs">
                          <div className="flex justify-between font-semibold text-slate-700 mb-1">
                            <span>{category}</span>
                            <span>
                              {count} docs ({percentage}%)
                            </span>
                          </div>
                          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-brand-500 rounded-full transition-all duration-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Department Distribution */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle">
                <div className="flex items-center gap-2 pb-4 border-b border-slate-100 mb-4">
                  <Building className="w-4 h-4 text-indigo-600" />
                  <h3 className="text-sm font-bold text-slate-900">
                    Documents by Department
                  </h3>
                </div>

                {Object.keys(analytics.departments).length === 0 ? (
                  <p className="text-xs text-slate-400 py-6 text-center">
                    No department data available.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(analytics.departments).map(([dept, count]) => {
                      const percentage = Math.round(
                        (count / (analytics.overview.total_documents || 1)) * 100
                      );
                      return (
                        <div key={dept} className="text-xs">
                          <div className="flex justify-between font-semibold text-slate-700 mb-1">
                            <span>{dept || "General"}</span>
                            <span>
                              {count} docs ({percentage}%)
                            </span>
                          </div>
                          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Satisfaction Breakdown */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-subtle">
              <div className="flex items-center gap-2 pb-4 border-b border-slate-100 mb-4">
                <Sparkles className="w-4 h-4 text-amber-500" />
                <h3 className="text-sm font-bold text-slate-900">
                  Student Feedback & Answer Quality Rating
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-xl">
                  <ThumbsUp className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
                  <div className="text-xl font-bold text-emerald-800">
                    {analytics.overview.feedback_stats.helpful}
                  </div>
                  <div className="text-[11px] text-emerald-600 font-medium">
                    Helpful Responses
                  </div>
                </div>

                <div className="p-4 bg-rose-50 border border-rose-100 rounded-xl">
                  <ThumbsDown className="w-5 h-5 text-rose-600 mx-auto mb-1" />
                  <div className="text-xl font-bold text-rose-800">
                    {analytics.overview.feedback_stats.not_helpful}
                  </div>
                  <div className="text-[11px] text-rose-600 font-medium">
                    Not Helpful Ratings
                  </div>
                </div>

                <div className="p-4 bg-brand-50 border border-brand-100 rounded-xl">
                  <PieChart className="w-5 h-5 text-brand-600 mx-auto mb-1" />
                  <div className="text-xl font-bold text-brand-800">
                    {analytics.overview.feedback_stats.satisfaction_rate_percent}%
                  </div>
                  <div className="text-[11px] text-brand-600 font-medium">
                    Overall Satisfaction
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
