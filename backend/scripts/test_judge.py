import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.api.routes.debate import create_debate, debate_turn, score_debate, CreateDebateRequest, TurnRequest
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
    
    print("2. Taking Turn 1: Student Argument")
    student_arg = "Consent is free even if obtained by fraud, as long as the person signs the paper."
    req2 = TurnRequest(student_argument=student_arg)
    await debate_turn(debate_id, req2)
    
    print("3. Scoring Debate via Judge Agent...")
    score_res = await score_debate(debate_id)
    print("\\n--- Judge Feedback ---")
    print(json.dumps(score_res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
