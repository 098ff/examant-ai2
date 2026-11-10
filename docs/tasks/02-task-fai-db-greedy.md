<p align="right">
  <b>🇬🇧 English</b> | <a href="02-task-fai-db-greedy.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 👩‍💻 Person 2 Guide: Chanatda Konchom (Fai) — 6631305321

> **Course:** AI2 (2110477)  
> **Assignee:** 6631305321 Chanatda Konchom (Fai)  
> **Role:** Infrastructure, Data Engineering & Greedy Baseline Developer  
> **Primary Files:**  
> 1. [`backend/scripts/seed_db.py`](../../backend/scripts/seed_db.py) (Programmatic generator & MongoDB seeder)  
> 2. [`backend/app/algorithms/greedy.py`](../../backend/app/algorithms/greedy.py)  
> 3. [`docker-compose.yml`](../../docker-compose.yml) & [`backend/app/database.py`](../../backend/app/database.py) *(Already configured)*

---

## 1. Action Checklist for Fai

- [x] **Task 1: Setup Repository, Docker Compose & MongoDB Connection** *(Completed in initial scaffolding)*
- [ ] **Task 2: Implement `Greedy` Baseline in `backend/app/algorithms/greedy.py`**
  - Replace the `# TODO [คนที่ 2 - ฝ้าย]` stub with the full Greedy logic as specified in `docs/01-project-idea-spec.md` (Section 7.1):
    1. Sort courses by conflict degree descending: `ordered_courses = graph.get_ordered_courses()`.
    2. For each course, fetch non-conflicting time slots: `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`.
    3. If `feasible_slots` is empty, return `no_solution_found` (`partial_schedule = None`).
    4. Otherwise, compute `delta_p = graph.calculate_delta_penalty(course_id, slot_id, partial_schedule)` for each candidate slot and pick the slot with **minimum $\Delta P$** (tie-break by slot chronological order).
- [ ] **Task 3: Create Synthetic Dataset Generator (3 Difficulty Levels) & Seed MongoDB in `backend/scripts/seed_db.py`**
  - Following `docs/00-idea-proposal.md` (Section 4) and `docs/01-project-idea-spec.md` (Section 3):
    - Generate at least 3 benchmark datasets:
      1. `easy_01` (or `demo_01`): ~10 courses, 40–50 students, 3 days (6 slots: morning & afternoon).
      2. `medium_01`: ~12 courses, 60–80 students, 3 days (6 slots) with higher enrollment density.
      3. `hard_01`: ~14–15 courses, 80–100 students, 3–4 days (6–8 slots) where Greedy is prone to higher penalties, giving ACO room to demonstrate superior optimization.
    - **Planted Feasible Coloring Technique (to guarantee solvability):**
      1. Partition courses into $2D$ slot groups upfront.
      2. When generating student enrollments (2–3 courses per student), sample courses from **distinct slot groups** to guarantee at least one valid schedule with `hard_conflict_count == 0`.
      3. Upsert datasets directly into MongoDB via `seed_db.py` or `POST /instances/seed`. No static mock JSON file is used.

---

## 2. Git Workflow & Feature Branch

Before writing code, pull the latest `main` branch and create your dedicated feature branch:

```bash
git checkout main
git pull origin main
git checkout -b feat/dataset-seeder-greedy
```

When committing changes, use Conventional Commits (e.g., `feat(dataset): implement synthetic instances generator`).

---

## 3. Running and Testing

```bash
# 1. Start system via Docker Compose
docker compose up --build -d

# 2. Run database seeder script
docker compose exec backend python -m scripts.seed_db

# 3. Verify data insertion in MongoDB
docker compose exec mongodb mongosh examant_db --eval "db.exam_instances.find({}, {instance_id: 1, name: 1, _id: 0}).pretty()"
```

---

## 4. Working with an AI Agent (Context Files & Prompt Template)

### Files to `@` for Context
1. `@docs/00-idea-proposal.md` & `@docs/01-project-idea-spec.md` (Sections 3, 4, 7.1)
2. `@docs/04-database-and-schema.md` (MongoDB `exam_instances` structure)
3. `@backend/app/core/graph.py` & `@backend/app/core/validator.py`
4. `@backend/app/algorithms/greedy.py` & `@backend/scripts/seed_db.py`

### 📋 Ready-to-Use Prompt Template

```text
I am Chanatda Konchom (Fai, 6631305321) responsible for generating synthetic datasets, seeding MongoDB, and implementing the Greedy baseline algorithm for ExamAnt in course AI2 (2110477).

Before writing code, review these files in order:
1. @docs/01-project-idea-spec.md (Section 3 on Data Schema and Section 7.1 on Greedy Behavior)
2. @docs/04-database-and-schema.md
3. @backend/app/core/graph.py and @backend/app/core/validator.py
4. @backend/app/algorithms/greedy.py and @backend/scripts/seed_db.py

Tasks:
1. In @backend/app/algorithms/greedy.py, complete the Greedy baseline algorithm according to Spec 7.1:
   - Order courses via `graph.get_ordered_courses()`.
   - For each course, fetch `feasible_slots = graph.get_feasible_slots(...)`.
   - Select the slot that minimizes `graph.calculate_delta_penalty(...)` (tie-break by slot order).
   - Return clean result via `build_solve_response(...)`.
2. In @backend/scripts/seed_db.py, generate 3 synthetic benchmark instances (`easy_01`, `medium_01`, `hard_01`) in addition to `demo_01`:
   - Use the Planted Feasible Assignment technique during enrollment generation so every dataset is mathematically proven to have a zero-conflict solution.
   - Validate each dataset with `validate_problem_input` and test run `solve_greedy` before upserting into MongoDB.
```
