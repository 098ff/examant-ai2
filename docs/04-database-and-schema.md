<p align="right">
  <b>🇬🇧 English</b> | <a href="04-database-and-schema.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 🍃 MongoDB Setup & Data Schema Specification

This document details the **MongoDB** database setup, the schema of the `exam_instances` collection, and how problem instances are transformed into input structures for algorithms according to `docs/01-project-idea-spec.md`.

---

## 1. Running and Connecting to MongoDB

MongoDB runs automatically inside a Docker container (`mongo:7.0`) via Docker Compose.

### 1.1 Starting MongoDB
```bash
# Start MongoDB only (when running Python scripts locally)
docker compose up -d mongodb

# Or start the entire stack (MongoDB + Backend + Frontend)
docker compose up --build
```

### 1.2 Inspecting Data with MongoDB Compass (GUI)
1. Open **MongoDB Compass** (or MongoDB extension in VS Code / Antigravity).
2. Connect using the mapped host port **`27018`**:
   ```text
   mongodb://localhost:27018
   ```
3. Open database **`examant_db`** $\rightarrow$ collection **`exam_instances`**.

### 1.3 Inspecting Data via Terminal CLI
```bash
docker compose exec mongodb mongosh examant_db --eval "db.exam_instances.find({}, {instance_id: 1, name: 1, _id: 0}).pretty()"
```

---

## 2. Collection Schema (`exam_instances`)

To fetch a complete scheduling problem in a single query without complex multi-table joins, each dataset is stored as an **Embedded Document** (`ExamInstanceDocument`):

```json
{
  "instance_id": "demo_01",
  "name": "Demo 01 — Small Benchmark Dataset (10 Courses, 3 Days / 6 Slots)",
  "seed": 42,
  "description": "Initial 10-course, 20-student benchmark across 3 days (6 slots: morning & afternoon).",
  "courses": [
    {
      "course_id": "C01",
      "course_name": "Artificial Intelligence II",
      "student_count": 7
    }
  ],
  "students": [
    {
      "student_id": "S001"
    }
  ],
  "enrollments": [
    {
      "student_id": "S001",
      "course_id": "C01"
    },
    {
      "student_id": "S001",
      "course_id": "C02"
    }
  ],
  "slots": [
    {
      "slot_id": "D1_S1",
      "day_index": 1,
      "slot_index": 1,
      "label": "Day 1 Morning"
    },
    {
      "slot_id": "D1_S2",
      "day_index": 1,
      "slot_index": 2,
      "label": "Day 1 Afternoon"
    }
  ]
}
```

### Data Integrity Rules
1. `instance_id` is unique across the collection (enforced by a unique MongoDB index).
2. Each exam day (`day_index = 1..D`) must have exactly **2 slots**: `slot_index = 1` (Morning) and `slot_index = 2` (Afternoon), totaling $2D$ slots.
3. Every enrollment must reference valid `student_id` and `course_id` records in the instance, with no duplicate pairs.

---

## 3. Transformation to Algorithm Input (`ProblemData`)

Solvers (`greedy.py`, `random_feasible.py`, `aco.py`) do not connect directly to MongoDB. The API router fetches `ExamInstanceDocument` from `app.database` and calls `.to_problem_data()` to generate a clean `ProblemData` payload:

```json
{
  "instance_id": "demo_01",
  "courses": ["C01", "C02", "C03"],
  "students": ["S001", "S002"],
  "enrollments": [
    {"student_id": "S001", "course_id": "C01"},
    {"student_id": "S001", "course_id": "C02"}
  ],
  "slots": [
    {"slot_id": "D1_S1", "day_index": 1, "slot_index": 1, "label": "Day 1 Morning"},
    {"slot_id": "D1_S2", "day_index": 1, "slot_index": 2, "label": "Day 1 Afternoon"}
  ]
}
```

---

## 4. Seeding Datasets into MongoDB

> [!IMPORTANT]
> **Strict MongoDB Requirement:** The project enforces true MongoDB persistence (no static mock JSON fallback). Ensure the MongoDB container is running via `docker compose up -d mongodb`. Data is stored in Docker volume `mongo_data` and persists across container restarts.

1. **Auto-Seed on Startup:**  
   When launching the backend container, if `exam_instances` is empty, programmatic datasets defined in [`backend/scripts/seed_db.py`](../backend/scripts/seed_db.py) are seeded automatically.
2. **Manual Seeding (Person 2 - Fai):**
   ```bash
   # Run directly via Python / Docker
   docker compose exec backend python -m scripts.seed_db

   # Or trigger via HTTP endpoint
   curl -X POST http://localhost:8000/instances/seed
   ```
3. **Frontend UI Seeding:**
   On the Streamlit dashboard, click the **"Seed Database ตอนนี้"** / **"Seed Database"** button (`:material/database:`) when the database is empty, or use **"Re-seed Datasets เข้า MongoDB"** (`:material/refresh:`) inside the Sidebar's **Database Tools** (`:material/build:`) expander to populate or refresh datasets.
