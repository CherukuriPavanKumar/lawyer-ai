from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from app.db.session import async_session
from app.db.models import Debate, Turn as DBTurn
from app.agents.graph import debate_graph
from app.agents.judge_agent import evaluate_debate
from sqlalchemy import select
import uuid

router = APIRouter()

class CreateDebateRequest(BaseModel):
    topic: str
    act_name: str = "Indian Contract Act, 1872"
    student_position: Literal["for", "against"]

class DebateResponse(BaseModel):
    debate_id: str
    topic: str

class TurnRequest(BaseModel):
    student_argument: str

class Citation(BaseModel):
    section_number: str
    snippet: str

class TurnResponse(BaseModel):
    turn_id: str
    counter_argument: str
    citations: List[Citation]

@router.post("/", response_model=DebateResponse)
async def create_debate(request: CreateDebateRequest):
    async with async_session() as session:
        debate = Debate(
            topic=request.topic,
            act_name=request.act_name,
            student_position=request.student_position
        )
        session.add(debate)
        await session.commit()
        await session.refresh(debate)
        return DebateResponse(debate_id=str(debate.id), topic=debate.topic)

@router.post("/{debate_id}/turn", response_model=TurnResponse)
async def debate_turn(debate_id: str, request: TurnRequest):
    async with async_session() as session:
        stmt = select(Debate).where(Debate.id == uuid.UUID(debate_id))
        result = await session.execute(stmt)
        debate = result.scalar_one_or_none()
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        stmt = select(DBTurn).where(DBTurn.debate_id == debate.id).order_by(DBTurn.id)
        result = await session.execute(stmt)
        db_turns = result.scalars().all()
        
        turn_history = []
        for t in db_turns:
            turn_history.append({
                "role": t.role,
                "content": t.content,
                "citations": t.citations
            })
            
        student_turn = DBTurn(
            debate_id=debate.id,
            role="student",
            content=request.student_argument,
            citations=[]
        )
        session.add(student_turn)
        await session.commit()
        
        initial_state = {
            "debate_id": debate_id,
            "topic": debate.topic,
            "student_position": debate.student_position,
            "turn_history": turn_history,
            "current_student_argument": request.student_argument,
            "retry_count": 0,
            "needs_regen": False
        }
        
        final_state = await debate_graph.ainvoke(initial_state)
        
        counter_arg = final_state["generated_counter_argument"]
        if final_state.get("needs_regen"):
            counter_arg = "I don't have a strong grounded counter-argument on this point."
            
        counsel_turn = DBTurn(
            debate_id=debate.id,
            role="counsel_agent",
            content=counter_arg,
            citations=final_state.get("citations", [])
        )
        session.add(counsel_turn)
        await session.commit()
        await session.refresh(counsel_turn)
        
        return TurnResponse(
            turn_id=str(counsel_turn.id),
            counter_argument=counter_arg,
            citations=[Citation(**c) for c in final_state.get("citations", [])]
        )

class ScoreResponse(BaseModel):
    issue_identification: dict
    application_of_law: dict
    logical_structure: dict
    rebuttal_responsiveness: dict
    overall_feedback: str

@router.post("/{debate_id}/score")
async def score_debate(debate_id: str):
    async with async_session() as session:
        stmt = select(Debate).where(Debate.id == uuid.UUID(debate_id))
        result = await session.execute(stmt)
        debate = result.scalar_one_or_none()
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        stmt = select(DBTurn).where(DBTurn.debate_id == debate.id).order_by(DBTurn.id)
        result = await session.execute(stmt)
        db_turns = result.scalars().all()
        
        if not db_turns:
            raise HTTPException(status_code=400, detail="No turns to score")
            
        turn_history = [{"role": t.role, "content": t.content} for t in db_turns]
        
        score_json = await evaluate_debate(
            topic=debate.topic,
            student_position=debate.student_position,
            turns=turn_history
        )
        
        if "error" in score_json:
            raise HTTPException(status_code=500, detail=score_json["error"])
            
        return score_json
