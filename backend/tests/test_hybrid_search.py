import pytest
from app.retrieval.hybrid_search import hybrid_search
from app.db.session import async_session, init_db
from sqlalchemy import text

QUERIES = [
    ("What is free consent?", "14"),
    ("Are agreements without consideration void?", "25"),
    ("What happens if consent is obtained by fraud?", "17"),
    ("Is a contract valid if consideration is unlawful?", "23"),
    ("Can a minor enter into a contract?", "11"),
    ("What are the damages for breach of contract?", "73"),
    ("What is undue influence?", "16"),
    ("What happens if there is a penalty stipulated for breach?", "74"),
    ("If an agreement has an unlawful object in part, is it void?", "24"),
    ("What is the definition of a proposal?", "2"),
    ("What does coercion mean?", "15"),
    ("Is misrepresentation a ground for not having free consent?", "18"),
]

@pytest.mark.asyncio
async def test_hybrid_search_eval():
    await init_db()
    
    async with async_session() as session:
        count = await session.execute(text("SELECT COUNT(*) FROM statutes"))
        num_statutes = count.scalar()
        if num_statutes == 0:
            pytest.skip("No statutes ingested in DB, skipping evaluation.")

    print(f"\\n--- Running Retrieval Evaluation on {len(QUERIES)} Queries ---")
    hits = 0
    
    for query, expected_section in QUERIES:
        results = await hybrid_search(query, k=3, act_name="Indian Contract Act, 1872")
        retrieved_sections = [r.section_number for r in results]
        
        if expected_section in retrieved_sections:
            hits += 1
            status = "PASS"
        else:
            status = "FAIL"
            
        print(f"[{status}] Query: '{query}' | Expected: {expected_section} | Retrieved: {retrieved_sections}")
        
    hit_rate = hits / len(QUERIES)
    print(f"\\nTotal Hit Rate: {hit_rate * 100:.2f}% ({hits}/{len(QUERIES)})")
    
    assert hit_rate >= 0.8, f"Hit rate {hit_rate*100}% is below acceptable threshold of 80%"
