<p align="right">
  <a href="01-task-maimai-lead-aco.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 👩‍💻 คู่มืองานของคนที่ 1: Sippapas Chavanont (Mai) — 6630333721 [Lead]

> **รายวิชา:** AI2 (2110477)  
> **ผู้รับผิดชอบ:** 6630333721 Sippapas Chavanont (Mai)  
> **บทบาท:** Core Optimization Developer  
> **ไฟล์ที่รับผิดชอบหลัก:**  
> 1. [`backend/app/algorithms/aco.py`](../../backend/app/algorithms/aco.py)  
> 2. [`backend/app/algorithms/random_feasible.py`](../../backend/app/algorithms/random_feasible.py)  
> 3. [`backend/app/routers/solver.py`](../../backend/app/routers/solver.py) *(เตรียมโครงไว้ให้แล้ว สามารถปรับจูนเพิ่มเติมได้)*

---

## 1. สรุปงานที่ไมไมต้องทำ (Checklist)

- [ ] **งานที่ 1: ตรวจสอบโมดูลกลาง (`ConflictGraph` และ `Central Validator`)**
  - เปิดดูไฟล์ [`backend/app/core/graph.py`](../../backend/app/core/graph.py) และ [`backend/app/core/validator.py`](../../backend/app/core/validator.py) ซึ่งถูกเขียนไว้ตามสเปก `01-project-idea-spec.md` ของไมไมเรียบร้อยแล้ว
- [ ] **งานที่ 2: พัฒนาอัลกอริทึม `Random Feasible` ใน `backend/app/algorithms/random_feasible.py`**
  - แทนที่โค้ด `# TODO [คนที่ 1 - ไมไม]` ด้วยลูปสุ่มสร้างตารางจำนวน `params.max_attempts` ครั้ง:
    1. ในแต่ละ attempt เรียงวิชาตาม `ordered_courses = graph.get_ordered_courses()` (หรือสุ่มลำดับวิชา) แล้วสุ่มเลือกช่วงสอบจาก `feasible_slots = graph.get_feasible_slots(course_id, partial_schedule)` ด้วย `rng.choice(feasible_slots)`
    2. หากเจอวิชาที่ `feasible_slots` ว่างเปล่า (ติดทางตัน) ให้ข้ามไปเริ่ม attempt ใหม่ทันที
    3. หากจัดครบทุกวิชา ให้คำนวณ Penalty (ใช้ `validate_and_score_schedule` หรือรวม `delta_p`) แล้วเก็บตารางที่มี Penalty ต่ำที่สุด (`best_schedule`) พร้อมบันทึก `best_iteration` และ `history`
- [ ] **งานที่ 3: พัฒนาอัลกอริทึม `ACO` ใน `backend/app/algorithms/aco.py`**
  - แทนที่โค้ด `# TODO [คนที่ 1 - ไมไม]` ด้วยลูป Ant System ตามสมการใน [`docs/02-aco-theory-and-mapping.md`](../02-aco-theory-and-mapping.md):
    1. สร้างตาราง Pheromone เริ่มต้น `tau[course_id][slot_id] = params.initial_pheromone`
    2. วนลูป `iteration = 1 .. params.iterations` โดยในแต่ละรอบส่งมด `params.num_ants` ตัวออกไปสร้างตารางทีละวิชาตาม `ordered_courses = graph.get_ordered_courses()`
    3. สำหรับมดแต่ละตัว เมื่อจะเลือกช่วงสอบให้วิชา $c$ จาก `feasible_slots`:
       - คำนวณ $\Delta P = \text{graph.calculate\_delta\_penalty}(c, t, \text{partial\_schedule})$
       - คำนวณ Heuristic $\eta(c, t) = \frac{1.0}{1.0 + \Delta P}$
       - คำนวณน้ำหนัก $w(c, t) = (\tau[c][t])^\alpha \times (\eta(c, t))^\beta$
       - สุ่มเลือก `slot_id` ตามความน่าจะเป็น $p(c, t) = \frac{w(c, t)}{\sum w}$ (ใช้ `rng.choices(feasible_slots, weights=weights, k=1)[0]`)
    4. เมื่อมดทั้ง `num_ants` ตัวทำงานเสร็จในรอบนั้น:
       - ประเมินค่า Penalty $P_k$ ของมดทุกตัวที่สร้างตารางสำเร็จ
       - อัปเดต `global_best_schedule` และ `global_best_penalty`
       - **Evaporation:** ลดค่าฟีโรโมนทุกช่อง $\tau[c][t] \leftarrow (1 - \rho) \cdot \tau[c][t]$
       - **Deposit:** สำหรับมดที่สร้างตารางสำเร็จ เติมฟีโรโมน $\Delta \tau = \frac{Q}{1.0 + P_k}$ ลงในช่อง $\tau[c][\text{assigned\_slot}]$ (และอาจเสริม Elitist deposit ให้ `global_best_schedule` ด้วยก็ได้)
       - บันทึก `IterationHistoryPoint(iteration=it, best_penalty=global_best_penalty, iteration_best_penalty=iter_best, feasible_ants=valid_count)` ลงในลิสต์ `history`

---

## 2. ขั้นตอนการทำงานบน Git & Feature Branch

ก่อนเริ่มเขียนโค้ด ให้ดึงโค้ดล่าสุดจาก `main` แล้วสร้าง Feature Branch เฉพาะของงานนี้:

```bash
git checkout main
git pull origin main
git checkout -b feat/aco-random-solvers
```

เมื่อ commit งาน ให้ใช้รูปแบบ Conventional Commits (เช่น `feat(aco): implement transition probability and pheromone update`)

---

## 3. วิธีรันและทดสอบส่วนของไมไม

```bash
# รันผ่าน Docker
docker compose up --build

# หรือทดสอบยิง API /solve สำหรับ ACO และ Random Feasible ที่
# http://localhost:8000/docs
```

---

## 4. การใช้ AI Agent ช่วยทำงาน (ลำดับไฟล์ที่ต้อง `@` และ Prompt Template)

เมื่อไมไมเปิดโปรเจกต์ใน Cursor / Antigravity / Claude Code หรือ AI Coding Assistant แนะนำให้อ้างอิงไฟล์ตามลำดับนี้เพื่อให้ AI เข้าใจบริบททั้งหมดทันทีโดยไม่หลุดสเปก:

### ลำดับการ `@` ไฟล์ให้อ่านก่อนสั่งงาน
1. `@docs/01-project-idea-spec.md` (ข้อกำหนดหลักและสัญญา API)
2. `@docs/02-aco-theory-and-mapping.md` (สมการ ACO จากสไลด์เรียน)
3. `@backend/app/core/graph.py` และ `@backend/app/core/validator.py` (ฟังก์ชันกลางที่มีให้เรียกใช้แล้ว)
4. `@backend/app/algorithms/base.py` (ตัวแปลงผลลัพธ์เป็น `SolveResponse`)
5. `@backend/app/algorithms/random_feasible.py` และ `@backend/app/algorithms/aco.py` (ไฟล์เป้าหมายที่จะแก้)

### 📋 Prompt Template สำเร็จรูป (คัดลอกไปวางใน AI Chat ได้เลย)

```text
ฉันคือ "Sippapas Chavanont (Mai, 6630333721)" รับผิดชอบการเขียนอัลกอริทึม Random Feasible และ Ant Colony Optimization (ACO) ของโปรเจกต์ ExamAnt ในวิชา AI2 (2110477)

ก่อนเริ่มเขียนโค้ด ให้ทำความเข้าใจไฟล์เหล่านี้ตามลำดับ:
1. @docs/01-project-idea-spec.md (โดยเฉพาะหัวข้อ 4, 5, 6, 7.2 และ 7.3)
2. @docs/02-aco-theory-and-mapping.md (สมการ Transition Rule, Evaporation และ Pheromone Deposit จากสไลด์เรียน)
3. @backend/app/core/graph.py และ @backend/app/core/validator.py (คลาส ConflictGraph และตัวตรวจกลางที่เตรียมไว้แล้ว)
4. @backend/app/algorithms/base.py

งานที่ต้องการให้ทำ:
1. แก้ไขไฟล์ @backend/app/algorithms/random_feasible.py เพื่อแทนที่ส่วน STUB ด้วยอัลกอริทึม Random Feasible เต็มรูปแบบ:
   - ใช้ `random.Random(params.seed)` เพื่อความสามารถในการทำซ้ำ
   - วนลูปไม่เกิน `params.max_attempts` ครั้ง สร้างตารางทีละวิชาจาก `graph.get_feasible_slots(...)`
   - ถ้าติดทางตันให้เริ่ม attempt ใหม่ ถ้าสร้างครบให้คำนวณ penalty และเก็บตารางที่ penalty ต่ำสุด พร้อมบันทึก `history` และคืนค่าผ่าน `build_solve_response(...)`
2. แก้ไขไฟล์ @backend/app/algorithms/aco.py เพื่อแทนที่ส่วน STUB ด้วยอัลกอริทึม ACO เต็มรูปแบบ:
   - ใช้ Pheromone matrix `tau[course_id][slot_id]` เริ่มต้นที่ `params.initial_pheromone`
   - ใช้ Heuristic `eta(c, t) = 1.0 / (1.0 + delta_p)` จาก `graph.calculate_delta_penalty(c, t, partial_schedule)`
   - สุ่มเลือกช่วงสอบที่ feasible ด้วยความน่าจะเป็นแปรผันตาม `(tau ** params.alpha) * (eta ** params.beta)`
   - หลังจบแต่ละ iteration ให้ระเหยฟีโรโมน `(1 - params.rho)` และฝากฟีโรโมน `params.q / (1.0 + penalty)` สำหรับมดที่สร้างตารางสำเร็จ
   - บันทึก `IterationHistoryPoint` ทุก iteration ลงใน `history` แล้วคืนค่าผ่าน `build_solve_response(...)`
3. เขียนเทสต์สั้นๆ หรือรันทดสอบกับชุดข้อมูล `demo_01` เพื่อยืนยันว่าทั้ง `random_feasible` และ `aco` คืนค่า `status == "success"` และ `hard_conflict_count == 0`
```
