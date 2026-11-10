<p align="right">
  <a href="03-system-architecture.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 🏗️ สถาปัตยกรรมระบบ (System Architecture) และการตั้งค่าพอร์ต

เอกสารนี้อธิบายโครงสร้างการทำงานร่วมกันของทั้ง 3 คอนเทนเนอร์ในโปรเจกต์ **ExamAnt** (`mongodb`, `backend`, `frontend`) รวมถึงแนวทางการตั้งค่าพอร์ตเพื่อป้องกันปัญหาพอร์ตชนกันบน macOS และ Windows

---

## 1. แผนผังสถาปัตยกรรม (System Architecture Diagram)

```mermaid
flowchart LR
    subgraph UserMachine["เครื่องผู้ใช้งาน (Browser / Compass)"]
        Browser["🌐 Web Browser\nhttp://localhost:8501"]
        Swagger["📄 API Docs (Swagger)\nhttp://localhost:8000/docs"]
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

        subgraph DB["Database Container (Mongo :27017)"]
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

## 2. ลำดับการทำงานตั้งแต่ต้นจนจบ (End-to-End Data Flow)

```mermaid
sequenceDiagram
    actor User as ผู้ใช้ (โรส / ตอน Demo)
    participant FE as Streamlit Frontend
    participant BE as FastAPI Backend
    participant DB as MongoDB (exam_instances)
    participant Algo as Solver (Greedy / Random / ACO)
    participant Val as Central Validator

    User->>FE: 1. เปิดหน้าเว็บ (http://localhost:8501)
    FE->>BE: GET /instances
    BE->>DB: ดึงรายการชุดข้อมูลทั้งหมด
    DB-->>BE: รายการ ExamInstance
    BE-->>FE: คืนรายการ Dataset ไปแสดงที่ Sidebar

    User->>FE: 2. เลือก Dataset + ปรับ Sliders (alpha, beta, rho, ants, iterations) + กดปุ่ม Run/Compare
    FE->>BE: POST /solve หรือ POST /compare
    BE->>DB: โหลดข้อมูล Instance แล้วแปลงเป็น ProblemData (Spec 3.6)
    BE->>Val: validate_problem_input(ProblemData)
    BE->>Algo: ส่ง ProblemData + AlgorithmParameters
    Algo->>Algo: สร้างตารางสอบโดยใช้ ConflictGraph เช็ก Feasible Slots & Delta P
    Algo->>Val: validate_and_score_schedule(problem, schedule)
    Val-->>Algo: คืนค่า hard_conflict_count, penalty_score, validation_details
    Algo-->>BE: คืน SolveResponse (พร้อม history ราย iteration)
    BE-->>FE: คืน JSON Response
    FE-->>User: 3. วาดตารางสอบ 2 ช่วง/วัน + กราฟ Convergence + ตารางเปรียบเทียบ
```

---

## 3. การจัดการพอร์ตสำหรับ macOS และ Windows (ป้องกันพอร์ตชน)

ปัญหาที่พบบ่อยเวลาทำโปรเจกต์กลุ่มข้าม OS (macOS vs Windows):
1. **พอร์ต `5000` และ `7000` บน macOS:** ถูกใช้งานโดยบริการ AirPlay Receiver ของระบบปฏิบัติการ macOS
2. **พอร์ต `27017` บนทั้ง macOS และ Windows:** มักชนกับบริการ MongoDB Server ที่ติดตั้งไว้ในเครื่องอยู่แล้ว

ดังนั้นเราจึงออกแบบพอร์ตเริ่มต้นในไฟล์ `.env` และ `docker-compose.yml` ดังนี้:

| บริการ | พอร์ตภายใน Docker | พอร์ตที่เปิดบนเครื่อง (Host Port) | ตัวแปรใน `.env` | เหตุผล |
| :--- | :---: | :---: | :--- | :--- |
| **MongoDB** | `27017` | **`27018`** | `MONGO_PORT=27018` | ไม่ชนกับ MongoDB ที่ลงไว้ในเครื่อง (`27017`) |
| **FastAPI Backend** | `8000` | **`8000`** | `BACKEND_PORT=8000` | หลีกเลี่ยงพอร์ต `5000`/`7000` ของ macOS AirPlay |
| **Streamlit Frontend** | `8501` | **`8501`** | `FRONTEND_PORT=8501` | พอร์ตมาตรฐานของ Streamlit |

### วิธีแก้ไขกรณีพอร์ต `8000` หรือ `8501` ชนกับโปรแกรมอื่นในเครื่อง
เพียงเปิดไฟล์ `.env` ที่โฟลเดอร์รากของโปรเจกต์ แล้วเปลี่ยนตัวเลข เช่น:
```env
MONGO_PORT=27019
BACKEND_PORT=8080
FRONTEND_PORT=8502
```
จากนั้นรัน `docker compose up -d` ใหม่ ตัว Container ภายในจะยังคงคุยกันผ่านเครือข่ายภายใน (`http://backend:8000` และ `mongodb://mongodb:27017`) ได้เหมือนเดิมโดยไม่ต้องแก้โค้ดแม้แต่บรรทัดเดียว!
