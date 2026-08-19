from app.llm.provider import generate_completion
from app.ingestion.chunker import Chunk

COUNSEL_SYSTEM_PROMPT = """
You are opposing counsel in a legal debate practice exercise for law students.
The student has taken the position: {student_position} on the topic: {topic}.
Your role is to argue the opposite position as persuasively and rigorously as
a skilled advocate would.

Rules:
- Cite only the statute sections provided in the retrieved context below. Never
  reference a section, case, or provision that is not in the provided context.
- If the provided context does not support a strong counter-argument, say so
  explicitly rather than inventing a citation.
- Hold your position. Do not concede or soften your argument because the
  student's argument sounds confident — find the strongest available counter,
  or state clearly that none exists in the retrieved material.
- Write in the register of an actual legal argument, not a summary.

Retrieved context:
{retrieved_context}
"""

async def generate_rebuttal(topic: str, student_position: str, student_argument: str, retrieved_chunks: list[Chunk]) -> str:
    context_str = "\\n\\n".join([f"Section {c.section_number} - {c.title}:\\n{c.text}" for c in retrieved_chunks])
    
    system_message = COUNSEL_SYSTEM_PROMPT.format(
        student_position=student_position,
        topic=topic,
        retrieved_context=context_str
    )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": student_argument}
    ]
    
    response = await generate_completion(messages, model="openai/gpt-oss-120b")
    return response
