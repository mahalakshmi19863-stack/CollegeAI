import { create } from "zustand";
import { api } from "../services/api";
import { Conversation, Message } from "../types";

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  activeConversation: Conversation | null;
  messages: Message[];
  isLoadingConversations: boolean;
  isLoadingMessages: boolean;
  isSendingMessage: boolean;
  error: string | null;

  fetchConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  createConversation: () => void;
  sendMessage: (question: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversationTitle: (id: string, title: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  activeConversation: null,
  messages: [],
  isLoadingConversations: false,
  isLoadingMessages: false,
  isSendingMessage: false,
  error: null,

  fetchConversations: async () => {
    set({ isLoadingConversations: true, error: null });
    try {
      const convs = await api.chat.listConversations();
      set({ conversations: convs, isLoadingConversations: false });
    } catch (err: any) {
      set({ error: err.message, isLoadingConversations: false });
    }
  },

  selectConversation: async (id: string) => {
    set({
      activeConversationId: id,
      isLoadingMessages: true,
      error: null,
      messages: [],
    });
    try {
      const data = await api.chat.getConversation(id);
      set({
        activeConversation: data.conversation,
        messages: data.messages,
        isLoadingMessages: false,
      });
    } catch (err: any) {
      set({ error: err.message, isLoadingMessages: false });
    }
  },

  createConversation: () => {
    set({
      activeConversationId: null,
      activeConversation: null,
      messages: [],
      error: null,
    });
  },

  sendMessage: async (question: string) => {
    const { activeConversationId, messages } = get();
    if (!question.trim()) return;

    // Optimistically append user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId || "temp",
      user_id: "current-user",
      role: "USER",
      content: question,
      created_at: new Date().toISOString(),
    };

    set({
      messages: [...messages, tempUserMsg],
      isSendingMessage: true,
      error: null,
    });

    try {
      const data = await api.chat.sendMessage(
        question,
        activeConversationId || undefined
      );

      const assistantMsg: Message = {
        id: data.message_id,
        conversation_id: data.conversation_id,
        user_id: "college-ai",
        role: "ASSISTANT",
        content: data.answer,
        sources: data.sources,
        retrieval_metadata: data.retrieval,
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        activeConversationId: data.conversation_id,
        messages: [...state.messages.filter((m) => m.id !== tempUserMsg.id), { ...tempUserMsg, id: `user-${data.message_id}` }, assistantMsg],
        isSendingMessage: false,
      }));

      // Refresh conversations list to update titles/counts
      get().fetchConversations();
    } catch (err: any) {
      set((state) => ({
        messages: state.messages.filter((m) => m.id !== tempUserMsg.id),
        error: err.message || "Failed to generate response. Please try again.",
        isSendingMessage: false,
      }));
    }
  },

  deleteConversation: async (id: string) => {
    try {
      await api.chat.deleteConversation(id);
      set((state) => ({
        conversations: state.conversations.filter((c) => c.id !== id),
        activeConversationId:
          state.activeConversationId === id ? null : state.activeConversationId,
        messages: state.activeConversationId === id ? [] : state.messages,
      }));
    } catch (err: any) {
      set({ error: err.message });
    }
  },

  updateConversationTitle: async (id: string, title: string) => {
    try {
      const updated = await api.chat.updateConversation(id, title);
      set((state) => ({
        conversations: state.conversations.map((c) =>
          c.id === id ? updated : c
        ),
        activeConversation:
          state.activeConversation?.id === id ? updated : state.activeConversation,
      }));
    } catch (err: any) {
      set({ error: err.message });
    }
  },
}));
