<p align="right">
  <a href="README.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 🐜 ExamAnt — ระบบจัดตารางสอบด้วย Ant Colony Optimization (ACO)

> **รายวิชา:** AI2 (2110477)  
> **หัวข้อ:** Ant Colony Optimization (ACO), Constraint Satisfaction Problem (CSP), Graph Coloring  
> **สมาชิกในกลุ่ม:**  
> 1. 6631305321 Chanatda Konchom (Fai)  
> 2. 6632213421 Sasarose Buranapin (Rose)  
> 3. 6630333721 Sippapas Chavanont (Mai)  

**ExamAnt** เป็นโปรเจกต์ทดลองเปรียบเทียบการนำ **Ant Colony Optimization (ACO)** มาแก้ปัญหาการจัดตารางสอบ (Examination Timetabling Problem) เทียบกับวิธีพื้นฐานอย่าง **Greedy** และ **Random Feasible** โดยมีเป้าหมายคือ:
1. **Hard Constraints (บังคับ):** นักศึกษาคนเดียวกันห้ามมีวิชาสอบชนกันในช่วงเวลาเดียวกัน และห้ามสอบเกิน 2 วิชาต่อวัน
2. **Soft Objective (เป้าหมายที่ต้องการลด):** ลดจำนวนครั้ง (`Penalty P`) ที่นักศึกษาคนเดียวกันต้องสอบติดกันทั้ง **ช่วงเช้า** และ **ช่วงบ่าย** ภายในวันเดียวกัน

---

## 🛠️ Tech Stack

| ส่วนระบบ | เทคโนโลยี | พอร์ตเริ่มต้น (Host -> Container) | หน้าที่ |
| :--- | :--- | :--- | :--- |
| **Frontend** | Streamlit + Plotly + NetworkX | `8501 -> 8501` | หน้าเว็บปรับจูน Parameter, แสดงตารางสอบสี และกราฟเปรียบเทียบ |
| **Backend** | FastAPI + Pydantic v2 | `8000 -> 8000` | ประมวลผลอัลกอริทึม (Greedy, Random Feasible, ACO) และตรวจคำตอบด้วย Central Validator |
| **Database** | MongoDB 7.0 | `27018 -> 27017` | เก็บชุดข้อมูลจำลอง (`exam_instances`) โดยใช้พอร์ต `27018` เพื่อไม่ให้ชนกับ MongoDB ในเครื่อง |

---

## 🚀 วิธีเริ่มต้นใช้งาน (Quick Start)

### วิธีที่ 1: รันผ่าน Docker Compose (แนะนำ — เหมือนกันทุกเครื่องทั้ง macOS และ Windows)

```bash
# 1. คัดลอกไฟล์ตั้งค่า Environment (หากยังไม่มี .env)
cp .env.example .env

# 2. สั่งรันทั้งระบบ (MongoDB + FastAPI + Streamlit)
docker compose up --build
```

เมื่อรันสำเร็จ สามารถเปิดใช้งานได้ที่:
- 🖥️ **Streamlit Frontend:** http://localhost:8501
- ⚙️ **FastAPI Swagger UI (API Docs):** http://localhost:8000/docs
- 🍃 **MongoDB (สำหรับต่อผ่าน MongoDB Compass):** `mongodb://localhost:27018` (Database: `examant_db`)

> **💡 กรณีพอร์ตชนบน macOS / Windows:**  
> สามารถเปิดไฟล์ `.env` แล้วเปลี่ยนเลขพอร์ต `FRONTEND_PORT`, `BACKEND_PORT`, หรือ `MONGO_PORT` ได้ทันทีโดยไม่ต้องแก้โค้ด (ดูรายละเอียดใน [docs/03-system-architecture.th.md](docs/03-system-architecture.th.md))

---

### วิธีที่ 2: รันแยกแบบ Local Development (กรณีต้องการรัน Python นอก Docker)

```bash
# 1. รันเฉพาะฐานข้อมูล MongoDB ด้วย Docker
docker compose up -d mongodb

# 2. รัน Backend (FastAPI)
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.seed_db                          # Seed ข้อมูลเริ่มต้นเข้า MongoDB
uvicorn app.main:app --reload --port 8000

# 3. เปิดอีก Terminal เพื่อรัน Frontend (Streamlit)
cd frontend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
BACKEND_API_URL=http://localhost:8000 streamlit run app.py --server.port 8501
```

---

## 📚 สารบัญเอกสารในโปรเจกต์ (`docs/`)

### 1. ขอบเขตโจทย์และทฤษฎี ACO
- 📄 [00-idea-proposal.th.md](docs/00-idea-proposal.th.md) — แนวคิดเริ่มต้นของโปรเจกต์ ExamAnt และแผนการเล่าเรื่องในวิดีโอ 10 นาที ([English](docs/00-idea-proposal.md))
- 📐 [01-project-idea-spec.th.md](docs/01-project-idea-spec.th.md) — ข้อกำหนดกลางของระบบ (Data Schema, กติกาการคิดคะแนน, สัญญา API และพารามิเตอร์) ([English](docs/01-project-idea-spec.md))
- 🐜 [02-aco-theory-and-mapping.th.md](docs/02-aco-theory-and-mapping.th.md) — สรุปเนื้อหาเรียนจาก `AI2 Slide.pdf` (Stigmergy, Ant System, AS-QAP) และการแปลงสูตรเข้าสู่โค้ด ExamAnt ([English](docs/02-aco-theory-and-mapping.md))

### 2. สถาปัตยกรรมและแนวทางการพัฒนาระบบ (Way of Work)
- 🏗️ [03-system-architecture.th.md](docs/03-system-architecture.th.md) — สถาปัตยกรรมระบบ, Data Flow และการจัดการพอร์ตบน macOS/Windows ([English](docs/03-system-architecture.md))
- 🍃 [04-database-and-schema.th.md](docs/04-database-and-schema.th.md) — วิธีตั้งค่า MongoDB, โครงสร้าง Collection `exam_instances` และวิธี Seed ข้อมูล ([English](docs/04-database-and-schema.md))
- ⚙️ [05-way-of-work-backend.th.md](docs/05-way-of-work-backend.th.md) — โครงสร้างโค้ด Backend, รายละเอียด API Endpoints และวิธีใช้งาน Central Validator ([English](docs/05-way-of-work-backend.md))
- 🎨 [06-way-of-work-frontend.th.md](docs/06-way-of-work-frontend.th.md) — โครงสร้างโค้ด Streamlit, รายการ Sliders ปรับค่าพารามิเตอร์ และแนวทางการวาดกราฟ ([English](docs/06-way-of-work-frontend.md))

### 3. การแบ่งงานรายบุคคลและ Prompt สำหรับ AI Agent (`docs/tasks/`)
- 👥 [00-tasks-overview.th.md](docs/tasks/00-tasks-overview.th.md) — ภาพรวมการแบ่งงาน 3 คน และขั้นตอนการเชื่อมงานเข้าด้วยกัน ([English](docs/tasks/00-tasks-overview.md))
- 👩‍💻 [01-task-mai-aco.th.md](docs/tasks/01-task-mai-aco.th.md) — **คนที่ 1 (ไม):** พัฒนา ACO, Random Feasible และระบบเปรียบเทียบ `/compare` ([English](docs/tasks/01-task-mai-aco.md))
- 👩‍💻 [02-task-fai-db-greedy.th.md](docs/tasks/02-task-fai-db-greedy.th.md) — **คนที่ 2 (ฝ้าย):** สร้าง Dataset Generator, MongoDB Seeder และอัลกอริทึม Greedy ([English](docs/tasks/02-task-fai-db-greedy.md))
- 👩‍💻 [03-task-rose-frontend.th.md](docs/tasks/03-task-rose-frontend.th.md) — **คนที่ 3 (โรส):** พัฒนาหน้าเว็บ Streamlit, ตารางสอบสี และกราฟสรุปผลการทดลอง ([English](docs/tasks/03-task-rose-frontend.md))
