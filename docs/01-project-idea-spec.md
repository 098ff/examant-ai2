<p align="right">
  <b>🇬🇧 English</b> | <a href="01-project-idea-spec.th.md">🇹🇭 ภาษาไทย</a>
</p>

# ExamAnt — Project Technical Specification (v3)

> **Course:** AI2 (2110477)  
> **Team Members:**  
> 1. 6631305321 Chanatda Konchom (Fai)  
> 2. 6632213421 Sasarose Buranapin (Rose)  
> 3. 6630333721 Sippapas Chavanont (Mai)  
>  
> This specification defines the problem formulation, data schema, algorithm API contracts, parameters, and evaluation rules for ExamAnt so that the backend, frontend, and benchmarking workflows operate under a unified contract.

---

## 1. Project Overview

**ExamAnt** is an experimental project applying Ant Colony Optimization (ACO) to schedule university courses into predefined examination time slots using synthetic student enrollment data.

The problem features two constraint tiers:
- **Hard Constraints (Mandatory):**
  1. A student must not have more than one course scheduled in the exact same exam time slot.
  2. A student must not have more than 2 exams on the same day.
- **Soft Objective (Minimization Target):**
  Once hard constraints are fully satisfied (0 conflicts), minimize the count of `(student, day)` occurrences where a student must take exams in both the morning and afternoon slots of the same day.

The system benchmarks three algorithms—**Greedy**, **Random Feasible**, and **ACO**—on identical problem instances, slot counts, and search budgets to compare schedule quality, solvability, and computational runtime.

---

## 2. Problem Formulation and Rules

Let $C$ be the set of courses, $S$ be the set of simulated students, and $T$ be the set of exam slots. An algorithm assigns exactly one slot $t \in T$ to each course $c \in C$.

- Two courses **conflict** if at least one student is enrolled in both. Conflicting courses must never share the same slot.
- Each examination day contains exactly **2 slots**:
  - `slot_index = 1`: Morning session
  - `slot_index = 2`: Afternoon session
- Because each day has only 2 slots and same-slot conflicts are forbidden, no student can ever take more than 2 exams in one day.
- **Consecutive Exam Definition:** A student taking exams in both the morning and afternoon of the same day incurs a **penalty of 1** for that `(student, day)`. Taking only a morning or only an afternoon exam incurs 0 penalty. Consecutive slots across different days (e.g., Day 1 afternoon and Day 2 morning) incur 0 penalty.

---

## 3. Dataset Schema

Data is stored as an embedded document inside the `exam_instances` MongoDB collection.

### 3.1 ExamInstance — Problem Instance Root
| Field | Type | Description |
| :--- | :--- | :--- |
| `instance_id` | string | Unique instance identifier, e.g., `demo_01` |
| `name` | string | Display name of the dataset |
| `seed` | integer | Random seed used during data generation |
| `description` | string | Dataset description and characteristics |

### 3.2 Course
| Field | Type | Description |
| :--- | :--- | :--- |
| `course_id` | string | Unique course code, e.g., `C01` |
| `course_name` | string | Display course title |
| `student_count` | integer (optional) | Number of enrolled students |

### 3.3 Student
| Field | Type | Description |
| :--- | :--- | :--- |
| `student_id` | string | Unique simulated student ID, e.g., `S001` |

### 3.4 Enrollment
| Field | Type | Description |
| :--- | :--- | :--- |
| `student_id` | string | Reference to `Student.student_id` |
| `course_id` | string | Reference to `Course.course_id` |

### 3.5 ExamSlot
| Field | Type | Description |
| :--- | :--- | :--- |
| `slot_id` | string | Unique slot ID, e.g., `D1_S1` |
| `day_index` | integer | Day number starting at 1 |
| `slot_index` | integer enum: 1, 2 | 1 = Morning, 2 = Afternoon |
| `label` | string | Display label, e.g., `Day 1 Morning` |

### 3.6 Standardized Algorithm Input (`ProblemData`)
The backend transforms an instance into this standardized format passed identically to all algorithms:
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

## 4. Algorithm & API Contract

### 4.1 Standard Request (`POST /solve`)
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
    "rho": 0.2
  }
}
```

### 4.2 Standard Response (`POST /solve`)
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
    "consecutive_exam_pair_count": 1,
    "penalty_score": 1,
    "runtime_ms": 12.4,
    "attempts": 400,
    "best_iteration": 14
  },
  "parameters_used": {"seed": 42},
  "history": [
    {"iteration": 1, "best_penalty": 5, "iteration_best_penalty": 5, "feasible_ants": 18}
  ],
  "validation_details": {
    "is_valid": true,
    "unassigned_courses": [],
    "hard_conflicts": [],
    "consecutive_cases": [
      {"student_id": "S001", "day_index": 1, "morning_course_id": "C01", "afternoon_course_id": "C02"}
    ]
  },
  "message": null
}
```

### 4.3 Independent Central Validator
All candidate schedules must be verified by `app.core.validator.validate_and_score_schedule` to independently recalculate hard conflicts, daily limits, and soft penalty scores.

---

## 5. Tunable Parameters

| Parameter | Type / Default | Scope | Meaning |
| :--- | :---: | :--- | :--- |
| `seed` | integer (`42`) | All algorithms | Random seed for exact reproducibility |
| `max_attempts` | integer (`400`) | Random Feasible | Maximum candidate schedule attempts |
| `runs` | integer (`10`) | Benchmark | Multi-seed benchmark runs |
| `num_ants` | integer (`20`) | ACO | Virtual ants per iteration |
| `iterations` | integer (`20`) | ACO | Optimization rounds |
| `alpha` ($\alpha$) | float (`1.0`) | ACO | Pheromone importance weight |
| `beta` ($\beta$) | float (`2.0`) | ACO | Heuristic visibility weight |
| `rho` ($\rho$) | float (`0.2`) | ACO | Pheromone evaporation rate |
| `q` ($Q$) | float (`1.0`) | ACO | Pheromone deposit scaling constant |
| `initial_pheromone` | float (`1.0`) | ACO | Base pheromone level $\tau_0$ |

> **Fair Comparison Guideline:** The search budget for Random Feasible (`max_attempts`) should equal `num_ants × iterations` of ACO.

---

## 6. Scoring and Ranking Hierarchy

1. **Validity First:** `hard_conflict_count == 0` and full course assignment are strictly required. Schedules with conflicts are rejected.
2. **Penalty Score ($P$):** Among valid schedules, lower `penalty_score` wins.
3. **Runtime:** Used as secondary performance context.

---

## 7. Algorithm Behaviors

### 7.1 Greedy
1. Sort courses by conflict degree descending (tie-break by `course_id`).
2. For each course, identify feasible slots using `ConflictGraph.get_feasible_slots()`.
3. Pick the slot that yields the minimum incremental penalty $\Delta P$ (tie-break by chronological slot order).
4. Return `no_solution_found` if no feasible slot exists.

### 7.2 Random Feasible
1. Attempt to construct a complete schedule up to `max_attempts` times.
2. For each course in order, randomly choose a slot from feasible slots.
3. If an ant hits a dead-end, discard the attempt.
4. Record and return the valid schedule with the lowest penalty $P$.

### 7.3 Ant Colony Optimization (ACO)
1. Initialize pheromone matrix $\tau[course][slot] = \tau_0$.
2. In each iteration, $m$ ants construct complete schedules sequentially.
3. Transition probability for slot $t \in \text{Feasible}$:
   $$p(c, t) \propto [\tau(c, t)]^\alpha \times \left[\frac{1}{1 + \Delta P(c, t)}\right]^\beta$$
4. Evaporate pheromone $\tau \leftarrow (1 - \rho)\tau$.
5. Deposit pheromone $\Delta\tau = \frac{Q}{1 + P_k}$ for successful ants.
6. Track convergence across iterations in `history`.

---

## 8. API Specification

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/instances` | List dataset summaries |
| `GET` | `/instances/{instance_id}` | Fetch full problem instance |
| `GET` | `/instances/{instance_id}/graph` | Fetch precomputed conflict graph |
| `POST` | `/solve` | Run a single solver |
| `POST` | `/compare` | Run multi-seed benchmark comparing Greedy, Random, and ACO |
| `POST` | `/instances/seed` | Trigger database seeding |
