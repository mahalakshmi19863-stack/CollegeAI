import logging
import uuid
from typing import List, Optional, Tuple
from ..config import settings

logger = logging.getLogger("college_ai.chunking")


class ChunkData:
    def __init__(
        self,
        document_id: str,
        document_name: str,
        document_version: int,
        content: str,
        chunk_index: int,
        page_number: Optional[int],
        category: str,
        department: Optional[str] = None,
        is_active: bool = True,
    ):
        self.id = str(uuid.uuid4())
        self.document_id = document_id
        self.document_name = document_name
        self.document_version = document_version
        self.content = content
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.category = category
        self.department = department or "General"
        self.is_active = is_active


class SemanticChunker:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_text_sliding_window(self, text: str) -> List[str]:
        """Split text into overlapping chunks using word/character boundaries."""
        if not text:
            return []

        text = text.strip()
        if len(text) <= self.chunk_size:
            return [text]

        chunks: List[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            # If not at the end of the text, try to split at a sentence or word boundary
            if end < text_len:
                # Look for sentence boundary (.!?) near end
                boundary = -1
                for char in [". ", ".\n", "? ", "!\n", "\n\n", "\n"]:
                    last_pos = text.rfind(char, start + self.chunk_size // 2, end)
                    if last_pos != -1:
                        boundary = max(boundary, last_pos + len(char))

                if boundary != -1:
                    end = boundary
                else:
                    # Fall back to space boundary
                    space_pos = text.rfind(" ", start + self.chunk_size // 2, end)
                    if space_pos != -1:
                        end = space_pos + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Step forward by chunk_size - chunk_overlap
            step = max(1, (end - start) - self.chunk_overlap)
            start += step

        return chunks

    def chunk_document_pages(
        self,
        pages_content: List[Tuple[int, str]],
        document_id: str,
        document_name: str,
        document_version: int,
        category: str,
        department: Optional[str] = "General",
    ) -> List[ChunkData]:
        """Chunk all extracted pages while strictly preserving page numbers and metadata."""
        all_chunks: List[ChunkData] = []
        global_chunk_index = 0

        for page_num, text in pages_content:
            page_text_chunks = self._split_text_sliding_window(text)
            for chunk_text in page_text_chunks:
                chunk = ChunkData(
                    document_id=document_id,
                    document_name=document_name,
                    document_version=document_version,
                    content=chunk_text,
                    chunk_index=global_chunk_index,
                    page_number=page_num,
                    category=category,
                    department=department,
                    is_active=True,
                )
                all_chunks.append(chunk)
                global_chunk_index += 1

        logger.info(
            f"Created {len(all_chunks)} chunks for document '{document_name}' (ID: {document_id})"
        )
        return all_chunks


chunker = SemanticChunker()
