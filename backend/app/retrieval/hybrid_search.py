from sqlalchemy import text
from app.db.session import async_session
from app.ingestion.embedder import embed_texts
from app.ingestion.chunker import Chunk

class SearchResultChunk(Chunk):
    score: float

async def hybrid_search(query: str, k: int = 8, act_name: str = "Indian Contract Act, 1872") -> list[SearchResultChunk]:
    query_embedding = (await embed_texts([query]))[0]

    sql = text("""
        WITH semantic_search AS (
            SELECT id, RANK() OVER (ORDER BY embedding <=> :query_embedding) AS rank
            FROM statutes
            WHERE act_name = :act_name
            ORDER BY embedding <=> :query_embedding
            LIMIT :k
        ),
        keyword_search AS (
            SELECT id, RANK() OVER (ORDER BY ts_rank(search_vector, websearch_to_tsquery('english', :query)) DESC) AS rank
            FROM statutes
            WHERE act_name = :act_name AND search_vector @@ websearch_to_tsquery('english', :query)
            ORDER BY ts_rank(search_vector, websearch_to_tsquery('english', :query)) DESC
            LIMIT :k
        )
        SELECT
            s.id,
            s.act_name,
            s.section_number,
            s.title,
            s.text,
            s.metadata AS metadata_,
            COALESCE(1.0 / (60 + ss.rank), 0.0) + COALESCE(1.0 / (60 + ks.rank), 0.0) AS score
        FROM statutes s
        LEFT JOIN semantic_search ss ON s.id = ss.id
        LEFT JOIN keyword_search ks ON s.id = ks.id
        WHERE ss.id IS NOT NULL OR ks.id IS NOT NULL
        ORDER BY score DESC
        LIMIT :k;
    """)
    
    async with async_session() as session:
        query_embedding_str = str(query_embedding)
        result = await session.execute(
            sql, 
            {
                "query": query, 
                "query_embedding": query_embedding_str, 
                "k": k, 
                "act_name": act_name
            }
        )
        rows = result.fetchall()
        
        chunks = []
        for row in rows:
            chunks.append(
                SearchResultChunk(
                    act_name=row.act_name,
                    section_number=row.section_number,
                    title=row.title,
                    text=row.text,
                    metadata=row.metadata_ if row.metadata_ else {},
                    score=float(row.score)
                )
            )
        return chunks
