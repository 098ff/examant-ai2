<p align="right">
  <a href="05-way-of-work-backend.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# ⚙️ แนวทางการพัฒนาฝั่ง Backend (Way of Work for Backend)

เอกสารนี้เป็นคู่มือสำหรับทีมพัฒนา Backend (**ไมไม - คนที่ 1** และ **ฝ้าย - คนที่ 2**) อธิบายโครงสร้างโฟลเดอร์ `backend/`, สัญญา API, พารามิเตอร์ของแต่ละอัลกอริทึม และวิธีเรียกใช้โมดูลกลาง (`ConflictGraph` และ `Central Validator`) เพื่อให้ทั้ง 3 อัลกอริทึมทำงานร่วมกันได้อย่างไร้รอยต่อ

---

## 1. โครงสร้างโฟลเดอร์ `backend/`

```text
backend/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py                  # FastAPI App Entrypoint & Lifespan Auto-Seed
│   ├── config.py                # โหลดค่า MONGO_URI, MONGO_DB_NAME
│   ├── database.py              # ฟังก์ชันอ่าน/เขียน MongoDB Collection `exam_instances`
│   ├── schemas/
│   │   └── models.py            # Pydantic Schemas กลางของทั้งระบบ (ห้ามแก้ชื่อฟิลด์หลักโดยไม่แจ้งทีม)
│   ├── core/
│   │   ├── graph.py             # [ส่วนกลาง] คลาส ConflictGraph ช่วยหา Feasible Slots และคำนวณ Delta P
│   │   └── validator.py         # [ส่วนกลาง] ตัวตรวจคำตอบกลาง validate_and_score_schedule()
│   ├── algorithms/
│   │   ├── base.py              # [ส่วนกลาง] ฟังก์ชัน build_solve_response() แปลงผลลัพธ์ส่งกลับตาม Schema
│   │   ├── greedy.py            # 👩‍💻 [งานฝ้าย - คนที่ 2] อัลกอริทึม Greedy Baseline
│   │   ├── random_feasible.py   # 👩‍💻 [งานไมไม - คนที่ 1] อัลกอริทึม Random Feasible Baseline
│   │   └── aco.py               # 👩‍💻 [งานไมไม - คนที่ 1] อัลกอริทึม Ant Colony Optimization (ACO)
│   └── routers/
│       ├── instances.py         # GET /instances, GET /instances/{id}, GET /instances/{id}/graph
│       └── solver.py            # POST /solve, POST /compare
└── scripts/
    └── seed_db.py               # 👩‍💻 [งานฝ้าย - คนที่ 2] สคริปต์สร้าง Dataset จำลองแบบ Programmatic และ Seed ลง MongoDB
```

---

## 2. วิธีใช้งานโมดูลกลาง (`ConflictGraph` & `build_solve_response`)

เพื่อให้ทั้ง **Greedy**, **Random Feasible** และ **ACO** ใช้กติกาการตรวจสอบการชนและคำนวณคะแนนสอบติดกัน (เช้า-บ่าย) ตรงกัน 100% ให้เรียกใช้คลาส `ConflictGraph` จาก `app/core/graph.py` ดังนี้:

```python
from app.core.graph import ConflictGraph
from app.algorithms.base import build_solve_response

graph = ConflictGraph(problem)

# 1. ดึงรายชื่อวิชาที่เรียงลำดับตามจำนวนวิชาที่ชนจากมากไปน้อย (Degree มากก่อน, ถ้าเท่ากันเรียงตาม course_id)
ordered_courses = graph.get_ordered_courses()

# 2. สมมติเรากำลังค่อยๆ จัดตารางลงใน dict ชื่อ partial_schedule: Dict[str, str] (course_id -> slot_id)
partial_schedule = {}

# 3. ขอรายชื่อ slot_id ที่สามารถจัดวิชา course_id ลงได้โดยไม่ชนและไม่เกิน 2 วิชา/วัน (Feasible Set J_c^k)
feasible_slots = graph.get_feasible_slots(course_id="C01", partial_schedule=partial_schedule)

# 4. คำนวณค่า Penalty ที่เพิ่มขึ้น (Delta P) หากวางวิชา course_id ลงใน slot_id นั้น
delta_p = graph.calculate_delta_penalty(course_id="C01", slot_id="D1_S1", partial_schedule=partial_schedule)

# 5. เมื่อจัดเสร็จครบทุกวิชา ส่งเข้า build_solve_response() เพื่อให้ Central Validator ตรวจและแพ็กเป็น SolveResponse
return build_solve_response(
    problem=problem,
    algorithm="aco",
    schedule_dict=best_schedule,       # Dict[course_id, slot_id] หรือ None ถ้าไม่พบคำตอบ
    runtime_ms=runtime_ms,
    attempts=total_attempts,
    parameters_used=params_dict,
    best_iteration=best_iter,
    history=history_points,
)
```

---

## 3. รายละเอียด API Endpoints ทั้งหมด

สามารถเปิดทดสอบผ่าน Swagger UI ได้ที่ `http://localhost:8000/docs`

### 3.1 `GET /instances`
คืนรายการชุดข้อมูลทั้งหมดในฐานข้อมูล:
```json
[
  {
    "instance_id": "demo_01",
    "name": "Demo 01 — ชุดข้อมูลสาธิตขนาดเล็ก (10 วิชา, 3 วัน / 6 ช่วงสอบ)",
    "seed": 42,
    "description": "...",
    "num_courses": 10,
    "num_students": 20,
    "num_enrollments": 50,
    "num_slots": 6,
    "num_days": 3
  }
]
```

### 3.2 `GET /instances/{instance_id}` และ `GET /instances/{instance_id}/graph`
- `GET /instances/{instance_id}`: คืนข้อมูลครบทุกฟิลด์ของชุดปัญหานั้น (`courses`, `students`, `enrollments`, `slots`)
- `GET /instances/{instance_id}/graph`: คืน `nodes` (พร้อม `degree` และ `student_count`) และ `edges` (`source`, `target`, `shared_students`) สำหรับให้ Frontend วาดกราฟความขัดแย้งทันที

### 3.3 `POST /solve`
รันอัลกอริทึม 1 วิธีบนชุดข้อมูลที่เลือก:

**Request Body:**
```json
{
  "instance_id": "demo_01",
  "algorithm": "aco",
  "parameters": {
    "seed": 42,
    "max_attempts": 400,
    "num_ants": 20,
    "iterations": 20,
    "alpha": 1.0,
    "beta": 2.0,
    "rho": 0.2,
    "q": 1.0,
    "initial_pheromone": 1.0
  }
}
```

**Response Body:**
```json
{
  "instance_id": "demo_01",
  "algorithm": "aco",
  "status": "success",
  "schedule": [
    {"course_id": "C01", "slot_id": "D1_S1"},
    {"course_id": "C02", "slot_id": "D1_S2"}
  ],
  "metrics": {
    "hard_conflict_count": 0,
    "consecutive_exam_pair_count": 2,
    "penalty_score": 2,
    "runtime_ms": 14.25,
    "attempts": 400,
    "best_iteration": 8
  },
  "parameters_used": {
    "seed": 42,
    "num_ants": 20,
    "iterations": 20,
    "alpha": 1.0,
    "beta": 2.0,
    "rho": 0.2,
    "q": 1.0,
    "initial_pheromone": 1.0
  },
  "history": [
    {"iteration": 1, "best_penalty": 5, "iteration_best_penalty": 5, "feasible_ants": 19},
    {"iteration": 2, "best_penalty": 3, "iteration_best_penalty": 3, "feasible_ants": 20}
  ],
  "validation_details": {
    "is_valid": true,
    "unassigned_courses": [],
    "duplicate_courses": [],
    "invalid_slots": [],
    "exceeded_daily_limit_students": [],
    "hard_conflicts": [],
    "consecutive_cases": [
      {
        "student_id": "S001",
        "day_index": 1,
        "morning_course_id": "C01",
        "afternoon_course_id": "C02"
      }
    ]
  },
  "message": null
}
```

### 3.4 `POST /compare`
รันเปรียบเทียบหลายอัลกอริทึมพร้อมกันหลาย Seed (`runs` รอบ โดยใช้ `seed = seed_start + i`):

**Request Body:**
```json
{
  "instance_id": "demo_01",
  "algorithms": ["greedy", "random_feasible", "aco"],
  "runs": 10,
  "seed_start": 100,
  "parameters": {
    "random_feasible": {"max_attempts": 400},
    "aco": {
      "num_ants": 20,
      "iterations": 20,
      "alpha": 1.0,
      "beta": 2.0,
      "rho": 0.2,
      "q": 1.0,
      "initial_pheromone": 1.0
    }
  }
}
```

**Response Body:**
คืนทั้ง `summaries` (ค่าสถิติ `success_rate`, `best_penalty`, `mean_penalty`, `median_penalty`, `std_penalty`, `mean_runtime_ms`, `best_run_schedule`, `best_run_history` แยกตามอัลกอริทึม) และ `raw_runs` (ผลลัพธ์รายรอบทั้งหมด) เพื่อให้ฝั่ง Frontend นำไปวาดกราฟเปรียบเทียบได้ทันที
