"""
[งานของคนที่ 2: ฝ้าย]
Dataset Generator & MongoDB Seeder Script (`backend/scripts/seed_db.py`).

หน้าที่ของไฟล์นี้:
1. โหลดชุดข้อมูลเริ่มต้นจาก `sample_instances.json`
2. (TODO สำหรับฝ้าย) สร้างฟังก์ชัน `generate_synthetic_instance(...)` เพื่อสร้างชุดข้อมูลจำลองอย่างน้อย 3 ชุด
   ที่มีความยากต่างกัน (เช่น `easy_01`, `medium_01`, `hard_01`) โดยต้องตรวจสอบว่ามีคำตอบที่ไม่ชนกันจริง (Solvable)
3. บันทึก (Upsert) ลงใน MongoDB Collection `exam_instances`

วิธีรัน:
- รันผ่าน Docker: `docker compose exec backend python -m scripts.seed_db`
- รันบนเครื่องตัวเอง: `cd backend && python -m scripts.seed_db`
"""

import sys
from pathlib import Path

# Ensure `app` package is importable when running script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import load_sample_instances_from_json, upsert_instance
from app.core.validator import validate_problem_input


def seed_all_instances() -> None:
    """Load starter instances (and generated instances) and upsert into MongoDB."""
    instances = load_sample_instances_from_json()

    # ==========================================================================
    # TODO [คนที่ 2 - ฝ้าย]:
    # เพิ่มการสร้าง Dataset จำลอง 2-3 ระดับความยาก (เช่น easy_01, medium_01, hard_01)
    # โดยใช้ technique Planted Coloring (แบ่งวิชาลงช่วงสอบจำลองก่อนสุ่มนักศึกษา)
    # เพื่อรับประกันว่ามีตารางสอบที่ Hard Conflict = 0 เสมอ
    # ==========================================================================

    print(f"Found {len(instances)} instance(s) to validate and seed...")
    success_count = 0

    for inst in instances:
        problem_data = inst.to_problem_data()
        err = validate_problem_input(problem_data)
        if err:
            print(f"[ERROR] Instance '{inst.instance_id}' failed input validation: {err}")
            continue

        ok = upsert_instance(inst)
        if ok:
            print(
                f"[OK] Seeded '{inst.instance_id}' ({len(inst.courses)} courses, "
                f"{len(inst.students)} students, {len(inst.slots)} slots)"
            )
            success_count += 1
        else:
            print(f"[WARN] Could not connect to MongoDB to seed '{inst.instance_id}'.")

    print(f"Done! Successfully seeded {success_count}/{len(instances)} instance(s).")


if __name__ == "__main__":
    seed_all_instances()
