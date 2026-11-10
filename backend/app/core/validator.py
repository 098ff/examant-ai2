"""
Independent Central Validator & Schedule Evaluator (Spec Section 4.3 & Section 9).
All 3 algorithms MUST pass their resulting schedule through `validate_and_score_schedule`
so that reported metrics (`hard_conflict_count`, `consecutive_exam_pair_count`, `penalty_score`)
are guaranteed to be evaluated by the exact same rules.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from app.schemas.models import (
    ConsecutiveCaseDetail,
    HardConflictDetail,
    ProblemData,
    ScheduleItem,
    ValidationDetails,
)


def validate_problem_input(problem: ProblemData) -> Optional[str]:
    """
    Validate input dataset structure before running any solver (Spec Section 9).
    Returns None if valid, or an error message string if invalid.
    """
    if not problem.instance_id or not problem.instance_id.strip():
        return "instance_id must not be empty."

    if len(problem.courses) == 0:
        return "Dataset must contain at least 1 course."

    if len(set(problem.courses)) != len(problem.courses):
        return "Duplicate course_id found in courses list."

    if len(set(problem.students)) != len(problem.students):
        return "Duplicate student_id found in students list."

    if len(problem.slots) == 0:
        return "Dataset must contain at least 1 exam day (2 slots)."

    slot_ids = [s.slot_id for s in problem.slots]
    if len(set(slot_ids)) != len(slot_ids):
        return "Duplicate slot_id found in slots list."

    # Verify each day has exactly 2 slots: slot_index 1 (Morning) and 2 (Afternoon)
    day_to_slots: Dict[int, List[int]] = defaultdict(list)
    for s in problem.slots:
        if s.day_index < 1:
            return f"Invalid day_index {s.day_index} in slot {s.slot_id}."
        if s.slot_index not in (1, 2):
            return f"Invalid slot_index {s.slot_index} in slot {s.slot_id} (must be 1 or 2)."
        day_to_slots[s.day_index].append(s.slot_index)

    for day_idx, indices in day_to_slots.items():
        if sorted(indices) != [1, 2]:
            return (
                f"Day {day_idx} must have exactly 2 slots (slot_index 1 and 2), "
                f"found: {indices}."
            )

    # Verify enrollment references
    course_set = set(problem.courses)
    student_set = set(problem.students)
    seen_enrollments = set()
    for enr in problem.enrollments:
        if enr.course_id not in course_set:
            return f"Enrollment references unknown course_id '{enr.course_id}'."
        if enr.student_id not in student_set:
            return f"Enrollment references unknown student_id '{enr.student_id}'."
        pair = (enr.student_id, enr.course_id)
        if pair in seen_enrollments:
            return f"Duplicate enrollment record for student '{enr.student_id}' and course '{enr.course_id}'."
        seen_enrollments.add(pair)

    return None


def validate_and_score_schedule(
    problem: ProblemData,
    schedule: List[ScheduleItem],
) -> Tuple[int, int, int, ValidationDetails]:
    """
    Independently validate a candidate `schedule` against `problem` and compute scores.

    Returns:
        (hard_conflict_count, consecutive_exam_pair_count, penalty_score, validation_details)
    """
    expected_courses = set(problem.courses)
    slot_map = {s.slot_id: s for s in problem.slots}

    assigned_map: Dict[str, str] = {}
    duplicate_courses: List[str] = []
    invalid_slots: List[str] = []

    for item in schedule:
        if item.course_id in assigned_map:
            duplicate_courses.append(item.course_id)
        assigned_map[item.course_id] = item.slot_id
        if item.slot_id not in slot_map:
            invalid_slots.append(item.slot_id)

    unassigned_courses = sorted(list(expected_courses - set(assigned_map.keys())))

    # Map student -> list of enrolled courses
    student_courses: Dict[str, List[str]] = defaultdict(list)
    for enr in problem.enrollments:
        student_courses[enr.student_id].append(enr.course_id)

    hard_conflicts: List[HardConflictDetail] = []
    consecutive_cases: List[ConsecutiveCaseDetail] = []
    exceeded_daily_limit_students: List[str] = []

    for student_id in sorted(student_courses.keys()):
        courses_of_student = sorted(student_courses[student_id])

        # 1. Check same-slot conflicts for this student
        for i in range(len(courses_of_student)):
            c_a = courses_of_student[i]
            slot_a = assigned_map.get(c_a)
            if not slot_a or slot_a not in slot_map:
                continue
            for j in range(i + 1, len(courses_of_student)):
                c_b = courses_of_student[j]
                slot_b = assigned_map.get(c_b)
                if slot_a == slot_b:
                    hard_conflicts.append(
                        HardConflictDetail(
                            student_id=student_id,
                            slot_id=slot_a,
                            course_a=c_a,
                            course_b=c_b,
                        )
                    )

        # 2. Check daily exam count (<= 2 per day) and consecutive morning+afternoon pairs
        day_to_slot_courses: Dict[int, Dict[int, List[str]]] = defaultdict(lambda: defaultdict(list))
        for cid in courses_of_student:
            sid = assigned_map.get(cid)
            if sid and sid in slot_map:
                s_obj = slot_map[sid]
                day_to_slot_courses[s_obj.day_index][s_obj.slot_index].append(cid)

        for day_idx in sorted(day_to_slot_courses.keys()):
            morning_courses = day_to_slot_courses[day_idx].get(1, [])
            afternoon_courses = day_to_slot_courses[day_idx].get(2, [])
            total_on_day = len(morning_courses) + len(afternoon_courses)
            if total_on_day > 2:
                exceeded_daily_limit_students.append(f"{student_id} (Day {day_idx}: {total_on_day} exams)")

            # Soft objective: 1 penalty per (student, day) having BOTH morning & afternoon exams
            if len(morning_courses) > 0 and len(afternoon_courses) > 0:
                consecutive_cases.append(
                    ConsecutiveCaseDetail(
                        student_id=student_id,
                        day_index=day_idx,
                        morning_course_id=morning_courses[0],
                        afternoon_course_id=afternoon_courses[0],
                    )
                )

    hard_conflict_count = len(hard_conflicts)
    consecutive_exam_pair_count = len(consecutive_cases)
    penalty_score = consecutive_exam_pair_count

    is_valid = (
        len(unassigned_courses) == 0
        and len(duplicate_courses) == 0
        and len(invalid_slots) == 0
        and len(exceeded_daily_limit_students) == 0
        and hard_conflict_count == 0
    )

    details = ValidationDetails(
        is_valid=is_valid,
        unassigned_courses=unassigned_courses,
        duplicate_courses=duplicate_courses,
        invalid_slots=invalid_slots,
        exceeded_daily_limit_students=exceeded_daily_limit_students,
        hard_conflicts=hard_conflicts,
        consecutive_cases=consecutive_cases,
    )

    return hard_conflict_count, consecutive_exam_pair_count, penalty_score, details
