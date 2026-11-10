<p align="right">
  <a href="02-aco-theory-and-mapping.md">🇬🇧 English</a> | <b>🇹🇭 ภาษาไทย</b>
</p>

# 🐜 สรุปทฤษฎี ACO จากสไลด์เรียน (`AI2 Slide.pdf`) และการประยุกต์ใช้ใน ExamAnt

> **รายวิชา:** AI2 (2110477)  
> **สมาชิกในกลุ่ม:**  
> 1. 6631305321 Chanatda Konchom (Fai)  
> 2. 6632213421 Sasarose Buranapin (Rose)  
> 3. 6630333721 Sippapas Chavanont (Mai)  
>  
> เอกสารนี้สรุปเนื้อหาสำคัญจากสไลด์วิชา AI2 (2110477) (**Swarm Intelligence: From Natural to Artificial Systems — Bonabeau, Dorigo, Theraulaz**) และเชื่อมโยงทุกสมการเข้ากับโค้ดของโปรเจกต์ **ExamAnt** โดยตรง เพื่อใช้ตรวจสอบความถูกต้องทางทฤษฎีและใช้อธิบายในวิดีโอนำเสนอ

---

## 1. แนวคิดพื้นฐานจากสไลด์เรียน (หน้า 1–17)

1. **Swarm Intelligence (SI) (หน้า 2):**
   - พฤติกรรมรวมหมู่ของ Agent ที่ไม่ซับซ้อน (มดแต่ละตัว) ซึ่งมีปฏิสัมพันธ์ในระดับท้องถิ่น (Local interaction) กับสภาพแวดล้อม จนเกิดเป็นรูปแบบการแก้ปัญหาระดับ Global โดยไม่ต้องมีศูนย์กลางควบคุม
2. **Stigmergy (หน้า 4–9):**
   - การสื่อสารทางอ้อม (Indirect communication) ผ่านการปรับเปลี่ยนสถานะของสภาพแวดล้อม (เช่น การวางรอย **Pheromone**) ซึ่งมดตัวอื่นสามารถรับรู้ได้ในระดับ Local และปรับพฤติกรรมการเลือกของตัวเองตามรอยนั้น
3. **Positive Feedback vs Negative Feedback (หน้า 11, 17):**
   - **Positive Feedback:** ตารางสอบที่ดี (Penalty ต่ำ) จะได้รับการสะสม Pheromone มากขึ้น ดึงดูดให้มดในรอบถัดๆ ไปเลือกจับคู่วิชากับช่วงสอบนั้นมากขึ้น
   - **Negative Feedback (Pheromone Evaporation):** การระเหยของฟีโรโมนด้วยอัตรา $\rho$ ช่วยป้องกันไม่ให้ฝูงมดติดอยู่ในคำตอบย่อยที่ยังไม่ใช่คำตอบที่ดีที่สุด (Premature Convergence / Local Optima)

---

## 2. การแปลงโจทย์จัดตารางสอบให้ตรงกับ Ant System (AS) & AS-QAP (หน้า 18–35)

ในสไลด์เรียนได้ยกตัวอย่างการนำ Ant System (AS) ไปแก้โจทย์ **TSP (หน้า 18–22)**, **Quadratic Assignment Problem: AS-QAP (หน้า 28–30)** และระบุใน **หน้า 35** ว่า ACO นำไปประยุกต์ใช้กับ **Job-scheduling problem** และ **Graph-coloring** ได้

สำหรับโปรเจกต์ **ExamAnt** เราจำลองปัญหาในรูปผสมระหว่าง **Graph Coloring** และ **Assignment Problem (AS-QAP)** ดังนี้:

| องค์ประกอบในสไลด์เรียน (`AI2 Slide.pdf`) | ความหมายในโจทย์ TSP / QAP | ความหมายและการแทนค่าในโปรเจกต์ **ExamAnt** |
| :--- | :--- | :--- |
| **Agent (มด $k = 1 \dots m$)** | มด 1 ตัวสร้างเส้นทางเดินครบทุกเมือง | มด 1 ตัวสร้างตารางสอบครบทุกวิชา (`partial_schedule`) |
| **Decision Step $(i \to j)$** | เลือกเมืองถัดไป หรือเลือก Activity $j$ ลง Location $i$ (หน้า 29) | เลือกช่วงสอบ $t \in \text{Slots}$ ให้กับรายวิชา $c \in \text{Courses}$ |
| **Tabu List / Feasible Set ($J_i^k$) (หน้า 18)** | รายชื่อเมืองที่ยังไม่เคยไปและสามารถเดินไปได้ | รายชื่อช่วงสอบที่ **ไม่ละเมิด Hard Constraint** (`graph.get_feasible_slots(c, partial_schedule)`) |
| **Visibility / Heuristic ($\eta_{ij}$) (หน้า 18)** | ข้อมูลเฉพาะหน้า เช่น $\frac{1}{d_{ij}}$ (ยิ่งใกล้ยิ่งค่าสูง) | $\eta(c, t) = \frac{1}{1 + \Delta P(c, t)}$ เมื่อ $\Delta P$ คือจำนวนนักศึกษาที่จะต้องสอบติดกัน (เช้า+บ่าย) เพิ่มขึ้นหากวางวิชา $c$ ลงช่วง $t$ |
| **Pheromone Trail ($\tau_{ij}(t)$) (หน้า 18)** | ความปรารถนาสะสมจากการเรียนรู้ของฝูงมด | $\tau[c][t]$ = ความเหมาะสมสะสมของการจัดวิชา $c$ ลงช่วงสอบ $t$ |

---

## 3. สมการคณิตศาสตร์ที่ใช้ใน `backend/app/algorithms/aco.py`

### 3.1 กฎการเลือกช่วงสอบ (Transition Rule — สไลด์หน้า 19, 20, 29)
เมื่อมดตัวที่ $k$ กำลังจะเลือกช่วงสอบให้กับวิชา $c$ ความน่าจะเป็นที่จะเลือกช่วงสอบ $t \in J_c^k$ (เมื่อ $J_c^k$ คือเซตของช่วงสอบที่ผ่าน Hard Constraint) คือ:

$$p_{c,t}^k = \frac{[\tau_{c,t}]^\alpha \cdot [\eta_{c,t}]^\beta}{\sum_{u \in J_c^k} [\tau_{c,u}]^\alpha \cdot [\eta_{c,u}]^\beta}$$

โดยที่:
- $\eta_{c,t} = \frac{1}{1 + \Delta P(c, t)}$ (บวก $1$ ในตัวส่วนเพื่อป้องกันการหารด้วย $0$ เมื่อ $\Delta P = 0$; หากช่วงสอบใดไม่เพิ่มการสอบติดกันเลย จะได้ $\eta_{c,t} = 1.0$ สูงสุด)
- **บทบาทของ $\alpha$ และ $\beta$ (สไลด์หน้า 20):**
  - ถ้า $\alpha = 0$: มดจะไม่สนใจ Pheromone เลย กลายเป็น Stochastic Greedy ที่ดูแต่ค่า Heuristic $\eta$
  - ถ้า $\beta = 0$: มดจะดูเฉพาะ Pheromone อย่างเดียว ซึ่งทำให้ลู่เข้าสู่คำตอบที่ไม่เหมาะสมอย่างรวดเร็ว (Rapid selection of suboptimal tours)
  - ดังนั้นจึงต้องปรับสมดุลระหว่าง $\alpha$ (Exploitation ข้อมูลสะสม) และ $\beta$ (Heuristic เฉพาะหน้า) เช่น ค่าตั้งต้น $\alpha = 1.0, \beta = 2.0$

### 3.2 กฎการระเหยและฝากฟีโรโมน (Pheromone Decay & Update — สไลด์หน้า 21, 30)
หลังจากมดทั้ง `num_ants` ตัวในรอบ (Iteration) นั้นสร้างตารางเสร็จ:

1. **การระเหยของฟีโรโมน (Pheromone Decay / Evaporation):**
   $$\tau_{c,t} \leftarrow (1 - \rho) \cdot \tau_{c,t}$$
   เมื่อ $\rho \in (0, 1)$ คืออัตราการระเหย (Evaporation rate)

2. **การเติมฟีโรโมน (Pheromone Deposit):**
   สำหรับมด $k$ ที่สร้างตารางสำเร็จครบทุกวิชาและไม่ชนกันเลย (Valid Schedule $T^k$) โดยมีคะแนนสอบติดกันรวมทั้งตารางเท่ากับ $P_k$:
   $$\Delta \tau_{c,t}^k = \begin{cases} \dfrac{Q}{1 + P_k} & \text{ถ้ามด } k \text{ จัดวิชา } c \text{ ลงช่วงสอบ } t \\ 0 & \text{กรณีอื่นๆ} \end{cases}$$
   จากนั้นอัปเดตค่าฟีโรโมนรวม:
   $$\tau_{c,t} \leftarrow \tau_{c,t} + \sum_{k \in \text{ValidAnts}} \Delta \tau_{c,t}^k$$

   > **หมายเหตุสำคัญสำหรับเขียนอธิบายในรายงาน/วิดีโอ:**  
   > ในโจทย์ TSP (สไลด์หน้า 21) ความยาวเส้นทาง $L_k > 0$ เสมอ จึงใช้ $Q / L_k$ ได้ แต่ในโจทย์ตารางสอบ ค่า Penalty $P_k$ สามารถเป็น $0$ ได้ (เมื่อไม่มีใครสอบติดกันเลย) เราจึงนิยามต้นทุนเป็น $L_k = 1 + P_k$ เพื่อให้ตารางที่มี $P_k = 0$ ได้รับฟีโรโมนสูงสุดเท่ากับ $Q$ โดยไม่เกิด Division by Zero

3. **ทางเลือกเสริม (Elitist / ACS Update — สไลด์หน้า 22, 25):**
   - สามารถเสริมฟีโรโมนพิเศษให้กับตารางที่ดีที่สุดตั้งแต่เริ่มรัน (`global_best_schedule`, $T^+$) ตามแนวคิด **Elitist Ant System (สไลด์หน้า 22)** เพื่อช่วยให้การลู่เข้าเสถียรขึ้นได้ด้วย
