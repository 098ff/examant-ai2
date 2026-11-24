<p align="right">
  <a href="07-benchmark-results-rose.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 📊 ผลการทดลองเปรียบเทียบอัลกอริทึมเบื้องต้นและการวิเคราะห์ผล (Baseline Benchmark Results)

> **รายวิชา:** AI2 (2110477)  
> **ผู้จัดทำ:** 6632213421 Sasarose Buranapin (Rose) — Frontend, Data Visualization & Experiment Analysis  
> **วันที่ทำการทดลอง:** 17 พฤศจิกายน 2026

---

## 1. การตั้งค่าการทดลอง (Experimental Setup)

- **อัลกอริทึมที่เปรียบเทียบ:** Greedy, Random Feasible และ Ant Colony Optimization (ACO)
- **ชุดข้อมูล (Datasets):** `demo_01`, `easy_01`, `medium_01` และ `hard_01`
- **จำนวนรอบการทดลอง (Stochastic Runs):** 10 รอบ (`seed = 42` ถึง `51`)
- **งบการค้นหาของ Random Feasible:** `max_attempts = 400`
- **งบการค้นหาของ ACO:** `num_ants = 20`, `iterations = 20` (สร้างตารางรวม `400` ตารางเท่ากันเพื่อความยุติธรรม)
- **ค่าพารามิเตอร์ ACO เริ่มต้น:** `alpha = 1.0`, `beta = 2.0`, `rho = 0.2`, `q = 1.0`, `initial_pheromone = 1.0`
- **วิธีพื้นฐานแบบ Deterministic:** Greedy ให้ผลลัพธ์เดิมเสมอ จึงรัน 1 รอบต่อชุดข้อมูล
- **เกณฑ์การวัดผล:** เวลาประมวลผล (Runtime) วัดเฉพาะส่วนคำนวณของอัลกอริทึม ตารางคำตอบทุกรอบผ่านการตรวจด้วย Central Validator (`hard_conflict_count == 0`) และสถิติค่า Penalty คำนวณเฉพาะรอบที่หาคำตอบสำเร็จ

---

## 2. ตารางผลการทดลอง (Empirical Results)

| ชุดข้อมูล | อัลกอริทึม | Success Rate | Best Penalty ($P$) | Mean Penalty | Median Penalty | Std Penalty | Mean Runtime (ms) | ผู้ชนะด้านคุณภาพบน Dashboard (Best Quality) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `demo_01` | Greedy | 100% | 7 | 7.0 | 7.0 | 0.00 | 0.22 | Random Feasible / ACO *(Median เท่ากันที่ 5.0)* |
| `demo_01` | Random Feasible | 100% | 5 | 5.0 | 5.0 | 0.00 | 42.10 | Random Feasible / ACO *(Median เท่ากันที่ 5.0)* |
| `demo_01` | ACO | 100% | 5 | 5.0 | 5.0 | 0.00 | 51.80 | Random Feasible / ACO *(Median เท่ากันที่ 5.0)* |
| `easy_01` | Greedy | 100% | 6 | 6.0 | 6.0 | 0.00 | 0.304 | **ACO** *(Median 3.0)* |
| `easy_01` | Random Feasible | 100% | 3 | 3.8 | 3.5 | 0.92 | 78.472 | **ACO** *(Median 3.0)* |
| `easy_01` | ACO | 100% | 3 | 3.0 | 3.0 | 0.00 | 84.327 | **ACO** *(Median 3.0)* |
| `medium_01` | Greedy | 100% | 15 | 15.0 | 15.0 | 0.00 | 0.363 | Random Feasible / ACO *(Median เท่ากันที่ 8.0)* |
| `medium_01` | Random Feasible | 100% | 8 | 8.0 | 8.0 | 0.00 | 40.227 | Random Feasible / ACO *(Median เท่ากันที่ 8.0)* |
| `medium_01` | ACO | 100% | 8 | 10.1 | 8.0 | 3.38 | 54.512 | Random Feasible / ACO *(Median เท่ากันที่ 8.0)* |
| `hard_01` | Greedy | 100% | 20 | 20.0 | 20.0 | 0.00 | 1.187 | **ACO** *(Median 12.0)* |
| `hard_01` | Random Feasible | 100% | 12 | 17.3 | 18.0 | 2.11 | 136.227 | **ACO** *(Median 12.0)* |
| `hard_01` | ACO | 100% | 12 | 12.2 | 12.0 | 0.63 | 162.535 | **ACO** *(Median 12.0)* |

---

## 3. ข้อค้นพบสำคัญ (Key Findings)

1. **ทุกอัลกอริทึมสร้างตารางสอบที่ถูกกฎ 100%:** ทั้ง 3 วิธีสร้างตารางที่ไม่มีการสอบชนกันเลย (`hard_conflict_count == 0`, `Success Rate = 100.0%` เท่ากันทั้ง `Greedy / Random Feasible / ACO`) ทำให้สามารถเปรียบเทียบคุณภาพการลดการสอบติดกัน (Penalty $P$) และเวลาประมวลผลได้อย่างตรงไปตรงมา
2. **ความเสถียรของ ACO บน `easy_01`:** ACO ให้ผลลัพธ์ที่สม่ำเสมอที่สุดบน `easy_01` โดยทำค่า Penalty ต่ำสุด $P = 3$ ได้ครบทั้ง 10 Seeds (`mean = 3.0, median = 3.0, std = 0.0`) ในขณะที่ Random Feasible มีค่า Median อยู่ที่ `3.5` (`mean = 3.8`) และ Greedy ได้ค่า Penalty `6`
3. **กรณีคะแนน Median เท่ากันและ Premature Convergence บน `medium_01`:** บน `medium_01` ทั้ง Random Feasible และ ACO ทำค่า Best และ Median Penalty ได้เท่ากันที่ `8.0` (แสดงผู้ชนะร่วมเป็น `Random Feasible / ACO` บนหน้า Dashboard) อย่างไรก็ตาม มี 3 Seeds ที่ฟีโรโมนในรอบแรกๆ ของ ACO (เมื่อใช้ค่าเริ่มต้น $\beta = 2.0$) ดึงฝูงมดไปติดอยู่ที่จุดต่ำสุดเฉพาะที่แบบเดียวกับ Greedy ($P = 15$) ทำให้ค่า Mean ของ ACO สูงกว่า (`10.1` เทียบกับ `8.0`)
4. **ความได้เปรียบที่ชัดเจนของ ACO บนโจทย์ยาก `hard_01`:** บนชุดข้อมูล `hard_01` (15 วิชา, 90 นักศึกษา, 8 ช่วงสอบ) ACO แสดงประสิทธิภาพเหนือกว่าวิธีอื่นอย่างชัดเจน โดยได้ค่า Median Penalty เพียง **`12.0`** (`mean = 12.2, std = 0.63`) เทียบกับ Random Feasible ที่ได้ Median `18.0` (`mean = 17.3, std = 2.11`) และ Greedy ที่ได้ `20.0`
5. **ความคุ้มค่าระหว่างคุณภาพคำตอบกับเวลาประมวลผล (Quality vs. Runtime Trade-off):** Greedy ใช้เวลาน้อยที่สุดในทุกชุดข้อมูล (ต่ำกว่า `1.2 ms`) แต่แลกมาด้วยค่า Penalty สูงที่สุดในทุกชุดข้อมูลเช่นกัน

---

## 4. การตีความผลลัพธ์ การแสดงผลบน UI และข้อจำกัด

- ผลการทดลองยืนยันว่าภายใต้จำนวนตารางที่ทดลองสร้างเท่ากัน (`400` ตาราง) การเรียนรู้ผ่านรอยฟีโรโมนของ ACO ช่วยลดจำนวนการสอบติดกันเช้า-บ่ายและเพิ่มความสม่ำเสมอของคำตอบได้อย่างมีนัยสำคัญบนโจทย์ที่มีความซับซ้อนสูง (`hard_01`)
- ในขณะเดียวกัน ผลลัพธ์บน `medium_01` สะท้อนทฤษฎี Swarm Intelligence จากสไลด์เรียนวิชา AI2 ได้อย่างชัดเจน: หากให้น้ำหนัก Heuristic ($\beta$) สูงร่วมกับ Positive Feedback ของฟีโรโมน อาจทำให้ฝูงมดลู่เข้าสู่คำตอบแบบ Greedy เร็วเกินไป (Premature Convergence) ซึ่งสามารถปรับจูน $\alpha, \beta, \rho$ บน Sidebar เพื่อศึกษาพฤติกรรมนี้ได้โดยตรง
- บนหน้าเว็บ **Streamlit Comparison Dashboard (`Tab 3`)** ระบบจะแสดงชื่อผู้ชนะร่วมโดยคั่นด้วย `" / "` เมื่อมีค่าสถิติเท่ากัน (เช่น `Greedy / Random Feasible / ACO` สำหรับ `100.0%` Success Rate หรือ `Random Feasible / ACO` เมื่อค่า Median Penalty เท่ากัน) และไฮไลต์การ์ดรายวิชาที่มีนักศึกษาสอบติดกันเช้า-บ่ายให้เห็นทันทีในตารางสอบแต่ละวัน
