"""
[Task for Person 3: Rose (Sasarose Buranapin)]
Sidebar Parameter Tuning Component (`frontend/components/sidebar.py`).

Provides sliders and numeric inputs for parameter tuning according to `docs/01-project-idea-spec.md` (Section 5):
- Dataset selector (`instance_id`)
- Shared parameters: `seed`, `runs`
- Random Feasible: `max_attempts`
- ACO parameters: `num_ants`, `iterations`, `alpha`, `beta`, `rho`, `q`, `initial_pheromone`
"""

from typing import Any, Dict, List
import streamlit as st


def render_sidebar(instances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Render sidebar controls and return selected dataset + parameter dictionary."""
    st.sidebar.header(":material/pest_control: ExamAnt Configuration")

    if not instances:
        st.sidebar.warning("ไม่พบชุดข้อมูลใน MongoDB", icon=":material/warning:")
        st.sidebar.caption("เริ่มรัน MongoDB และ Seed ข้อมูลเข้าสู่ระบบ:")
        from api_client import seed_database
        if st.sidebar.button("Seed Database", icon=":material/database:", type="primary"):
            try:
                res = seed_database()
                st.sidebar.success(res.get("message", "Seeded successfully!"))
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"เกิดข้อผิดพลาด: {e}")
        return {}

    instance_options = {
        f"{item['instance_id']} ({item['num_courses']} วิชา, {item['num_days']} วัน)": item["instance_id"]
        for item in instances
    }
    selected_label = st.sidebar.selectbox(
        "1. เลือกชุดข้อมูล (Dataset Instance)",
        options=list(instance_options.keys()),
    )
    instance_id = instance_options[selected_label]

    st.sidebar.markdown("---")
    st.sidebar.subheader("2. พารามิเตอร์หลัก (Common)")
    seed = st.sidebar.number_input("Random Seed (`seed`)", min_value=1, max_value=999999, value=42, step=1)
    runs = st.sidebar.slider("จำนวนรอบเปรียบเทียบหลาย Seed (`runs`)", min_value=1, max_value=30, value=10, step=1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("3. พารามิเตอร์ ACO (Ant System)")
    num_ants = st.sidebar.slider("จำนวนมดต่อรอบ (`num_ants`)", min_value=1, max_value=100, value=20, step=1)
    iterations = st.sidebar.slider("จำนวนรอบ (`iterations`)", min_value=1, max_value=200, value=20, step=1)
    alpha = st.sidebar.slider("น้ำหนัก Pheromone (`alpha` α)", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
    beta = st.sidebar.slider("น้ำหนัก Heuristic (`beta` β)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)
    rho = st.sidebar.slider("อัตราระเหย (`rho` ρ)", min_value=0.01, max_value=0.99, value=0.20, step=0.05)

    with st.sidebar.expander("ตั้งค่าขั้นสูง (Advanced ACO & Random Budget)"):
        q = st.number_input("ค่าคงที่การฝากฟีโรโมน (`q`)", min_value=0.1, max_value=100.0, value=1.0, step=0.5)
        initial_pheromone = st.number_input(
            "ค่าฟีโรโมนเริ่มต้น (`initial_pheromone`)", min_value=0.1, max_value=50.0, value=1.0, step=0.5
        )
        default_budget = int(num_ants * iterations)
        sync_budget = st.checkbox(
            "ตั้งงบ Random `max_attempts` = `num_ants × iterations` (เพื่อเปรียบเทียบอย่างยุติธรรม)",
            value=True,
        )
        if sync_budget:
            max_attempts = default_budget
            st.caption(f"งบการค้นหา (`max_attempts`) = **{max_attempts}** ตาราง")
        else:
            max_attempts = st.number_input(
                "จำนวนครั้งสุ่มสูงสุด (`max_attempts`)", min_value=1, max_value=10000, value=400, step=50
            )

    with st.sidebar.expander(":material/build: เครื่องมือจัดการฐานข้อมูล (Database Tools)"):
        st.caption("อัปเดตหรือเพิ่มชุดข้อมูลล่าสุดลง MongoDB:")
        from api_client import seed_database
        if st.button("Re-seed Datasets เข้า MongoDB", icon=":material/refresh:"):
            try:
                res = seed_database()
                st.success(res.get("message", "Seeded successfully!"))
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    return {
        "instance_id": instance_id,
        "seed": int(seed),
        "runs": int(runs),
        "max_attempts": int(max_attempts),
        "aco": {
            "num_ants": int(num_ants),
            "iterations": int(iterations),
            "alpha": float(alpha),
            "beta": float(beta),
            "rho": float(rho),
            "q": float(q),
            "initial_pheromone": float(initial_pheromone),
        },
    }
