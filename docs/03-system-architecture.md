<p align="right">
  <b>🇬🇧 English</b> | <a href="03-system-architecture.th.md">🇹🇭 ภาษาไทย</a>
</p>

# 🏗️ System Architecture & Cross-Platform Port Configuration

This document outlines the system architecture, inter-service communications, end-to-end data flow, and port isolation strategy across the 3 Docker containers in **ExamAnt** (`mongodb`, `backend`, `frontend`).

---

## 1. System Architecture Diagram

```mermaid
flowchart LR
    subgraph UserMachine["User Workstation (Browser / Compass)"]
        Browser["🌐 Web Browser\nhttp://localhost:8501"]
        Swagger["📄 API Docs (Swagger UI)\nhttp://localhost:8000/docs"]
        Compass["🍃 MongoDB Compass\nmongodb://localhost:27018"]
    end

    subgraph DockerNet["Docker Compose Network"]
        subgraph FE["Frontend Container (Streamlit :8501)"]
            AppPy["app.py"]
            Sidebar["components/sidebar.py"]
            Grid["components/schedule_grid.py"]
            Charts["components/charts.py"]
            Client["api_client.py"]
        end

        subgraph BE["Backend Container (FastAPI :8000)"]
            MainPy["app/main.py"]
            Routers["routers/instances.py\nrouters/solver.py"]
            Graph["core/graph.py\n(ConflictGraph)"]
            Validator["core/validator.py\n(Central Validator)"]
            Algos["algorithms/\ngreedy.py | random_feasible.py | aco.py"]
            DBLayer["app/database.py"]
        end

        subgraph DB["Database Container (MongoDB :27017)"]
            MongoCol[("examant_db\ncollection: exam_instances")]
        end
    end

    Browser -->|"Port 8501"| AppPy
    Swagger -->|"Port 8000"| MainPy
    Compass -->|"Port 27018 -> 27017"| MongoCol

    AppPy --> Sidebar & Grid & Charts
    AppPy --> Client
    Client -->|"HTTP REST (http://backend:8000)"| Routers
    MainPy --> Routers
    Routers --> DBLayer
    DBLayer -->|"PyMongo (mongodb://mongodb:27017)"| MongoCol
    Routers --> Algos
    Algos --> Graph
    Algos --> Validator
```

---

## 2. End-to-End Data Flow

```mermaid
sequenceDiagram
    actor User as User / Presenter
    participant FE as Streamlit Frontend
    participant BE as FastAPI Backend
    participant DB as MongoDB (exam_instances)
    participant Algo as Solver (Greedy / Random / ACO)
    participant Val as Central Validator

    User->>FE: 1. Opens Web UI (http://localhost:8501)
    FE->>BE: GET /instances
    BE->>DB: Fetch instance list
    DB-->>BE: List of ExamInstance summaries
    BE-->>FE: Return dataset list to populate Sidebar

    User->>FE: 2. Selects Dataset + Tunes Sliders (alpha, beta, rho, ants, iterations) + Clicks Run/Compare
    FE->>BE: POST /solve or POST /compare
    BE->>DB: Load full ExamInstance document and convert to ProblemData (Spec 3.6)
    BE->>Val: validate_problem_input(ProblemData)
    BE->>Algo: Dispatch ProblemData + AlgorithmParameters
    Algo->>Algo: Construct timetable using ConflictGraph to find feasible slots & Delta P
    Algo->>Val: validate_and_score_schedule(problem, schedule)
    Val-->>Algo: Return hard_conflict_count, penalty_score, validation_details
    Algo-->>BE: Return SolveResponse (with convergence history)
    BE-->>FE: Return JSON Response
    FE-->>User: 3. Render colored timetable grid + Convergence curve + Comparison charts
```

---

## 3. Cross-Platform Port Isolation (macOS & Windows)

Common environment issues when collaborating across operating systems:
1. **Ports `5000` and `7000` on macOS:** Utilized by macOS's native AirPlay Receiver service.
2. **Port `27017` on macOS and Windows:** Often collides with a locally installed MongoDB daemon.

To eliminate port contention, default ports in `.env` and `docker-compose.yml` are configured as follows:

| Service | Internal Container Port | Host Port Mapping | Environment Variable | Rationale |
| :--- | :---: | :---: | :--- | :--- |
| **MongoDB** | `27017` | **`27018`** | `MONGO_PORT=27018` | Avoids collision with local host MongoDB on `27017` |
| **FastAPI Backend** | `8000` | **`8000`** | `BACKEND_PORT=8000` | Safely avoids macOS AirPlay ports (`5000`/`7000`) |
| **Streamlit Frontend** | `8501` | **`8501`** | `FRONTEND_PORT=8501` | Standard Streamlit web port |

### Modifying Ports
If port `8000` or `8501` is occupied on your machine, edit `.env` in the root folder:
```env
MONGO_PORT=27019
BACKEND_PORT=8080
FRONTEND_PORT=8502
```
Re-run `docker compose up -d`. Inter-container communication (`http://backend:8000` and `mongodb://mongodb:27017`) remains unaffected.
