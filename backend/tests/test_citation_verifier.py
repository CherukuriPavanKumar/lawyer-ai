import pytest
from app.agents.citation_verifier import verify_citations
from app.ingestion.chunker import Chunk

@pytest.mark.asyncio
async def test_layer1_regex_catch():
    chunks = [
        Chunk(act_name="Indian Contract Act, 1872", section_number="10", text="All agreements are contracts...")
    ]
    
    generated_text = "As per Section 99, this is completely invalid."
    result = await verify_citations(generated_text, chunks)
    
    assert result.passed is False
    assert "99" in result.failed_citations

@pytest.mark.asyncio
async def test_layer2_llm_catch():
    chunks = [
        Chunk(act_name="Indian Contract Act, 1872", section_number="10", text="All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object...")
    ]
    
    generated_text = "According to Section 10, an agreement is valid even if it lacks lawful consideration."
    result = await verify_citations(generated_text, chunks)
    
    assert result.passed is False
    assert "misattributed_claim" in result.failed_citations

@pytest.mark.asyncio
async def test_valid_citation():
    chunks = [
        Chunk(act_name="Indian Contract Act, 1872", section_number="10", text="All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object...")
    ]
    
    generated_text = "According to Section 10, all agreements are contracts if they are made by the free consent of parties competent to contract."
    result = await verify_citations(generated_text, chunks)
    
    assert result.passed is True
