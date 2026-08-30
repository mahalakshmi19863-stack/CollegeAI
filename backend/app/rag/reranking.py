import logging
from typing import List
from ..models.chunk import ChunkSearchCandidate

logger = logging.getLogger("college_ai.reranking")


class Reranker:
    """Optional reranking component to reorder candidates based on lexical/semantic cross-encoding."""

    @staticmethod
    def rerank(
        query: str, candidates: List[ChunkSearchCandidate]
    ) -> List[ChunkSearchCandidate]:
        if not candidates:
            return []

        query_terms = set(query.lower().split())
        for c in candidates:
            content_words = set(c.content.lower().split())
            overlap = len(query_terms.intersection(content_words))
            boost = (overlap / max(1, len(query_terms))) * 0.1
            c.score = min(1.0, c.score + boost)

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates


reranker = Reranker()
