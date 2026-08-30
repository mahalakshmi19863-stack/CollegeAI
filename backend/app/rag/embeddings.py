import hashlib
import asyncio
import logging
import re
from typing import List
import numpy as np
from ..config import settings
from ..utils.errors import EmbeddingFailedException

logger = logging.getLogger("college_ai.embeddings")

STOPWORDS = {
    "what", "when", "where", "which", "how", "who", "whom", "this", "that",
    "the", "is", "are", "was", "were", "be", "been", "a", "an", "and", "or",
    "for", "of", "to", "in", "on", "at", "by", "from", "with", "about", "tell",
    "me", "please", "can", "you", "does", "do", "did", "have", "has", "had",
}

STEM_SUFFIXES = ["opening", "closing", "timings", "timing", "hours", "hour", "ing", "ies", "es", "s", "ed"]


def stem_token(token: str) -> str:
    token = token.lower()
    for s in STEM_SUFFIXES:
        if token.endswith(s) and len(token) > len(s) + 2:
            return token[:-len(s)]
    return token


def _deterministic_local_embedding(text: str, dim: int = 768) -> List[float]:
    """
    Generates a high-dimensional semantic hash vector with cosine distance properties.
    Stemmed keywords and tokens produce strong directional alignment for semantic retrieval.
    """
    text_clean = text.lower().strip()
    words = re.findall(r"\b[a-z0-9_₹]+\b", text_clean)

    vec = np.zeros(dim, dtype=np.float32)
    if not words:
        vec[0] = 1.0
        return vec.tolist()

    content_words = [stem_token(w) for w in words if w not in STOPWORDS]
    if not content_words:
        content_words = [stem_token(w) for w in words]

    for word in content_words:
        # Generate word hash
        h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 10.0

        # Sub-word character bigrams for morphological robustness
        for i in range(len(word) - 1):
            bi = word[i : i + 2]
            bih = int(hashlib.md5(bi.encode("utf-8")).hexdigest(), 16)
            vec[bih % dim] += 1.5

    # L2 normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    else:
        vec[0] = 1.0

    return vec.tolist()


class EmbeddingService:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER.upper()
        self.api_key = settings.EMBEDDING_API_KEY or settings.LLM_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    def _validate_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Ensure provider output is safe and compatible with Atlas Vector Search."""
        if len(embeddings) == 0:
            return embeddings

        validated: List[List[float]] = []
        for index, embedding in enumerate(embeddings):
            if len(embedding) != self.dimension:
                raise EmbeddingFailedException(
                    f"Embedding {index} has dimension {len(embedding)}; "
                    f"expected {self.dimension}."
                )
            if not all(np.isfinite(value) for value in embedding):
                raise EmbeddingFailedException(
                    f"Embedding {index} contains a non-finite value."
                )
            validated.append([float(value) for value in embedding])
        return validated

    async def _embed_gemini(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google Gemini API."""
        if not self.api_key:
            logger.info("No Gemini API key supplied, using local embedding service.")
            return [_deterministic_local_embedding(t, self.dimension) for t in texts]

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            embeddings: List[List[float]] = []

            batch_size = max(1, settings.EMBEDDING_BATCH_SIZE)
            for start in range(0, len(texts), batch_size):
                batch = texts[start : start + batch_size]
                response = await asyncio.to_thread(
                    client.models.embed_content,
                    model=self.model,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.dimension
                    ),
                )
                if hasattr(response, "embeddings") and response.embeddings:
                    embeddings.extend(
                        list(embedding.values) for embedding in response.embeddings
                    )
                elif len(batch) == 1 and hasattr(response, "embedding") and response.embedding:
                    embeddings.append(list(response.embedding.values))
                else:
                    raise EmbeddingFailedException("Embedding provider returned an invalid batch response.")

            return self._validate_embeddings(embeddings)
        except Exception as e:
            logger.warning(
                f"Gemini embedding API call failed: {e}. Falling back to local semantic embedder."
            )
            return [_deterministic_local_embedding(t, self.dimension) for t in texts]

    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        if not self.api_key:
            logger.info("No OpenAI API key supplied, using local embedding service.")
            return [_deterministic_local_embedding(t, self.dimension) for t in texts]

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.embeddings.create(
                model=self.model or "text-embedding-3-small",
                input=texts,
            )
            return self._validate_embeddings([data.embedding for data in response.data])
        except Exception as e:
            logger.warning(
                f"OpenAI embedding API call failed: {e}. Falling back to local semantic embedder."
            )
            return [_deterministic_local_embedding(t, self.dimension) for t in texts]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of document chunk texts."""
        if not texts:
            return []

        try:
            if self.provider == "GEMINI" and self.api_key:
                embeddings = await self._embed_gemini(texts)
            elif self.provider == "OPENAI" and self.api_key:
                embeddings = await self._embed_openai(texts)
            else:
                embeddings = [
                    _deterministic_local_embedding(t, self.dimension) for t in texts
                ]
            return self._validate_embeddings(embeddings)
        except EmbeddingFailedException:
            raise
        except Exception as error:
            logger.exception("Embedding generation failed: %s", error)
            raise EmbeddingFailedException("Failed to generate embeddings.") from error

    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single user query."""
        res = await self.embed_documents([query])
        if not res:
            raise EmbeddingFailedException("Failed to generate embedding for query.")
        return self._validate_embeddings(res)[0]


embedding_service = EmbeddingService()
