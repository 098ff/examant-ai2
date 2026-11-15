"""Solver and API checks that do not require a running MongoDB server."""

import math
import random
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.algorithms.aco import solve_aco
from app.algorithms.random_feasible import solve_random_feasible
from app.core.validator import validate_and_score_schedule
from app.main import app
from app.schemas.models import AlgorithmParameters, ProblemData
from scripts.seed_db import build_starter_instance, get_all_seed_instances

SOLVERS = [solve_random_feasible, solve_aco]


def tiny_problem(course_count=2, days=1):
    return ProblemData(
        instance_id="tiny", courses=[f"C{i}" for i in range(course_count)], students=["S"],
        enrollments=[{"student_id": "S", "course_id": f"C{i}"} for i in range(course_count)],
        slots=[{"slot_id": f"D{d}S{s}", "day_index": d, "slot_index": s, "label": f"{d}/{s}"}
               for d in range(1, days + 1) for s in (1, 2)],
    )


@pytest.mark.parametrize("solver", SOLVERS)
@pytest.mark.parametrize("instance", get_all_seed_instances(), ids=lambda i: i.instance_id)
def test_datasets_and_reproducibility(solver, instance):
    problem = instance.to_problem_data()
    params = AlgorithmParameters(seed=42, max_attempts=60, num_ants=10, iterations=6)
    before = problem.model_dump()
    random_state = random.getstate()
    result = solver(problem, params)
    repeated = solver(problem, params)
    assert result.status == "success"
    assert result.message is None
    assert result.validation_details.is_valid
    assert len(result.schedule) == len(problem.courses)
    hard, _, penalty, details = validate_and_score_schedule(problem, result.schedule)
    assert hard == 0 and details.is_valid
    assert penalty == result.metrics.penalty_score
    assert result.metrics.attempts == 60
    assert result.history[-1].best_penalty == penalty
    known = [p.best_penalty for p in result.history if p.best_penalty is not None]
    assert known == sorted(known, reverse=True)
    assert result.metrics.best_iteration == next(p.iteration for p in result.history if p.best_penalty == penalty)
    assert len(result.history) == (60 if solver == solve_random_feasible else 6)
    for point in result.history:
        assert 0 <= point.feasible_ants <= (1 if solver == solve_random_feasible else 10)
        assert (point.iteration_best_penalty is None) == (point.feasible_ants == 0)
    a, b = result.model_dump(), repeated.model_dump()
    a["metrics"].pop("runtime_ms")
    b["metrics"].pop("runtime_ms")
    assert a == b
    assert problem.model_dump() == before
    assert random.getstate() == random_state


@pytest.mark.parametrize("solver", SOLVERS)
def test_impossible_search_exhausts_budget(solver):
    result = solver(tiny_problem(3), AlgorithmParameters(max_attempts=12, num_ants=3, iterations=4))
    assert result.status == "no_solution_found"
    assert result.schedule == []
    assert result.metrics.attempts == 12
    assert result.metrics.best_iteration is None
    assert all(p.best_penalty is None and p.iteration_best_penalty is None and p.feasible_ants == 0
               for p in result.history)


@pytest.mark.parametrize("solver", SOLVERS)
@pytest.mark.parametrize("courses,expected", [(1, 0), (2, 1)])
def test_known_penalty_and_full_budget(solver, courses, expected):
    result = solver(tiny_problem(courses), AlgorithmParameters(max_attempts=6, num_ants=2, iterations=3))
    assert result.status == "success"
    assert result.metrics.penalty_score == expected
    assert result.metrics.best_iteration == 1
    assert result.metrics.attempts == 6
    assert all(p.best_penalty == expected and p.iteration_best_penalty == expected for p in result.history)


def test_random_restarts_and_keeps_best():
    # For two conflicting courses across two days, force penalties 1, 0, 1.
    picks = ["D1S1", "D1S2", "D1S1", "D2S1", "D1S1", "D1S2"]
    with patch("app.algorithms.random_feasible.random.Random") as factory:
        factory.return_value.choice.side_effect = picks
        result = solve_random_feasible(tiny_problem(2, 2), AlgorithmParameters(max_attempts=3))
    assert [p.iteration_best_penalty for p in result.history] == [1, 0, 1]
    assert [p.best_penalty for p in result.history] == [1, 0, 0]
    assert result.metrics.best_iteration == 2
    assert result.metrics.penalty_score == 0


def test_aco_transition_evaporation_and_all_ant_deposits():
    # One course has zero heuristic penalty. Both ants choose slot 1.
    # After round 1: tau(slot1)=0.8+2*1=2.8, tau(slot2)=0.8.
    seen = []
    def choose(population, weights, k):
        seen.append(list(weights))
        return [population[0]]
    with patch("app.algorithms.aco.random.Random") as factory:
        factory.return_value.choices.side_effect = choose
        result = solve_aco(tiny_problem(1), AlgorithmParameters(num_ants=2, iterations=2, rho=0.2))
    assert seen[0] == pytest.approx([1, 1])
    assert seen[1] == pytest.approx([1, 1])
    assert seen[2] == pytest.approx([1, 0.8 / 2.8])
    assert seen[3] == pytest.approx(seen[2])
    assert result.metrics.penalty_score == 0


def test_aco_heuristic_weights():
    seen = []
    def choose(population, weights, k):
        seen.append(list(zip(population, weights)))
        return [population[0]]
    with patch("app.algorithms.aco.random.Random") as factory:
        factory.return_value.choices.side_effect = choose
        solve_aco(tiny_problem(2, 2), AlgorithmParameters(num_ants=1, iterations=1, beta=2))
    assert dict(seen[1]) == pytest.approx({"D1S2": 0.25, "D2S1": 1, "D2S2": 1})


def test_aco_extreme_evaporation_without_success():
    result = solve_aco(tiny_problem(3), AlgorithmParameters(
        num_ants=1, iterations=500, rho=0.99, alpha=5, beta=5,
    ))
    assert result.status == "no_solution_found"
    assert len(result.history) == 500
    assert math.isfinite(result.metrics.runtime_ms)


@pytest.mark.parametrize("algorithm", ["random_feasible", "aco"])
def test_solve_api_without_database(algorithm):
    problem = build_starter_instance().to_problem_data()
    response = TestClient(app).post("/solve", json={
        "instance_id": problem.instance_id, "problem_data": problem.model_dump(),
        "algorithm": algorithm, "parameters": {"max_attempts": 50, "num_ants": 10, "iterations": 5},
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["validation_details"]["is_valid"]
    assert data["metrics"]["hard_conflict_count"] == 0
    assert data["metrics"]["attempts"] == 50
    assert data["message"] is None


def test_compare_api_with_in_memory_dataset(monkeypatch):
    # Substitute only the database lookup; exercise the real router and solvers.
    monkeypatch.setattr("app.routers.solver.get_instance_by_id", lambda _: build_starter_instance())
    response = TestClient(app).post("/compare", json={
        "instance_id": "demo_01", "runs": 2,
        "parameters": {"random_feasible": {"max_attempts": 50}, "aco": {"num_ants": 10, "iterations": 5}},
    })
    assert response.status_code == 200
    data = response.json()
    for algo in ("random_feasible", "aco"):
        assert data["summaries"][algo]["successful_runs"] == 2
        assert data["summaries"][algo]["mean_attempts"] == 50
        assert all(r["validation_details"]["is_valid"] for r in data["raw_runs"][algo])
