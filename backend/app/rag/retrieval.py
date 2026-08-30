import logging
import time
from typing import List, Optional, Tuple
from ..config import settings
from ..models.chunk import ChunkSearchCandidate
from ..models.message import RetrievalStats, SourceItem
from .embeddings import embedding_service
from .vector_search import vector_search_engine

logger = logging.getLogger("college_ai.retrieval")


class RetrievalResult:
    def __init__(
        self,
        candidates: List[ChunkSearchCandidate],
        relevant_candidates: List[ChunkSearchCandidate],
        sources: List[SourceItem],
        formatted_context: str,
        stats: RetrievalStats,
    ):
        self.candidates = candidates
        self.relevant_candidates = relevant_candidates
        self.sources = sources
        self.formatted_context = formatted_context
        self.stats = stats


class RetrievalService:
    def __init__(
        self,
        top_k: int = settings.TOP_K,
        relevance_threshold: float = settings.RELEVANCE_THRESHOLD,
    ):
        self.top_k = top_k
        self.relevance_threshold = relevance_threshold

    async def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        department: Optional[str] = None,
    ) -> RetrievalResult:
        """Execute complete retrieval pipeline for user query."""
        start_time = time.time()

        # Step 1: Generate query embedding vector
        query_vector = await embedding_service.embed_query(query)

        # Step 2: Perform vector similarity search
        candidates = await vector_search_engine.search(
            query_vector=query_vector,
            top_k=self.top_k,
            category=category,
            department=department,
        )

        # Step 3: Filter candidates by relevance threshold
        relevant_candidates = [
            c for c in candidates if c.score >= self.relevance_threshold
        ]

        # Step 4: Construct source items and formatted context
        sources: List[SourceItem] = []
        context_blocks: List[str] = []

        for candidate in relevant_candidates:
            source = SourceItem(
                document_id=candidate.document_id,
                document_name=candidate.document_name,
                page_number=candidate.page_number,
                relevance_score=round(candidate.score, 3),
                category=candidate.category,
                department=candidate.department,
                snippet=(
                    candidate.content[:200] + "..."
                    if len(candidate.content) > 200
                    else candidate.content
                ),
            )
            sources.append(source)

            page_info = (
                f" (Page {candidate.page_number})"
                if candidate.page_number is not None
                else ""
            )
            block = (
                f"--- [SOURCE: {candidate.document_name}{page_info} | Category: {candidate.category}] ---\n"
                f"{candidate.content}\n"
            )
            context_blocks.append(block)

        formatted_context = "\n".join(context_blocks).strip()

        duration_ms = round((time.time() - start_time) * 1000, 2)
        stats = RetrievalStats(
            chunks_retrieved=len(candidates),
            chunks_used=len(relevant_candidates),
            processing_time_ms=duration_ms,
        )

        logger.info(
            f"Retrieval complete in {duration_ms}ms: {len(relevant_candidates)}/{len(candidates)} chunks used for query: '{query[:40]}...'"
        )

        return RetrievalResult(
            candidates=candidates,
            relevant_candidates=relevant_candidates,
            sources=sources,
            formatted_context=formatted_context,
            stats=stats,
        )


retrieval_service = RetrievalService()
