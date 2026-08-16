# Project brief: Advocatus — AI legal debate practice tool

> Working title, rename freely. Read this entire document before writing any code.

## 1. What this is

A web tool that lets law students practice adversarial debate against an AI opposing counsel, grounded in real statute text via retrieval, instead of requiring a human moderator to always be available. Built for a college law department as a faculty-sponsored project. Domain for v1: **Indian Contract Act, 1872** only — do not expand corpus until Phase 1 passes its acceptance criteria.

## 2. Core build rule — read this before anything else

**Build and verify phases in strict order. Do not scaffold Phase N+1 code until Phase N's acceptance criteria pass.** This is not a preference, it's a requirement — if retrieval quality is bad (Phase 1) or the base generation is weak (Phase 2), building the orchestration graph on top of it just buries a broken foundation under harder-to-debug layers. If you are an agent implementing this: after finishing each phase, stop, report the acceptance criteria results, and wait for confirmation before continuing.

## 3. Fixed tech stack — do not substitute without asking

| Layer | Choice |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| Database | PostgreSQL + `pgvector` extension (native `tsvector` for keyword search — no separate search engine) |
| Orchestration | LangGraph (only from Phase 4 onward) |
| LLM | Abstracted behind a single provider interface — support Anthropic Claude and OpenAI, selected via env var. Do not hardcode a provider into agent logic. |
| Embeddings | Configurable via env var; default `text-embedding-3-small` or equivalent — dimension must match the `pgvector` column, don't hardcode 1536 if the model changes |
| Frontend | Next.js (App Router), TypeScript strict mode, Tailwind CSS |
| Local dev DB | Docker Compose, `pgvector/pgvector` image |
| Deployment target | Vercel (frontend) + Supabase or Railway (Postgres with pgvector) — no browser automation needed, don't add Playwright/heavier infra |

## 4. Repository structure

Scaffold exactly this — don't invent an alternate layout:

```
advocatus/
  backend/
    app/
      main.py
      config.py                    # env var loading, pydantic Settings
      db/
        models.py
        session.py
        migrations/
      ingestion/
        chunker.py                 # section-boundary chunking, not token-based
        embedder.py
        ingest_statute.py          # CLI script: JSON -> DB
      retrieval/
        hybrid_search.py
      llm/
        provider.py                 # abstraction over Claude/OpenAI
      agents/
        counsel_agent.py            # Phase 2
        citation_verifier.py        # Phase 3
        judge_agent.py               # Phase 5
        graph.py                     # LangGraph state machine, Phase 4
      api/
        routes/
          debate.py
    tests/
      test_chunker.py
      test_hybrid_search.py         # retrieval eval set lives here
      test_citation_verifier.py
    requirements.txt
    .env.example
    docker-compose.yml
  frontend/
    app/
      debate/
        new/page.tsx
        [id]/page.tsx
    components/
    lib/
      api-client.ts
    package.json
  data/
    statutes/
      contract_act_1872.json        # source JSON: [{section_number, title, text}]
  README.md
```

## 5. Database schema (Phase 1)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for gen_random_uuid()

CREATE TABLE statutes (
    id SERIAL PRIMARY KEY,
    act_name TEXT NOT NULL,
    section_number TEXT NOT NULL,
    title TEXT,
    text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),  -- match embedding model dimension, do not hardcode blindly
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || text)
    ) STORED
);

CREATE INDEX idx_statutes_search ON statutes USING GIN (search_vector);
CREATE INDEX idx_statutes_embedding ON statutes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE UNIQUE INDEX idx_statutes_section ON statutes (act_name, section_number);

CREATE TABLE debates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    act_name TEXT NOT NULL,
    student_position TEXT CHECK (student_position IN ('for', 'against')),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    debate_id UUID REFERENCES debates(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('student', 'counsel_agent', 'judge')),
    content TEXT NOT NULL,
    citations JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE citation_checks (
    id SERIAL PRIMARY KEY,
    turn_id UUID REFERENCES turns(id) ON DELETE CASCADE,
    citation_text TEXT NOT NULL,
    verified BOOLEAN NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## 6. Phase 1 — Ingestion + hybrid retrieval

**Build:**
- `chunker.py`: splits statute JSON into one chunk per section/sub-section. Never split mid-section on token count.
- `embedder.py`: thin wrapper calling the configured embedding provider.
- `ingest_statute.py`: CLI script, `python -m app.ingestion.ingest_statute data/statutes/contract_act_1872.json`, upserts into `statutes` table.
- `hybrid_search.py`: implement

```python
async def hybrid_search(query: str, k: int = 8) -> list[Chunk]:
    """
    Run keyword search (ts_rank on search_vector) and semantic search
    (cosine similarity on embedding) in parallel, combine via reciprocal
    rank fusion: score = sum(1 / (60 + rank_i)) across both rankings.
    Return top-k Chunk objects with section_number, title, text, score.
    """
```

**Definition of done (do not proceed to Phase 2 until this passes):**
- Ingest the full Indian Contract Act 1872 (source it from a public-domain bare-acts source, e.g. India Code).
- Write 15-20 hand-written test queries covering common contract-law concepts (consideration, free consent, void agreements, breach, damages) with the section number(s) you'd expect a competent researcher to retrieve, into `test_hybrid_search.py`.
- Hit rate on that eval set must be manually reviewed and judged acceptable before moving on — don't just eyeball one or two queries.

## 7. Phase 2 — Single-turn rebuttal endpoint

**Endpoint:** `POST /api/debate/rebut`

```json
// request
{ "topic": "string", "student_position": "for" | "against", "student_argument": "string" }

// response
{ "counter_argument": "string", "citations": [{ "section_number": "string", "snippet": "string" }] }
```

**`counsel_agent.py` system prompt (draft, refine as needed):**

```
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
{retrieved_chunks}
```

**Definition of done:** manually run 15-20 student arguments through this endpoint (no orchestration, no verification yet) and read every output. Bad retrieval or weak arguments must be caught and understood here — this is the cheapest place to catch them.

## 8. Phase 3 — Citation verification

**`citation_verifier.py`:**

```python
def verify_citations(generated_text: str, retrieved_chunks: list[Chunk]) -> VerificationResult:
    """
    Layer 1 (cheap, always run): regex-extract citation-like patterns
    (Section \d+[A-Za-z]?(\(\d+\))?) from generated_text. Reject if any
    extracted citation's section_number is not in retrieved_chunks.

    Layer 2 (LLM call, run in Phase 3 eval and optionally in prod): for each
    claim tied to a citation, ask a cheap model "does this chunk support this
    claim, yes/no". Reject if any answer is not an unambiguous yes.

    Return VerificationResult(passed: bool, reason: str | None,
    failed_citations: list[str]).
    """
```

Wire into the rebuttal endpoint: on verification failure, regenerate with the failure reason appended to the prompt (max 2 retries), then fall back to a graceful "I don't have a strong grounded counter-argument on this point" rather than shipping an unverified claim.

**Definition of done:** unit tests in `test_citation_verifier.py` with deliberately fabricated citations (a section number that doesn't exist, a real section number with a misattributed claim) — both must be caught.

## 9. Phase 4 — LangGraph multi-turn orchestrator

Only start this once Phases 1-3 are independently verified.

```python
class DebateState(TypedDict):
    debate_id: str
    topic: str
    student_position: Literal["for", "against"]
    turn_history: list[Turn]
    retrieved_context: list[Chunk]
    needs_regen: bool
    retry_count: int
```

Graph: `retrieve -> counsel_agent -> verify_citations -> (conditional: back to counsel_agent on failure, up to 2 retries, else -> persist_turn)`. Persist every turn to the `turns` table. New endpoint: `POST /api/debate/{debate_id}/turn` continues an existing session.

## 10. Phase 5 — Judge/scoring agent

`POST /api/debate/{debate_id}/score` — separate LLM call scoring the full exchange against a rubric: issue identification, correct application of cited law, logical structure, rebuttal responsiveness. Return structured per-criterion scores plus short written feedback, not just a number. Optional for the v1 demo if time-constrained — the opposing-counsel loop alone already delivers the core value.

## 11. Phase 6 — Frontend

- `/debate/new` — topic input, position selector (for/against).
- `/debate/[id]` — turn-by-turn chat interface. Each AI turn shows citations as expandable references (section number + snippet), not just inline text — the citation should be visibly checkable by the student.
- Dark mode as the default theme.
- Score panel (if Phase 5 is built) shown after a debate session ends, not intrusively during it.

## 12. Environment variables

```
LLM_PROVIDER=anthropic|openai
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
DATABASE_URL=
EMBEDDING_MODEL=
EMBEDDING_DIMENSION=
```

## 13. Explicitly out of scope for v1

- User accounts/auth
- Multi-statute corpus (single act only)
- WhatsApp or any channel beyond the web app
- Any fine-tuning
- Production-scale rate limiting or caching (Redis can be added later if needed, not now)

## 14. Testing requirements

- `test_chunker.py`: verify section boundaries are never split mid-section.
- `test_hybrid_search.py`: the 15-20 query eval set from Phase 1, with a script to compute and print hit rate — not just pass/fail assertions, actual visibility into ranking quality.
- `test_citation_verifier.py`: fabricated-citation and misattributed-citation cases must both be rejected.

## 15. General implementation standards

- Pydantic v2 models for every API request/response, no untyped dicts crossing the API boundary.
- TypeScript strict mode on the frontend, no `any`.
- Every LLM call goes through `llm/provider.py` — no direct API calls scattered through agent code.
- If a design decision isn't specified in this document, stop and ask rather than guessing.
