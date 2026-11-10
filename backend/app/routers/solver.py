"""
Solver & Comparison API Router (`backend/app/routers/solver.py`).
Implements `POST /solve` and `POST /compare` according to `docs/01-project-idea-spec.md`.
"""

import statistics
from typing import Dict, List
from fastapi import APIRouter

from app.algorithms.aco import solve_aco
from app.algorithms.greedy import solve_greedy
from app.algorithms.random_feasible import solve_random_feasible
from app.core.validator import validate_problem_input
from app.database import get_instance_by_id
from app.schemas.models import (
    AlgorithmComparisonSummary,
    AlgorithmParameters,
    AlgorithmType,
    CompareRequest,
    CompareResponse,
    ProblemData,
    SolveMetrics,
    SolveRequest,
    SolveResponse,
)

router = APIRouter(tags=["Solver & Comparison"])


def _dispatch_algorithm(
    algorithm: AlgorithmType,
    problem: ProblemData,
    params: AlgorithmParameters,
) -> SolveResponse:
    """Dispatch a single solve request to the selected algorithm implementation."""
    if algorithm == "greedy":
        return solve_greedy(problem, params)
    if algorithm == "random_feasible":
        return solve_random_feasible(problem, params)
    if algorithm == "aco":
        return solve_aco(problem, params)
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def _build_invalid_input_response(
    instance_id: str,
    algorithm: AlgorithmType,
    params: AlgorithmParameters,
    error_msg: str,
) -> SolveResponse:
    """Return a clean `invalid_input` response without exposing stack traces (Spec Section 9)."""
    return SolveResponse(
        instance_id=instance_id,
        algorithm=algorithm,
        status="invalid_input",
        schedule=[],
        metrics=SolveMetrics(
            hard_conflict_count=0,
            consecutive_exam_pair_count=0,
            penalty_score=0,
            runtime_ms=0.0,
            attempts=0,
            best_iteration=None,
        ),
        parameters_used=params.model_dump(),
        history=[],
        validation_details=None,
        message=error_msg,
    )


@router.post("/solve", response_model=SolveResponse)
def run_single_solver(req: SolveRequest) -> SolveResponse:
    """
    Run a single algorithm (`greedy`, `random_feasible`, or `aco`) on an instance (`POST /solve`).
    """
    if req.problem_data is not None:
        problem = req.problem_data
    else:
        doc = get_instance_by_id(req.instance_id)
        if doc is None:
            return _build_invalid_input_response(
                instance_id=req.instance_id,
                algorithm=req.algorithm,
                params=req.parameters,
                error_msg=f"Instance '{req.instance_id}' not found in database.",
            )
        problem = doc.to_problem_data()

    input_err = validate_problem_input(problem)
    if input_err:
        return _build_invalid_input_response(
            instance_id=req.instance_id,
            algorithm=req.algorithm,
            params=req.parameters,
            error_msg=input_err,
        )

    return _dispatch_algorithm(req.algorithm, problem, req.parameters)


@router.post("/compare", response_model=CompareResponse)
def run_comparison(req: CompareRequest) -> CompareResponse:
    """
    Run multiple algorithms across `req.runs` seeds on the same instance (`POST /compare`)
    and return both raw run results and aggregated statistics (best, mean, median, std, success rate).
    """
    doc = get_instance_by_id(req.instance_id)
    if doc is None:
        return CompareResponse(
            instance_id=req.instance_id,
            runs=req.runs,
            seed_start=req.seed_start,
            summaries={},
            raw_runs={},
        )

    problem = doc.to_problem_data()
    summaries: Dict[str, AlgorithmComparisonSummary] = {}
    raw_runs: Dict[str, List[SolveResponse]] = {}

    for algo in req.algorithms:
        algo_overrides = req.parameters.get(algo, {})
        # Greedy is deterministic so 1 run is sufficient, or repeat if needed;
        # Spec 5.3 notes Greedy is deterministic baseline (run once or report clearly).
        num_runs_for_algo = 1 if algo == "greedy" else req.runs
        algo_results: List[SolveResponse] = []

        for r_idx in range(num_runs_for_algo):
            current_seed = req.seed_start + r_idx
            merged_params_dict = {**algo_overrides, "seed": current_seed}
            params = AlgorithmParameters(**merged_params_dict)
            res = _dispatch_algorithm(algo, problem, params)
            algo_results.append(res)

        raw_runs[algo] = algo_results

        # Compute summary metrics across runs
        successful = [r for r in algo_results if r.status == "success"]
        penalties = [r.metrics.penalty_score for r in successful]
        runtimes = [r.metrics.runtime_ms for r in algo_results]
        attempts_list = [r.metrics.attempts for r in algo_results]

        best_run = min(successful, key=lambda r: r.metrics.penalty_score) if successful else None

        summaries[algo] = AlgorithmComparisonSummary(
            algorithm=algo,
            total_runs=num_runs_for_algo,
            successful_runs=len(successful),
            success_rate=round(len(successful) / num_runs_for_algo, 4) if num_runs_for_algo > 0 else 0.0,
            best_penalty=min(penalties) if penalties else None,
            mean_penalty=round(statistics.mean(penalties), 2) if penalties else None,
            median_penalty=round(statistics.median(penalties), 2) if penalties else None,
            std_penalty=round(statistics.stdev(penalties), 2) if len(penalties) > 1 else 0.0 if penalties else None,
            mean_runtime_ms=round(statistics.mean(runtimes), 3) if runtimes else 0.0,
            mean_attempts=round(statistics.mean(attempts_list), 1) if attempts_list else 0.0,
            best_run_schedule=best_run.schedule if best_run else [],
            best_run_history=best_run.history if best_run else [],
        )

    return CompareResponse(
        instance_id=req.instance_id,
        runs=req.runs,
        seed_start=req.seed_start,
        summaries=summaries,
        raw_runs=raw_runs,
    )
