"""Random feasible timetable search with independent candidate validation."""

import random
import time
from typing import Dict, List, Optional

from app.algorithms.base import build_solve_response
from app.core.graph import ConflictGraph
from app.core.validator import validate_and_score_schedule
from app.schemas.models import AlgorithmParameters, IterationHistoryPoint, ProblemData, ScheduleItem, SolveResponse


def solve_random_feasible(problem: ProblemData, params: AlgorithmParameters) -> SolveResponse:
    """Try the full search budget and return the best valid timetable found."""
    start_time = time.perf_counter()
    rng = random.Random(params.seed)
    graph = ConflictGraph(problem)
    ordered_courses = graph.get_ordered_courses()
    best_schedule: Optional[Dict[str, str]] = None
    best_penalty: Optional[int] = None
    best_iteration: Optional[int] = None
    history: List[IterationHistoryPoint] = []

    for attempt in range(1, params.max_attempts + 1):
        partial_schedule: Dict[str, str] = {}
        penalty = None
        for course_id in ordered_courses:
            feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)
            if not feasible_slots:
                break
            partial_schedule[course_id] = rng.choice(feasible_slots)
        else:
            _, _, candidate_penalty, details = validate_and_score_schedule(
                problem, [ScheduleItem(course_id=c, slot_id=s) for c, s in partial_schedule.items()]
            )
            if details.is_valid:
                penalty = candidate_penalty
                if best_penalty is None or penalty < best_penalty:
                    best_schedule = partial_schedule.copy()
                    best_penalty = penalty
                    best_iteration = attempt

        history.append(IterationHistoryPoint(
            iteration=attempt, best_penalty=best_penalty,
            iteration_best_penalty=penalty, feasible_ants=int(penalty is not None),
        ))

    return build_solve_response(
        problem=problem, algorithm="random_feasible", schedule_dict=best_schedule,
        runtime_ms=(time.perf_counter() - start_time) * 1000.0,
        attempts=params.max_attempts,
        parameters_used={"seed": params.seed, "max_attempts": params.max_attempts},
        best_iteration=best_iteration, history=history, message=None,
    )
