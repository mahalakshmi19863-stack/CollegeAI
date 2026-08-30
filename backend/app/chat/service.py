import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from ..database.mongodb import db_manager
from ..models.conversation import (
    ConversationInDB,
    ConversationResponse,
    ConversationUpdate,
)
from ..models.message import (
    ChatResponseData,
    MessageCreate,
    MessageInDB,
    MessageResponse,
    MessageRole,
    SourceItem,
)
from ..rag.pipeline import rag_pipeline
from ..utils.errors import ConversationNotFoundException

# In-memory storage fallback
_memory_conversations: Dict[str, dict] = {}
_memory_messages: List[dict] = []


def utc_now():
    return datetime.now(timezone.utc)


class ChatService:
    @classmethod
    async def create_conversation(
        cls, user_id: str, title: str = "New Conversation"
    ) -> ConversationResponse:
        conv_id = str(uuid.uuid4())
        now = utc_now()
        conv_doc = {
            "_id": conv_id,
            "user_id": user_id,
            "title": title[:100],
            "created_at": now,
            "updated_at": now,
        }

        if db_manager.is_connected and db_manager.conversations is not None:
            await db_manager.conversations.insert_one(conv_doc)
        else:
            _memory_conversations[conv_id] = conv_doc

        return ConversationResponse(
            id=conv_id,
            user_id=user_id,
            title=conv_doc["title"],
            created_at=now,
            updated_at=now,
            message_count=0,
        )

    @classmethod
    async def list_conversations(cls, user_id: str) -> List[ConversationResponse]:
        results: List[ConversationResponse] = []

        if db_manager.is_connected and db_manager.conversations is not None:
            cursor = db_manager.conversations.find({"user_id": user_id}).sort(
                "updated_at", -1
            )
            convs = await cursor.to_list(length=200)
            for c in convs:
                msg_count = await db_manager.messages.count_documents(
                    {"conversation_id": str(c["_id"])}
                )
                results.append(
                    ConversationResponse(
                        id=str(c["_id"]),
                        user_id=c["user_id"],
                        title=c["title"],
                        created_at=c["created_at"],
                        updated_at=c.get("updated_at", c["created_at"]),
                        message_count=msg_count,
                    )
                )
        else:
            user_convs = [
                c for c in _memory_conversations.values() if c["user_id"] == user_id
            ]
            user_convs.sort(key=lambda x: x["updated_at"], reverse=True)
            for c in user_convs:
                msg_count = sum(
                    1
                    for m in _memory_messages
                    if m["conversation_id"] == c["_id"]
                )
                results.append(
                    ConversationResponse(
                        id=c["_id"],
                        user_id=c["user_id"],
                        title=c["title"],
                        created_at=c["created_at"],
                        updated_at=c["updated_at"],
                        message_count=msg_count,
                    )
                )

        return results

    @classmethod
    async def get_conversation_with_messages(
        cls, conversation_id: str, user_id: str
    ) -> dict:
        conv_doc = None
        if db_manager.is_connected and db_manager.conversations is not None:
            conv_doc = await db_manager.conversations.find_one(
                {"_id": conversation_id, "user_id": user_id}
            )
        else:
            c = _memory_conversations.get(conversation_id)
            if c and c["user_id"] == user_id:
                conv_doc = c

        if not conv_doc:
            raise ConversationNotFoundException(
                f"Conversation {conversation_id} not found."
            )

        messages: List[MessageResponse] = []
        if db_manager.is_connected and db_manager.messages is not None:
            cursor = db_manager.messages.find(
                {"conversation_id": conversation_id}
            ).sort("created_at", 1)
            msg_docs = await cursor.to_list(length=500)
            for m in msg_docs:
                messages.append(
                    MessageResponse(
                        id=str(m["_id"]),
                        conversation_id=m["conversation_id"],
                        user_id=m["user_id"],
                        role=MessageRole(m["role"]),
                        content=m["content"],
                        sources=m.get("sources"),
                        retrieval_metadata=m.get("retrieval_metadata"),
                        created_at=m["created_at"],
                    )
                )
        else:
            msg_docs = [
                m
                for m in _memory_messages
                if m["conversation_id"] == conversation_id
            ]
            msg_docs.sort(key=lambda x: x["created_at"])
            for m in msg_docs:
                messages.append(
                    MessageResponse(
                        id=m["_id"],
                        conversation_id=m["conversation_id"],
                        user_id=m["user_id"],
                        role=MessageRole(m["role"]),
                        content=m["content"],
                        sources=m.get("sources"),
                        retrieval_metadata=m.get("retrieval_metadata"),
                        created_at=m["created_at"],
                    )
                )

        return {
            "conversation": ConversationResponse(
                id=str(conv_doc["_id"]),
                user_id=conv_doc["user_id"],
                title=conv_doc["title"],
                created_at=conv_doc["created_at"],
                updated_at=conv_doc.get("updated_at", conv_doc["created_at"]),
                message_count=len(messages),
            ),
            "messages": messages,
        }

    @classmethod
    async def update_conversation(
        cls, conversation_id: str, user_id: str, updates: ConversationUpdate
    ) -> ConversationResponse:
        now = utc_now()
        if db_manager.is_connected and db_manager.conversations is not None:
            result = await db_manager.conversations.find_one_and_update(
                {"_id": conversation_id, "user_id": user_id},
                {"$set": {"title": updates.title, "updated_at": now}},
                return_document=True,
            )
            if not result:
                raise ConversationNotFoundException()
            return ConversationResponse(
                id=str(result["_id"]),
                user_id=result["user_id"],
                title=result["title"],
                created_at=result["created_at"],
                updated_at=now,
            )
        else:
            c = _memory_conversations.get(conversation_id)
            if not c or c["user_id"] != user_id:
                raise ConversationNotFoundException()
            c["title"] = updates.title
            c["updated_at"] = now
            return ConversationResponse(
                id=c["_id"],
                user_id=c["user_id"],
                title=c["title"],
                created_at=c["created_at"],
                updated_at=now,
            )

    @classmethod
    async def delete_conversation(
        cls, conversation_id: str, user_id: str
    ) -> bool:
        if db_manager.is_connected and db_manager.conversations is not None:
            result = await db_manager.conversations.delete_one(
                {"_id": conversation_id, "user_id": user_id}
            )
            if result.deleted_count == 0:
                raise ConversationNotFoundException()
            await db_manager.messages.delete_many(
                {"conversation_id": conversation_id}
            )
        else:
            c = _memory_conversations.get(conversation_id)
            if not c or c["user_id"] != user_id:
                raise ConversationNotFoundException()
            _memory_conversations.pop(conversation_id, None)
            global _memory_messages
            _memory_messages = [
                m
                for m in _memory_messages
                if m["conversation_id"] != conversation_id
            ]
        return True

    @classmethod
    async def process_chat(
        cls, user_id: str, message_in: MessageCreate
    ) -> ChatResponseData:
        conv_id = message_in.conversation_id
        if not conv_id:
            title = message_in.question[:40].strip()
            if len(message_in.question) > 40:
                title += "..."
            new_conv = await cls.create_conversation(user_id, title=title)
            conv_id = new_conv.id

        now = utc_now()

        conversation_context = await cls._get_recent_context(conv_id, user_id)

        # Store user message
        user_msg_id = str(uuid.uuid4())
        user_msg_doc = {
            "_id": user_msg_id,
            "conversation_id": conv_id,
            "user_id": user_id,
            "role": MessageRole.USER.value,
            "content": message_in.question,
            "sources": None,
            "retrieval_metadata": None,
            "created_at": now,
        }

        if db_manager.is_connected and db_manager.messages is not None:
            await db_manager.messages.insert_one(user_msg_doc)
        else:
            _memory_messages.append(user_msg_doc)

        # Run RAG Pipeline
        rag_res = await rag_pipeline.generate_response(
            message_in.question,
            conversation_context=conversation_context,
        )

        # Store assistant message
        assistant_msg_id = str(uuid.uuid4())
        sources_dict = [s.model_dump() for s in rag_res["sources"]]
        retrieval_dict = rag_res["retrieval"].model_dump()

        assistant_msg_doc = {
            "_id": assistant_msg_id,
            "conversation_id": conv_id,
            "user_id": user_id,
            "role": MessageRole.ASSISTANT.value,
            "content": rag_res["answer"],
            "sources": sources_dict,
            "retrieval_metadata": retrieval_dict,
            "created_at": utc_now(),
        }

        if db_manager.is_connected and db_manager.messages is not None:
            await db_manager.messages.insert_one(assistant_msg_doc)
            await db_manager.conversations.update_one(
                {"_id": conv_id}, {"$set": {"updated_at": utc_now()}}
            )
        else:
            _memory_messages.append(assistant_msg_doc)
            if conv_id in _memory_conversations:
                _memory_conversations[conv_id]["updated_at"] = utc_now()

        return ChatResponseData(
            conversation_id=conv_id,
            message_id=assistant_msg_id,
            answer=rag_res["answer"],
            sources=rag_res["sources"],
            retrieval=rag_res["retrieval"],
        )

    @classmethod
    async def _get_recent_context(cls, conversation_id: str, user_id: str) -> str:
        """Provide recent turns for reference resolution without making them evidence."""
        if db_manager.is_connected and db_manager.messages is not None:
            cursor = db_manager.messages.find(
                {"conversation_id": conversation_id, "user_id": user_id}
            ).sort("created_at", -1)
            messages = list(reversed(await cursor.to_list(length=6)))
        else:
            messages = [
                message
                for message in _memory_messages
                if message["conversation_id"] == conversation_id
                and message["user_id"] == user_id
            ][-6:]

        return "\n".join(
            f"{message['role']}: {message['content']}" for message in messages
        )


chat_service = ChatService()
