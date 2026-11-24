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
├── .streamlit/
│   └── config.toml               # Default light theme palette & typography configuration
├── app.py                        # Streamlit web application entrypoint (Sidebar + 3 Tabs)
├── api_client.py                 # Backend HTTP client helper (ready to use)
└── components/
    ├── sidebar.py                # Appearance toggle + Parameter controls (sliders & selectors)
    ├── schedule_grid.py          # 2-slots-per-day colored timetable cards, consecutive course highlights & student inspector
    ├── charts.py                 # Conflict Graph, Convergence Curve, Winner Cards, & Benchmark plots
    └── theme.py                  # Shared Light/Dark theme tokens, CSS variables, & algorithm color map
```

> **💡 Modular Design & Code Conventions:**  
> - Rose can customize the timetable visual styling in `components/schedule_grid.py` or tweak Plotly graphs in `components/charts.py` without worrying about API URLs or data parsing, as `api_client.py` handles backend interactions cleanly.
> - **UI Icons:** Use Google Material Icons natively supported by Streamlit (`:material/<icon_name>:`, e.g., `:material/pest_control:`, `:material/play_arrow:`, `:material/rocket_launch:`) instead of raw Unicode emojis.
> - **Code Comments:** All Python comments and docstrings in `frontend/` must be written in English without emojis.

---

## 2. Parameter Tuning Controls (Sidebar)

In `frontend/components/sidebar.py`, controls must adhere to the parameters defined in `docs/01-project-idea-spec.md` (Section 5):

| Parameter | UI Component | Value Range | Default | Applies To | Description |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `theme_mode` | `st.radio` | `Light` / `Dark` | `Light` | UI Theme | Switches dashboard, timetable cards, and Plotly charts between Light and Dark themes |
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

To facilitate presentation delivery as outlined in `docs/00-idea-proposal.md`, `frontend/app.py` is organized into 3 tabs using Streamlit Material Icons:

### Tab 1: `:material/menu_book:` Dataset & Conflict Graph Explorer
- **Content:**
  - Metric cards: total courses, students, enrollments, and exam days.
  - **Interactive Course Conflict Graph:** Plotly NetworkX graph depicting courses as nodes and student overlap as edges. Darker colors denote higher conflict degrees.
- **Demo Goal:** Explains why examination timetabling maps to Graph Coloring.

### Tab 2: `:material/science:` Single Algorithm Run
- **Controls:**
  - Algorithm radio selector (`:material/pest_control: Ant Colony Optimization (ACO)`, `:material/casino: Random Feasible`, `:material/bolt: Greedy Baseline`)
  - **`รันจัดตารางสอบ (Solve)`** button (`icon=":material/play_arrow:"`)
- **State & UX Behavior:**
  - Single-run results are cached per algorithm (`single_results_by_algo`) for the active dataset so presenters can switch between Greedy, Random Feasible, and ACO to compare single runs without showing mismatched metrics from another algorithm. If sidebar parameters change after a run, a `:material/sync:` notice prompts the user to re-run.
- **Results:**
  1. **5 KPI Cards:** Status, Hard Conflicts, Penalty Score ($P$), Attempts, Runtime.
  2. **Colored Timetable Grid (`:material/calendar_month:`):** Shows courses placed into morning (`ช่วงเช้า (Slot 1)`) and afternoon (`ช่วงบ่าย (Slot 2)`) session cards for each day, including unique student attendance per slot, day-level penalty status badges, and inline warning highlights (`สอบติดกัน N คน คู่กับ ...`) directly on any course cards involved in consecutive morning-afternoon exams.
  3. **Consecutive Exam Student Inspector (`:material/search:`):** Expandable list of students with morning and afternoon exams on the same day (`validation_details.consecutive_cases`), or a `:material/check_circle:` banner when Penalty = 0.
  4. **ACO Convergence Curve:** Plots global-best and iteration-best penalty $P$ across iterations.

### Tab 3: `:material/leaderboard:` Multi-Algorithm Comparison
- **Controls:** **`เริ่มรันเปรียบเทียบทั้ง 3 วิธี (Run Benchmark)`** button (`icon=":material/rocket_launch:"`, `POST /compare`).
- **Results:**
  1. **Winner Cards (`:material/emoji_events:`):** Highlights the top algorithm(s) for **Best quality** (lowest median penalty), **Fastest** (lowest mean runtime), and **Most reliable** (highest success rate), automatically displaying tied co-winners separated by `" / "` (e.g., `Greedy / Random Feasible / ACO` or `Random Feasible / ACO`).
  2. **Summary Table (`:material/bar_chart:`):** Compares Runs, Successful Runs, Success Rate, Best/Mean/Median/Std Penalty, Mean Runtime, and Mean Attempts for Greedy, Random Feasible, and ACO.
  3. **Export Options (`:material/download:`):** Download both aggregated Summary CSV (`*_summary.csv`) and per-run Raw Runs CSV (`*_runs.csv`).
  4. **3 Comparative Bar Charts:** Side-by-side Plotly bar charts for Solution Quality (Best vs. Mean Penalty), Success Rate (%), and Mean Runtime (ms).
  5. **Run-by-Run Penalty Trajectory (`:material/timeline:`):** Line chart and table of Penalty across each Run/Seed to evaluate stability across seeds.
  6. **Best Timetable & Convergence Inspectors (`:material/calendar_month:` & `:material/trending_down:`):** Interactive tabs to inspect the best schedule (`best_run_schedule`) and convergence curve (`best_run_history`) of each algorithm.
  7. **Experiment Insights (`:material/lightbulb:`):** Automated data-backed summary bullets comparing quality, speed, and reliability.
