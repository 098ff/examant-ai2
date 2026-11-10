<p align="right">
  <b>🇬🇧 English</b> | <a href="00-idea-proposal.th.md">🇹🇭 ภาษาไทย</a>
</p>

# ExamAnt — Conflict-Free Examination Timetabling with Reduced Consecutive Exams using Ant Colony Optimization

> **Course:** AI2 (2110477)  
> **Category:** Apply Algorithm / Proof of Concept  
> **Course Topics:** Ant Colony Optimization (ACO), Constraint Satisfaction Problem (CSP), Graph Coloring  
> **Team Members:**  
> 1. 6631305321 Chanatda Konchom (Fai)  
> 2. 6632213421 Sasarose Buranapin (Rose)  
> 3. 6630333721 Sippapas Chavanont (Mai)  
> **Scope:** Group of 3 students, total budget <= 24 person-hours, video <= 10 minutes  
> **Data:** Fully simulated synthetic courses and student enrollments (no real student data used)

---

## 1. Project Concept (Elevator Pitch)

During examination periods, university scheduling is far more than just fitting courses into empty slots. If a student is taking both Artificial Intelligence and Discrete Mathematics, and both exams are assigned to Monday morning, it is physically impossible for that student to take both exams simultaneously—no matter how many exam halls are available. Even if there are no direct time conflicts, having three exams scheduled back-to-back on the same day causes extreme student fatigue.

**ExamAnt** applies **Ant Colony Optimization (ACO)** to solve this scheduling challenge: each virtual ant constructs a complete timetable by assigning courses to exam slots one by one. Ants are forbidden from placing conflicting courses in the same slot. Then, candidate timetables are evaluated on how well they reduce back-to-back exams for enrolled students. Over multiple iterations, the ant colony learns from high-performing timetables through pheromone trails.

**Core Research Question:** Given a fixed number of exam slots, can ACO reliably generate conflict-free exam timetables that achieve significantly fewer consecutive exam occurrences than Greedy heuristics or Random search?

---

## 2. Problem Formulation

- **Inputs:** List of courses, simulated student enrollment records per course, and predefined exam time slots.
- **Outputs:** An assigned time slot for every course along with comprehensive schedule quality metrics.
- **Hard Constraints:**
  1. A student must not have two conflicting exams scheduled in the exact same time slot.
  2. A student must not have more than 2 exams on the same day (naturally enforced by 2 slots/day).
- **Soft Objective:** After guaranteeing 0 hard conflicts, minimize the number of occurrences where a student has two exams in consecutive slots on the same day (morning and afternoon).
- **MVP Scope:** Optimizes slot assignments only; physical room capacities, proctors, and personal student preferences are excluded.

---

## 3. Why ACO Fits This Problem

This problem can be mathematically framed as **Graph Coloring**:
- Each course represents a **node (vertex)**.
- An **edge** is drawn between two courses if at least one student is enrolled in both.
- Each **color** corresponds to an exam time slot.
- Any two adjacent nodes connected by an edge must receive different colors (Hard Constraint).
- Among multiple valid colorings, we seek the one that minimizes consecutive morning-afternoon exam pairs (Soft Objective).

In ACO, each ant constructs a complete schedule incrementally by assigning an exam slot to each course sequentially, choosing only from valid (conflict-free) slots. Decisions that minimize consecutive exam penalties and have accumulated strong pheromone trails have a higher probability of being chosen.

---

## 4. Simulated Dataset Design

We start with small-to-medium benchmark instances: **10–15 courses, 20–80 students, and 6–8 exam slots** (e.g., 3 days with 2 slots per day: morning and afternoon), where each student enrolls in 2–3 courses.

Example enrollment structure:
```csv
student_id,course_id
S001,C01
S001,C02
S002,C01
S002,C04
S003,C02
```

To guarantee that a conflict-free solution exists (solvability), datasets are generated using a planted coloring technique before adding students.

---

## 5. Schedule Evaluation & Scoring Rules

Let $T(c)$ be the assigned time slot of course $c$, and $C(a, b)$ be the count of shared students between courses $a$ and $b$:

1. **Hard Conflict Count:** Total occurrences of shared students taking exams in the same slot. **Must be 0** for any accepted schedule.
2. **Consecutive Exam Penalty ($P$):** Total count of `(student, day)` pairs having exams in both the morning and afternoon slots of the same day. Lower is better.

> **Evaluation Rule:** Among schedules with 0 hard conflicts using the same number of exam slots, the schedule with the lowest penalty score $P$ wins. Hard conflicts can never be traded off for lower $P$.

---

## 6. Simplified ACO Algorithm for the Project Scope

1. Sort courses by conflict degree descending (courses with the most conflicts are scheduled first).
2. Each ant initializes an empty schedule and assigns slots sequentially, selecting only from slots that do not violate hard constraints.
3. Let $\tau(c, t)$ be the pheromone intensity for assigning course $c$ to slot $t$, and let $\eta(c, t) = \frac{1}{1 + \Delta P}$ be the heuristic visibility, where $\Delta P$ is the incremental consecutive exam penalty incurred.
4. Select feasible slots probabilistically proportional to $[\tau(c, t)]^\alpha \times [\eta(c, t)]^\beta$.
5. If an ant reaches a dead-end (no feasible slot), the attempt is marked as failed.
6. After all ants in an iteration finish, apply pheromone evaporation ($\rho$) to all pairs, and deposit new pheromone proportional to $\frac{Q}{1 + P}$ for valid schedules.

---

## 7. Comparative Baselines

| Algorithm | Mechanism | Purpose of Comparison |
| :--- | :--- | :--- |
| **Greedy** | Sorts courses by conflict degree and greedily assigns the slot with minimum $\Delta P$. | Standard deterministic heuristic baseline that finds conflict-free schedules rapidly. |
| **Random Feasible** | Stochastically selects from valid slots; restarts if a dead-end is encountered. | Evaluates whether pheromone-guided learning outperforms random search within the same budget. |
| **ACO** | Probabilistic selection balancing learned pheromone trails and local heuristic visibility. | Proposed core algorithm of the project. |

---

## 8. Visualizations & 10-Minute Video Storyline

1. **Introduction:** Real-world exam scheduling conflict (student enrolled in AI and Math scheduled simultaneously).
2. **Problem Representation:** Visualizing the **Course Conflict Graph** where edges indicate shared students.
3. **Algorithm Animation:** Showing ants building schedules and pheromone reinforcement.
4. **Final Results:** Side-by-side comparison of **Greedy vs Random Feasible vs ACO** with colored timetable grids and convergence curves.

---

## 9. Work Breakdown (24 Person-Hours Total)

| Task | Estimated Person-Hours | Assignee |
| :--- | :---: | :--- |
| Project Spec + Synthetic Dataset Generator & MongoDB Seeder | 4 | Person 2 (Fai) |
| Central Validator + Greedy Baseline | 4 | Person 2 (Fai) |
| Random Feasible + ACO Implementation | 6 | Person 1 (Mai) |
| Multi-Seed Benchmarking + Streamlit Visualization & Charts | 5 | Person 3 (Rose) |
| Video Script, Recording, and Final Presentation | 5 | All Members |
| **Total** | **24** | |

---

## 10. Honest Discussion & Caveats

- Penalty $P$ models student convenience but does not capture all complex university constraints (proctor limits, special needs).
- On very small or loosely constrained datasets, Greedy may already find an optimal schedule ($P=0$), making ACO's additional runtime less impactful.
- All candidate schedules must be verified by an independent Central Validator separate from the optimization algorithms.
