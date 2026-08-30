from typing import Dict, List
from ..database.mongodb import db_manager
from ..documents.service import _memory_documents, document_service
from ..feedback.routes import _memory_feedback
from ..auth.service import _memory_users
from ..chat.service import _memory_messages


class AdminService:
    @classmethod
    async def get_dashboard_metrics(cls) -> dict:
        total_docs = 0
        processed_docs = 0
        failed_docs = 0
        total_students = 0
        total_questions = 0
        total_feedback = 0
        helpful_count = 0
        not_helpful_count = 0
        recent_uploads = []

        if db_manager.is_connected and db_manager.db is not None:
            total_docs = await db_manager.documents.count_documents({})
            processed_docs = await db_manager.documents.count_documents(
                {"status": "PROCESSED"}
            )
            failed_docs = await db_manager.documents.count_documents(
                {"status": "FAILED"}
            )
            total_students = await db_manager.users.count_documents(
                {"role": "STUDENT"}
            )
            total_questions = await db_manager.messages.count_documents(
                {"role": "USER"}
            )
            total_feedback = await db_manager.feedback.count_documents({})
            helpful_count = await db_manager.feedback.count_documents(
                {"rating": "helpful"}
            )
            not_helpful_count = await db_manager.feedback.count_documents(
                {"rating": "not_helpful"}
            )

            cursor = db_manager.documents.find().sort("uploaded_at", -1).limit(5)
            recent_docs = await cursor.to_list(length=5)
            recent_uploads = [
                document_service._to_response(d).model_dump() for d in recent_docs
            ]
        else:
            total_docs = len(_memory_documents)
            processed_docs = sum(
                1 for d in _memory_documents.values() if d.get("status") == "PROCESSED"
            )
            failed_docs = sum(
                1 for d in _memory_documents.values() if d.get("status") == "FAILED"
            )
            total_students = sum(
                1 for u in _memory_users.values() if u.get("role") == "STUDENT"
            )
            total_questions = sum(
                1 for m in _memory_messages if m.get("role") == "USER"
            )
            total_feedback = len(_memory_feedback)
            helpful_count = sum(
                1 for f in _memory_feedback if f.get("rating") == "helpful"
            )
            not_helpful_count = sum(
                1 for f in _memory_feedback if f.get("rating") == "not_helpful"
            )

            sorted_docs = sorted(
                _memory_documents.values(),
                key=lambda x: x.get("uploaded_at"),
                reverse=True,
            )
            recent_uploads = [
                document_service._to_response(d).model_dump()
                for d in sorted_docs[:5]
            ]

        satisfaction_rate = (
            round((helpful_count / total_feedback) * 100, 1)
            if total_feedback > 0
            else 100.0
        )

        return {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "failed_documents": failed_docs,
            "total_students": total_students,
            "total_questions": total_questions,
            "feedback_stats": {
                "total": total_feedback,
                "helpful": helpful_count,
                "not_helpful": not_helpful_count,
                "satisfaction_rate_percent": satisfaction_rate,
            },
            "recent_uploads": recent_uploads,
        }

    @classmethod
    async def get_analytics(cls) -> dict:
        category_counts: Dict[str, int] = {}
        department_counts: Dict[str, int] = {}

        if db_manager.is_connected and db_manager.db is not None:
            cat_pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ]
            async for doc in db_manager.documents.aggregate(cat_pipeline):
                cat = doc["_id"] or "General"
                category_counts[cat] = doc["count"]

            dept_pipeline = [
                {"$group": {"_id": "$department", "count": {"$sum": 1}}}
            ]
            async for doc in db_manager.documents.aggregate(dept_pipeline):
                dept = doc["_id"] or "General"
                department_counts[dept] = doc["count"]
        else:
            for doc in _memory_documents.values():
                cat = doc.get("category", "General")
                category_counts[cat] = category_counts.get(cat, 0) + 1
                dept = doc.get("department", "General")
                department_counts[dept] = department_counts.get(dept, 0) + 1

        dashboard_stats = await cls.get_dashboard_metrics()

        return {
            "categories": category_counts,
            "departments": department_counts,
            "overview": dashboard_stats,
        }


admin_service = AdminService()
