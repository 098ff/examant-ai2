"""
[งานของคนที่ 2: ฝ้าย]
Greedy Baseline Algorithm (`backend/app/algorithms/greedy.py`).

กติกาจาก `docs/01-project-idea-spec.md` (หัวข้อ 7.1):
1. สร้างกราฟความขัดแย้งจาก enrollment (`graph = ConflictGraph(problem)`)
2. เรียงวิชาจาก degree มากไปน้อย (วิชาที่ชนกับวิชาอื่นมากก่อน); หากเสมอให้เรียง `course_id`
   -> ใช้ `ordered_courses = graph.get_ordered_courses()` ได้เลย
3. สำหรับแต่ละวิชา เลือกช่วงสอบที่ไม่มีวิชาขัดแย้งถูกจัดอยู่แล้ว และไม่ทำให้นักศึกษาสอบเกิน 2 วิชา/วัน
   -> ใช้ `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
4. ในบรรดาช่วงที่ถูกต้อง เลือกช่วงที่ทำให้ penalty เพิ่มน้อยที่สุด (`graph.calculate_delta_penalty(...)`)
5. หากเสมอ เลือก slot ที่เรียงก่อนตามลำดับเวลา
6. ถ้าไม่มี slot ที่ใช้ได้ ให้คืน `no_solution_found` (ส่ง `schedule_dict=None`)
"""

import time
from typing import Dict, Optional
from app.algorithms.base import build_solve_response
from app.core.graph import ConflictGraph
from app.schemas.models import AlgorithmParameters, ProblemData, SolveResponse


def solve_greedy(problem: ProblemData, params: AlgorithmParameters) -> SolveResponse:
    """Run Greedy examination timetabling baseline."""
    start_time = time.perf_counter()
    graph = ConflictGraph(problem)

    # ==========================================================================
    # TODO [คนที่ 2 - ฝ้าย]:
    # แทนที่โค้ด Stub ด้านล่างด้วยการเลือก slot ที่ให้ `calculate_delta_penalty` ต่ำที่สุด
    # (ปัจจุบัน Stub ด้านล่างเลือก feasible slot ช่วงแรกสุดที่ว่างเพื่อให้ระบบทดสอบยิง API ได้ก่อน)
    # ==========================================================================
    partial_schedule: Optional[Dict[str, str]] = {}
    ordered_courses = graph.get_ordered_courses()

    for course_id in ordered_courses:
        feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)
        if not feasible_slots:
            partial_schedule = None
            break
        # STUB: เลือก slot แรกที่ว่าง (ฝ้ายต้องแก้ให้เลือก slot ที่ delta_penalty น้อยที่สุด)
        partial_schedule[course_id] = feasible_slots[0]

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
        message="[STUB] Greedy starter stub executed. (TODO: Person 2 implement min delta_penalty selection)",
    )
