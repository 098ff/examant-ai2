"""Ant System search for examination timetables."""

import math
import random
import time
from typing import Dict, List, Optional

from app.algorithms.base import build_solve_response
from app.core.graph import ConflictGraph
from app.core.validator import validate_and_score_schedule
from app.schemas.models import AlgorithmParameters, IterationHistoryPoint, ProblemData, ScheduleItem, SolveResponse


def solve_aco(problem: ProblemData, params: AlgorithmParameters) -> SolveResponse:
    """Construct ants, evaporate pheromone, and reinforce every valid ant per round."""
    start_time = time.perf_counter()
    rng = random.Random(params.seed)
    graph = ConflictGraph(problem)
    ordered_courses = graph.get_ordered_courses()
    # Log pheromone preserves the Ant System equations without underflow during
    # long runs with strong evaporation. log_tau[c][s] represents log(tau[c][s]).
    log_tau = {
        c: {s: math.log(params.initial_pheromone) for s in graph.slot_ids}
        for c in ordered_courses
    }
    best_schedule: Optional[Dict[str, str]] = None
    best_penalty: Optional[int] = None
    best_iteration: Optional[int] = None
    history: List[IterationHistoryPoint] = []

    for iteration in range(1, params.iterations + 1):
        valid_ants = []
        for _ in range(params.num_ants):
            partial_schedule: Dict[str, str] = {}
            for course_id in ordered_courses:
                feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)
                if not feasible_slots:
                    break
                log_weights = [
                    params.alpha * log_tau[course_id][slot_id]
                    - params.beta * math.log1p(graph.calculate_delta_penalty(
                        course_id, slot_id, partial_schedule
                    ))
                    for slot_id in feasible_slots
                ]
                # Common scaling leaves probabilities unchanged and ensures at
                # least one positive weight even at extreme allowed parameters.
                largest = max(log_weights)
                weights = [math.exp(w - largest) for w in log_weights]
                partial_schedule[course_id] = rng.choices(feasible_slots, weights=weights, k=1)[0]
            else:
                _, _, penalty, details = validate_and_score_schedule(
                    problem, [ScheduleItem(course_id=c, slot_id=s) for c, s in partial_schedule.items()]
                )
                if details.is_valid:
                    valid_ants.append((partial_schedule, penalty))
                    if best_penalty is None or penalty < best_penalty:
                        best_schedule = partial_schedule.copy()
                        best_penalty = penalty
                        best_iteration = iteration

        evaporation = math.log1p(-params.rho)
        for course_id in ordered_courses:
            for slot_id in graph.slot_ids:
                log_tau[course_id][slot_id] += evaporation
        for schedule, penalty in valid_ants:
            log_deposit = math.log(params.q) - math.log1p(penalty)
            for course_id, slot_id in schedule.items():
                old = log_tau[course_id][slot_id]
                larger = max(old, log_deposit)
                log_tau[course_id][slot_id] = larger + math.log1p(math.exp(-abs(old - log_deposit)))

        history.append(IterationHistoryPoint(
            iteration=iteration, best_penalty=best_penalty,
            iteration_best_penalty=min((p for _, p in valid_ants), default=None),
            feasible_ants=len(valid_ants),
        ))

    return build_solve_response(
        problem=problem, algorithm="aco", schedule_dict=best_schedule,
        runtime_ms=(time.perf_counter() - start_time) * 1000.0,
        attempts=params.num_ants * params.iterations,
        parameters_used={key: getattr(params, key) for key in (
            "seed", "num_ants", "iterations", "alpha", "beta", "rho", "q", "initial_pheromone"
        )},
        best_iteration=best_iteration, history=history, message=None,
    )
