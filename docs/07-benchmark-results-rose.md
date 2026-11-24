# ExamAnt Baseline Benchmark Results

**Experiment date:** 17 November 2026  
**Prepared by:** Rose — Frontend, Data Visualization, and Experiment Analysis

## Experimental setup

- Algorithms: Greedy, Random Feasible, and Ant Colony Optimization (ACO)
- Datasets: `easy_01`, `medium_01`, and `hard_01`
- Stochastic runs: 10 seeds, from 42 through 51
- Random Feasible budget: `max_attempts = 400`
- ACO budget: `num_ants = 20`, `iterations = 20` (400 candidate schedules)
- ACO parameters: `alpha = 1.0`, `beta = 2.0`, `rho = 0.2`, `q = 1.0`, `initial_pheromone = 1.0`
- Greedy is deterministic and was run once per dataset.
- Runtime covers solver computation only. Penalty statistics include successful runs only.

## Results

| Dataset | Algorithm | Success rate | Best penalty | Mean penalty | Median penalty | Std penalty | Mean runtime (ms) |
|---|---|---:|---:|---:|---:|---:|---:|
| easy_01 | Greedy | 100% | 6 | 6.0 | 6.0 | 0.0 | 0.304 |
| easy_01 | Random Feasible | 100% | 3 | 3.8 | 3.5 | 0.92 | 78.472 |
| easy_01 | ACO | 100% | 3 | 3.0 | 3.0 | 0.0 | 84.327 |
| medium_01 | Greedy | 100% | 15 | 15.0 | 15.0 | 0.0 | 0.363 |
| medium_01 | Random Feasible | 100% | 8 | 8.0 | 8.0 | 0.0 | 40.227 |
| medium_01 | ACO | 100% | 8 | 10.1 | 8.0 | 3.38 | 54.512 |
| hard_01 | Greedy | 100% | 20 | 20.0 | 20.0 | 0.0 | 1.187 |
| hard_01 | Random Feasible | 100% | 12 | 17.3 | 18.0 | 2.11 | 136.227 |
| hard_01 | ACO | 100% | 12 | 12.2 | 12.0 | 0.63 | 162.535 |

## Key findings

1. All three algorithms produced valid schedules in every tested run, so this experiment compares solution quality and runtime without a success-rate trade-off.
2. ACO was the most consistent method on `easy_01`: it reached penalty 3 in every run, compared with Random Feasible's median of 3.5 and Greedy's penalty of 6.
3. On `medium_01`, ACO and Random Feasible had the same best and median penalty of 8. Random Feasible had a lower mean penalty and runtime in this run set, so ACO did not provide a clear advantage on this dataset with the default parameters.
4. ACO showed its strongest advantage on `hard_01`. Its median penalty was 12, compared with 18 for Random Feasible and 20 for Greedy. Its standard deviation was also much lower than Random Feasible's, indicating more consistent solution quality.
5. Greedy was substantially faster, but it produced the highest penalty on all three datasets. The results show a clear quality-versus-runtime trade-off.

## Interpretation and limitations

The baseline results support the claim that ACO can improve timetable quality on the more difficult synthetic dataset under an equal candidate-schedule budget. They do not show that ACO is universally superior: on `medium_01`, Random Feasible matched ACO's median quality and was faster.

These findings apply only to the selected synthetic datasets, seeds, and parameter values. A parameter-sensitivity experiment for `alpha`, `beta`, `rho`, and search budget is still required before making a broader conclusion about ACO behavior.
