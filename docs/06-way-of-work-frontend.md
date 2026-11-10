<p align="right">
  <b>🇬🇧 English</b> | <a href="06-way-of-work-frontend.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 🎨 Frontend Development Guidelines (Way of Work for Frontend — Streamlit)

This guide is designed for the frontend developer (**Person 3: Rose**). It details the `frontend/` directory structure, the UI controls for parameter tuning, interactive components for the 10-minute presentation demo, and integration with the FastAPI backend.

---

## 1. Directory Structure (`frontend/`)

```text
frontend/
├── Dockerfile
├── requirements.txt
├── app.py                        # Streamlit web application entrypoint (Sidebar + 3 Tabs)
├── api_client.py                 # Backend HTTP client helper (ready to use)
└── components/
    ├── sidebar.py                # Parameter controls (sliders & selectors)
    ├── schedule_grid.py          # 2-slots-per-day colored timetable grid & consecutive list
    └── charts.py                 # Conflict Graph, Convergence Curve, & Benchmark plots
```

> **💡 Modular Design Benefit:**  
> Rose can customize the timetable visual styling in `components/schedule_grid.py` or tweak Plotly graphs in `components/charts.py` without worrying about API URLs or data parsing, as `api_client.py` handles backend interactions cleanly.

---

## 2. Parameter Tuning Controls (Sidebar)

In `frontend/components/sidebar.py`, controls must adhere to the parameters defined in `docs/01-project-idea-spec.md` (Section 5):

| Parameter | UI Component | Value Range | Default | Applies To | Description |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `instance_id` | `st.selectbox` | Pulled from `GET /instances` | `demo_01` | All | Selects problem dataset |
| `seed` | `st.number_input` | `1 – 999999` | `42` | All | Random seed for reproducibility |
| `runs` | `st.slider` | `1 – 30` | `10` | `/compare` | Number of multi-seed benchmark repetitions |
| `num_ants` | `st.slider` | `1 – 100` | `20` | ACO | Number of virtual ants per iteration |
| `iterations` | `st.slider` | `1 – 200` | `20` | ACO | Number of optimization iterations |
| `alpha` ($\alpha$) | `st.slider` | `0.0 – 5.0` (step `0.1`) | `1.0` | ACO | Pheromone importance weight |
| `beta` ($\beta$) | `st.slider` | `0.0 – 5.0` (step `0.1`) | `2.0` | ACO | Heuristic visibility weight |
| `rho` ($\rho$) | `st.slider` | `0.01 – 0.99` (step `0.05`) | `0.20` | ACO | Pheromone evaporation rate |
| `q` ($Q$) | `st.number_input` | `0.1 – 100.0` | `1.0` | ACO | Pheromone deposit scaling constant |
| `initial_pheromone` | `st.number_input` | `0.1 – 50.0` | `1.0` | ACO | Base pheromone level $\tau_0$ |
| `max_attempts` | `st.checkbox` + `st.number_input` | `1 – 10000` | `num_ants × iterations` (`400`) | Random Feasible | Search budget for random schedule attempts |

> **Crucial Rule:** The slot structure per day is strictly fixed to **2 slots (Morning `slot_index=1` and Afternoon `slot_index=2`)**. There should be **no control** allowing the user to change slot counts per day.

---

## 3. UI Structure & Demo Tabs (10-Minute Video Storyline)

To facilitate presentation delivery as outlined in `docs/00-idea-proposal.md`, `frontend/app.py` is organized into 3 tabs:

### Tab 1: 📚 Dataset & Conflict Graph Explorer
- **Content:**
  - Metric cards: total courses, students, enrollments, and exam days.
  - **Interactive Course Conflict Graph:** Plotly NetworkX graph depicting courses as nodes and student overlap as edges. Darker colors denote higher conflict degrees.
- **Demo Goal:** Explains why examination timetabling maps to Graph Coloring.

### Tab 2: 🧪 Single Algorithm Run
- **Controls:** Algorithm radio selector (`ACO`, `Random Feasible`, `Greedy`) and **`▶️ Solve Timetable`** button.
- **Results:**
  1. **5 KPI Cards:** Status, Hard Conflicts, Penalty Score ($P$), Attempts, Runtime.
  2. **Colored Timetable Grid:** Shows courses placed into morning and afternoon slots for each day.
  3. **Consecutive Exam Student Inspector:** Expandable list of students with morning and afternoon exams on the same day (`validation_details.consecutive_cases`).
  4. **ACO Convergence Curve:** Plots best-so-far penalty $P$ across iterations.

### Tab 3: 🏆 Multi-Algorithm Comparison
- **Controls:** **`🚀 Run Benchmark`** button (`POST /compare`).
- **Results:**
  1. **Summary Table:** Compares Success Rate, Best/Mean/Median/Std Penalty, and Mean Runtime for Greedy, Random Feasible, and ACO.
  2. **Bar Chart:** Visualizes Best vs. Mean Penalty across all three methods.
  3. **Box Plot:** Displays penalty distribution over all seeds to evaluate stability.
  4. **Export Options:** Download results as CSV for slides and report writing.
