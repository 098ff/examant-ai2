<p align="right">
  <a href="06-way-of-work-frontend.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 🎨 แนวทางการพัฒนาฝั่ง Frontend (Way of Work for Frontend — Streamlit)

เอกสารนี้เป็นคู่มือสำหรับผู้พัฒนา Frontend (**โรส - คนที่ 3**) อธิบายโครงสร้างโฟลเดอร์ `frontend/`, รายการตัวแปรที่ต้องเปิดให้ผู้ใช้ปรับจูนผ่าน UI, ปุ่มกดและส่วนประกอบหน้าจอสำหรับการนำเสนอ (Demo 10 นาที) และวิธีเชื่อมกับ FastAPI Backend

---

## 1. โครงสร้างโฟลเดอร์ `frontend/`

```text
frontend/
├── Dockerfile
├── requirements.txt
├── .streamlit/
│   └── config.toml               # ตั้งค่าธีมสีเริ่มต้น (Light theme) และฟอนต์ของ Streamlit
├── app.py                        # หน้าหลักของเว็บ (แบ่งเป็น Sidebar + 3 Tabs)
├── api_client.py                 # ฟังก์ชันยิง HTTP Request ไปหา FastAPI (พร้อมใช้งานแล้ว)
└── components/
    ├── sidebar.py                # สวิตช์สลับโหมดสี (Light/Dark) + แถบเลือก Dataset และเลื่อนปรับค่า Parameters
    ├── schedule_grid.py          # การ์ดตารางแสดงผลช่วงสอบ (เช้า-บ่าย), ไฮไลต์วิชาที่สอบติดกัน และรายชื่อนักศึกษาที่ได้รับผลกระทบ
    ├── charts.py                 # กราฟ Conflict Graph, Convergence Curve, การ์ดผู้ชนะ และกราฟเปรียบเทียบ 3 วิธี
    └── theme.py                  # โทเคนสี Light/Dark, CSS variables และสีประจำอัลกอริทึม
```

> **💡 จุดเด่นของการแยกไฟล์และข้อตกลงการเขียนโค้ด (Code & Icon Conventions):**  
> - โรสสามารถแก้ไขความสวยงามของตารางสอบใน `components/schedule_grid.py` หรือตกแต่งกราฟใน `components/charts.py` ได้อย่างอิสระ โดยไม่ต้องกังวลเรื่อง URL ของ Backend เพราะ `api_client.py` จัดการเชื่อมต่อให้เรียบร้อยแล้ว
> - **การใช้ไอคอนบน UI:** ใช้ Google Material Icons ของ Streamlit (`:material/<icon_name>:` เช่น `:material/pest_control:`, `:material/play_arrow:`, `:material/rocket_launch:`) แทนการใช้อีโมจิ (Emoji) โดยตรงในโค้ด
> - **การเขียนคอมเมนต์ในโค้ด:** คอมเมนต์และ Docstring ทั้งหมดใน `frontend/` เขียนเป็นภาษาอังกฤษและไม่มีอีโมจิ

---

## 2. ตัวแปรและ Component สำหรับปรับจูนค่า (Parameter Tuning Controls)

ในไฟล์ `frontend/components/sidebar.py` ต้องมี UI Controls ให้ปรับค่าพารามิเตอร์ตรงตาม `docs/01-project-idea-spec.md` (หัวข้อ 5) ดังนี้:

| ชื่อตัวแปรใน API | ชนิด UI Component | ช่วงค่า (Min – Max) | ค่าเริ่มต้น (Default) | ใช้กับอัลกอริทึม | คำอธิบายบนหน้าจอ |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `theme_mode` | `st.radio` | `Light` / `Dark` | `Light` | ธีมหน้าเว็บ | สลับโหมดสีของหน้าเว็บ ตารางสอบ และกราฟ Plotly ระหว่างโหมดสว่างและมืด |
| `instance_id` | `st.selectbox` | ดึงจาก `GET /instances` | `demo_01` | ทุกวิธี | เลือกชุดข้อมูลปัญหาจัดตารางสอบ |
| `seed` | `st.number_input` | `1 – 999999` | `42` | ทุกวิธี | Random Seed (เพื่อให้ทำซ้ำผลเดิมได้) |
| `runs` | `st.slider` | `1 – 30` | `10` | หน้า `/compare` | จำนวนรอบการทดลอง (Seeds) ตอนเปรียบเทียบ |
| `num_ants` | `st.slider` | `1 – 100` | `20` | ACO | จำนวนมดที่สร้างตารางต่อ 1 Iteration |
| `iterations` | `st.slider` | `1 – 200` | `20` | ACO | จำนวนรอบการเรียนรู้ของฝูงมด |
| `alpha` ($\alpha$) | `st.slider` | `0.0 – 5.0` (step `0.1`) | `1.0` | ACO | น้ำหนักความสำคัญของรอยฟีโรโมน ($\tau^\alpha$) |
| `beta` ($\beta$) | `st.slider` | `0.0 – 5.0` (step `0.1`) | `2.0` | ACO | น้ำหนักความสำคัญของ Heuristic ($\eta^\beta$) |
| `rho` ($\rho$) | `st.slider` | `0.01 – 0.99` (step `0.05`) | `0.20` | ACO | อัตราการระเหยของฟีโรโมนต่อรอบ |
| `q` ($Q$) | `st.number_input` | `0.1 – 100.0` | `1.0` | ACO | ค่าคงที่ในการฝากฟีโรโมน ($\Delta\tau = Q/(1+P)$) |
| `initial_pheromone` | `st.number_input` | `0.1 – 50.0` | `1.0` | ACO | ค่าฟีโรโมนตั้งต้น ($\tau_0$) |
| `max_attempts` | `st.checkbox` + `st.number_input` | `1 – 10000` | `num_ants × iterations` (`400`) | Random Feasible | งบจำนวนตารางที่พยายามสุ่มสร้าง (ตั้งให้เท่ากับ `num_ants × iterations` เพื่อความยุติธรรม) |

> **ข้อควรระวังตาม Spec ข้อ 5:**  
> จำนวนช่วงสอบต่อวันถูกกำหนดตายตัวที่ **2 ช่วง (เช้า `slot_index=1` และบ่าย `slot_index=2`)** จึง **ไม่ต้อง** สร้างปุ่มหรือ Slider ให้ปรับจำนวนช่วงต่อวันบนหน้า Frontend

---

## 3. โครงสร้างหน้าจอและปุ่มกดสำหรับการนำเสนอ (3 Tabs สำหรับเล่าเรื่องในวิดีโอ 10 นาที)

เพื่อให้สอดคล้องกับแนวทางการเล่าเรื่องใน `docs/00-idea-proposal.md` (หัวข้อ 8) หน้าเว็บใน `frontend/app.py` จึงแบ่งเป็น 3 แท็บหลักโดยใช้ Material Icons:

### แท็บที่ 1: `:material/menu_book:` ข้อมูลรายวิชา & กราฟความขัดแย้ง (Dataset & Conflict Graph)
- **สิ่งที่แสดง:**
  - การ์ดสรุปจำนวนวิชา, จำนวนนักศึกษา, จำนวนการลงทะเบียน และจำนวนวันสอบ
  - **กราฟความขัดแย้งของรายวิชา (Course Conflict Graph):** ดึงข้อมูลจาก `GET /instances/{instance_id}/graph` แสดงจุด (Node) เป็นรายวิชา และเส้นเชื่อม (Edge) เมื่อมีนักศึกษาลงเรียนร่วมกัน (ยิ่งชนหลายวิชายิ่งสีเข้ม)
- **จุดประสงค์ตอนอัดวิดีโอ:** ใช้เปิดเรื่องเพื่ออธิบายว่าทำไมโจทย์จัดตารางสอบจึงแปลงเป็นปัญหา **Graph Coloring** ได้

### แท็บที่ 2: `:material/science:` ทดลองรันเดี่ยว (Single Algorithm Run)
- **ปุ่มกดสำคัญ:**
  - ปุ่มเลือกวิธี (`:material/pest_control: Ant Colony Optimization (ACO)`, `:material/casino: Random Feasible`, `:material/bolt: Greedy Baseline`)
  - ปุ่ม **`รันจัดตารางสอบ (Solve)`** (`icon=":material/play_arrow:"`) ซึ่งยิงไปที่ `POST /solve`
- **การจัดการ State และ UX:**
  - แยกเก็บผลลัพธ์รายอัลกอริทึม (`single_results_by_algo`) สำหรับชุดข้อมูลปัจจุบัน ทำให้สลับปุ่ม Radio ดูผลลัพธ์ของแต่ละวิธีที่รันไปแล้วได้ทันทีโดยไม่แสดงตัวเลขข้ามวิธี และมีแบนเนอร์ `:material/sync:` แจ้งเตือนเมื่อมีการขยับพารามิเตอร์ใน Sidebar
- **สิ่งที่แสดงหลังกดปุ่ม:**
  1. **Metric Cards 5 ช่อง:** `Status`, `Hard Conflict Count`, `Penalty Score (P)`, `Attempts`, `Runtime (ms)`
  2. **ตารางสอบสี 2 ช่วงต่อวัน (`:material/calendar_month:` Morning vs Afternoon Schedule Cards):** แสดงการ์ดรายวิชาในช่วงเช้า (`ช่วงเช้า (Slot 1)`) และช่วงบ่าย (`ช่วงบ่าย (Slot 2)`) ของแต่ละวัน พร้อมจำนวนผู้เข้าสอบไม่ซ้ำต่อช่วงสอบ ป้ายสถานะ Penalty รายวัน และการไฮไลต์กรอบสีเตือนพร้อมป้าย `สอบติดกัน N คน คู่กับ ...` บนกล่องรายวิชาที่ทำให้เกิดการสอบติดกันโดยตรง
  3. **ตารางรายชื่อนักศึกษาที่โดนสอบติดกัน เช้า-บ่าย (`:material/search:` `validation_details.consecutive_cases`):** คลิกเปิดดูได้ว่านักศึกษาคนไหน (`S001` ฯลฯ) สอบติดกันในวันไหน หรือแสดงแบนเนอร์ `:material/check_circle:` เมื่อ `Penalty = 0`
  4. **กราฟการลู่เข้า (Convergence Curve):** วาดจากฟิลด์ `history` แสดงค่า `Global best penalty` และ `Iteration best penalty` ตามรอบของอัลกอริทึม

### แท็บที่ 3: `:material/leaderboard:` เปรียบเทียบ 3 อัลกอริทึม (Multi-Seed Benchmark Compare)
- **ปุ่มกดสำคัญ:**
  - ปุ่ม **`เริ่มรันเปรียบเทียบทั้ง 3 วิธี (Run Benchmark)`** (`icon=":material/rocket_launch:"`) ซึ่งยิงไปที่ `POST /compare`
- **สิ่งที่แสดงหลังกดปุ่ม:**
  1. **การ์ดสรุปผู้ชนะ 3 ด้าน (`:material/emoji_events: ผลลัพธ์เด่น`):** แสดงวิธีที่ได้ **Best quality** (Median Penalty ต่ำสุด), **Fastest** (เวลาเฉลี่ยต่ำสุด) และ **Most reliable** (Success Rate สูงสุด) โดยแสดงชื่อผู้ชนะร่วมคั่นด้วย `" / "` เมื่อคะแนนเท่ากัน (เช่น `Greedy / Random Feasible / ACO` หรือ `Random Feasible / ACO`)
  2. **ตารางสรุปผลรวม (`:material/bar_chart: สรุปผลการทดลอง`):** เทียบ `Runs`, `Successful runs`, `Success rate (%)`, `Best penalty`, `Mean penalty`, `Median penalty`, `Std penalty`, `Mean runtime (ms)` และ `Mean attempts` ของทั้ง 3 วิธี
  3. **ปุ่มดาวน์โหลด CSV (`:material/download:`):** ดาวน์โหลดได้ทั้งตารางสรุป (`*_summary.csv`) และข้อมูลผลลัพธ์รายรอบ (`*_runs.csv`)
  4. **กราฟแท่งเปรียบเทียบ 3 มิติ (3 Bar Charts):** เทียบคุณภาพคำตอบ (Best vs. Mean Penalty), Success Rate (%) และเวลาเฉลี่ย (Mean Runtime ms)
  5. **กราฟเส้นและตารางผลแบบรอบต่อรอบ (`:material/timeline:`):** แสดงค่า Penalty ในแต่ละ Run / Seed เพื่อดูความสม่ำเสมอของคำตอบ
  6. **แท็บตารางสอบที่ดีที่สุดและกราฟ Convergence ของแต่ละวิธี (`:material/calendar_month:` & `:material/trending_down:`):** สลับดูตารางสอบที่ดีที่สุด (`best_run_schedule`) และกราฟการลู่เข้า (`best_run_history`) ของแต่ละวิธีได้ทันที
  7. **สรุปข้อค้นพบจากการทดลอง (`:material/lightbulb: Experiment Insights`):** สรุปประเด็นสำคัญจากตัวเลขผลการทดลองโดยอัตโนมัติ
