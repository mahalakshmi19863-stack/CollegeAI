import React, { useEffect } from "react";
import { useRouter } from "next/router";
import DashboardPage from "../dashboard";
import { useChatStore } from "../../store/chatStore";

export default function ChatPage() {
  const router = useRouter();
  const { id } = router.query;
  const { selectConversation, activeConversationId } = useChatStore();

  useEffect(() => {
    if (id && typeof id === "string" && id !== activeConversationId) {
      selectConversation(id);
    }
  }, [id, selectConversation, activeConversationId]);

  return <DashboardPage />;
}
