<p align="right">
  <b>🇬🇧 English</b> | <a href="07-benchmark-results-rose.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 📊 ExamAnt Baseline Benchmark Results & Analysis

> **Course:** AI2 (2110477)  
> **Prepared by:** 6632213421 Sasarose Buranapin (Rose) — Frontend, Data Visualization & Experiment Analysis  
> **Experiment Date:** 17 November 2026

---

## 1. Experimental Setup

- **Algorithms:** Greedy, Random Feasible, and Ant Colony Optimization (ACO)
- **Datasets:** `demo_01`, `easy_01`, `medium_01`, and `hard_01`
- **Stochastic Runs:** 10 seeds (`seed = 42` through `51`)
- **Random Feasible Budget:** `max_attempts = 400`
- **ACO Budget:** `num_ants = 20`, `iterations = 20` (`400` candidate schedules — equal search budget)
- **ACO Parameters:** `alpha = 1.0`, `beta = 2.0`, `rho = 0.2`, `q = 1.0`, `initial_pheromone = 1.0`
- **Deterministic Baseline:** Greedy is deterministic and runs once per dataset.
- **Evaluation Rules:** Runtime covers solver computation only. Every schedule is independently verified by the Central Validator (`hard_conflict_count == 0`). Penalty statistics include successful runs only.

---

## 2. Empirical Results

| Dataset | Algorithm | Success Rate | Best Penalty ($P$) | Mean Penalty | Median Penalty | Std Penalty | Mean Runtime (ms) | Dashboard Best Quality Winner |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `demo_01` | Greedy | 100% | 7 | 7.0 | 7.0 | 0.00 | 0.22 | Random Feasible / ACO *(tied median 5.0)* |
| `demo_01` | Random Feasible | 100% | 5 | 5.0 | 5.0 | 0.00 | 42.10 | Random Feasible / ACO *(tied median 5.0)* |
| `demo_01` | ACO | 100% | 5 | 5.0 | 5.0 | 0.00 | 51.80 | Random Feasible / ACO *(tied median 5.0)* |
| `easy_01` | Greedy | 100% | 6 | 6.0 | 6.0 | 0.00 | 0.304 | **ACO** *(median 3.0)* |
| `easy_01` | Random Feasible | 100% | 3 | 3.8 | 3.5 | 0.92 | 78.472 | **ACO** *(median 3.0)* |
| `easy_01` | ACO | 100% | 3 | 3.0 | 3.0 | 0.00 | 84.327 | **ACO** *(median 3.0)* |
| `medium_01` | Greedy | 100% | 15 | 15.0 | 15.0 | 0.00 | 0.363 | Random Feasible / ACO *(tied median 8.0)* |
| `medium_01` | Random Feasible | 100% | 8 | 8.0 | 8.0 | 0.00 | 40.227 | Random Feasible / ACO *(tied median 8.0)* |
| `medium_01` | ACO | 100% | 8 | 10.1 | 8.0 | 3.38 | 54.512 | Random Feasible / ACO *(tied median 8.0)* |
| `hard_01` | Greedy | 100% | 20 | 20.0 | 20.0 | 0.00 | 1.187 | **ACO** *(median 12.0)* |
| `hard_01` | Random Feasible | 100% | 12 | 17.3 | 18.0 | 2.11 | 136.227 | **ACO** *(median 12.0)* |
| `hard_01` | ACO | 100% | 12 | 12.2 | 12.0 | 0.63 | 162.535 | **ACO** *(median 12.0)* |

---

## 3. Key Findings

1. **100% Feasibility Across All Methods:** All three algorithms produced valid schedules (`0` hard conflicts) in every tested run (`Greedy / Random Feasible / ACO` tied at `100.0%` success rate), allowing direct comparison of soft penalty optimization and runtime without a feasibility trade-off.
2. **Consistency on `easy_01`:** ACO was the most consistent method on `easy_01`, reaching the best penalty $P = 3$ on all 10 seeds (`mean = 3.0, median = 3.0, std = 0.0`), compared with Random Feasible's median of `3.5` (`mean = 3.8`) and Greedy's penalty of `6`.
3. **Tie and Premature Convergence on `medium_01`:** On `medium_01`, both Random Feasible and ACO achieved the same best and median penalty of `8.0` (displayed as co-winners `Random Feasible / ACO` on the dashboard). However, on 3 of the 10 seeds, early pheromone reinforcement with default $\beta = 2.0$ pulled ACO toward the greedy local optimum ($P = 15$), resulting in a higher mean penalty (`10.1`).
4. **Strongest ACO Advantage on `hard_01`:** ACO demonstrated its clearest superiority on `hard_01` (15 courses, 90 students, 8 slots). Its median penalty was **`12.0`** (`mean = 12.2, std = 0.63`), substantially outperforming Random Feasible (`median = 18.0, mean = 17.3, std = 2.11`) and Greedy (`penalty = 20.0`).
5. **Quality vs. Runtime Trade-off:** Greedy finished in under `1.2 ms` across all datasets (`Fastest` winner) but consistently incurred the highest consecutive-exam penalties.

---

## 4. Interpretation, UI Integration & Limitations

- The baseline experiments confirm that pheromone-guided search (ACO) significantly improves timetable quality and stability on larger, higher-density problem instances (`hard_01`) under an equal candidate-schedule budget (`400` evaluations).
- Simultaneously, the `medium_01` results illustrate a classic Swarm Intelligence phenomenon from the AI2 lecture slides: strong heuristic weighting ($\beta$) combined with positive feedback can occasionally cause premature convergence to a greedy trap unless balanced by sufficient exploration or higher evaporation ($\rho$).
- In the **Streamlit Comparison Dashboard (`Tab 3`)**, tied metrics are explicitly reported as co-winners (e.g., `Greedy / Random Feasible / ACO` for `100.0%` success rate, or `Random Feasible / ACO` when median penalties tie), and courses involved in same-day back-to-back exams are highlighted directly inside the timetable session cards.
