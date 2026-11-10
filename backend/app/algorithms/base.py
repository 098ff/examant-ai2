"""
Base Solver Contract & Response Builder (`backend/app/algorithms/base.py`).
Ensures all 3 algorithms (Greedy, Random Feasible, ACO) return a standardized `SolveResponse`
evaluated by the independent Central Validator (`app.core.validator`).
"""

from typing import Any, Dict, List, Optional
from app.core.validator import validate_and_score_schedule
from app.schemas.models import (
    AlgorithmType,
    IterationHistoryPoint,
    ProblemData,
    ScheduleItem,
    SolveMetrics,
    SolveResponse,
    SolveStatusType,
)


def build_solve_response(
    problem: ProblemData,
    algorithm: AlgorithmType,
    schedule_dict: Optional[Dict[str, str]],
    runtime_ms: float,
    attempts: int,
    parameters_used: Dict[str, Any],
    best_iteration: Optional[int] = None,
    history: Optional[List[IterationHistoryPoint]] = None,
    message: Optional[str] = None,
) -> SolveResponse:
    """
    Convert a dictionary `{course_id: slot_id}` (or None if no solution found)
    into a validated `SolveResponse` using the Central Validator.
    """
    if not schedule_dict or len(schedule_dict) < len(problem.courses):
        return SolveResponse(
            instance_id=problem.instance_id,
            algorithm=algorithm,
            status="no_solution_found",
            schedule=[],
            metrics=SolveMetrics(
                hard_conflict_count=0,
                consecutive_exam_pair_count=0,
                penalty_score=0,
                runtime_ms=round(runtime_ms, 3),
                attempts=attempts,
                best_iteration=best_iteration,
            ),
            parameters_used=parameters_used,
            history=history or [],
            validation_details=None,
            message=message or "No feasible schedule found within the given search budget.",
        )

    schedule_items = [
        ScheduleItem(course_id=cid, slot_id=schedule_dict[cid])
        for cid in sorted(schedule_dict.keys())
    ]

    hard_conflicts, consecutive_pairs, penalty, details = validate_and_score_schedule(
        problem=problem,
        schedule=schedule_items,
    )

    status: SolveStatusType = "success" if details.is_valid else "no_solution_found"
    if not details.is_valid and not message:
        message = "Candidate schedule failed central validation (hard constraint violated)."

    return SolveResponse(
        instance_id=problem.instance_id,
        algorithm=algorithm,
        status=status,
        schedule=schedule_items if details.is_valid else [],
        metrics=SolveMetrics(
            hard_conflict_count=hard_conflicts,
            consecutive_exam_pair_count=consecutive_pairs,
            penalty_score=penalty,
            runtime_ms=round(runtime_ms, 3),
            attempts=attempts,
            best_iteration=best_iteration,
        ),
        parameters_used=parameters_used,
        history=history or [],
        validation_details=details,
        message=message,
    )
