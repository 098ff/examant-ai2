"""
[งานของคนที่ 1: ไมไม (Lead)]
Ant Colony Optimization (ACO) Algorithm (`backend/app/algorithms/aco.py`).

อ้างอิงทฤษฎีจาก `AI2 Slide.pdf` (หน้า 18-30: Ant System & AS-QAP) และ `docs/01-project-idea-spec.md` (หัวข้อ 7.3):
1. โครงสร้าง Pheromone `tau[course_id][slot_id]`:
   - กำหนดค่าเริ่มต้นทุกคู่ (course, slot) เท่ากับ `params.initial_pheromone` (tau_0)
2. ลำดับการจัดวิชา:
   - เรียงตาม degree ความขัดแย้งจากมากไปน้อย: `ordered_courses = graph.get_ordered_courses()`
3. ในแต่ละ Iteration (1 ถึง `params.iterations`):
   - สร้างมด `params.num_ants` ตัว แต่ละตัวเริ่มจาก `partial_schedule = {}`
   - มดแต่ละตัวจัดวิชาทีละตัวตาม `ordered_courses`:
     a) หาช่วงสอบที่ถูกต้องตาม Hard Constraint (Tabu / Feasible set):
        `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
        หากไม่มีช่วงสอบที่ใช้ได้ -> มดตัวนี้ติดทางตัน (Dead-end) ให้ข้ามมดตัวนี้ไป
     b) คำนวณ Heuristic Visibility `eta(c, t)` สำหรับแต่ละ `t` ใน `feasible_slots`:
        `delta_p = graph.calculate_delta_penalty(course_id, t, partial_schedule)`
        `eta = 1.0 / (1.0 + delta_p)`
     c) คำนวณน้ำหนักความน่าจะเป็น (Transition Rule - AI2 Slide หน้า 19, 29):
        `weight(c, t) = (tau[c][t] ** params.alpha) * (eta ** params.beta)`
        แล้วสุ่มเลือก `slot_id` ตามสัดส่วนความน่าจะเป็น `weight(c, t) / sum(weights)`
   - ประเมินค่า Penalty `P_k` ของมดทุกตัวที่สร้างตารางสำเร็จใน Iteration นั้น
   - อัปเดต `global_best_schedule` และ `global_best_penalty`
   - Pheromone Evaporation (AI2 Slide หน้า 21, 30):
     `tau[c][t] = (1.0 - params.rho) * tau[c][t]` สำหรับทุก `(c, t)`
   - Pheromone Deposit (AI2 Slide หน้า 21, 30):
     สำหรับมดที่สร้างตารางสำเร็จ: `deposit = params.q / (1.0 + P_k)`
     บวก `deposit` เข้าไปใน `tau[c][assigned_slot]`
   - บันทึก `IterationHistoryPoint(iteration=it, best_penalty=global_best_penalty, ...)` ลงใน `history`
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
    # TODO [คนที่ 1 - ไมไม]:
    # แทนที่โค้ด Stub ด้านล่างด้วยลูป ACO เต็มรูปแบบ (Pheromone matrix, Transition rule,
    # Evaporation, Deposit และเก็บ IterationHistoryPoint จริงในแต่ละรอบ)
    # ==========================================================================
    best_schedule: Optional[Dict[str, str]] = {}
    ordered_courses = graph.get_ordered_courses()

    for course_id in ordered_courses:
        feasible_slots = graph.get_feasible_slots(course_id, best_schedule)
        if not feasible_slots:
            best_schedule = None
            break
        # STUB: เลือก slot ที่มี delta_penalty ต่ำปนสุ่มเล็กน้อย เพื่อให้ระบบทดสอบแสดงผลได้ก่อน
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
