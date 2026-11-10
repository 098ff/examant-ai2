"""
Dataset Instances API Router (`backend/app/routers/instances.py`).
Provides endpoints to list datasets, inspect an instance, and fetch its conflict graph.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from app.core.graph import ConflictGraph
from app.database import get_instance_by_id, list_all_instances
from app.schemas.models import ExamInstanceDocument, ExamInstanceSummary
from scripts.seed_db import seed_all_instances

router = APIRouter(prefix="/instances", tags=["Dataset Instances"])


@router.get("", response_model=List[ExamInstanceSummary])
def get_instances() -> List[ExamInstanceSummary]:
    """List all available dataset instances (`GET /instances`)."""
    return list_all_instances()


@router.get("/{instance_id}", response_model=ExamInstanceDocument)
def get_instance_detail(instance_id: str) -> ExamInstanceDocument:
    """Get full dataset details for a single `instance_id` (`GET /instances/{instance_id}`)."""
    doc = get_instance_by_id(instance_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset instance '{instance_id}' not found.",
        )
    return doc


@router.get("/{instance_id}/graph", response_model=Dict[str, Any])
def get_instance_conflict_graph(instance_id: str) -> Dict[str, Any]:
    """
    Get precomputed Course Conflict Graph (nodes and shared-student edges)
    for Frontend visualization (`GET /instances/{instance_id}/graph`).
    """
    doc = get_instance_by_id(instance_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset instance '{instance_id}' not found.",
        )
    graph = ConflictGraph(doc.to_problem_data())
    return graph.to_graph_dict()


@router.post("/seed", response_model=Dict[str, str])
def trigger_seed_instances() -> Dict[str, str]:
    """Trigger seeding/re-seeding of dataset instances into MongoDB (`POST /instances/seed`)."""
    seed_all_instances()
    return {"status": "ok", "message": "Dataset instances seeded into MongoDB."}
