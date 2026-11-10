<p align="right">
  <b>🇬🇧 English</b> | <a href="05-way-of-work-backend.th.md">🇹🇭 ภาษาไทย</a>
</p>

# ⚙️ Backend Development Guidelines (Way of Work for Backend)

This guide is designed for the backend engineering team (**Person 1: Mai** and **Person 2: Fai**). It covers the `backend/` directory structure, API contracts, parameters, and how to utilize the central modules (`ConflictGraph` and `Central Validator`) so that all 3 algorithms integrate seamlessly.

> **Code Style Convention:** All Python code comments and docstrings across `backend/` are written in English without emojis.

---

## 1. Directory Structure (`backend/`)

```text
backend/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py                  # FastAPI App Entrypoint & Lifespan Auto-Seed
│   ├── config.py                # Environment variable loader (MONGO_URI, MONGO_DB_NAME)
│   ├── database.py              # Strict MongoDB access layer for `exam_instances` collection
│   ├── schemas/
│   │   └── models.py            # Central Pydantic schemas (frozen contract)
│   ├── core/
│   │   ├── graph.py             # [Shared] ConflictGraph helper for feasible slots & Delta P
│   │   └── validator.py         # [Shared] Independent schedule validator & evaluator
│   ├── algorithms/
│   │   ├── base.py              # [Shared] build_solve_response helper
│   │   ├── greedy.py            # [Person 2: Fai] Greedy baseline implementation
│   │   ├── random_feasible.py   # [Person 1: Mai] Random Feasible implementation
│   │   └── aco.py               # [Person 1: Mai] Ant Colony Optimization implementation
│   └── routers/
│       ├── instances.py         # GET /instances, GET /instances/{id}, GET /instances/{id}/graph, POST /instances/seed
│       └── solver.py            # POST /solve, POST /compare
└── scripts/
    └── seed_db.py               # [Person 2: Fai] Programmatic dataset generator & MongoDB seeder script
```

---

## 2. Using Central Helpers (`ConflictGraph` & `build_solve_response`)

To guarantee 100% evaluation parity across **Greedy**, **Random Feasible**, and **ACO**, all algorithms must leverage `ConflictGraph` from `app.core.graph`:

```python
from app.core.graph import ConflictGraph
from app.algorithms.base import build_solve_response

graph = ConflictGraph(problem)

# 1. Get courses sorted by conflict degree descending (degree first, tie-break by course_id)
ordered_courses = graph.get_ordered_courses()

# 2. Track assignments in a dictionary: Dict[str, str] (course_id -> slot_id)
partial_schedule = {}

# 3. Retrieve all slots that satisfy hard constraints (no conflict, <= 2 exams/day)
feasible_slots = graph.get_feasible_slots(course_id="C01", partial_schedule=partial_schedule)

# 4. Calculate incremental soft penalty (Delta P) for placing a course in a given slot
delta_p = graph.calculate_delta_penalty(course_id="C01", slot_id="D1_S1", partial_schedule=partial_schedule)

# 5. Build standardized, validated response via Central Validator
return build_solve_response(
    problem=problem,
    algorithm="aco",
    schedule_dict=best_schedule,       # Dict[course_id, slot_id] or None if unfeasible
    runtime_ms=runtime_ms,
    attempts=total_attempts,
    parameters_used=params_dict,
    best_iteration=best_iter,
    history=history_points,
)
```

---

## 3. API Endpoints Reference

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 3.1 `GET /instances`
Returns a summary of all problem instances stored in MongoDB:
```json
[
  {
    "instance_id": "demo_01",
    "name": "Demo 01 — Small Benchmark Dataset (10 Courses, 3 Days / 6 Slots)",
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

### 3.2 `GET /instances/{instance_id}`, `GET /instances/{instance_id}/graph` & `POST /instances/seed`
- `GET /instances/{instance_id}`: Full problem instance data (`courses`, `students`, `enrollments`, `slots`).
- `GET /instances/{instance_id}/graph`: Precomputed graph payload with `nodes` (degrees, enrollments) and `edges` (shared students) for frontend visualization.
- `POST /instances/seed`: Triggers programmatic dataset seeding/re-seeding into MongoDB via `scripts.seed_db.seed_all_instances()`.

### 3.3 `POST /solve`
Executes a single algorithm run on a dataset instance:

**Request Body:**
```json
{
  "instance_id": "demo_01",
  "algorithm": "aco",
  "parameters": {
    "seed": 42,
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

### 3.4 `POST /compare`
Executes multi-seed benchmarking across algorithms (`runs` repetitions with `seed = seed_start + i`):

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
      "rho": 0.2
    }
  }
}
```

**Response Body:**
Returns both `summaries` (aggregated metrics: `success_rate`, `best_penalty`, `mean_penalty`, `median_penalty`, `std_penalty`, `mean_runtime_ms`, `best_run_schedule`, `best_run_history`) and `raw_runs` (all individual run outputs) ready for plotting.
