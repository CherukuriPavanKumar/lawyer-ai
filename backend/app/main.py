from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import debate
import uvicorn

app = FastAPI(title="Advocatus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(debate.router, prefix="/api/debate", tags=["debate"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
