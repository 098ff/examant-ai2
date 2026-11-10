"""
[Task for Person 2: Fai (Chanatda Konchom)]
Greedy Baseline Algorithm (`backend/app/algorithms/greedy.py`).

Rules from `docs/01-project-idea-spec.md` (Section 7.1):
1. Build conflict graph from enrollments (`graph = ConflictGraph(problem)`)
2. Order courses by degree descending (courses with the most conflicts first); break ties by `course_id`
   -> Use `ordered_courses = graph.get_ordered_courses()`
3. For each course, find time slots with no conflict and without exceeding 2 exams/day per student
   -> Use `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
4. Among feasible slots, choose the slot that minimizes incremental penalty (`graph.calculate_delta_penalty(...)`)
5. Break ties by choosing the earlier chronological slot
6. If no feasible slot exists, return `no_solution_found` (pass `schedule_dict=None`)
"""

import time
from typing import Dict, Optional
from app.algorithms.base import build_solve_response
from app.core.graph import ConflictGraph
from app.schemas.models import AlgorithmParameters, ProblemData, SolveResponse


def solve_greedy(problem: ProblemData, params: AlgorithmParameters) -> SolveResponse:
    """
    Run deterministic Greedy examination timetabling baseline (Spec Section 7.1).

    Courses are ordered by conflict degree descending (tie-broken by course_id).
    Each course is sequentially assigned to the feasible exam slot that minimizes
    the incremental consecutive-exam penalty (Delta P), tie-breaking by earlier
    chronological slot order.
    """
    start_time = time.perf_counter()
    graph = ConflictGraph(problem)

    partial_schedule: Optional[Dict[str, str]] = {}
    ordered_courses = graph.get_ordered_courses()

    for course_id in ordered_courses:
        feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)
        if not feasible_slots:
            partial_schedule = None
            break

        # Select the feasible slot that minimizes incremental soft penalty (Delta P).
        # Because feasible_slots is already ordered chronologically and min() is stable,
        # ties are automatically broken by earlier chronological slot order.
        best_slot = min(
            feasible_slots,
            key=lambda slot_id: graph.calculate_delta_penalty(
                course_id, slot_id, partial_schedule
            ),
        )
        partial_schedule[course_id] = best_slot

    runtime_ms = (time.perf_counter() - start_time) * 1000.0
    return build_solve_response(
        problem=problem,
        algorithm="greedy",
        schedule_dict=partial_schedule,
        runtime_ms=runtime_ms,
        attempts=1,
        parameters_used={"seed": params.seed},
        best_iteration=1 if partial_schedule else None,
        history=[],
        message=None,
    )
