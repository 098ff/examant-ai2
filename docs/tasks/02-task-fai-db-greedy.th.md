<p align="right">
  <a href="02-task-fai-db-greedy.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 👩‍💻 คู่มืองานของคนที่ 2: Chanatda Konchom (Fai) — 6631305321

> **รายวิชา:** AI2 (2110477)  
> **ผู้รับผิดชอบ:** 6631305321 Chanatda Konchom (Fai)  
> **บทบาท:** Infrastructure, Data Engineering & Greedy Baseline Developer  
> **ไฟล์ที่รับผิดชอบหลัก:**  
> 1. [`backend/scripts/seed_db.py`](../../backend/scripts/seed_db.py) และ [`backend/scripts/sample_instances.json`](../../backend/scripts/sample_instances.json)  
> 2. [`backend/app/algorithms/greedy.py`](../../backend/app/algorithms/greedy.py)  
> 3. [`docker-compose.yml`](../../docker-compose.yml) และ [`backend/app/database.py`](../../backend/app/database.py) *(ตั้งค่าโครงสร้างให้เรียบร้อยแล้ว)*

---

## 1. สรุปงานที่ฝ้ายต้องทำต่อ (Checklist)

- [x] **งานที่ 1: Setup Repository, Docker Compose และ MongoDB Connection** *(ดำเนินการวางโครงสร้างไว้ให้เรียบร้อยแล้วในรอบนี้)*
- [ ] **งานที่ 2: พัฒนาอัลกอริทึม `Greedy` ใน `backend/app/algorithms/greedy.py`**
  - แทนที่โค้ด `# TODO [คนที่ 2 - ฝ้าย]` ให้ครบตามกติกาใน `docs/01-project-idea-spec.md` (หัวข้อ 7.1):
    1. เรียงลำดับวิชาจาก Degree ความขัดแย้งมากไปน้อย (`ordered_courses = graph.get_ordered_courses()`)
    2. สำหรับแต่ละวิชา `course_id` ดึงช่วงสอบที่ไม่ชน (`feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`)
    3. หาก `feasible_slots` ว่างเปล่า ให้คืนค่า `no_solution_found` (`partial_schedule = None`)
    4. หากมีช่วงสอบที่ใช้ได้ ให้คำนวณ `delta_p = graph.calculate_delta_penalty(course_id, slot_id, partial_schedule)` ของแต่ละช่วงสอบ แล้วเลือก `slot_id` ที่ทำให้ **`delta_p` น้อยที่สุด** (หากเท่ากัน เลือกช่วงสอบที่มาก่อนตามลำดับใน `feasible_slots`)
- [ ] **งานที่ 3: สร้าง Dataset Generator (อย่างน้อย 3 ชุดที่มีความยากต่างกัน) และ Seed ลง MongoDB ใน `backend/scripts/seed_db.py`**
  - ตาม `docs/00-idea-proposal.md` (หัวข้อ 4) และ `docs/01-project-idea-spec.md` (หัวข้อ 3):
    - สร้างข้อมูลจำลองอย่างน้อย 3 ชุด เช่น:
      1. `easy_01` (หรือ `demo_01`): ~10 วิชา, นักศึกษา 40–50 คน, 3 วัน (6 ช่วงสอบ เช้า-บ่าย)
      2. `medium_01`: ~12 วิชา, นักศึกษา 60–80 คน, 3 วัน (6 ช่วงสอบ เช้า-บ่าย) ที่มีความหนาแน่นของการลงทะเบียนร่วมกันสูงขึ้น
      3. `hard_01`: ~14–15 วิชา, นักศึกษา 80–100 คน, 3–4 วัน (6–8 ช่วงสอบ) ที่ Greedy มักได้ค่า Penalty สูงกว่าคำตอบที่ดีที่สุด เพื่อให้เห็นความแตกต่างเมื่อ ACO เข้ามาช่วยค้นหา
    - **เทคนิคสำคัญเพื่อให้มั่นใจว่ามีตารางที่ไม่ชนจริง (Planted Feasible Coloring):**
      1. แบ่งรายวิชาออกเป็น $2D$ กลุ่มล่วงหน้า (สมมติว่าเป็นคำตอบที่ซ่อนไว้ 1 แบบ)
      2. ตอนสุ่มให้นักศึกษาแต่ละคนลงทะเบียน 2–3 วิชา ให้สุ่มเลือกวิชาที่อยู่ **คนละกลุ่มช่วงสอบ** (เพื่อให้มั่นใจ 100% ว่ามีตารางสอบที่ `hard_conflict_count == 0` อย่างน้อย 1 แบบเสมอ!)
      3. บันทึกทั้งลงใน `backend/scripts/sample_instances.json` และสั่ง Upsert เข้า MongoDB ผ่าน `seed_db.py`

---

## 2. ขั้นตอนการทำงานบน Git & Feature Branch

ก่อนเริ่มเขียนโค้ด ให้ดึงโค้ดล่าสุดจาก `main` แล้วสร้าง Feature Branch เฉพาะของงานนี้:

```bash
git checkout main
git pull origin main
git checkout -b feat/dataset-seeder-greedy
```

เมื่อ commit งาน ให้ใช้รูปแบบ Conventional Commits (เช่น `feat(dataset): implement synthetic instances generator`)

---

## 3. วิธีรันและทดสอบส่วนของฝ้าย

```bash
# 1. รันระบบผ่าน Docker Compose
docker compose up --build -d

# 2. รันสคริปต์สร้างและ Seed ข้อมูลลง MongoDB
docker compose exec backend python -m scripts.seed_db

# 3. ตรวจสอบว่าข้อมูลเข้า MongoDB แล้ว
docker compose exec mongodb mongosh examant_db --eval "db.exam_instances.find({}, {instance_id: 1, name: 1, _id: 0}).pretty()"
```

---

## 4. การใช้ AI Agent ช่วยทำงาน (ลำดับไฟล์ที่ต้อง `@` และ Prompt Template)

### ลำดับการ `@` ไฟล์ให้อ่านก่อนสั่งงาน
1. `@docs/00-idea-proposal.md` และ `@docs/01-project-idea-spec.md` (หัวข้อ 3, 4, 7.1)
2. `@docs/04-database-and-schema.md` (โครงสร้าง Collection `exam_instances`)
3. `@backend/app/core/graph.py` และ `@backend/app/core/validator.py`
4. `@backend/app/algorithms/greedy.py` และ `@backend/scripts/seed_db.py`

### 📋 Prompt Template สำเร็จรูป (คัดลอกไปวางใน AI Chat ได้เลย)

```text
ฉันคือ "Chanatda Konchom (Fai, 6631305321)" รับผิดชอบการสร้าง Dataset จำลองใส่ MongoDB และการพัฒนาอัลกอริทึม Greedy Baseline ของโปรเจกต์ ExamAnt ในวิชา AI2 (2110477)

ก่อนเริ่มเขียนโค้ด ให้ทำความเข้าใจไฟล์เหล่านี้ตามลำดับ:
1. @docs/01-project-idea-spec.md (โดยเฉพาะหัวข้อ 3 โครงสร้างข้อมูล และหัวข้อ 7.1 พฤติกรรมของ Greedy)
2. @docs/04-database-and-schema.md
3. @backend/app/core/graph.py และ @backend/app/core/validator.py
4. @backend/app/algorithms/greedy.py และ @backend/scripts/seed_db.py

งานที่ต้องการให้ทำ:
1. แก้ไขไฟล์ @backend/app/algorithms/greedy.py เพื่อพัฒนาอัลกอริทึม Greedy ให้สมบูรณ์ตาม Spec ข้อ 7.1:
   - เรียงลำดับวิชาด้วย `graph.get_ordered_courses()` (degree มากไปน้อย, tie-break ด้วย course_id)
   - สำหรับแต่ละวิชา หา `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)`
   - เลือก slot ที่ทำให้ `graph.calculate_delta_penalty(course_id, slot_id, partial_schedule)` มีค่าน้อยที่สุด (หากเท่ากันให้เลือก slot แรกสุดตามลำดับ)
   - คืนค่าผ่าน `build_solve_response(...)` โดยไม่มีข้อความ `[STUB]`
2. แก้ไขไฟล์ @backend/scripts/seed_db.py (และอัปเดต @backend/scripts/sample_instances.json) เพื่อสร้างชุดข้อมูลจำลอง 3 ระดับความยาก (`easy_01`, `medium_01`, `hard_01`) เพิ่มเติมจาก `demo_01`:
   - ใช้เทคนิค Planted Feasible Assignment ตอนสุ่มนักศึกษาลงทะเบียน เพื่อให้รับประกันว่าทุกชุดข้อมูลมีคำตอบที่ `hard_conflict_count == 0` จริง
   - ตรวจสอบความถูกต้องของทุกชุดข้อมูลด้วย `validate_problem_input` และทดสอบรัน `solve_greedy` กับทุกชุดข้อมูลก่อนบันทึกเข้า MongoDB
```
