import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.api.routes.debate import create_debate, debate_turn, CreateDebateRequest, TurnRequest
from app.db.session import init_db

async def main():
    await init_db()
    
    print("1. Creating Debate...")
    req1 = CreateDebateRequest(
        topic="Free Consent",
        student_position="for"
    )
    debate_response = await create_debate(req1)
    debate_id = debate_response.debate_id
    print(f"   Debate ID: {debate_id}")
    
    print("\\n2. Taking Turn 1: Student Argument")
    student_arg = "Consent is free even if obtained by fraud, as long as the person signs the paper."
    print(f"   Student: {student_arg}")
    
    req2 = TurnRequest(student_argument=student_arg)
    turn_response = await debate_turn(debate_id, req2)
    
    print("\\n3. Counsel Agent Response (via LangGraph):")
    print(turn_response.counter_argument)
    print("\\n   Citations:")
    for c in turn_response.citations:
        print(f"   - Section {c.section_number}: {c.snippet}")

if __name__ == "__main__":
    asyncio.run(main())
