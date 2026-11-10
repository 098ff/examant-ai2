"""
ExamAnt FastAPI Main Application (`backend/app/main.py`).
"""

from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import ensure_initial_seed
from app.routers import instances, solver


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure starter dataset is seeded into MongoDB on startup."""
    ensure_initial_seed()
    yield


app = FastAPI(
    title="ExamAnt API — Examination Timetabling with ACO",
    description=(
        "Backend API for ExamAnt (AI2 Project): Compares Greedy, Random Feasible, "
        "and Ant Colony Optimization (ACO) on the Examination Timetabling Problem."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instances.router)
app.include_router(solver.router)


@app.get("/", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "service": "ExamAnt Backend API",
        "status": "running",
        "docs": "/docs",
    }
