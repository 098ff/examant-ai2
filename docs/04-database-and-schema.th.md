<p align="right">
  <a href="04-database-and-schema.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 🍃 คู่มือการตั้งค่าฐานข้อมูล MongoDB และโครงสร้างข้อมูล (Data Schema)

เอกสารนี้อธิบายวิธีตั้งค่าและใช้งานฐานข้อมูล **MongoDB** สำหรับโปรเจกต์ **ExamAnt** รวมถึงโครงสร้าง Collection `exam_instances` และการแปลงข้อมูลเข้าสู่อัลกอริทึมตาม `docs/01-project-idea-spec.md`

---

## 1. วิธีรันและเชื่อมต่อกับ MongoDB

ในโปรเจกต์นี้ MongoDB ถูกรันผ่าน Docker Container (`mongo:7.0`) โดยอัตโนมัติเมื่อสั่งรัน Docker Compose

### 1.1 คำสั่งรันฐานข้อมูล
```bash
# รันเฉพาะ MongoDB (กรณีต้องการเขียนโค้ด Python บนเครื่องตัวเอง)
docker compose up -d mongodb

# หรือรันพร้อมกันทั้งระบบ (MongoDB + Backend + Frontend)
docker compose up --build
```

### 1.2 การเชื่อมต่อเพื่อดูข้อมูลด้วยโปรแกรม MongoDB Compass (GUI)
หากต้องการเปิดดูข้อมูลตารางในฐานข้อมูลแบบกราฟิก:
1. ดาวน์โหลดและเปิดโปรแกรม **MongoDB Compass** (หรือส่วนเสริม MongoDB ใน VS Code / Cursor / Antigravity)
2. ใส่ Connection String ด้านล่าง (สังเกตว่าใช้พอร์ต **`27018`** ตามที่ตั้งไว้ใน `.env`):
   ```text
   mongodb://localhost:27018
   ```
3. กด **Connect** แล้วเลือก Database ชื่อ **`examant_db`** -> Collection ชื่อ **`exam_instances`**

### 1.3 การดูข้อมูลผ่าน Terminal (ไม่ต้องลงโปรแกรมเพิ่ม)
```bash
docker compose exec mongodb mongosh examant_db --eval "db.exam_instances.find({}, {instance_id: 1, name: 1, _id: 0}).pretty()"
```

---

## 2. โครงสร้างข้อมูลใน MongoDB (`exam_instances` Collection)

เพื่อให้ดึงข้อมูลชุดปัญหาส่งเข้าอัลกอริทึมได้รวดเร็วใน 1 Query โดยไม่ต้อง Join ข้ามหลาย Collection เราเก็บข้อมูลแบบ **Embedded Document** (1 Document = 1 ชุดปัญหา `ExamInstanceDocument`) ซึ่งบรรจุข้อมูลครบทุก Entity ตาม `docs/01-project-idea-spec.md` (หัวข้อ 3.1 – 3.5):

```json
{
  "instance_id": "demo_01",
  "name": "Demo 01 — ชุดข้อมูลสาธิตขนาดเล็ก (10 วิชา, 3 วัน / 6 ช่วงสอบ)",
  "seed": 42,
  "description": "ข้อมูลจำลองเริ่มต้น 10 วิชา นักศึกษา 20 คน ช่วงสอบ 3 วัน (6 ช่วง เช้า-บ่าย)",
  "courses": [
    {
      "course_id": "C01",
      "course_name": "Artificial Intelligence II",
      "student_count": 7
    }
  ],
  "students": [
    {
      "student_id": "S001"
    }
  ],
  "enrollments": [
    {
      "student_id": "S001",
      "course_id": "C01"
    },
    {
      "student_id": "S001",
      "course_id": "C02"
    }
  ],
  "slots": [
    {
      "slot_id": "D1_S1",
      "day_index": 1,
      "slot_index": 1,
      "label": "วันที่ 1 ช่วงเช้า"
    },
    {
      "slot_id": "D1_S2",
      "day_index": 1,
      "slot_index": 2,
      "label": "วันที่ 1 ช่วงบ่าย"
    }
  ]
}
```

### กฎความถูกต้องของข้อมูล (Data Integrity Rules)
1. `instance_id` ต้องไม่ซ้ำกันใน Collection `exam_instances` (มี Unique Index กำกับ)
2. ในแต่ละวัน (`day_index = 1..D`) ต้องมีช่วงสอบ **2 ช่วงเสมอ** คือ `slot_index = 1` (เช้า) และ `slot_index = 2` (บ่าย) รวมเป็น $2D$ ช่วงสอบ
3. ทุก `enrollment` ต้องอ้างอิง `student_id` และ `course_id` ที่มีอยู่ในรายการ `students` และ `courses` ของชุดปัญหานั้น และห้ามมีคู่ `(student_id, course_id)` ซ้ำกัน

---

## 3. การแปลงข้อมูลจาก MongoDB ส่งให้ Algorithm (`ProblemData` - Spec ข้อ 3.6)

แต่ละอัลกอริทึม (`greedy.py`, `random_feasible.py`, `aco.py`) **ไม่ต้องเชื่อมต่อ MongoDB เอง** ตัว Router จะดึง `ExamInstanceDocument` จาก `app/database.py` แล้วเรียกเมธอด `.to_problem_data()` เพื่อแปลงเป็นออบเจกต์ `ProblemData` มาตรฐานก่อนส่งให้ทุกอัลกอริทึม:

```json
{
  "instance_id": "demo_01",
  "courses": ["C01", "C02", "C03"],
  "students": ["S001", "S002"],
  "enrollments": [
    {"student_id": "S001", "course_id": "C01"},
    {"student_id": "S001", "course_id": "C02"}
  ],
  "slots": [
    {"slot_id": "D1_S1", "day_index": 1, "slot_index": 1, "label": "วันที่ 1 ช่วงเช้า"},
    {"slot_id": "D1_S2", "day_index": 1, "slot_index": 2, "label": "วันที่ 1 ช่วงบ่าย"}
  ]
}
```

---

## 4. วิธีรันสคริปต์ Seed ข้อมูลเข้า MongoDB

1. **Auto-Seed ตอนเปิดระบบครั้งแรก:**  
   เมื่อรัน `docker compose up` หาก Collection `exam_instances` ยังว่างอยู่ ระบบจะนำข้อมูลชุดตัวอย่าง `demo_01` จากไฟล์ [`backend/scripts/sample_instances.json`](../backend/scripts/sample_instances.json) เข้าไปใส่ให้อัตโนมัติ
2. **สั่งรันสคริปต์ Seed ด้วยตัวเอง (หลังจากคนที่ 2 - ฝ้าย เพิ่มชุดข้อมูลใหม่):**
   ```bash
   # กรณีรันผ่าน Docker
   docker compose exec backend python -m scripts.seed_db

   # หรือเรียกผ่าน API Endpoint
   curl -X POST http://localhost:8000/instances/seed
   ```
