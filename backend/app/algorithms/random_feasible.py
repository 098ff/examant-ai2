"""
[งานของคนที่ 1: ไมไม]
Random Feasible Baseline Algorithm (`backend/app/algorithms/random_feasible.py`).

กติกาจาก `docs/01-project-idea-spec.md` (หัวข้อ 7.2):
1. ใช้ `rng = random.Random(params.seed)` เพื่อให้ทำซ้ำผลเดิมได้ (Reproducible)
2. วนลูปสร้างตารางไม่เกินงบ `params.max_attempts` ครั้ง:
   - ในแต่ละ attempt สร้างตารางทีละวิชา โดยสุ่มเลือกจาก `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
   - หากมีวิชาใดที่ `feasible_slots` ว่างเปล่า (ติดทางตัน / Dead-end) ให้ถือว่า attempt นั้นล้มเหลวและเริ่ม attempt ถัดไป
3. สำหรับทุกตารางที่จัดครบทุกวิชา คำนวณค่า penalty (หรือใช้ `validate_and_score_schedule`)
   และเก็บตารางที่มี `penalty_score` ต่ำที่สุด (`best_schedule`) พร้อมบันทึก `best_iteration` และ `history`
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
    # TODO [คนที่ 1 - ไมไม]:
    # พัฒนาลูปสุ่มสร้างตารางจำนวน `params.max_attempts` รอบ และเก็บตารางที่ Penalty ต่ำสุด
    # (ด้านล่างเป็นโค้ด Stub เบื้องต้นที่สุ่ม 1 รอบเพื่อให้ Frontend ทดสอบเชื่อม API ได้ทันที)
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
