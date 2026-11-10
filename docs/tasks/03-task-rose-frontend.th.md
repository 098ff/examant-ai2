<p align="right">
  <a href="03-task-rose-frontend.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 👩‍💻 คู่มืองานของคนที่ 3: Sasarose Buranapin (Rose) — 6632213421

> **รายวิชา:** AI2 (2110477)  
> **ผู้รับผิดชอบ:** 6632213421 Sasarose Buranapin (Rose)  
> **บทบาท:** Frontend Developer, Data Visualization & Experiment Analyst  
> **ไฟล์ที่รับผิดชอบหลัก:**  
> 1. [`frontend/app.py`](../../frontend/app.py)  
> 2. [`frontend/components/sidebar.py`](../../frontend/components/sidebar.py)  
> 3. [`frontend/components/schedule_grid.py`](../../frontend/components/schedule_grid.py)  
> 4. [`frontend/components/charts.py`](../../frontend/components/charts.py)  
> 5. [`frontend/api_client.py`](../../frontend/api_client.py) *(เตรียมฟังก์ชันเชื่อม Backend ไว้ให้ครบแล้ว)*

---

## 1. สรุปงานที่โรสต้องทำต่อ (Checklist)

ใน Repository นี้ได้วางโครงหน้าเว็บ Streamlit เบื้องต้นที่เชื่อมกับ FastAPI Backend ไว้ให้แล้ว โรสสามารถรัน `docker compose up --build` แล้วเปิด `http://localhost:8501` เพื่อดูหน้าเว็บตั้งต้นได้เลย โดยสิ่งที่โรสสามารถพัฒนาเพิ่มเติมเพื่อให้หน้าเว็บและการสรุปผลสมบูรณ์แบบสำหรับการอัดวิดีโอ 10 นาที มีดังนี้:

- [ ] **งานที่ 1: ตกแต่งตารางสอบสี (`frontend/components/schedule_grid.py`) ให้ดูง่ายและสวยงาม**
  - ปรับการแสดงผลตารางสอบ 2 ช่วงต่อวัน (เช้า `slot_index=1` / บ่าย `slot_index=2`) ให้มีสีสันแยกตามวันหรือไฮไลต์คู่รายวิชาที่ทำให้นักศึกษาต้องสอบติดกัน เช้า-บ่าย (ใช้ข้อมูลจาก `validation_details["consecutive_cases"]`)
  - เพิ่มการแสดงผลว่าในแต่ละช่องสอบมีนักศึกษาเข้าสอบรวมกี่คน
- [ ] **งานที่ 2: พัฒนาหน้าเปรียบเทียบ 3 อัลกอริทึม (`Tab 3` ใน `frontend/app.py` และ `frontend/components/charts.py`)**
  - ในหน้าเปรียบเทียบ (`POST /compare`) นอกจากตาราง Summary และกราฟ Bar/Boxplot แล้ว ให้เพิ่มส่วนแสดง **ตารางสอบที่ดีที่สุดของทั้ง 3 วิธี (`best_run_schedule` ของ Greedy, Random Feasible, ACO) วางเทียบกัน** หรือเลือกสลับดูได้
  - เพิ่มกราฟเปรียบเทียบ **Convergence Curve** ของรอบที่ดีที่สุด (`best_run_history`)
  - เพิ่มปุ่ม **Download CSV / สรุปผลการทดลอง** เพื่อนำตารางตัวเลขไปใส่สไลด์หรือรายงานได้ทันที
- [ ] **งานที่ 3: รันการทดลองเปรียบเทียบและเขียนสรุปผล (Analysis & Key Findings)**
  - ทดลองรันเปรียบเทียบทั้ง 3 วิธีบนชุดข้อมูลทั้งหมดที่ฝ้ายสร้าง (`easy_01`, `medium_01`, `hard_01`) และทดลองปรับพารามิเตอร์ของ ACO (เช่น ปรับ $\alpha, \beta, \rho$ หรือจำนวนมด)
  - เพิ่มส่วนสรุปผลวิเคราะห์ (Markdown / Expander บนหน้าเว็บ) ตามหัวข้อที่ 10 ของ `docs/00-idea-proposal.md`:
    - เมื่อใดที่ ACO ชนะ Greedy และ Random Feasible?
    - ในชุดข้อมูลขนาดเล็กที่ Greedy ได้คำตอบดีอยู่แล้ว ACO ใช้เวลาเพิ่มขึ้นคุ้มค่าหรือไม่?
    - อิทธิพลของค่า $\alpha$ (Pheromone) และ $\beta$ (Heuristic) ส่งผลต่อค่า Penalty อย่างไร?

---

## 2. ขั้นตอนการทำงานบน Git & Feature Branch

ก่อนเริ่มเขียนโค้ด ให้ดึงโค้ดล่าสุดจาก `main` แล้วสร้าง Feature Branch เฉพาะของงานนี้:

```bash
git checkout main
git pull origin main
git checkout -b feat/streamlit-frontend-viz
```

เมื่อ commit งาน ให้ใช้รูปแบบ Conventional Commits (เช่น `feat(ui): add side-by-side timetable comparison`)

---

## 3. วิธีรันและแก้ไขโค้ด Streamlit แบบเห็นผลทันที (Live Reload)

```bash
# รันทั้งระบบผ่าน Docker Compose
docker compose up --build
```
เมื่อโรสแก้ไฟล์ในโฟลเดอร์ `frontend/` แล้วกด Save หน้าเว็บที่ `http://localhost:8501` จะอัปเดตให้ทันทีโดยไม่ต้องสั่ง Build Docker ใหม่!

---

## 4. การใช้ AI Agent ช่วยทำงาน (ลำดับไฟล์ที่ต้อง `@` และ Prompt Template)

### ลำดับการ `@` ไฟล์ให้อ่านก่อนสั่งงาน
1. `@docs/00-idea-proposal.md` (โดยเฉพาะหัวข้อ 7, 8 และ 10 เรื่องภาพและการเล่าเรื่องในวิดีโอ)
2. `@docs/01-project-idea-spec.md` (หัวข้อ 4 และ 5 เรื่อง Response Schema และพารามิเตอร์)
3. `@docs/06-way-of-work-frontend.md` (คู่มือโครงสร้าง Frontend และรายการ Sliders/Tabs)
4. `@frontend/api_client.py`, `@frontend/app.py`, `@frontend/components/sidebar.py`, `@frontend/components/schedule_grid.py`, `@frontend/components/charts.py`

### 📋 Prompt Template สำเร็จรูป (คัดลอกไปวางใน AI Chat ได้เลย)

```text
ฉันคือ "Sasarose Buranapin (Rose, 6632213421)" รับผิดชอบการพัฒนาหน้าเว็บ Streamlit Frontend, การสร้างกราฟ Visualization และการเปรียบเทียบผลลัพธ์ของทั้ง 3 อัลกอริทึม (Greedy, Random Feasible, ACO) ในโปรเจกต์ ExamAnt ในวิชา AI2 (2110477)

ก่อนเริ่มเขียนโค้ด ให้ทำความเข้าใจไฟล์เหล่านี้ตามลำดับ:
1. @docs/00-idea-proposal.md (หัวข้อ 7, 8, 10 สำหรับแนวทางการแสดงผลและสรุปผลการทดลอง)
2. @docs/01-project-idea-spec.md (หัวข้อ 4 และ 5)
3. @docs/06-way-of-work-frontend.md
4. @frontend/api_client.py, @frontend/app.py, @frontend/components/sidebar.py, @frontend/components/schedule_grid.py และ @frontend/components/charts.py

งานที่ต้องการให้ทำ:
1. อัปเกรดการแสดงผลตารางสอบใน @frontend/components/schedule_grid.py:
   - แสดงตารางสอบแยกตามวันและช่วงเช้า/บ่ายให้สวยงาม มีสีสันชัดเจน
   - ไฮไลต์หรือแสดงป้ายกำกับเมื่อมีคู่รายวิชาในวันเดียวกันที่ทำให้นักศึกษาต้องสอบติดกัน (อ้างอิงจาก `validation_details["consecutive_cases"]`)
2. อัปเกรดหน้าเปรียบเทียบ 3 อัลกอริทึมใน @frontend/app.py และ @frontend/components/charts.py:
   - แสดงตารางเปรียบเทียบ Metrics (Success Rate, Best/Mean/Median/Std Penalty, Runtime, Attempts)
   - เพิ่มส่วนเปรียบเทียบตารางสอบที่ดีที่สุด (`best_run_schedule`) ของ Greedy vs Random Feasible vs ACO แบบวางเทียบกันหรือสลับดูได้ง่าย
   - เพิ่มกราฟเปรียบเทียบ Runtime และปุ่ม Download ตารางสรุปผลการทดลองเป็นไฟล์ CSV
   - เพิ่มกล่องสรุปคำอธิบายผลการทดลอง (Experiment Insights) ที่ช่วยให้ผู้ชมเข้าใจผลลัพธ์ตอนอัดวิดีโอเดโม 10 นาที
```
