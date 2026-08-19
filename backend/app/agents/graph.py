from typing import TypedDict, List, Literal, Optional
from langgraph.graph import StateGraph, END
from app.ingestion.chunker import Chunk
from app.retrieval.hybrid_search import hybrid_search
from app.agents.counsel_agent import generate_rebuttal
from app.agents.citation_verifier import verify_citations
from app.llm.provider import generate_completion

class Turn(TypedDict):
    role: Literal["student", "counsel_agent", "judge"]
    content: str
    citations: List[dict]

class DebateState(TypedDict):
    debate_id: str
    topic: str
    student_position: Literal["for", "against"]
    turn_history: List[Turn]
    current_student_argument: str
    search_query: Optional[str]  # reformulated query for retrieval
    retrieved_context: List[Chunk]
    generated_counter_argument: str
    citations: List[dict]
    needs_regen: bool
    retry_count: int
    failure_reason: Optional[str]

async def reformulate_query_node(state: DebateState):
    """Condense the student's full argument into 3-5 focused legal keywords for retrieval."""
    student_arg = state["current_student_argument"]
    topic = state["topic"]
    
    messages = [
        {"role": "system", "content": (
            "You are a legal research assistant. Given a student's debate argument and topic, "
            "extract the 3-5 most specific legal keywords or concepts that should be searched "
            "in the Indian Contract Act. Output ONLY the keywords as a comma-separated list. "
            "No explanation, no punctuation except commas."
        )},
        {"role": "user", "content": f"Topic: {topic}\n\nArgument: {student_arg}"}
    ]
    keywords = await generate_completion(messages, model="openai/gpt-oss-20b")
    # Clean up and use as search query
    search_query = keywords.strip().replace("\n", " ")
    print(f"[RETRIEVAL] Reformulated query: '{search_query}'")
    return {"search_query": search_query}

async def retrieve_node(state: DebateState):
    query = state.get("search_query") or state["current_student_argument"]
    chunks = await hybrid_search(query, k=10)
    return {"retrieved_context": chunks}

async def counsel_node(state: DebateState):
    student_arg = state["current_student_argument"]
    if state.get("needs_regen") and state.get("failure_reason"):
        student_arg += f"\\n\\n[SYSTEM NOTE: Your previous response was rejected by the citation verifier. Reason: {state['failure_reason']}. Please regenerate and ensure strict grounding.]"
        
    counter_arg = await generate_rebuttal(
        topic=state["topic"],
        student_position=state["student_position"],
        student_argument=student_arg,
        retrieved_chunks=state.get("retrieved_context", [])
    )
    
    citations = []
    for chunk in state.get("retrieved_context", []):
        if f"Section {chunk.section_number}" in counter_arg or f"section {chunk.section_number}" in counter_arg:
            citations.append({
                "section_number": chunk.section_number,
                "snippet": chunk.text[:100] + "..."
            })
            
    return {
        "generated_counter_argument": counter_arg,
        "citations": citations,
        "retry_count": state.get("retry_count", 0) + 1
    }

async def verify_node(state: DebateState):
    verification = await verify_citations(state["generated_counter_argument"], state.get("retrieved_context", []))
    if verification.passed:
        return {"needs_regen": False, "failure_reason": None}
    else:
        return {"needs_regen": True, "failure_reason": verification.reason}

def verify_router(state: DebateState):
    if state.get("needs_regen") and state.get("retry_count", 0) <= 2:
        return "counsel_node"
    return END

def build_debate_graph():
    workflow = StateGraph(DebateState)
    
    workflow.add_node("reformulate_query_node", reformulate_query_node)
    workflow.add_node("retrieve_node", retrieve_node)
    workflow.add_node("counsel_node", counsel_node)
    workflow.add_node("verify_node", verify_node)
    
    workflow.set_entry_point("reformulate_query_node")
    workflow.add_edge("reformulate_query_node", "retrieve_node")
    workflow.add_edge("retrieve_node", "counsel_node")
    workflow.add_edge("counsel_node", "verify_node")
    
    workflow.add_conditional_edges(
        "verify_node",
        verify_router,
        {"counsel_node": "counsel_node", END: END}
    )
    
    return workflow.compile()

debate_graph = build_debate_graph()
