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
├── app.py                        # หน้าหลักของเว็บ (แบ่งเป็น Sidebar + 3 Tabs)
├── api_client.py                 # ฟังก์ชันยิง HTTP Request ไปหา FastAPI (พร้อมใช้งานแล้ว)
└── components/
    ├── sidebar.py                # แถบด้านข้างสำหรับเลือก Dataset และเลื่อนปรับค่า Parameters
    ├── schedule_grid.py          # ตารางแสดงผลช่วงสอบ (เช้า-บ่าย) และรายชื่อคนสอบติดกัน
    └── charts.py                 # กราฟ Conflict Graph, Convergence Curve และกราฟเปรียบเทียบ 3 วิธี
```

> **💡 จุดเด่นของการแยกไฟล์แบบนี้:**  
> โรสสามารถแก้ไขความสวยงามของตารางสอบใน `components/schedule_grid.py` หรือตกแต่งกราฟใน `components/charts.py` ได้อย่างอิสระ โดยไม่ต้องกังวลเรื่อง URL ของ Backend เพราะ `api_client.py` จัดการเชื่อมต่อให้เรียบร้อยแล้ว

---

## 2. ตัวแปรและ Component สำหรับปรับจูนค่า (Parameter Tuning Controls)

ในไฟล์ `frontend/components/sidebar.py` ต้องมี UI Controls ให้ปรับค่าพารามิเตอร์ตรงตาม `docs/01-project-idea-spec.md` (หัวข้อ 5) ดังนี้:

| ชื่อตัวแปรใน API | ชนิด UI Component | ช่วงค่า (Min – Max) | ค่าเริ่มต้น (Default) | ใช้กับอัลกอริทึม | คำอธิบายบนหน้าจอ |
| :--- | :--- | :---: | :---: | :--- | :--- |
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

เพื่อให้สอดคล้องกับแนวทางการเล่าเรื่องใน `docs/00-idea-proposal.md` (หัวข้อ 8) หน้าเว็บใน `frontend/app.py` จึงแบ่งเป็น 3 แท็บหลัก:

### แท็บที่ 1: 📚 ข้อมูลรายวิชา & กราฟความขัดแย้ง (Dataset & Conflict Graph)
- **สิ่งที่แสดง:**
  - การ์ดสรุปจำนวนวิชา, จำนวนนักศึกษา, จำนวนการลงทะเบียน และจำนวนวันสอบ
  - **กราฟความขัดแย้งของรายวิชา (Course Conflict Graph):** ดึงข้อมูลจาก `GET /instances/{instance_id}/graph` แสดงจุด (Node) เป็นรายวิชา และเส้นเชื่อม (Edge) เมื่อมีนักศึกษาลงเรียนร่วมกัน (ยิ่งชนหลายวิชายิ่งสีเข้ม)
- **จุดประสงค์ตอนอัดวิดีโอ:** ใช้เปิดเรื่องเพื่ออธิบายว่าทำไมโจทย์จัดตารางสอบจึงแปลงเป็นปัญหา **Graph Coloring** ได้

### แท็บที่ 2: 🧪 ทดลองรันเดี่ยว (Single Algorithm Run)
- **ปุ่มกดสำคัญ:**
  - ปุ่มเลือกวิธี (`🐜 ACO`, `🎲 Random Feasible`, `⚡ Greedy`)
  - ปุ่ม **`▶️ รันจัดตารางสอบ (Solve)`** ซึ่งยิงไปที่ `POST /solve`
- **สิ่งที่แสดงหลังกดปุ่ม:**
  1. **Metric Cards 5 ช่อง:** `Status`, `Hard Conflict Count`, `Penalty Score (P)`, `Attempts`, `Runtime (ms)`
  2. **ตารางสอบสี 2 ช่วงต่อวัน (Morning vs Afternoon Schedule Grid):** แสดงว่าวันที่ 1..D ช่วงเช้าและช่วงบ่ายมีวิชาอะไรสอบบ้าง
  3. **ตารางรายชื่อนักศึกษาที่โดนสอบติดกัน เช้า-บ่าย (`validation_details.consecutive_cases`):** คลิกเปิดดูได้ว่านักศึกษาคนไหน (`S001` ฯลฯ) สอบติดกันในวันไหน
  4. **กราฟการลู่เข้า (Convergence Curve):** วาดจากฟิลด์ `history` แสดงค่า `best_penalty` ที่ลดลงตาม Iteration ของ ACO

### แท็บที่ 3: 🏆 เปรียบเทียบ 3 อัลกอริทึม (Multi-Seed Benchmark Compare)
- **ปุ่มกดสำคัญ:**
  - ปุ่ม **`🚀 เริ่มรันเปรียบเทียบทั้ง 3 วิธี (Run Benchmark)`** ซึ่งยิงไปที่ `POST /compare`
- **สิ่งที่แสดงหลังกดปุ่ม:**
  1. **ตารางสรุปผลรวม (Summary Table):** เทียบ `Success Rate (%)`, `Best Penalty`, `Mean Penalty`, `Median Penalty`, `Std Penalty`, `Mean Runtime (ms)` ของ Greedy vs Random Feasible vs ACO
  2. **กราฟแท่ง (Bar Chart):** เปรียบเทียบ Best Penalty และ Mean Penalty ของทั้ง 3 วิธี
  3. **กราฟกระจายตัว (Box Plot):** แสดงการกระจายของค่า Penalty ในแต่ละ Seed เพื่อพิสูจน์ว่า ACO ให้ผลลัพธ์ที่สม่ำเสมอเพียงใด
  4. *(สิ่งที่โรสพัฒนาต่อยอดได้)*: แสดงตารางสอบที่ดีที่สุดของทั้ง 3 วิธีวางเทียบกัน และปุ่ม Download ผลลัพธ์เป็น CSV สำหรับทำสไลด์สรุป
