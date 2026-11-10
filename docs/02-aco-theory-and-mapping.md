<p align="right">
  <b>🇬🇧 English</b> | <a href="02-aco-theory-and-mapping.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 🐜 ACO Theory from Course Slides (`AI2 Slide.pdf`) & Domain Mapping in ExamAnt

> **Course:** AI2 (2110477)  
> **Team Members:**  
> 1. 6631305321 Chanatda Konchom (Fai)  
> 2. 6632213421 Sasarose Buranapin (Rose)  
> 3. 6630333721 Sippapas Chavanont (Mai)  
>  
> This document summarizes core theoretical concepts from the AI2 (2110477) course slides (**Swarm Intelligence: From Natural to Artificial Systems — Bonabeau, Dorigo, Theraulaz**) and maps every mathematical equation directly to the **ExamAnt** codebase.

---

## 1. Foundational Concepts from Lecture Slides (Slides 1–17)

1. **Swarm Intelligence (SI) (Slide 2):**
   - The collective behavior of decentralized, self-organized agents (virtual ants) interacting locally with their environment, producing coherent global problem-solving patterns without centralized control.
2. **Stigmergy (Slides 4–9):**
   - Indirect communication mediated by modifications to environmental states (e.g., depositing chemical **pheromone trails**). Other ants perceive these local marks, influencing their future probabilistic decisions.
3. **Positive vs. Negative Feedback (Slides 11, 17):**
   - **Positive Feedback:** High-quality timetables (low penalty $P$) receive larger pheromone reinforcement, guiding subsequent ants toward promising course-slot assignments.
   - **Negative Feedback (Pheromone Evaporation):** Evaporation at rate $\rho$ prevents premature convergence to suboptimal local minima and maintains exploration diversity.

---

## 2. Mapping Ant System (AS) & AS-QAP to Exam Timetabling (Slides 18–35)

The lecture notes illustrate Ant System applied to the **Traveling Salesperson Problem (TSP, Slides 18–22)**, the **Quadratic Assignment Problem (AS-QAP, Slides 28–30)**, and mention applications in **Job-scheduling** and **Graph Coloring (Slide 35)**.

ExamAnt models examination scheduling as a hybrid between **Graph Coloring** and **Activity Assignment (AS-QAP)**:

| Concept in Lecture Slides (`AI2 Slide.pdf`) | Role in TSP / AS-QAP | Representation in **ExamAnt** |
| :--- | :--- | :--- |
| **Agent (Ant $k = 1 \dots m$)** | Ant completing a full tour of $n$ cities | Ant constructing a complete timetable for all courses |
| **Decision Step $(i \to j)$** | Next city to visit, or assigning activity $j$ to location $i$ (Slide 29) | Assigning exam slot $t \in \text{Slots}$ to course $c \in \text{Courses}$ |
| **Tabu List / Feasible Set ($J_i^k$) (Slide 18)** | Unvisited cities | Time slots that **satisfy Hard Constraints** (`ConflictGraph.get_feasible_slots()`) |
| **Heuristic Visibility ($\eta_{ij}$) (Slide 18)** | Local information, e.g., $\frac{1}{d_{ij}}$ | $\eta(c, t) = \frac{1}{1 + \Delta P(c, t)}$ where $\Delta P$ is the added consecutive exam penalty |
| **Pheromone Trail ($\tau_{ij}(t)$) (Slide 18)** | Learned desirability of an edge | $\tau[c][t]$ = Learned collective suitability of placing course $c$ in slot $t$ |

---

## 3. Mathematical Equations Implemented in `backend/app/algorithms/aco.py`

### 3.1 Transition Rule (Slides 19, 20, 29)
When ant $k$ is assigning a time slot to course $c$, the probability of choosing slot $t \in J_c^k$ (where $J_c^k$ is the set of feasible slots) is:

$$p_{c,t}^k = \frac{[\tau_{c,t}]^\alpha \cdot [\eta_{c,t}]^\beta}{\sum_{u \in J_c^k} [\tau_{c,u}]^\alpha \cdot [\eta_{c,u}]^\beta}$$

- **Heuristic visibility:** $\eta_{c,t} = \frac{1}{1 + \Delta P(c, t)}$. Adding $1$ in the denominator prevents division by zero when $\Delta P = 0$. A slot causing zero additional back-to-back exams receives maximal heuristic desirability $\eta = 1.0$.
- **Parameter Sensitivity (Slide 20):**
  - $\alpha = 0$: Ants ignore pheromone entirely, degenerating into a purely greedy heuristic search.
  - $\beta = 0$: Ants rely exclusively on pheromone trails, causing rapid premature convergence to suboptimal solutions.
  - A balanced combination (e.g., $\alpha = 1.0, \beta = 2.0$) maintains optimal exploration-exploitation trade-offs.

### 3.2 Pheromone Evaporation and Deposit (Slides 21, 30)
After all $m$ ants finish constructing timetables in an iteration:

1. **Evaporation (Negative Feedback):**
   $$\tau_{c,t} \leftarrow (1 - \rho) \cdot \tau_{c,t} \quad \forall (c, t)$$
   where $\rho \in (0, 1)$ is the evaporation rate.

2. **Pheromone Deposit (Positive Feedback):**
   For each ant $k$ that generated a valid schedule $T^k$ with total penalty score $P_k$:
   $$\Delta \tau_{c,t}^k = \begin{cases} \dfrac{Q}{1 + P_k} & \text{if course } c \text{ is assigned to slot } t \text{ in } T^k \\ 0 & \text{otherwise} \end{cases}$$
   Accumulated update:
   $$\tau_{c,t} \leftarrow \tau_{c,t} + \sum_{k \in \text{ValidAnts}} \Delta \tau_{c,t}^k$$

   > **Academic Justification:**  
   > In classic TSP (Slide 21), tour length $L_k > 0$ always, allowing $\Delta\tau = Q / L_k$. In examination scheduling, an optimal schedule may achieve $P_k = 0$ (no back-to-back exams). We define cost $L_k = 1 + P_k$ to avoid division by zero while rewarding zero-penalty solutions with the maximum deposit $Q$.

3. **Elitist Extension (Slides 22, 25):**
   - An additional deposit can be awarded to the best-so-far solution ($T^+$) to accelerate convergence toward global optima.
