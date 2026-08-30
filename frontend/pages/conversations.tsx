import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { Layout } from "../components/layout/Layout";
import { useChatStore } from "../store/chatStore";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import {
  MessageSquare,
  Trash2,
  Clock,
  ArrowRight,
  Plus,
  Search,
} from "lucide-react";

export default function ConversationsPage() {
  const router = useRouter();
  const {
    conversations,
    isLoadingConversations,
    fetchConversations,
    deleteConversation,
    selectConversation,
  } = useChatStore();

  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  const handleOpen = async (id: string) => {
    await selectConversation(id);
    router.push(`/dashboard`);
  };

  return (
    <Layout title="Conversation History - CollegeAI" requireAuth>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Conversation History</h1>
            <p className="text-xs text-slate-500 mt-1">
              Review and manage your previous grounded assistant conversations.
            </p>
          </div>

          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            New Question
          </Link>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search past conversations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full text-sm rounded-xl border border-slate-200 pl-10 pr-4 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
          />
        </div>

        {/* Conversation List */}
        {isLoadingConversations ? (
          <div className="py-20 text-center text-slate-400">
            <LoadingSpinner size="lg" />
            <p className="text-xs mt-3">Loading conversations...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-200">
            <MessageSquare className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-800">No conversations yet</h3>
            <p className="text-xs text-slate-500 mt-1">
              Ask your first college-related question to start a grounded conversation.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map((conv) => (
              <div
                key={conv.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-subtle hover:border-brand-300 hover:shadow transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-semibold text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full">
                      {conv.message_count} Messages
                    </span>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-900 text-sm line-clamp-2">
                    {conv.title}
                  </h3>
                </div>

                <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <button
                    onClick={() => handleOpen(conv.id)}
                    className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
                  >
                    <span>Resume Chat</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => deleteConversation(conv.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                    title="Delete Conversation"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
