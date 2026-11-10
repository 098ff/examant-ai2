"""
Unit tests for Person 2 (Fai): Greedy Algorithm & Planted Dataset Generator.
Verifies input validation, planted coloring guarantee (0 hard conflicts),
and Greedy baseline behavior across all benchmark datasets.
"""

import sys
from pathlib import Path

# Ensure backend root is always in sys.path regardless of how pytest is invoked
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import pytest
except ImportError:
    pytest = None

from app.algorithms.greedy import solve_greedy
from app.core.validator import validate_problem_input
from app.schemas.models import AlgorithmParameters
from scripts.seed_db import generate_synthetic_instance, get_all_seed_instances


def test_seed_instances_generation_and_validation():
    """Verify that all 4 instances (demo_01, easy_01, medium_01, hard_01) are valid."""
    instances = get_all_seed_instances()
    assert len(instances) == 4

    expected_ids = ["demo_01", "easy_01", "medium_01", "hard_01"]
    actual_ids = [inst.instance_id for inst in instances]
    assert actual_ids == expected_ids

    for inst in instances:
        problem = inst.to_problem_data()
        err = validate_problem_input(problem)
        assert err is None, f"Dataset '{inst.instance_id}' failed input validation: {err}"
        assert len(problem.courses) > 0
        assert len(problem.students) > 0
        assert len(problem.enrollments) > 0
        assert len(problem.slots) % 2 == 0


def _check_synthetic_structure(difficulty: str, expected_courses: int, expected_students: int, expected_slots: int):
    inst = generate_synthetic_instance(difficulty)
    assert len(inst.courses) == expected_courses
    assert len(inst.students) == expected_students
    assert len(inst.slots) == expected_slots


def _check_solve_greedy(instance_id: str):
    instances_map = {inst.instance_id: inst for inst in get_all_seed_instances()}
    inst = instances_map[instance_id]
    problem = inst.to_problem_data()

    res = solve_greedy(problem, AlgorithmParameters(seed=inst.seed))

    assert res.status == "success"
    assert res.message is None
    assert res.metrics.hard_conflict_count == 0
    assert res.validation_details is not None
    assert res.validation_details.is_valid is True
    assert len(res.schedule) == len(problem.courses)
    assert res.metrics.runtime_ms > 0


if pytest:
    @pytest.mark.parametrize("difficulty,expected_courses,expected_students,expected_slots", [
        ("easy", 10, 45, 6),
        ("medium", 12, 70, 6),
        ("hard", 15, 90, 8),
    ])
    def test_synthetic_instances_structure(difficulty, expected_courses, expected_students, expected_slots):
        _check_synthetic_structure(difficulty, expected_courses, expected_students, expected_slots)

    @pytest.mark.parametrize("instance_id", ["demo_01", "easy_01", "medium_01", "hard_01"])
    def test_solve_greedy_all_instances(instance_id):
        _check_solve_greedy(instance_id)
else:
    def test_synthetic_instances_structure():
        for d, c, s, sl in [("easy", 10, 45, 6), ("medium", 12, 70, 6), ("hard", 15, 90, 8)]:
            _check_synthetic_structure(d, c, s, sl)

    def test_solve_greedy_all_instances():
        for inst_id in ["demo_01", "easy_01", "medium_01", "hard_01"]:
            _check_solve_greedy(inst_id)


if __name__ == "__main__":
    test_seed_instances_generation_and_validation()
    test_synthetic_instances_structure()
    test_solve_greedy_all_instances()
    print("All tests in test_greedy_and_datasets.py passed successfully!")
