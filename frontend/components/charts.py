"""
[Task for Person 3: Rose (Sasarose Buranapin)]
Visualization Charts Component (`frontend/components/charts.py`).

Provides key visualization charts for experimental evaluation and presentation:
1. Course Conflict Graph (connected courses sharing enrolled students)
2. Convergence Curve (best penalty score vs ACO iterations)
3. Multi-Algorithm Comparison Bar/Box Plot (Greedy vs Random Feasible vs ACO)
"""

from typing import Any, Dict, List
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_conflict_graph(graph_data: Dict[str, Any]) -> None:
    """Render an interactive Course Conflict Graph using NetworkX + Plotly."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    if not nodes:
        st.info("ไม่มีข้อมูลกราฟความขัดแย้ง")
        return

    G = nx.Graph()
    for n in nodes:
        G.add_node(n["course_id"], degree=n["degree"], student_count=n["student_count"])
    for e in edges:
        G.add_edge(e["source"], e["target"], weight=e["shared_students"])

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#94a3b8"),
        hoverinfo="none",
        mode="lines",
    )

    node_x, node_y, node_text, node_deg = [], [], [], []
    for cid in G.nodes():
        x, y = pos[cid]
        deg = G.nodes[cid]["degree"]
        scount = G.nodes[cid]["student_count"]
        node_x.append(x)
        node_y.append(y)
        node_deg.append(deg)
        node_text.append(f"{cid}<br>ชนกับ {deg} วิชา<br>นศ. {scount} คน")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[cid for cid in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlOrRd",
            color=node_deg,
            size=26,
            colorbar=dict(title="Conflict Degree"),
            line_width=2,
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="กราฟความขัดแย้งของรายวิชา (Course Conflict Graph)",
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=420,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_convergence_chart(history: List[Dict[str, Any]], title: str = "ACO Convergence Curve") -> None:
    """Plot best penalty score across iterations."""
    if not history:
        st.info("อัลกอริทึมนี้ไม่มีข้อมูล History รายรอบ (เช่น Greedy รันเพียงรอบเดียว)")
        return

    df_hist = pd.DataFrame(history)
    fig = go.Figure()
    if "best_penalty" in df_hist.columns:
        fig.add_trace(
            go.Scatter(
                x=df_hist["iteration"],
                y=df_hist["best_penalty"],
                mode="lines+markers",
                name="Global Best Penalty (P)",
                line=dict(width=3, color="#2563eb"),
            )
        )
    if "iteration_best_penalty" in df_hist.columns:
        fig.add_trace(
            go.Scatter(
                x=df_hist["iteration"],
                y=df_hist["iteration_best_penalty"],
                mode="lines+markers",
                name="Iteration Best Penalty",
                line=dict(width=2, dash="dot", color="#f59e0b"),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Iteration",
        yaxis_title="Penalty Score P (จำนวนคู่สอบติดกัน เช้า-บ่าย)",
        height=360,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_comparison_charts(compare_resp: Dict[str, Any]) -> None:
    """Render summary table and comparison charts from `POST /compare` response."""
    summaries = compare_resp.get("summaries", {})
    raw_runs = compare_resp.get("raw_runs", {})
    if not summaries:
        st.warning("ไม่มีข้อมูลผลลัพธ์การเปรียบเทียบ")
        return

    summary_rows = []
    for algo_key, s in summaries.items():
        summary_rows.append(
            {
                "Algorithm": algo_key.upper(),
                "Success Rate (%)": round(s["success_rate"] * 100, 1),
                "Best Penalty (P)": s["best_penalty"],
                "Mean Penalty": s["mean_penalty"],
                "Median Penalty": s["median_penalty"],
                "Std Penalty": s["std_penalty"],
                "Mean Runtime (ms)": s["mean_runtime_ms"],
                "Mean Attempts": s["mean_attempts"],
            }
        )
    df_sum = pd.DataFrame(summary_rows)
    st.subheader(":material/bar_chart: ตารางสรุปผลการทดลองเปรียบเทียบ (Summary Metrics)")
    st.dataframe(df_sum, use_container_width=True, hide_index=True)

    # Bar chart of Best vs Mean Penalty
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(
            df_sum,
            x="Algorithm",
            y=["Best Penalty (P)", "Mean Penalty"],
            barmode="group",
            title="เปรียบเทียบคะแนนสอบติดกัน (Penalty P — ยิ่งต่ำยิ่งดี)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Boxplot across runs
        run_records = []
        for algo_key, runs_list in raw_runs.items():
            for r in runs_list:
                if r.get("status") == "success":
                    run_records.append(
                        {
                            "Algorithm": algo_key.upper(),
                            "Penalty (P)": r["metrics"]["penalty_score"],
                            "Runtime (ms)": r["metrics"]["runtime_ms"],
                        }
                    )
        if run_records:
            df_runs = pd.DataFrame(run_records)
            fig_box = px.box(
                df_runs,
                x="Algorithm",
                y="Penalty (P)",
                points="all",
                color="Algorithm",
                title="การกระจายตัวของ Penalty (P) ในหลาย Random Seeds",
            )
            st.plotly_chart(fig_box, use_container_width=True)
