import logging
import re
from typing import List, Optional
from ..config import settings
from ..models.message import RetrievalStats, SourceItem
from .prompting import SYSTEM_PROMPT, UNKNOWN_INFORMATION_MESSAGE, build_rag_prompt
from .retrieval import RetrievalResult, retrieval_service

logger = logging.getLogger("college_ai.pipeline")


class RAGPipeline:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.upper()
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    @staticmethod
    def _is_semantically_relevant(question: str, retrieval_res: RetrievalResult) -> bool:
        if not retrieval_res or not retrieval_res.relevant_candidates:
            return False
        return any(
            retrieval_service._is_relevant_to_query(question, candidate.content)
            for candidate in retrieval_res.relevant_candidates
        )

    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini generative API."""
        if not self.api_key:
            raise ValueError("No Gemini API Key provided")

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,  # Low temperature for strict factual adherence
            ),
        )
        return response.text.strip()

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI chat completion API."""
        if not self.api_key:
            raise ValueError("No OpenAI API Key provided")

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.chat.completions.create(
            model=self.model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _extract_course_subjects(chunks: List[str]) -> List[str]:
        """Extract grounded course titles and codes from syllabus chunk text."""
        found_courses = []
        seen_codes = set()

        for chunk in chunks:
            lines = [line.strip() for line in chunk.splitlines() if line.strip()]
            for i, line in enumerate(lines):
                match = re.search(r"Course\s+Code\s*:?\s*([0-9A-Z]+)", line, re.IGNORECASE)
                if match:
                    code = match.group(1).upper()
                    if code in seen_codes:
                        continue

                    title = None
                    ignore_patterns = [
                        r"^Draft\s+Syllabus",
                        r"^VTU",
                        r"^\d+$",
                        r"^template",
                        r"^IPCC",
                        r"^PCC",
                        r"^AEC",
                        r"^Credits",
                    ]

                    for back in range(1, min(i + 1, 5)):
                        candidate_line = lines[i - back].strip()
                        if any(re.search(pat, candidate_line, re.IGNORECASE) for pat in ignore_patterns):
                            continue
                        if len(candidate_line) >= 3 and not candidate_line.startswith("Course Code"):
                            title = candidate_line
                            break

                    if not title:
                        cleaned_line = re.sub(r"Course\s+Code.*", "", line, flags=re.IGNORECASE).strip()
                        if cleaned_line and not any(re.search(pat, cleaned_line, re.IGNORECASE) for pat in ignore_patterns):
                            title = cleaned_line

                    if title:
                        title = re.sub(r"\s*Scheme\s*\d{4}", "", title, flags=re.IGNORECASE).strip()
                        if title.isupper():
                            title = title.title()
                        seen_codes.add(code)
                        found_courses.append(f"{title} ({code})")

        return found_courses

    def _local_grounded_synthesis(
        self, question: str, relevant_chunks: List[str]
    ) -> str:
        """Synthesizes factual answer strictly from retrieved chunk sentences when offline/local."""
        if not relevant_chunks:
            return UNKNOWN_INFORMATION_MESSAGE

        q_lower = question.lower()
        is_subject_query = any(
            k in q_lower for k in ["subject", "subjects", "course", "courses", "syllabus", "scheme", "curriculum"]
        )

        # Extract structured course list if course headers are present in retrieved chunks
        if is_subject_query:
            courses = self._extract_course_subjects(relevant_chunks)
            if courses:
                return (
                    "The 3rd semester CSE syllabus includes the following subjects:\n"
                    + "\n".join(f"- {c}" for c in courses)
                )

        # Extract sentences from relevant chunks that directly match query keywords
        q_words = set(
            re.findall(r"\b\w{3,}\b", question.lower())
        ) - {"what", "when", "where", "which", "how", "the", "are", "for", "and", "about"}

        all_text = " ".join(relevant_chunks)
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", all_text)
        matching_sentences = []

        for sentence in sentences:
            s_clean = sentence.strip()
            if not s_clean:
                continue
            s_words = set(re.findall(r"\b\w{3,}\b", s_clean.lower()))
            if q_words.intersection(s_words):
                matching_sentences.append(s_clean)

        if matching_sentences:
            return " ".join(matching_sentences[:3])

        # If chunks exist and are relevant, return clean chunk extract
        return relevant_chunks[0].strip()

    async def generate_response(
        self,
        question: str,
        category: Optional[str] = None,
        department: Optional[str] = None,
        conversation_context: str = "",
    ) -> dict:
        """Execute end-to-end grounded RAG generation pipeline."""
        # 1. Retrieve relevant candidates
        retrieval_res: RetrievalResult = await retrieval_service.retrieve(
            query=question,
            category=category,
            department=department,
        )

        # 2. Strict hallucination guard: reject weak or semantically mismatched retrieval
        if (
            not retrieval_res.relevant_candidates
            or not retrieval_res.formatted_context
            or not self._is_semantically_relevant(question, retrieval_res)
        ):
            logger.info(
                f"Question rejected due to insufficient or irrelevant context: '{question}'"
            )
            return {
                "answer": UNKNOWN_INFORMATION_MESSAGE,
                "sources": [],
                "retrieval": retrieval_res.stats,
            }

        # 3. Build grounded prompt
        prompt = build_rag_prompt(
            question,
            retrieval_res.formatted_context,
            conversation_context=conversation_context,
        )

        # 4. Generate answer via LLM
        answer = ""
        try:
            if self.provider == "GEMINI" and self.api_key:
                answer = await self._call_gemini(prompt)
            elif self.provider == "OPENAI" and self.api_key:
                answer = await self._call_openai(prompt)
            else:
                chunk_texts = [c.content for c in retrieval_res.relevant_candidates]
                answer = self._local_grounded_synthesis(question, chunk_texts)
        except Exception as e:
            logger.warning(
                f"LLM API call failed ({e}). Using local grounded synthesis fallback."
            )
            chunk_texts = [c.content for c in retrieval_res.relevant_candidates]
            answer = self._local_grounded_synthesis(question, chunk_texts)

        if not answer.strip():
            answer = UNKNOWN_INFORMATION_MESSAGE

        return {
            "answer": answer,
            "sources": retrieval_res.sources,
            "retrieval": retrieval_res.stats,
        }


rag_pipeline = RAGPipeline()
