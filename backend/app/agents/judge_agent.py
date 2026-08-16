import json
from typing import List, Dict, Any
from app.llm.provider import generate_completion

JUDGE_PROMPT = """
You are a senior law professor evaluating a student's performance in a legal debate against an AI opposing counsel.
The topic was: {topic}
The student argued: {student_position}

Below is the full transcript of the debate:
{transcript}

Evaluate the student's performance across 4 criteria on a scale of 1-10.
You must return your response as a raw JSON object with the exact following schema, and absolutely no markdown formatting, markdown blocks (like ```json), or extra text:

{{
  "issue_identification": {{
    "score": 1,
    "feedback": "string"
  }},
  "application_of_law": {{
    "score": 1,
    "feedback": "string"
  }},
  "logical_structure": {{
    "score": 1,
    "feedback": "string"
  }},
  "rebuttal_responsiveness": {{
    "score": 1,
    "feedback": "string"
  }},
  "overall_feedback": "string"
}}
"""

async def evaluate_debate(topic: str, student_position: str, turns: List[Dict[str, Any]]) -> dict:
    transcript = ""
    for t in turns:
        role = "Student" if t["role"] == "student" else "Opposing Counsel"
        transcript += f"{role}: {t['content']}\\n\\n"
        
    system_message = JUDGE_PROMPT.format(
        topic=topic,
        student_position=student_position,
        transcript=transcript.strip()
    )
    
    messages = [{"role": "system", "content": system_message}]
    
    response_text = await generate_completion(messages, model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
    
    try:
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse judge output as JSON",
            "raw_output": response_text
        }
