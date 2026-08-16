import asyncio
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ingestion.chunker import chunk_statute
from app.ingestion.embedder import embed_texts
from app.db.session import async_session, init_db
from app.db.models import Statute
from sqlalchemy.dialects.postgresql import insert

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=str)
    parser.add_argument("--act-name", type=str, default="Indian Contract Act, 1872")
    args = parser.parse_args()

    await init_db()

    chunks = chunk_statute(args.json_path, args.act_name)
    print(f"Loaded {len(chunks)} chunks from {args.json_path}.")
    
    batch_size = 50
    async with async_session() as session:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            texts = [c.text for c in batch]
            print(f"Embedding batch {i} to {i+len(batch)}...")
            embeddings = await embed_texts(texts)
            
            for chunk, emb in zip(batch, embeddings):
                # Use PostgreSQL INSERT ... ON CONFLICT DO UPDATE (upsert)
                # so re-running the script never causes duplicate key errors.
                stmt = insert(Statute).values(
                    act_name=chunk.act_name,
                    section_number=chunk.section_number,
                    title=chunk.title,
                    text=chunk.text,
                    metadata_=chunk.metadata,
                    embedding=emb,
                ).on_conflict_do_update(
                    index_elements=["act_name", "section_number"],
                    set_={
                        "title": chunk.title,
                        "text": chunk.text,
                        "metadata": chunk.metadata,  # DB column name, not Python attr name
                        "embedding": emb,
                    }
                )
                await session.execute(stmt)
            await session.commit()
            print(f"Upserted {len(batch)} chunks.")

    print(f"\nDone! Total sections embedded: {len(chunks)}")

if __name__ == "__main__":
    asyncio.run(main())
