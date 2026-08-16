import json
from pydantic import BaseModel
from typing import List, Optional

class Chunk(BaseModel):
    act_name: str
    section_number: str
    title: Optional[str] = None
    text: str
    metadata: dict = {}

def chunk_statute(json_path: str, act_name: str) -> List[Chunk]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = []
    for item in data:
        chunk = Chunk(
            act_name=act_name,
            section_number=str(item["section_number"]),
            title=item.get("title"),
            text=item["text"],
            metadata=item.get("metadata", {})
        )
        chunks.append(chunk)
    return chunks
