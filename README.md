<p align="right">
  <b>🇬🇧 English</b> | <a href="README.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 🐜 ExamAnt — Examination Timetabling with Ant Colony Optimization (ACO)

> **Course:** AI2 (2110477)  
> **Topics:** Ant Colony Optimization (ACO), Constraint Satisfaction Problem (CSP), Graph Coloring  
> **Team Members:**  
> 1. 6631305321 Chanatda Konchom (Fai)  
> 2. 6632213421 Sasarose Buranapin (Rose)  
> 3. 6630333721 Sippapas Chavanont (Mai)  

**ExamAnt** is an academic project investigating the application of **Ant Colony Optimization (ACO)** to solve the Examination Timetabling Problem compared against baseline approaches (**Greedy** and **Random Feasible**). The optimization objectives are:

1. **Hard Constraints (Mandatory):** No student may be scheduled for two exams in the same time slot, and no student may have more than 2 exams on the same day.
2. **Soft Objective (Minimization Target):** Minimize the number of occurrences (`Penalty Score P`) where a student has consecutive exams across both **morning** and **afternoon** slots on the same day.

---

## 🛠️ Tech Stack

| Component | Technology | Default Port (Host -> Container) | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend** | Streamlit + Plotly + NetworkX | `8501 -> 8501` | Interactive parameter tuning, colored timetable grid, convergence and comparison charts |
| **Backend** | FastAPI + Pydantic v2 | `8000 -> 8000` | High-performance algorithm execution (Greedy, Random Feasible, ACO) & Central Validator |
| **Database** | MongoDB 7.0 | `27018 -> 27017` | Storage for simulated datasets (`exam_instances`) using port `27018` to avoid host MongoDB collision |

---

## 🚀 Quick Start

### Option 1: Run with Docker Compose (Recommended — Identical across macOS & Windows)

```bash
# 1. Copy environment configuration (if .env doesn't exist yet)
cp .env.example .env

# 2. Build and start all services (MongoDB + FastAPI + Streamlit)
docker compose up --build
```

Once started, access the services:
- 🖥️ **Streamlit Web UI:** http://localhost:8501
- ⚙️ **FastAPI Swagger Docs:** http://localhost:8000/docs
- 🍃 **MongoDB (via MongoDB Compass):** `mongodb://localhost:27018` (Database: `examant_db`)

> **💡 Port Collision Handling (macOS & Windows):**  
> Simply modify `FRONTEND_PORT`, `BACKEND_PORT`, or `MONGO_PORT` inside `.env`. Containers communicate over Docker's internal network (`http://backend:8000`), so no code modification is required. (See [docs/03-system-architecture.md](docs/03-system-architecture.md)).

---

### Option 2: Local Development Setup (Running outside Docker)

```bash
# 1. Start MongoDB only
docker compose up -d mongodb

# 2. Run Backend (FastAPI)
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.seed_db                          # Seed starter dataset into MongoDB
uvicorn app.main:app --reload --port 8000

# 3. In another terminal, run Frontend (Streamlit)
cd frontend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
BACKEND_API_URL=http://localhost:8000 streamlit run app.py --server.port 8501
```

---

## 📚 Documentation Index (`docs/`)

All documentation is available in both **English** (main) and **Thai** (`*.th.md`).

### 1. Problem Definition & ACO Theory
- 📄 [00-idea-proposal.md](docs/00-idea-proposal.md) — Original project concept, motivations, and 10-minute video outline ([ภาษาไทย](docs/00-idea-proposal.th.md))
- 📐 [01-project-idea-spec.md](docs/01-project-idea-spec.md) — Master technical specification: data schema, scoring rules, API contracts, parameters ([ภาษาไทย](docs/01-project-idea-spec.th.md))
- 🐜 [02-aco-theory-and-mapping.md](docs/02-aco-theory-and-mapping.md) — AI2 lecture notes summary (Stigmergy, Ant System, AS-QAP) mapped to ExamAnt implementation ([ภาษาไทย](docs/02-aco-theory-and-mapping.th.md))

### 2. Architecture & Development Guidelines (Way of Work)
- 🏗️ [03-system-architecture.md](docs/03-system-architecture.md) — System architecture, container communication, end-to-end data flow, and port handling ([ภาษาไทย](docs/03-system-architecture.th.md))
- 🍃 [04-database-and-schema.md](docs/04-database-and-schema.md) — MongoDB setup, embedded `exam_instances` collection schema, Compass guide, and DB seeder ([ภาษาไทย](docs/04-database-and-schema.th.md))
- ⚙️ [05-way-of-work-backend.md](docs/05-way-of-work-backend.md) — Backend folder structure, API endpoints, ConflictGraph, and Central Validator usage ([ภาษาไทย](docs/05-way-of-work-backend.th.md))
- 🎨 [06-way-of-work-frontend.md](docs/06-way-of-work-frontend.md) — Streamlit structure, parameter slider controls, demo tabs, and visualization guidelines ([ภาษาไทย](docs/06-way-of-work-frontend.th.md))

### 3. Task Allocation & AI Agent Workflow (`docs/tasks/`)
- 👥 [00-tasks-overview.md](docs/tasks/00-tasks-overview.md) — 3-person team workflow, milestones, and integration roadmap ([ภาษาไทย](docs/tasks/00-tasks-overview.th.md))
- 👩‍💻 [01-task-mai-aco.md](docs/tasks/01-task-mai-aco.md) — **Person 1 (Mai):** ACO, Random Feasible, and `/compare` benchmark logic ([ภาษาไทย](docs/tasks/01-task-mai-aco.th.md))
- 👩‍💻 [02-task-fai-db-greedy.md](docs/tasks/02-task-fai-db-greedy.md) — **Person 2 (Fai):** Dataset generator (3 difficulty levels), MongoDB seeder, and Greedy baseline ([ภาษาไทย](docs/tasks/02-task-fai-db-greedy.th.md))
- 👩‍💻 [03-task-rose-frontend.md](docs/tasks/03-task-rose-frontend.md) — **Person 3 (Rose):** Streamlit frontend, timetable grid, visualization charts, and comparison report ([ภาษาไทย](docs/tasks/03-task-rose-frontend.th.md))
