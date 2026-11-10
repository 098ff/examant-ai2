"""
[Person 2: Fai]
Dataset Generator & MongoDB Seeder Script (`backend/scripts/seed_db.py`).

Responsibilities of this module:
1. Programmatically generate datasets (pure code generator, no static mock JSON file).
2. Connect strictly to MongoDB and seed/upsert instances into the `exam_instances` collection.
3. Validate every generated instance using `validate_problem_input`.

Usage:
- In Docker: `docker compose exec backend python -m scripts.seed_db`
- Outside Docker: `python -m scripts.seed_db`
"""

import sys
from pathlib import Path
from typing import List

# Ensure `app` package is importable when running script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.validator import validate_problem_input
from app.database import get_collection, upsert_instance
from app.schemas.models import (
    CourseRecord,
    EnrollmentRecord,
    ExamInstanceDocument,
    ExamSlotRecord,
    StudentRecord,
)


def build_starter_instance() -> ExamInstanceDocument:
    """
    Construct starter benchmark instance `demo_01` programmatically.
    10 courses, 20 students, 6 slots (3 days, 2 slots/day: morning and afternoon).
    """
    course_data = [
        ("C01", "Artificial Intelligence II", 7),
        ("C02", "Discrete Mathematics", 7),
        ("C03", "Database Systems", 6),
        ("C04", "Operating Systems", 6),
        ("C05", "Computer Networks", 5),
        ("C06", "Software Engineering", 5),
        ("C07", "Linear Algebra", 5),
        ("C08", "Data Structures", 5),
        ("C09", "Machine Learning", 4),
        ("C10", "Cloud Computing", 4),
    ]
    courses = [
        CourseRecord(course_id=cid, course_name=name, student_count=cnt)
        for cid, name, cnt in course_data
    ]

    students = [StudentRecord(student_id=f"S{i:03d}") for i in range(1, 21)]

    raw_enrollments = [
        ("S001", "C01"), ("S001", "C02"), ("S001", "C03"),
        ("S002", "C01"), ("S002", "C02"), ("S002", "C04"),
        ("S003", "C01"), ("S003", "C05"), ("S003", "C09"),
        ("S004", "C01"), ("S004", "C06"), ("S004", "C07"),
        ("S005", "C02"), ("S005", "C03"), ("S005", "C08"),
        ("S006", "C02"), ("S006", "C04"), ("S006", "C07"),
        ("S007", "C03"), ("S007", "C05"), ("S007", "C10"),
        ("S008", "C03"), ("S008", "C06"),
        ("S009", "C04"), ("S009", "C08"), ("S009", "C09"),
        ("S010", "C04"), ("S010", "C05"),
        ("S011", "C05"), ("S011", "C06"), ("S011", "C08"),
        ("S012", "C07"), ("S012", "C09"), ("S012", "C10"),
        ("S013", "C01"), ("S013", "C08"),
        ("S014", "C02"), ("S014", "C09"),
        ("S015", "C03"), ("S015", "C07"),
        ("S016", "C04"), ("S016", "C10"),
        ("S017", "C01"), ("S017", "C10"),
        ("S018", "C02"), ("S018", "C06"),
        ("S019", "C05"), ("S019", "C07"),
        ("S020", "C06"), ("S020", "C08"),
    ]
    enrollments = [
        EnrollmentRecord(student_id=sid, course_id=cid) for sid, cid in raw_enrollments
    ]

    slots = [
        ExamSlotRecord(slot_id="D1_S1", day_index=1, slot_index=1, label="Day 1 Morning"),
        ExamSlotRecord(slot_id="D1_S2", day_index=1, slot_index=2, label="Day 1 Afternoon"),
        ExamSlotRecord(slot_id="D2_S1", day_index=2, slot_index=1, label="Day 2 Morning"),
        ExamSlotRecord(slot_id="D2_S2", day_index=2, slot_index=2, label="Day 2 Afternoon"),
        ExamSlotRecord(slot_id="D3_S1", day_index=3, slot_index=1, label="Day 3 Morning"),
        ExamSlotRecord(slot_id="D3_S2", day_index=3, slot_index=2, label="Day 3 Afternoon"),
    ]

    return ExamInstanceDocument(
        instance_id="demo_01",
        name="Demo 01 — Small Benchmark Dataset (10 Courses, 3 Days / 6 Slots)",
        seed=42,
        description="Programmatically generated 10-course, 20-student instance across 3 exam days (6 slots).",
        courses=courses,
        students=students,
        enrollments=enrollments,
        slots=slots,
    )


def get_all_seed_instances() -> List[ExamInstanceDocument]:
    """
    Return all dataset instances to be seeded into MongoDB.
    
    TODO [Person 2 - Fai]:
    Add `generate_synthetic_instance(difficulty='easy')`, `medium`, `hard` here
    using the Planted Coloring technique to guarantee zero hard-conflict solvability.
    """
    instances = [build_starter_instance()]
    return instances


def seed_all_instances() -> int:
    """
    Seed/Upsert all programmatic instances directly into MongoDB.
    Returns the count of successfully seeded instances.
    """
    collection = get_collection()
    if collection is None:
        print("[ERROR] MongoDB is unavailable. Please ensure MongoDB is running via 'docker compose up -d mongodb'.")
        return 0

    instances = get_all_seed_instances()
    print(f"Connecting to MongoDB... Found {len(instances)} instance(s) to seed.")
    success_count = 0

    for inst in instances:
        err = validate_problem_input(inst.to_problem_data())
        if err:
            print(f"[ERROR] Instance '{inst.instance_id}' failed input validation: {err}")
            continue

        ok = upsert_instance(inst)
        if ok:
            print(
                f"[OK] Seeded '{inst.instance_id}' into MongoDB ({len(inst.courses)} courses, "
                f"{len(inst.students)} students, {len(inst.slots)} slots)"
            )
            success_count += 1
        else:
            print(f"[ERROR] Failed to upsert '{inst.instance_id}' into MongoDB.")

    print(f"Done! Successfully seeded {success_count}/{len(instances)} instance(s) into MongoDB.")
    return success_count


if __name__ == "__main__":
    seed_all_instances()
