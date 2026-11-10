"""
Automated Verification Tests for ExamAnt Backend (`backend/tests/test_api_and_validator.py`).
Tests input validation, ConflictGraph, Central Validator, and all FastAPI endpoints.
"""

import sys
from pathlib import Path

# Ensure backend root is always in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"


def test_list_and_get_instances():
    resp = client.get("/instances")
    assert resp.status_code == 200
    instances = resp.json()
    assert len(instances) >= 1
    assert instances[0]["instance_id"] == "demo_01"

    detail_resp = client.get("/instances/demo_01")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["courses"]) == 10
    assert len(detail["slots"]) == 6

    graph_resp = client.get("/instances/demo_01/graph")
    assert graph_resp.status_code == 200
    graph_data = graph_resp.json()
    assert len(graph_data["nodes"]) == 10
    assert len(graph_data["edges"]) > 0


def test_solve_all_three_algorithms():
    for algo in ("greedy", "random_feasible", "aco"):
        resp = client.post(
            "/solve",
            json={
                "instance_id": "demo_01",
                "algorithm": algo,
                "parameters": {"seed": 42, "num_ants": 10, "iterations": 5, "max_attempts": 50},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["instance_id"] == "demo_01"
        assert data["algorithm"] == algo
        assert data["status"] == "success"
        assert data["metrics"]["hard_conflict_count"] == 0
        assert len(data["schedule"]) == 10
        assert data["validation_details"]["is_valid"] is True


def test_compare_endpoint():
    resp = client.post(
        "/compare",
        json={
            "instance_id": "demo_01",
            "algorithms": ["greedy", "random_feasible", "aco"],
            "runs": 3,
            "seed_start": 100,
            "parameters": {
                "random_feasible": {"max_attempts": 50},
                "aco": {"num_ants": 10, "iterations": 5, "alpha": 1.0, "beta": 2.0, "rho": 0.2},
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "greedy" in data["summaries"]
    assert "random_feasible" in data["summaries"]
    assert "aco" in data["summaries"]
    assert data["summaries"]["aco"]["success_rate"] > 0
