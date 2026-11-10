"""
HTTP Client Wrapper for communicating with the ExamAnt FastAPI Backend (`frontend/api_client.py`).
"""

import os
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")


def fetch_instances() -> List[Dict[str, Any]]:
    """Call `GET /instances` to retrieve available dataset summaries."""
    resp = requests.get(f"{BACKEND_API_URL}/instances", timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_instance_detail(instance_id: str) -> Dict[str, Any]:
    """Call `GET /instances/{instance_id}` for full dataset details."""
    resp = requests.get(f"{BACKEND_API_URL}/instances/{instance_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_conflict_graph(instance_id: str) -> Dict[str, Any]:
    """Call `GET /instances/{instance_id}/graph` for course conflict graph nodes & edges."""
    resp = requests.get(f"{BACKEND_API_URL}/instances/{instance_id}/graph", timeout=10)
    resp.raise_for_status()
    return resp.json()


def post_solve(
    instance_id: str,
    algorithm: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    """Call `POST /solve` to run a single algorithm."""
    payload = {
        "instance_id": instance_id,
        "algorithm": algorithm,
        "parameters": parameters,
    }
    resp = requests.post(f"{BACKEND_API_URL}/solve", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def post_compare(
    instance_id: str,
    algorithms: List[str],
    runs: int,
    seed_start: int,
    parameters: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Call `POST /compare` to benchmark multiple algorithms across multiple seeds."""
    payload = {
        "instance_id": instance_id,
        "algorithms": algorithms,
        "runs": runs,
        "seed_start": seed_start,
        "parameters": parameters,
    }
    resp = requests.post(f"{BACKEND_API_URL}/compare", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()
