import re
from pydantic import BaseModel
from typing import List, Optional
from app.ingestion.chunker import Chunk
from app.llm.provider import generate_completion

class VerificationResult(BaseModel):
    passed: bool
    reason: Optional[str] = None
    failed_citations: List[str] = []

async def verify_citations(generated_text: str, retrieved_chunks: List[Chunk]) -> VerificationResult:
    """
    Layer 1: regex-extract citation-like patterns and reject if section_number is not in retrieved_chunks.
    Layer 2: LLM call to verify support.
    """
    # Layer 1
    pattern = r'(?i)\b(?:section|sec\.?)\s+(\d+[A-Za-z]?(?:\(\d+\))?)'
    matches = re.finditer(pattern, generated_text)
    
    extracted_sections = []
    for match in matches:
        extracted_sections.append(match.group(1).strip())
        
    retrieved_section_numbers = [c.section_number for c in retrieved_chunks]
    
    failed_citations = []
    for sec in extracted_sections:
        base_sec = re.match(r'^(\d+[A-Za-z]?)', sec)
        if base_sec:
            base_sec_str = base_sec.group(1)
            if base_sec_str not in retrieved_section_numbers:
                failed_citations.append(sec)
                
    if failed_citations:
        return VerificationResult(
            passed=False, 
            reason=f"Fabricated or un-retrieved citations found: {', '.join(failed_citations)}", 
            failed_citations=failed_citations
        )
        
    # Layer 2
    if not extracted_sections:
        return VerificationResult(passed=True)
        
    context_str = "\\n\\n".join([f"Section {c.section_number}:\\n{c.text}" for c in retrieved_chunks])
    
    prompt = f"""
    You are a strict citation verification system.
    Evaluate if the generated text accurately represents the provided statutory context.
    If the text makes any legal claims attributed to a section that CONTRADICT or are NOT found in the text of that section, you must reject it.
    However, partial quotes or summaries that omit parts of a section are completely ACCEPTABLE, as long as the claim they do make is factually supported by the context.
    
    Context:
    {context_str}
    
    Generated Text:
    {generated_text}
    
    Reply ONLY with "YES" if the text is supported by the context (even if it's a partial summary).
    Reply with "NO: <reason>" if there is any misattribution or hallucinated claim.
    """
    
    messages = [{"role": "user", "content": prompt}]
    
    # Use a cheap/fast model for verification. 
    response = await generate_completion(messages, model="openai/gpt-oss-20b")
    
    if response.strip().upper().startswith("YES"):
        return VerificationResult(passed=True)
    else:
        return VerificationResult(
            passed=False,
            reason=response.strip(),
            failed_citations=["misattributed_claim"]
        )
