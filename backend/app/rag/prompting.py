from typing import Optional

UNKNOWN_INFORMATION_MESSAGE = (
    "I couldn't find this information in the available college documents."
)

SYSTEM_PROMPT = """You are CollegeAI, an official, grounded artificial intelligence assistant for the college.
Your primary objective is to provide accurate, truthful, and helpful answers based STRICTLY and ONLY on the provided college document context.

### MANDATORY INSTRUCTIONS:
1. Grounding: The supplied retrieved context is your absolute source of truth. Do NOT use outside assumptions or prior training data for college-specific details.
2. Anti-Hallucination: Never invent or assume salaries, fees, dates, rules, faculty names, department info, policies, schedules, or contact details.
3. Missing Information: If the provided context does NOT contain the exact answer to the student's question, you must clearly output:
"I couldn't find this information in the available college documents."
4. Conciseness: Answer the question directly and concisely without fluff.
5. Citation: Refer naturally to the source documents provided in the context (e.g. "According to the Hostel Information Handbook...").
6. Tone: Professional, courteous, helpful, and academic.
"""


def build_rag_prompt(
    question: str, context: str, conversation_context: str = ""
) -> str:
    """Construct the final prompt for the LLM combining system context, retrieved documents, and question."""
    if not context or not context.strip():
        return (
            f"Question: {question}\n\n"
            f"Context: None\n\n"
            f"Instruction: Return the unavailable information response."
        )

    history = (
        f"Recent conversation (use only to resolve references, never as a source of college facts):\n"
        f"{conversation_context.strip()}\n\n"
        if conversation_context.strip()
        else ""
    )

    return f"""{history}Context from College Official Knowledge Base:
=====================================================
{context}
=====================================================

Student Question: {question}

Provide a direct, grounded answer citing the facts from the context above. If the context does not contain the answer, respond with the exact unavailable information message."""
