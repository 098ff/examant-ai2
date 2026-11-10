"""
[งานของคนที่ 3: โรส]
ExamAnt Streamlit Main Application (`frontend/app.py`).

แบ่งหน้าจอออกเป็น 3 Tabs เพื่อรองรับการทดลองและการอัดวิดีโอ 10 นาที:
- Tab 1: 📚 สำรวจชุดข้อมูลและกราฟวิชาที่ชนกัน (Dataset & Conflict Graph)
- Tab 2: 🧪 ทดลองรันรายอัลกอริทึม (Single Algorithm Run & Schedule Grid)
- Tab 3: 🏆 เปรียบเทียบทั้ง 3 อัลกอริทึม (Greedy vs Random Feasible vs ACO)
"""

import streamlit as st
from api_client import (
    fetch_conflict_graph,
    fetch_instance_detail,
    fetch_instances,
    post_compare,
    post_solve,
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
    page_icon="🐜",
    layout="wide",
)

st.title("🐜 ExamAnt — จัดตารางสอบไม่ให้ชน และลดการสอบติดกันด้วย ACO")
st.caption(
    "เปรียบเทียบ **Greedy**, **Random Feasible** และ **Ant Colony Optimization (ACO)** "
    "ภายใต้ข้อจำกัดห้ามสอบชนกัน และลดการสอบติดกัน (เช้า+บ่าย) ในวันเดียวกัน"
)

# 1. Load dataset instances from Backend
try:
    instances = fetch_instances()
except Exception as exc:
    st.error(f"ไม่สามารถเชื่อมต่อกับ FastAPI Backend ได้: {exc}")
    st.stop()

config = render_sidebar(instances)
if not config:
    st.stop()

instance_id = config["instance_id"]
instance_detail = fetch_instance_detail(instance_id)

tab1, tab2, tab3 = st.tabs(
    [
        "📚 1. ข้อมูลรายวิชา & กราฟความขัดแย้ง",
        "🧪 2. ทดลองรันเดี่ยว (Single Run)",
        "🏆 3. เปรียบเทียบ 3 อัลกอริทึม (Multi-Seed Compare)",
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
    st.subheader("🧪 ทดลองจัดตารางสอบรายอัลกอริทึม")
    col_algo, col_btn = st.columns([3, 1])
    with col_algo:
        selected_algo = st.radio(
            "เลือกอัลกอริทึมที่ต้องการรัน:",
            options=["aco", "random_feasible", "greedy"],
            format_func=lambda x: {
                "aco": "🐜 Ant Colony Optimization (ACO)",
                "random_feasible": "🎲 Random Feasible",
                "greedy": "⚡ Greedy Baseline",
            }[x],
            horizontal=True,
        )
    with col_btn:
        st.write("")
        run_single_clicked = st.button("▶️ รันจัดตารางสอบ (Solve)", type="primary", use_container_width=True)

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

        st.markdown("#### 📅 ตารางสอบที่จัดได้ (2 ช่วงต่อวัน: เช้า / บ่าย)")
        render_schedule_grid(instance_detail, res.get("schedule", []), res.get("validation_details"))

        if res.get("history"):
            render_convergence_chart(res["history"], title=f"กราฟการลู่เข้าของ {res['algorithm'].upper()}")

# ==============================================================================
# TAB 3: Multi-Algorithm Comparison
# ==============================================================================
with tab3:
    st.subheader("🏆 เปรียบเทียบ Greedy vs Random Feasible vs ACO")
    st.write(
        f"รันเปรียบเทียบทั้ง 3 อัลกอริทึมบนชุดข้อมูล **`{instance_id}`** "
        f"จำนวน **{config['runs']} รอบ (Seeds {config['seed']} ถึง {config['seed'] + config['runs'] - 1})**"
    )

    if st.button("🚀 เริ่มรันเปรียบเทียบทั้ง 3 วิธี (Run Benchmark)", type="primary"):
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
