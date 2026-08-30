import logging
from typing import Any, Dict, List, Optional
import numpy as np
from ..config import settings
from ..database.mongodb import db_manager
from ..models.chunk import ChunkSearchCandidate
from ..utils.errors import VectorSearchFailedException

logger = logging.getLogger("college_ai.vector_search")

# In-memory chunk store for local testing
_memory_chunks: List[dict] = []


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    dot = np.dot(a, b)
    similarity = dot / (norm_a * norm_b)
    return float(similarity)


class VectorSearchEngine:
    @staticmethod
    def register_memory_chunk(chunk_dict: dict):
        """Store chunk in memory cache for offline/standalone execution."""
        # Replace if ID exists
        for i, existing in enumerate(_memory_chunks):
            if existing.get("_id") == chunk_dict.get("_id"):
                _memory_chunks[i] = chunk_dict
                return
        _memory_chunks.append(chunk_dict)

    @staticmethod
    def remove_memory_chunks_for_doc(doc_id: str):
        """Remove chunks for a document from memory cache."""
        _memory_chunks[:] = [
            c for c in _memory_chunks if c.get("document_id") != doc_id
        ]

    @staticmethod
    def set_memory_chunks_active(doc_id: str, is_active: bool):
        """Update is_active status of memory chunks."""
        for c in _memory_chunks:
            if c.get("document_id") == doc_id:
                c["is_active"] = is_active

    async def search(
        self,
        query_vector: List[float],
        top_k: int = settings.TOP_K,
        category: Optional[str] = None,
        department: Optional[str] = None,
    ) -> List[ChunkSearchCandidate]:
        """Perform semantic vector similarity search."""
        candidates: List[ChunkSearchCandidate] = []

        # Strategy 1: MongoDB Atlas Vector Search
        if db_manager.is_connected and db_manager.document_chunks is not None:
            try:
                pipeline: List[Dict[str, Any]] = [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "embedding",
                            "queryVector": query_vector,
                            "numCandidates": top_k * 10,
                            "limit": top_k,
                            "filter": {
                                "$and": [
                                    {"is_active": {"$eq": True}},
                                    *(
                                        [{"category": {"$eq": category}}]
                                        if category
                                        else []
                                    ),
                                    *(
                                        [{"department": {"$eq": department}}]
                                        if department
                                        else []
                                    ),
                                ]
                            },
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "document_id": 1,
                            "document_name": 1,
                            "document_version": 1,
                            "content": 1,
                            "chunk_index": 1,
                            "page_number": 1,
                            "category": 1,
                            "department": 1,
                            "score": {"$meta": "vectorSearchScore"},
                        }
                    },
                ]

                cursor = db_manager.document_chunks.aggregate(pipeline)
                results = await cursor.to_list(length=top_k)

                for doc in results:
                    candidates.append(
                        ChunkSearchCandidate(
                            chunk_id=str(doc["_id"]),
                            document_id=doc["document_id"],
                            document_name=doc["document_name"],
                            document_version=doc.get("document_version", 1),
                            page_number=doc.get("page_number"),
                            category=doc.get("category", "General"),
                            department=doc.get("department"),
                            content=doc["content"],
                            score=float(doc.get("score", 0.0)),
                        )
                    )

                if candidates:
                    return candidates

            except Exception as e:
                logger.info(
                    f"Atlas $vectorSearch not available ({e}), falling back to direct collection cosine comparison."
                )
                try:
                    # Fallback: Read active chunks from MongoDB and perform cosine similarity
                    fallback_filter = {"is_active": True}
                    if category:
                        fallback_filter["category"] = category
                    if department:
                        fallback_filter["department"] = department
                    cursor = db_manager.document_chunks.find(fallback_filter)
                    all_chunks = await cursor.to_list(length=5000)
                    scored = []
                    for c in all_chunks:
                        if "embedding" in c and c["embedding"]:
                            sim = cosine_similarity(query_vector, c["embedding"])
                            scored.append((sim, c))

                    scored.sort(key=lambda x: x[0], reverse=True)
                    top_scored = scored[:top_k]

                    for sim, c in top_scored:
                        candidates.append(
                            ChunkSearchCandidate(
                                chunk_id=str(c["_id"]),
                                document_id=c["document_id"],
                                document_name=c["document_name"],
                                document_version=c.get("document_version", 1),
                                page_number=c.get("page_number"),
                                category=c.get("category", "General"),
                                department=c.get("department"),
                                content=c["content"],
                                score=sim,
                            )
                        )
                    return candidates
                except Exception as inner_e:
                    logger.warning(f"Database scan failed: {inner_e}")

        # Strategy 2: In-Memory Cosine Vector Comparison
        scored = []
        for c in _memory_chunks:
            if not c.get("is_active", True):
                continue
            if category and c.get("category") != category:
                continue
            if department and c.get("department") != department:
                continue
            if "embedding" in c and c["embedding"]:
                sim = cosine_similarity(query_vector, c["embedding"])
                scored.append((sim, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_scored = scored[:top_k]

        for sim, c in top_scored:
            candidates.append(
                ChunkSearchCandidate(
                    chunk_id=str(c.get("_id", c.get("id"))),
                    document_id=c["document_id"],
                    document_name=c["document_name"],
                    document_version=c.get("document_version", 1),
                    page_number=c.get("page_number"),
                    category=c.get("category", "General"),
                    department=c.get("department"),
                    content=c["content"],
                    score=sim,
                )
            )

        return candidates


vector_search_engine = VectorSearchEngine()
