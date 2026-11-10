"""
[Task for Person 1: Mai (Sippapas Chavanont)]
Ant Colony Optimization (ACO) Algorithm (`backend/app/algorithms/aco.py`).

Theory reference from `AI2 Slide.pdf` (pages 18-30: Ant System & AS-QAP) and `docs/01-project-idea-spec.md` (Section 7.3):
1. Pheromone Structure `tau[course_id][slot_id]`:
   - Initialize all (course, slot) pairs to `params.initial_pheromone` (tau_0)
2. Course Ordering:
   - Order by conflict degree descending: `ordered_courses = graph.get_ordered_courses()`
3. In each iteration (1 to `params.iterations`):
   - Construct `params.num_ants` ants, each starting with `partial_schedule = {}`
   - Each ant schedules courses one-by-one according to `ordered_courses`:
     a) Find slots satisfying Hard Constraints (Tabu / Feasible set):
        `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
        If no slots are feasible -> ant reaches dead-end; skip this ant.
     b) Compute Heuristic Visibility `eta(c, t)` for each `t` in `feasible_slots`:
        `delta_p = graph.calculate_delta_penalty(course_id, t, partial_schedule)`
        `eta = 1.0 / (1.0 + delta_p)`
     c) Compute transition probability weights (Transition Rule - AI2 Slide pages 19, 29):
        `weight(c, t) = (tau[c][t] ** params.alpha) * (eta ** params.beta)`
        Then probabilistically sample `slot_id` proportional to `weight(c, t) / sum(weights)`
   - Evaluate penalty `P_k` for all ants that successfully completed a schedule in this iteration.
   - Update `global_best_schedule` and `global_best_penalty`
   - Pheromone Evaporation (AI2 Slide pages 21, 30):
     `tau[c][t] = (1.0 - params.rho) * tau[c][t]` for all `(c, t)`
   - Pheromone Deposit (AI2 Slide pages 21, 30):
     For successful ants: `deposit = params.q / (1.0 + P_k)`
     Add `deposit` into `tau[c][assigned_slot]`
   - Record `IterationHistoryPoint(iteration=it, best_penalty=global_best_penalty, ...)` into `history`
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


def solve_aco(problem: ProblemData, params: AlgorithmParameters) -> SolveResponse:
    """Run Ant Colony Optimization (ACO) for examination timetabling."""
    start_time = time.perf_counter()
    rng = random.Random(params.seed)
    graph = ConflictGraph(problem)

    # ==========================================================================
    # TODO [Person 1 - Mai]:
    # Replace the stub code below with the full ACO loop (Pheromone matrix,
    # transition rule, evaporation, deposit, and real IterationHistoryPoint tracking).
    # ==========================================================================
    best_schedule: Optional[Dict[str, str]] = {}
    ordered_courses = graph.get_ordered_courses()

    for course_id in ordered_courses:
        feasible_slots = graph.get_feasible_slots(course_id, best_schedule)
        if not feasible_slots:
            best_schedule = None
            break
        # STUB: Select slot with lowest delta_penalty with minor randomization for initial frontend verification
        scored_slots = sorted(
            feasible_slots,
            key=lambda sid: (graph.calculate_delta_penalty(course_id, sid, best_schedule), rng.random()),
        )
        best_schedule[course_id] = scored_slots[0]

    # Sample convergence history for Frontend chart testing
    history: List[IterationHistoryPoint] = [
        IterationHistoryPoint(
            iteration=it,
            best_penalty=max(1, 6 - (it // 4)),
            iteration_best_penalty=max(1, 7 - (it // 3)),
            feasible_ants=params.num_ants,
        )
        for it in range(1, min(params.iterations, 20) + 1)
    ]

    total_attempts = params.num_ants * params.iterations
    runtime_ms = (time.perf_counter() - start_time) * 1000.0

    return build_solve_response(
        problem=problem,
        algorithm="aco",
        schedule_dict=best_schedule,
        runtime_ms=runtime_ms,
        attempts=total_attempts,
        parameters_used={
            "seed": params.seed,
            "num_ants": params.num_ants,
            "iterations": params.iterations,
            "alpha": params.alpha,
            "beta": params.beta,
            "rho": params.rho,
            "q": params.q,
            "initial_pheromone": params.initial_pheromone,
        },
        best_iteration=1 if best_schedule else None,
        history=history,
        message="[STUB] ACO starter stub executed. (TODO: Person 1 implement full Ant System pheromone loop)",
    )
