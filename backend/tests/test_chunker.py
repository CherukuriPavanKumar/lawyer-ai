import os
import pytest
from app.ingestion.chunker import chunk_statute

def test_chunk_boundaries():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "statutes", "contract_act_1872.json")
    if not os.path.exists(json_path):
        pytest.skip(f"Mock data not found at {json_path}")
        
    chunks = chunk_statute(json_path, "Indian Contract Act, 1872")
    assert len(chunks) > 0, "Should load at least one chunk"
    
    section_numbers = set()
    for chunk in chunks:
        assert chunk.act_name == "Indian Contract Act, 1872"
        assert chunk.section_number, "Chunk must have a section number"
        assert len(chunk.text) > 20
        # Check uniqueness to ensure no mid-section splits
        assert chunk.section_number not in section_numbers, f"Duplicate section chunk found for section {chunk.section_number}, indicating a mid-section split."
        section_numbers.add(chunk.section_number)
