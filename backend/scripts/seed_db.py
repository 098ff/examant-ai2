"""
[Person 2: Fai (Chanatda Konchom)]
Dataset Generator & MongoDB Seeder Script (`backend/scripts/seed_db.py`).

Responsibilities of this module:
1. Programmatically generate datasets using the Planted Feasible Assignment technique
   (pure code generator, no static mock JSON file).
2. Validate every generated instance using `validate_problem_input` and verify baseline
   solvability via `solve_greedy`.
3. Connect strictly to MongoDB and seed/upsert instances into the `exam_instances` collection.

Usage:
- In Docker: `docker compose exec backend python -m scripts.seed_db`
- Outside Docker: `python -m scripts.seed_db`
"""

from collections import Counter
import random
import sys
from pathlib import Path
from typing import Dict, List, Literal

# Ensure `app` package is importable when running script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.algorithms.greedy import solve_greedy
from app.core.validator import validate_problem_input
from app.database import get_collection, upsert_instance
from app.schemas.models import (
    AlgorithmParameters,
    CourseRecord,
    EnrollmentRecord,
    ExamInstanceDocument,
    ExamSlotRecord,
    StudentRecord,
)

COURSE_CATALOG: List[str] = [
    "Artificial Intelligence II",
    "Discrete Mathematics",
    "Database Systems",
    "Operating Systems",
    "Computer Networks",
    "Software Engineering",
    "Linear Algebra",
    "Data Structures",
    "Machine Learning",
    "Cloud Computing",
    "Computer Security",
    "Theory of Computation",
    "Compiler Design",
    "Distributed Systems",
    "Computer Vision",
    "Natural Language Processing",
]


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


def generate_synthetic_instance(
    difficulty: Literal["easy", "medium", "hard"],
) -> ExamInstanceDocument:
    """
    Generate a synthetic examination timetabling benchmark dataset (`easy_01`, `medium_01`, or `hard_01`)
    using the Planted Feasible Assignment (Planted Coloring) technique.

    Planted Feasible Assignment Guarantee:
    1. All `num_courses` courses are first partitioned across the `2 * num_days` exam slots,
       forming a hidden conflict-free reference schedule.
    2. Each simulated student enrolls in 2 or 3 courses drawn strictly from distinct planted
       slot groups. Consequently, no two courses taken by the same student ever share a planted
       slot, mathematically guaranteeing that at least one valid schedule with 0 hard conflicts
       and at most 2 exams per day exists.
    3. Most students sample courses from distinct planted exam days, ensuring that the planted
       assignment also achieves a low consecutive-exam penalty while creating non-trivial degree
       distributions where myopic greedy ordering incurs higher consecutive penalties.
    """
    presets: Dict[str, Dict] = {
        "easy": {
            "instance_id": "easy_01",
            "name": "Easy 01 — Low-Density Synthetic Dataset (10 Courses, 3 Days / 6 Slots)",
            "seed": 105,
            "num_courses": 10,
            "num_students": 45,
            "num_days": 3,
            "three_course_ratio": 0.30,
            "same_day_planted_prob": 0.10,
            "description": (
                "Planted-coloring synthetic benchmark with 10 courses, 45 students, "
                "and 6 exam slots (3 days: morning and afternoon) with low-to-moderate conflict density."
            ),
        },
        "medium": {
            "instance_id": "medium_01",
            "name": "Medium 01 — Moderate-Density Synthetic Dataset (12 Courses, 3 Days / 6 Slots)",
            "seed": 214,
            "num_courses": 12,
            "num_students": 70,
            "num_days": 3,
            "three_course_ratio": 0.45,
            "same_day_planted_prob": 0.15,
            "description": (
                "Planted-coloring synthetic benchmark with 12 courses, 70 students, "
                "and higher shared-student overlap across 3 exam days (6 slots)."
            ),
        },
        "hard": {
            "instance_id": "hard_01",
            "name": "Hard 01 — High-Density Synthetic Dataset (15 Courses, 4 Days / 8 Slots)",
            "seed": 300,
            "num_courses": 15,
            "num_students": 90,
            "num_days": 4,
            "three_course_ratio": 0.50,
            "same_day_planted_prob": 0.12,
            "description": (
                "High-density planted-coloring synthetic benchmark with 15 courses and 90 students "
                "across 4 exam days (8 slots), designed to challenge greedy heuristics on soft penalties."
            ),
        },
    }

    if difficulty not in presets:
        raise ValueError(f"Unsupported difficulty preset: {difficulty}")

    cfg = presets[difficulty]
    rng = random.Random(cfg["seed"])
    num_courses: int = cfg["num_courses"]
    num_students: int = cfg["num_students"]
    num_days: int = cfg["num_days"]
    num_slots: int = num_days * 2

    # Build chronological exam slots (2 slots per day: Morning = 1, Afternoon = 2)
    slots: List[ExamSlotRecord] = []
    for day_idx in range(1, num_days + 1):
        slots.append(
            ExamSlotRecord(
                slot_id=f"D{day_idx}_S1",
                day_index=day_idx,
                slot_index=1,
                label=f"Day {day_idx} Morning",
            )
        )
        slots.append(
            ExamSlotRecord(
                slot_id=f"D{day_idx}_S2",
                day_index=day_idx,
                slot_index=2,
                label=f"Day {day_idx} Afternoon",
            )
        )

    course_ids = [f"C{i:02d}" for i in range(1, num_courses + 1)]
    student_ids = [f"S{i:03d}" for i in range(1, num_students + 1)]

    # Step 1: Planted Feasible Assignment — partition courses across the 2*D slot groups
    shuffled_courses = list(course_ids)
    rng.shuffle(shuffled_courses)

    slot_groups: Dict[str, List[str]] = {s.slot_id: [] for s in slots}
    for idx, cid in enumerate(shuffled_courses):
        target_slot_id = slots[idx % num_slots].slot_id
        slot_groups[target_slot_id].append(cid)

    day_to_slot_ids: Dict[int, List[str]] = {
        d: [f"D{d}_S1", f"D{d}_S2"] for d in range(1, num_days + 1)
    }

    # Step 2: Sample student enrollments strictly across distinct planted slot groups
    enrollments: List[EnrollmentRecord] = []
    course_enrollment_counts: Counter = Counter()

    for sid in student_ids:
        k = 3 if rng.random() < cfg["three_course_ratio"] else 2
        k = min(k, num_slots)

        if rng.random() < cfg["same_day_planted_prob"]:
            # Allow one planted day to contribute both morning and afternoon slots
            chosen_days = rng.sample(
                range(1, num_days + 1), k=min(num_days, max(1, k - 1))
            )
            chosen_slot_ids = list(day_to_slot_ids[chosen_days[0]])
            for extra_d in chosen_days[1:]:
                if len(chosen_slot_ids) < k:
                    chosen_slot_ids.append(rng.choice(day_to_slot_ids[extra_d]))
            while len(chosen_slot_ids) < k:
                remaining = [s.slot_id for s in slots if s.slot_id not in chosen_slot_ids]
                chosen_slot_ids.append(rng.choice(remaining))
        else:
            # Prefer picking slots from distinct planted days to keep planted penalty low
            available_days = list(range(1, num_days + 1))
            rng.shuffle(available_days)
            chosen_slot_ids = []
            for d in available_days[: min(k, num_days)]:
                chosen_slot_ids.append(rng.choice(day_to_slot_ids[d]))
            while len(chosen_slot_ids) < k:
                remaining = [s.slot_id for s in slots if s.slot_id not in chosen_slot_ids]
                chosen_slot_ids.append(rng.choice(remaining))

        selected_courses = sorted(
            [rng.choice(slot_groups[slot_id]) for slot_id in chosen_slot_ids]
        )
        for cid in selected_courses:
            enrollments.append(EnrollmentRecord(student_id=sid, course_id=cid))
            course_enrollment_counts[cid] += 1

    courses: List[CourseRecord] = [
        CourseRecord(
            course_id=cid,
            course_name=(
                COURSE_CATALOG[idx]
                if idx < len(COURSE_CATALOG)
                else f"Advanced Topic in Computer Science {idx + 1}"
            ),
            student_count=course_enrollment_counts[cid],
        )
        for idx, cid in enumerate(course_ids)
    ]
    students: List[StudentRecord] = [
        StudentRecord(student_id=sid) for sid in student_ids
    ]

    return ExamInstanceDocument(
        instance_id=cfg["instance_id"],
        name=cfg["name"],
        seed=cfg["seed"],
        description=cfg["description"],
        courses=courses,
        students=students,
        enrollments=enrollments,
        slots=slots,
    )


def get_all_seed_instances() -> List[ExamInstanceDocument]:
    """
    Return all dataset instances (`demo_01`, `easy_01`, `medium_01`, `hard_01`)
    to be validated and seeded into MongoDB.
    """
    return [
        build_starter_instance(),
        generate_synthetic_instance("easy"),
        generate_synthetic_instance("medium"),
        generate_synthetic_instance("hard"),
    ]


def seed_all_instances() -> int:
    """
    Validate each programmatic dataset with `validate_problem_input`, verify solvability
    with `solve_greedy`, and upsert all valid instances directly into MongoDB.
    Returns the count of successfully seeded instances.
    """
    collection = get_collection()
    if collection is None:
        print(
            "[ERROR] MongoDB is unavailable. Please ensure MongoDB is running via "
            "'docker compose up -d mongodb'."
        )
        return 0

    instances = get_all_seed_instances()
    print(f"Connecting to MongoDB... Found {len(instances)} instance(s) to seed.")
    success_count = 0

    for inst in instances:
        problem = inst.to_problem_data()
        err = validate_problem_input(problem)
        if err:
            print(f"[ERROR] Instance '{inst.instance_id}' failed input validation: {err}")
            continue

        greedy_res = solve_greedy(problem, AlgorithmParameters(seed=inst.seed))
        if (
            greedy_res.status != "success"
            or greedy_res.validation_details is None
            or not greedy_res.validation_details.is_valid
            or greedy_res.metrics.hard_conflict_count != 0
        ):
            print(
                f"[ERROR] Instance '{inst.instance_id}' failed Greedy baseline verification "
                f"(status={greedy_res.status})."
            )
            continue

        ok = upsert_instance(inst)
        if ok:
            print(
                f"[OK] Seeded '{inst.instance_id}' into MongoDB ({len(inst.courses)} courses, "
                f"{len(inst.students)} students, {len(inst.enrollments)} enrollments, "
                f"{len(inst.slots)} slots, greedy_penalty={greedy_res.metrics.penalty_score})"
            )
            success_count += 1
        else:
            print(f"[ERROR] Failed to upsert '{inst.instance_id}' into MongoDB.")

    print(
        f"Done! Successfully seeded {success_count}/{len(instances)} instance(s) into MongoDB."
    )
    return success_count


if __name__ == "__main__":
    seed_all_instances()
