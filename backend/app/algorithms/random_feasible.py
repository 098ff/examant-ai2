"""
[Task for Person 1: Mai (Sippapas Chavanont)]
Random Feasible Baseline Algorithm (`backend/app/algorithms/random_feasible.py`).

Rules from `docs/01-project-idea-spec.md` (Section 7.2):
1. Use `rng = random.Random(params.seed)` for reproducibility.
2. Loop to generate schedules up to `params.max_attempts` budget:
   - In each attempt, construct the schedule course-by-course by randomly choosing from:
     `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
   - If any course encounters an empty `feasible_slots` (dead-end), mark the attempt failed and continue.
3. For every fully assigned schedule, compute penalty (or use `validate_and_score_schedule`),
   and track the schedule with the lowest `penalty_score` (`best_schedule`) along with `best_iteration` and `history`.
"""

import random
import time
from typing import Dict, List, Optional
from app.algorithms.base import build_solve_response
from app.core.graph import ConflictGraph
from app.schemas.models import (
    AlgorithmParameters,
    IterationHistoryPoint,
    ProblemData,
    SolveResponse,
)


def solve_random_feasible(problem: ProblemData, params: AlgorithmParameters) -> SolveResponse:
    """Run Random Feasible baseline within `params.max_attempts` budget."""
    start_time = time.perf_counter()
    rng = random.Random(params.seed)
    graph = ConflictGraph(problem)

    # ==========================================================================
    # TODO [Person 1 - Mai]:
    # Implement random schedule generation loop for `params.max_attempts` rounds
    # and keep the schedule with minimum penalty score.
    # (Below is starter stub code that generates 1 round for early frontend testing)
    # ==========================================================================
    best_schedule: Optional[Dict[str, str]] = {}
    ordered_courses = graph.get_ordered_courses()

    for course_id in ordered_courses:
        feasible_slots = graph.get_feasible_slots(course_id, best_schedule)
        if not feasible_slots:
            best_schedule = None
            break
        best_schedule[course_id] = rng.choice(feasible_slots)

    history: List[IterationHistoryPoint] = [
        IterationHistoryPoint(iteration=1, best_penalty=4, iteration_best_penalty=4, feasible_ants=1)
    ]

    runtime_ms = (time.perf_counter() - start_time) * 1000.0
    return build_solve_response(
        problem=problem,
        algorithm="random_feasible",
        schedule_dict=best_schedule,
        runtime_ms=runtime_ms,
        attempts=params.max_attempts,
        parameters_used={
            "seed": params.seed,
            "max_attempts": params.max_attempts,
        },
        best_iteration=1 if best_schedule else None,
        history=history,
        message="[STUB] Random Feasible starter stub executed. (TODO: Person 1 implement full max_attempts loop)",
    )
