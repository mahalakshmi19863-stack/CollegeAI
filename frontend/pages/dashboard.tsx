import React, { useEffect, useState, useRef } from "react";
import { Layout } from "../components/layout/Layout";
import { useAuthStore } from "../store/authStore";
import { useChatStore } from "../store/chatStore";
import { MessageBubble } from "../components/chat/MessageBubble";
import { SuggestedQuestions } from "../components/chat/SuggestedQuestions";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import {
  Plus,
  Send,
  MessageSquare,
  Trash2,
  Edit2,
  Sparkles,
  AlertCircle,
  GraduationCap,
  Layers,
  Search,
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuthStore();
  const {
    conversations,
    activeConversationId,
    activeConversation,
    messages,
    isLoadingConversations,
    isLoadingMessages,
    isSendingMessage,
    error,
    fetchConversations,
    selectConversation,
    createConversation,
    sendMessage,
    deleteConversation,
    updateConversationTitle,
  } = useChatStore();

  const [inputQuery, setInputQuery] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSendingMessage]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isSendingMessage) return;

    const query = inputQuery;
    setInputQuery("");
    await sendMessage(query);
  };

  const handleSelectSuggested = (question: string) => {
    setInputQuery(question);
  };

  const handleSaveTitle = async (id: string) => {
    if (editTitle.trim()) {
      await updateConversationTitle(id, editTitle.trim());
    }
    setEditingConvId(null);
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout title="Assistant - CollegeAI" requireAuth>
      <div className="flex-1 flex overflow-hidden h-[calc(100vh-4rem)]">
        {/* Sidebar: Conversations List */}
        <aside className="w-80 border-r border-slate-200 bg-white flex flex-col hidden md:flex">
          {/* New Chat Action */}
          <div className="p-4 border-b border-slate-100">
            <button
              onClick={createConversation}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 font-semibold text-xs border border-brand-200 transition"
            >
              <Plus className="w-4 h-4" />
              New Conversation
            </button>

            {/* Search filter */}
            <div className="relative mt-3">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search chats..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full text-xs rounded-xl border border-slate-200 pl-8 pr-3 py-2 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
          </div>

          {/* Conversations Scrollable List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {isLoadingConversations ? (
              <div className="p-8 text-center text-slate-400">
                <LoadingSpinner size="sm" />
                <p className="text-xs mt-2">Loading history...</p>
              </div>
            ) : filteredConversations.length === 0 ? (
              <div className="p-6 text-center text-slate-400 text-xs">
                No past conversations found.
              </div>
            ) : (
              filteredConversations.map((conv) => {
                const isActive = conv.id === activeConversationId;
                const isEditing = conv.id === editingConvId;

                return (
                  <div
                    key={conv.id}
                    className={`group relative flex items-center justify-between p-2.5 rounded-xl text-xs font-medium cursor-pointer transition ${
                      isActive
                        ? "bg-brand-50 text-brand-900 font-semibold"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                    onClick={() => !isEditing && selectConversation(conv.id)}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                      <MessageSquare
                        className={`w-4 h-4 flex-shrink-0 ${
                          isActive ? "text-brand-600" : "text-slate-400"
                        }`}
                      />
                      {isEditing ? (
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onBlur={() => handleSaveTitle(conv.id)}
                          onKeyDown={(e) =>
                            e.key === "Enter" && handleSaveTitle(conv.id)
                          }
                          autoFocus
                          className="w-full px-1.5 py-0.5 rounded border border-brand-300 text-xs bg-white focus:outline-none"
                        />
                      ) : (
                        <span className="truncate">{conv.title}</span>
                      )}
                    </div>

                    {!isEditing && (
                      <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingConvId(conv.id);
                            setEditTitle(conv.title);
                          }}
                          className="p-1 text-slate-400 hover:text-slate-600 rounded"
                          title="Rename"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteConversation(conv.id);
                          }}
                          className="p-1 text-slate-400 hover:text-rose-600 rounded"
                          title="Delete"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* Main Chat Interface */}
        <section className="flex-1 flex flex-col bg-slate-50 relative overflow-hidden">
          {/* Active Conversation Header */}
          <div className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur px-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center">
                <GraduationCap className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 truncate">
                  {activeConversation?.title || "College Information Assistant"}
                </h2>
                <p className="text-[10px] text-slate-400">
                  Strictly grounded in verified official college notices & handbooks
                </p>
              </div>
            </div>

            {/* Mobile new chat button */}
            <div className="md:hidden">
              <button
                onClick={createConversation}
                className="p-2 rounded-lg bg-brand-50 text-brand-600 text-xs font-semibold"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            {isLoadingMessages ? (
              <div className="py-20 text-center text-slate-400">
                <LoadingSpinner size="lg" />
                <p className="text-xs mt-3">Loading message history...</p>
              </div>
            ) : messages.length === 0 ? (
              /* Empty State */
              <div className="max-w-2xl mx-auto py-12 text-center">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center mx-auto shadow-glow mb-4">
                  <Sparkles className="w-7 h-7" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">
                  Welcome, {user?.name}!
                </h3>
                <p className="text-xs text-slate-500 mt-1.5 max-w-md mx-auto leading-relaxed">
                  I am your AI knowledge assistant. Ask anything about courses, fees, exams, hostels, or scholarships.
                </p>

                <div className="mt-8 pt-6 border-t border-slate-200">
                  <SuggestedQuestions onSelect={handleSelectSuggested} />
                </div>
              </div>
            ) : (
              messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
            )}

            {/* In-flight loading animation */}
            {isSendingMessage && (
              <div className="flex justify-start gap-3.5 my-6">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm animate-pulse">
                  <GraduationCap className="w-5 h-5" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm p-4 shadow-subtle flex items-center gap-3">
                  <LoadingSpinner size="sm" />
                  <span className="text-xs font-medium text-slate-600">
                    Retrieving college documents & synthesizing grounded answer...
                  </span>
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Prompt Input Bar */}
          <div className="p-4 bg-white border-t border-slate-200">
            <div className="max-w-4xl mx-auto">
              <form onSubmit={handleSend} className="relative flex items-center">
                <input
                  type="text"
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  placeholder="Ask a question about fees, admissions, exams, hostel, policies..."
                  disabled={isSendingMessage}
                  className="w-full text-sm rounded-2xl border border-slate-300 pl-4 pr-14 py-3.5 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition shadow-inner"
                />
                <button
                  type="submit"
                  disabled={!inputQuery.trim() || isSendingMessage}
                  className="absolute right-2 p-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white transition disabled:opacity-30 shadow-sm"
                  title="Send Question"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
              <div className="flex items-center justify-between px-2 pt-2 text-[10px] text-slate-400">
                <span>Press Enter to send</span>
                <span>Grounded Retrieval Augmented Generation • MongoDB Atlas Vector Search</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
