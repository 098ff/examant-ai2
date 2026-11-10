"""
[Task for Person 3: Rose (Sasarose Buranapin)]
ExamAnt Streamlit Main Application (`frontend/app.py`).

Organized into 3 main tabs for interactive experimentation and 10-minute presentation:
- Tab 1: Dataset & Conflict Graph Explorer
- Tab 2: Single Algorithm Run & Schedule Grid
- Tab 3: Multi-Algorithm Comparison (Greedy vs Random Feasible vs ACO)
"""

import requests
import streamlit as st
from api_client import (
    fetch_conflict_graph,
    fetch_instance_detail,
    fetch_instances,
    post_compare,
    post_solve,
    seed_database,
)
from components.charts import (
    render_comparison_charts,
    render_conflict_graph,
    render_convergence_chart,
)
from components.schedule_grid import render_schedule_grid
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="ExamAnt — ACO Exam Timetabling",
    page_icon=":material/pest_control:",
    layout="wide",
)

st.title(":material/pest_control: ExamAnt — จัดตารางสอบไม่ให้ชน และลดการสอบติดกันด้วย ACO")
st.caption(
    "เปรียบเทียบ **Greedy**, **Random Feasible** และ **Ant Colony Optimization (ACO)** "
    "ภายใต้ข้อจำกัดห้ามสอบชนกัน และลดการสอบติดกัน (เช้า+บ่าย) ในวันเดียวกัน"
)

# 1. Load dataset instances from Backend
try:
    instances = fetch_instances()
except requests.exceptions.HTTPError as exc:
    if exc.response is not None and exc.response.status_code == 503:
        st.error("**MongoDB ยังไม่พร้อมใช้งาน (Service Unavailable - HTTP 503)**", icon=":material/warning:")
        st.warning(
            "โปรดตรวจสอบว่าได้รัน MongoDB Container หรือยัง โดยใช้คำสั่งในเทอร์มินัล:\n\n"
            "```bash\n"
            "docker compose up -d mongodb\n"
            "```\n"
            "หรือหากต้องการรันทั้งระบบพร้อมกัน:\n\n"
            "```bash\n"
            "docker compose up --build\n"
            "```"
        )
    else:
        st.error(f"HTTP Error จาก Backend: {exc}")
    st.stop()
except Exception as exc:
    st.error(f"ไม่สามารถเชื่อมต่อกับ FastAPI Backend ได้: {exc}")
    st.info("ตรวจสอบว่า FastAPI Backend รันอยู่ที่พอร์ต 8000 หรือยัง: `docker compose up -d backend`")
    st.stop()

if not instances:
    st.warning("**ยังไม่มีชุดข้อมูลใน MongoDB (Database is empty)**", icon=":material/warning:")
    st.info(
        "ชุดข้อมูล mock ถูกนำออกแล้ว ข้อมูลต้องถูกบันทึกลง MongoDB จริงๆ ผ่าน Seeder Script\n\n"
        "กรุณากดปุ่มด้านล่างเพื่อ Seed ข้อมูลตั้งต้นเข้า MongoDB หรือรันคำสั่ง:\n"
        "```bash\n"
        "python backend/scripts/seed_db.py\n"
        "```"
    )
    if st.button("Seed Database ตอนนี้", icon=":material/database:", type="primary"):
        try:
            with st.spinner("กำลัง seed ข้อมูลเข้า MongoDB..."):
                res = seed_database()
            st.success(res.get("message", "Seed ข้อมูลสำเร็จ!"))
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการ seed: {e}")
    st.stop()

config = render_sidebar(instances)
if not config:
    st.stop()

instance_id = config["instance_id"]
instance_detail = fetch_instance_detail(instance_id)

tab1, tab2, tab3 = st.tabs(
    [
        ":material/menu_book: 1. ข้อมูลรายวิชา & กราฟความขัดแย้ง",
        ":material/science: 2. ทดลองรันเดี่ยว (Single Run)",
        ":material/leaderboard: 3. เปรียบเทียบ 3 อัลกอริทึม (Multi-Seed Compare)",
    ]
)

# ==============================================================================
# TAB 1: Dataset & Conflict Graph Explorer
# ==============================================================================
with tab1:
    st.subheader(f"ชุดข้อมูล: `{instance_detail['instance_id']}` — {instance_detail['name']}")
    st.write(instance_detail.get("description", ""))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("จำนวนรายวิชา (Courses)", len(instance_detail["courses"]))
    c2.metric("จำนวนนักศึกษา (Students)", len(instance_detail["students"]))
    c3.metric("จำนวนการลงทะเบียน (Enrollments)", len(instance_detail["enrollments"]))
    c4.metric("จำนวนช่วงสอบ (Slots)", f"{len(instance_detail['slots'])} ({len(instance_detail['slots']) // 2} วัน)")

    graph_data = fetch_conflict_graph(instance_id)
    render_conflict_graph(graph_data)

# ==============================================================================
# TAB 2: Single Algorithm Run
# ==============================================================================
with tab2:
    st.subheader(":material/science: ทดลองจัดตารางสอบรายอัลกอริทึม")
    col_algo, col_btn = st.columns([3, 1])
    with col_algo:
        selected_algo = st.radio(
            "เลือกอัลกอริทึมที่ต้องการรัน:",
            options=["aco", "random_feasible", "greedy"],
            format_func=lambda x: {
                "aco": ":material/pest_control: Ant Colony Optimization (ACO)",
                "random_feasible": ":material/casino: Random Feasible",
                "greedy": ":material/bolt: Greedy Baseline",
            }[x],
            horizontal=True,
        )
    with col_btn:
        st.write("")
        run_single_clicked = st.button("รันจัดตารางสอบ (Solve)", icon=":material/play_arrow:", type="primary", use_container_width=True)

    if run_single_clicked:
        params_payload = {
            "seed": config["seed"],
            "max_attempts": config["max_attempts"],
            **config["aco"],
        }
        with st.spinner(f"กำลังรัน {selected_algo.upper()}..."):
            res = post_solve(instance_id, selected_algo, params_payload)
            st.session_state["last_single_result"] = res

    if "last_single_result" in st.session_state:
        res = st.session_state["last_single_result"]
        if res.get("message"):
            st.info(res["message"])

        metrics = res["metrics"]
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("สถานะ (Status)", res["status"].upper())
        m2.metric("สอบชนกัน (Hard Conflict)", metrics["hard_conflict_count"])
        m3.metric("สอบติดกัน เช้า-บ่าย (Penalty P)", metrics["penalty_score"])
        m4.metric("จำนวนตารางที่ลอง (Attempts)", metrics["attempts"])
        m5.metric("เวลาที่ใช้ (Runtime)", f"{metrics['runtime_ms']:.2f} ms")

        st.markdown("#### :material/calendar_month: ตารางสอบที่จัดได้ (2 ช่วงต่อวัน: เช้า / บ่าย)")
        render_schedule_grid(instance_detail, res.get("schedule", []), res.get("validation_details"))

        if res.get("history"):
            render_convergence_chart(res["history"], title=f"กราฟการลู่เข้าของ {res['algorithm'].upper()}")

# ==============================================================================
# TAB 3: Multi-Algorithm Comparison
# ==============================================================================
with tab3:
    st.subheader(":material/leaderboard: เปรียบเทียบ Greedy vs Random Feasible vs ACO")
    st.write(
        f"รันเปรียบเทียบทั้ง 3 อัลกอริทึมบนชุดข้อมูล **`{instance_id}`** "
        f"จำนวน **{config['runs']} รอบ (Seeds {config['seed']} ถึง {config['seed'] + config['runs'] - 1})**"
    )

    if st.button("เริ่มรันเปรียบเทียบทั้ง 3 วิธี (Run Benchmark)", icon=":material/rocket_launch:", type="primary"):
        compare_params = {
            "random_feasible": {"max_attempts": config["max_attempts"]},
            "aco": config["aco"],
        }
        with st.spinner("กำลังรันเปรียบเทียบทั้ง 3 อัลกอริทึม..."):
            comp_res = post_compare(
                instance_id=instance_id,
                algorithms=["greedy", "random_feasible", "aco"],
                runs=config["runs"],
                seed_start=config["seed"],
                parameters=compare_params,
            )
            st.session_state["last_compare_result"] = comp_res

    if "last_compare_result" in st.session_state:
        comp_res = st.session_state["last_compare_result"]
        render_comparison_charts(comp_res)
