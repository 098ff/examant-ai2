"""
Dataset Instances API Router (`backend/app/routers/instances.py`).
Provides endpoints to list datasets, inspect an instance, and fetch its conflict graph.
Strictly relies on MongoDB and provides clear guidance when MongoDB is offline.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from app.core.graph import ConflictGraph
from app.database import get_collection, get_instance_by_id, list_all_instances
from app.schemas.models import ExamInstanceDocument, ExamInstanceSummary
from scripts.seed_db import seed_all_instances

router = APIRouter(prefix="/instances", tags=["Dataset Instances"])


@router.get("", response_model=List[ExamInstanceSummary])
def get_instances() -> List[ExamInstanceSummary]:
    """List all available dataset instances (`GET /instances`)."""
    if get_collection() is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "MongoDB is not reachable. Please start the MongoDB container via "
                "'docker compose up -d mongodb' and run 'python -m scripts.seed_db'."
            ),
        )
    return list_all_instances()


@router.get("/{instance_id}", response_model=ExamInstanceDocument)
def get_instance_detail(instance_id: str) -> ExamInstanceDocument:
    """Get full dataset details for a single `instance_id` (`GET /instances/{instance_id}`)."""
    if get_collection() is None:
        raise HTTPException(
            status_code=503,
            detail="MongoDB is not reachable. Please ensure MongoDB is running via 'docker compose up -d mongodb'.",
        )
    doc = get_instance_by_id(instance_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset instance '{instance_id}' not found in MongoDB.",
        )
    return doc


@router.get("/{instance_id}/graph", response_model=Dict[str, Any])
def get_instance_conflict_graph(instance_id: str) -> Dict[str, Any]:
    """
    Get precomputed Course Conflict Graph (nodes and shared-student edges)
    for Frontend visualization (`GET /instances/{instance_id}/graph`).
    """
    if get_collection() is None:
        raise HTTPException(
            status_code=503,
            detail="MongoDB is not reachable. Please ensure MongoDB is running via 'docker compose up -d mongodb'.",
        )
    doc = get_instance_by_id(instance_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset instance '{instance_id}' not found in MongoDB.",
        )
    graph = ConflictGraph(doc.to_problem_data())
    return graph.to_graph_dict()


@router.post("/seed", response_model=Dict[str, Any])
def trigger_seed_instances() -> Dict[str, Any]:
    """Trigger seeding/re-seeding of dataset instances into MongoDB (`POST /instances/seed`)."""
    if get_collection() is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Cannot seed dataset: MongoDB is not reachable. "
                "Please start the MongoDB container via 'docker compose up -d mongodb'."
            ),
        )
    seeded_count = seed_all_instances()
    return {
        "status": "ok",
        "message": f"Successfully seeded {seeded_count} dataset instance(s) into MongoDB.",
        "seeded_count": seeded_count,
    }
