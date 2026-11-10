<p align="right">
  <b>🇬🇧 English</b> | <a href="01-task-mai-aco.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 👩‍💻 Person 1 Guide: Sippapas Chavanont (Mai) — 6630333721

> **Course:** AI2 (2110477)  
> **Assignee:** 6630333721 Sippapas Chavanont (Mai)  
> **Role:** Core Optimization Developer  
> **Primary Files:**  
> 1. [`backend/app/algorithms/aco.py`](../../backend/app/algorithms/aco.py)  
> 2. [`backend/app/algorithms/random_feasible.py`](../../backend/app/algorithms/random_feasible.py)  
> 3. [`backend/app/routers/solver.py`](../../backend/app/routers/solver.py) *(Router structure ready; customize if needed)*

---

## 1. Action Checklist for Mai

- [ ] **Task 1: Review Shared Core Modules (`ConflictGraph` & `Central Validator`)**
  - Inspect [`backend/app/core/graph.py`](../../backend/app/core/graph.py) and [`backend/app/core/validator.py`](../../backend/app/core/validator.py), which are fully implemented according to your `01-project-idea-spec.md` specification.
- [ ] **Task 2: Implement `Random Feasible` in `backend/app/algorithms/random_feasible.py`**
  - Replace the `# TODO [Person 1 - Mai]:` stub (and remove the `[STUB]` response message) with a loop running up to `params.max_attempts` candidate schedule attempts:
    1. For each attempt, iterate through `ordered_courses = graph.get_ordered_courses()`. For each course, retrieve `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)` and randomly select a slot using `rng.choice(feasible_slots)`.
    2. If any course has no feasible slots (dead-end), discard the candidate and begin the next attempt immediately.
    3. If all courses are successfully assigned, compute the total penalty score and track the best schedule found (`best_schedule`), recording `best_iteration` and `history`.
- [ ] **Task 3: Implement `ACO` in `backend/app/algorithms/aco.py`**
  - Replace the `# TODO [Person 1 - Mai]:` stub (and remove the `[STUB]` response message) with the full Ant System algorithm based on [`docs/02-aco-theory-and-mapping.md`](../02-aco-theory-and-mapping.md):
    1. Initialize the pheromone matrix: `tau[course_id][slot_id] = params.initial_pheromone`.
    2. Loop through `iteration = 1 .. params.iterations`. In each iteration, launch `params.num_ants` ants. Each ant assigns slots to courses following `ordered_courses = graph.get_ordered_courses()`.
    3. For each assignment decision on course $c$ from `feasible_slots`:
       - Calculate $\Delta P = \text{graph.calculate\_delta\_penalty}(c, t, \text{partial\_schedule})$.
       - Compute heuristic visibility $\eta(c, t) = \frac{1.0}{1.0 + \Delta P}$.
       - Compute decision weight $w(c, t) = (\tau[c][t])^\alpha \times (\eta(c, t))^\beta$.
       - Select `slot_id` with probability proportional to $w(c, t)$ using `rng.choices(feasible_slots, weights=weights, k=1)[0]`.
    4. Once all ants complete their schedules in the iteration:
       - Evaluate penalty score $P_k$ for each successful ant.
       - Update `global_best_schedule` and `global_best_penalty`.
       - **Evaporation:** Decay all pheromone values: $\tau[c][t] \leftarrow (1 - \rho) \cdot \tau[c][t]$.
       - **Deposit:** For each valid ant, deposit $\Delta\tau = \frac{Q}{1.0 + P_k}$ onto the visited $(c, \text{assigned\_slot})$ pairs (optionally reinforce with an elitist bonus for `global_best_schedule`).
       - Record `IterationHistoryPoint(iteration=it, best_penalty=global_best_penalty, iteration_best_penalty=iter_best, feasible_ants=valid_count)` in `history`.

---

## 2. Git Workflow & Feature Branch

Before writing code, pull the latest `main` branch and create your dedicated feature branch:

```bash
git checkout main
git pull origin main
git checkout -b feat/aco-random-solvers
```

When committing changes, use Conventional Commits (e.g., `feat(aco): implement transition probability and pheromone update`).

---

## 3. Running and Testing

```bash
# Run via Docker
docker compose up --build

# Or test the /solve endpoints for ACO and Random Feasible at:
# http://localhost:8000/docs
```

---

## 4. Working with an AI Agent (Context Files & Prompt Template)

When using Cursor, Antigravity, or Claude Code, reference these files in this exact order:

### Files to `@` for Context
1. `@docs/01-project-idea-spec.md` (Specification & API contract)
2. `@docs/02-aco-theory-and-mapping.md` (ACO equations from course slides)
3. `@backend/app/core/graph.py` & `@backend/app/core/validator.py` (Core helpers)
4. `@backend/app/algorithms/base.py` (Response builder)
5. `@backend/app/algorithms/random_feasible.py` & `@backend/app/algorithms/aco.py` (Target files)

### 📋 Ready-to-Use Prompt Template

```text
I am Sippapas Chavanont (Mai, 6630333721) responsible for implementing the Random Feasible and Ant Colony Optimization (ACO) algorithms for ExamAnt in course AI2 (2110477).

Before writing code, review these files in order:
1. @docs/01-project-idea-spec.md (Sections 4, 5, 6, 7.2, and 7.3)
2. @docs/02-aco-theory-and-mapping.md (Transition Rule, Evaporation, and Pheromone Deposit equations from course slides)
3. @backend/app/core/graph.py and @backend/app/core/validator.py (ConflictGraph and Central Validator)
4. @backend/app/algorithms/base.py

Tasks:
1. In @backend/app/algorithms/random_feasible.py, replace the `# TODO [Person 1 - Mai]:` stub with a complete Random Feasible implementation:
   - Use `random.Random(params.seed)` for reproducibility.
   - Loop up to `params.max_attempts` times, assigning slots from `graph.get_feasible_slots(...)`.
   - On dead-ends, restart the attempt; on success, record the lowest penalty schedule and history, returning via `build_solve_response(...)` (with `message=None`).
2. In @backend/app/algorithms/aco.py, replace the `# TODO [Person 1 - Mai]:` stub with a complete ACO Ant System implementation:
   - Maintain a 2D pheromone matrix `tau[course_id][slot_id]` initialized to `params.initial_pheromone`.
   - Compute heuristic visibility `eta(c, t) = 1.0 / (1.0 + delta_p)` from `graph.calculate_delta_penalty(...)`.
   - Select slots proportionally to `(tau ** params.alpha) * (eta ** params.beta)`.
   - After each iteration, apply evaporation `(1 - params.rho)` and deposit `params.q / (1.0 + penalty)` for valid schedules.
   - Log `IterationHistoryPoint` for each iteration into `history` and return via `build_solve_response(...)` (with `message=None`).
3. Write all code comments and docstrings in clear English without emojis.
4. Verify against `demo_01` to ensure `status == "success"` and `hard_conflict_count == 0`.
```
