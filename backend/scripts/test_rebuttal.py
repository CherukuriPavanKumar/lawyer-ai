import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.api.routes.debate import rebut, RebuttalRequest

async def main():
    req = RebuttalRequest(
        topic="Void Agreements",
        student_position="for",
        student_argument="An agreement is completely valid even if part of the consideration is unlawful, because the lawful part saves the contract."
    )
    print(f"Topic: {req.topic}")
    print(f"Student Position: {req.student_position}")
    print(f"Student Argument: {req.student_argument}")
    print("\\nGenerating rebuttal via Counsel Agent...")
    
    response = await rebut(req)
    print("\\n--- Counsel Agent Counter Argument ---")
    print(response.counter_argument)
    print("\\n--- Extracted Citations ---")
    for c in response.citations:
        print(f"Section {c.section_number}: {c.snippet}")

if __name__ == "__main__":
    asyncio.run(main())
