"""Interactive visualizations and experiment reporting for ExamAnt."""

from typing import Any, Dict, List

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.schedule_grid import render_schedule_grid
from components.theme import ALGORITHM_COLORS, theme_tokens


ALGORITHM_LABELS = {
    "greedy": "Greedy",
    "random_feasible": "Random Feasible",
    "aco": "ACO",
}


def _render_table(frame: pd.DataFrame) -> None:
    """Render a theme-aware, scrollable HTML table."""
    st.markdown(
        f'<div class="examant-table-wrap">{frame.to_html(index=False, classes="examant-table", border=0)}</div>',
        unsafe_allow_html=True,
    )


def _apply_figure_theme(figure: go.Figure, theme_mode: str) -> None:
    """Apply explicit colors so charts switch themes without restarting Streamlit."""
    tokens = theme_tokens(theme_mode)
    figure.update_layout(
        template=tokens["plotly"],
        paper_bgcolor=tokens["surface"],
        plot_bgcolor=tokens["surface"],
        font=dict(color=tokens["text"]),
    )


def render_conflict_graph(graph_data: Dict[str, Any], theme_mode: str = "Light") -> None:
    """Render a weighted course-conflict graph."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    if not nodes:
        st.info("ไม่มีข้อมูลกราฟความขัดแย้ง")
        return

    graph = nx.Graph()
    for node in nodes:
        graph.add_node(
            node["course_id"],
            degree=node["degree"],
            student_count=node["student_count"],
        )
    for edge in edges:
        graph.add_edge(edge["source"], edge["target"], weight=edge["shared_students"])

    positions = nx.spring_layout(graph, seed=42, weight="weight")
    traces: List[go.Scatter] = []
    max_weight = max((data["weight"] for _, _, data in graph.edges(data=True)), default=1)
    for source, target, data in graph.edges(data=True):
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        weight = data["weight"]
        traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=1 + (4 * weight / max_weight), color="#94a3b8"),
                hovertext=f"{source} ↔ {target}<br>นักศึกษาร่วม {weight} คน",
                hoverinfo="text",
                showlegend=False,
            )
        )

    node_x, node_y, node_text, node_hover, node_degree = [], [], [], [], []
    for course_id in graph.nodes():
        x, y = positions[course_id]
        degree = graph.nodes[course_id]["degree"]
        student_count = graph.nodes[course_id]["student_count"]
        node_x.append(x)
        node_y.append(y)
        node_text.append(course_id)
        node_degree.append(degree)
        node_hover.append(f"{course_id}<br>ชนกับ {degree} วิชา<br>นักศึกษา {student_count} คน")

    traces.append(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            hovertext=node_hover,
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="YlOrRd",
                color=node_degree,
                size=26,
                colorbar=dict(title="Conflict degree"),
                line_width=2,
            ),
            showlegend=False,
        )
    )

    figure = go.Figure(
        data=traces,
        layout=go.Layout(
            title="กราฟความขัดแย้งของรายวิชา — เส้นหนาหมายถึงมีนักศึกษาร่วมมาก",
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=60),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=460,
        ),
    )
    _apply_figure_theme(figure, theme_mode)
    st.plotly_chart(figure, use_container_width=True, theme=None)


def render_convergence_chart(
    history: List[Dict[str, Any]],
    title: str = "ACO Convergence Curve",
    theme_mode: str = "Light",
) -> None:
    """Plot global-best and iteration-best penalty across search iterations."""
    if not history:
        st.info("อัลกอริทึมนี้ไม่มีข้อมูล History รายรอบ")
        return

    history_frame = pd.DataFrame(history)
    figure = go.Figure()
    if "best_penalty" in history_frame.columns:
        figure.add_trace(
            go.Scatter(
                x=history_frame["iteration"],
                y=history_frame["best_penalty"],
                mode="lines+markers",
                name="Global best penalty",
                line=dict(width=3, color="#2563eb"),
            )
        )
    if "iteration_best_penalty" in history_frame.columns:
        figure.add_trace(
            go.Scatter(
                x=history_frame["iteration"],
                y=history_frame["iteration_best_penalty"],
                mode="lines",
                name="Iteration best penalty",
                line=dict(width=2, dash="dot", color="#f59e0b"),
            )
        )
    figure.update_layout(
        title=title,
        xaxis_title="Iteration / Attempt",
        yaxis_title="Penalty score (ยิ่งต่ำยิ่งดี)",
        height=360,
        hovermode="x unified",
        template=theme_tokens(theme_mode)["plotly"],
    )
    _apply_figure_theme(figure, theme_mode)
    st.plotly_chart(figure, use_container_width=True, theme=None)


def _summary_frame(summaries: Dict[str, Any]) -> pd.DataFrame:
    """Convert API comparison summaries to a presentation-ready table."""
    rows = []
    for algorithm, summary in summaries.items():
        rows.append(
            {
                "Algorithm": ALGORITHM_LABELS.get(algorithm, algorithm),
                "Runs": summary.get("total_runs", 0),
                "Successful runs": summary.get("successful_runs", 0),
                "Success rate (%)": round(summary.get("success_rate", 0) * 100, 1),
                "Best penalty": summary.get("best_penalty"),
                "Mean penalty": summary.get("mean_penalty"),
                "Median penalty": summary.get("median_penalty"),
                "Std penalty": summary.get("std_penalty"),
                "Mean runtime (ms)": summary.get("mean_runtime_ms"),
                "Mean attempts": summary.get("mean_attempts"),
            }
        )
    return pd.DataFrame(rows)


def _runs_frame(raw_runs: Dict[str, Any]) -> pd.DataFrame:
    """Flatten all raw solver runs for charts and CSV export."""
    rows = []
    for algorithm, runs in raw_runs.items():
        for run_number, result in enumerate(runs, start=1):
            metrics = result.get("metrics", {})
            parameters = result.get("parameters_used", {})
            rows.append(
                {
                    "Algorithm": ALGORITHM_LABELS.get(algorithm, algorithm),
                    "Run": run_number,
                    "Seed": parameters.get("seed"),
                    "Status": result.get("status"),
                    "Penalty": metrics.get("penalty_score") if result.get("status") == "success" else None,
                    "Hard conflicts": metrics.get("hard_conflict_count"),
                    "Runtime (ms)": metrics.get("runtime_ms"),
                    "Attempts": metrics.get("attempts"),
                    "Best iteration": metrics.get("best_iteration"),
                }
            )
    return pd.DataFrame(rows)


def _best_run(raw_runs: Dict[str, Any], algorithm: str, schedule: List[Dict[str, str]]) -> Dict[str, Any] | None:
    """Find the raw run associated with a summary's best schedule."""
    candidates = [run for run in raw_runs.get(algorithm, []) if run.get("status") == "success"]
    for run in candidates:
        if run.get("schedule") == schedule:
            return run
    return min(candidates, key=lambda run: run.get("metrics", {}).get("penalty_score", float("inf")), default=None)


def _experiment_insights(summaries: Dict[str, Any]) -> List[str]:
    """Generate cautious, data-backed observations from comparison summaries."""
    successful = {
        algorithm: summary
        for algorithm, summary in summaries.items()
        if summary.get("successful_runs", 0) > 0 and summary.get("median_penalty") is not None
    }
    if not successful:
        return ["ยังไม่มีอัลกอริทึมใดสร้างตารางสำเร็จ จึงยังเปรียบเทียบคุณภาพคำตอบไม่ได้"]

    best_quality = min(successful, key=lambda algorithm: successful[algorithm]["median_penalty"])
    fastest = min(summaries, key=lambda algorithm: summaries[algorithm].get("mean_runtime_ms", float("inf")))
    most_reliable = max(summaries, key=lambda algorithm: summaries[algorithm].get("success_rate", 0))
    insights = [
        f"{ALGORITHM_LABELS.get(best_quality, best_quality)} มี median penalty ต่ำที่สุด "
        f"({successful[best_quality]['median_penalty']}) ในรอบที่สำเร็จ",
        f"{ALGORITHM_LABELS.get(fastest, fastest)} ใช้เวลาเฉลี่ยต่ำที่สุด "
        f"({summaries[fastest].get('mean_runtime_ms', 0):.2f} ms)",
        f"{ALGORITHM_LABELS.get(most_reliable, most_reliable)} มี success rate สูงที่สุด "
        f"({summaries[most_reliable].get('success_rate', 0) * 100:.1f}%)",
    ]
    if "aco" in successful and "greedy" in successful:
        difference = successful["greedy"]["median_penalty"] - successful["aco"]["median_penalty"]
        if difference > 0:
            insights.append(f"ACO ลด median penalty จาก Greedy ได้ {difference:g} คะแนน แต่ควรพิจารณา runtime ร่วมด้วย")
        elif difference == 0:
            insights.append("ACO และ Greedy มี median penalty เท่ากันในชุดทดลองนี้ จึงยังไม่เห็นประโยชน์ด้านคุณภาพจาก ACO")
        else:
            insights.append(f"Greedy มี median penalty ต่ำกว่า ACO {abs(difference):g} คะแนนในชุดทดลองนี้")
    return insights


def _render_winner_cards(summaries: Dict[str, Any]) -> None:
    """Show the three most important benchmark outcomes before detailed charts."""
    successful = {
        algorithm: summary
        for algorithm, summary in summaries.items()
        if summary.get("successful_runs", 0) > 0 and summary.get("median_penalty") is not None
    }
    if not successful:
        st.warning("ยังไม่มีรอบที่สร้างตารางสำเร็จ จึงยังระบุผู้ชนะไม่ได้")
        return

    best_quality = min(successful, key=lambda algorithm: successful[algorithm]["median_penalty"])
    fastest = min(summaries, key=lambda algorithm: summaries[algorithm].get("mean_runtime_ms", float("inf")))
    most_reliable = max(summaries, key=lambda algorithm: summaries[algorithm].get("success_rate", 0))
    cards = [
        (
            "Best quality",
            ALGORITHM_LABELS.get(best_quality, best_quality),
            f"Median penalty {successful[best_quality]['median_penalty']}",
        ),
        (
            "Fastest",
            ALGORITHM_LABELS.get(fastest, fastest),
            f"{summaries[fastest].get('mean_runtime_ms', 0):.2f} ms average",
        ),
        (
            "Most reliable",
            ALGORITHM_LABELS.get(most_reliable, most_reliable),
            f"{summaries[most_reliable].get('success_rate', 0) * 100:.1f}% success rate",
        ),
    ]
    columns = st.columns(3)
    for column, (eyebrow, winner, value) in zip(columns, cards):
        with column:
            st.markdown(
                f'<div class="winner-card"><div class="eyebrow">{eyebrow}</div>'
                f'<div class="winner">{winner}</div><div class="value">{value}</div></div>',
                unsafe_allow_html=True,
            )


def render_comparison_charts(
    compare_response: Dict[str, Any],
    instance_detail: Dict[str, Any],
    theme_mode: str = "Light",
) -> None:
    """Render complete benchmark results, best schedules, exports, and insights."""
    summaries = compare_response.get("summaries", {})
    raw_runs = compare_response.get("raw_runs", {})
    if not summaries:
        st.warning("ไม่มีข้อมูลผลลัพธ์การเปรียบเทียบ")
        return

    summary_frame = _summary_frame(summaries)
    runs_frame = _runs_frame(raw_runs)

    st.subheader(":material/emoji_events: ผลลัพธ์เด่น")
    _render_winner_cards(summaries)

    st.subheader(":material/bar_chart: สรุปผลการทดลอง")
    st.caption("Penalty statistics คำนวณเฉพาะรอบที่สร้างตารางสำเร็จ ส่วน Success rate ใช้ทุกรอบ")
    _render_table(summary_frame)

    download_summary, download_runs, spacer = st.columns([1, 1, 2])
    with download_summary:
        st.download_button(
            "ดาวน์โหลด Summary CSV",
            summary_frame.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{compare_response.get('instance_id', 'examant')}_summary.csv",
            mime="text/csv",
            icon=":material/download:",
            use_container_width=True,
        )
    with download_runs:
        st.download_button(
            "ดาวน์โหลดผลรายรอบ CSV",
            runs_frame.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{compare_response.get('instance_id', 'examant')}_runs.csv",
            mime="text/csv",
            icon=":material/download:",
            use_container_width=True,
        )

    penalty_col, success_col, runtime_col = st.columns(3)
    with penalty_col:
        penalty_data = summary_frame.dropna(subset=["Best penalty", "Mean penalty"])
        if not penalty_data.empty:
            penalty_long = penalty_data.melt(
                id_vars=["Algorithm"],
                value_vars=["Best penalty", "Mean penalty"],
                var_name="Metric",
                value_name="Penalty",
            )
            figure = px.bar(
                penalty_long,
                x="Algorithm",
                y="Penalty",
                color="Algorithm",
                pattern_shape="Metric",
                barmode="group",
                title="คุณภาพคำตอบ",
                color_discrete_map=ALGORITHM_COLORS,
                template=theme_tokens(theme_mode)["plotly"],
            )
            _apply_figure_theme(figure, theme_mode)
            st.plotly_chart(figure, use_container_width=True, theme=None)
    with success_col:
        figure = px.bar(
            summary_frame,
            x="Algorithm",
            y="Success rate (%)",
            title="Success rate",
            range_y=[0, 100],
            color="Algorithm",
            color_discrete_map=ALGORITHM_COLORS,
            template=theme_tokens(theme_mode)["plotly"],
        )
        figure.update_layout(showlegend=False)
        _apply_figure_theme(figure, theme_mode)
        st.plotly_chart(figure, use_container_width=True, theme=None)
    with runtime_col:
        figure = px.bar(
            summary_frame,
            x="Algorithm",
            y="Mean runtime (ms)",
            title="เวลาเฉลี่ย",
            color="Algorithm",
            color_discrete_map=ALGORITHM_COLORS,
            template=theme_tokens(theme_mode)["plotly"],
        )
        figure.update_layout(showlegend=False)
        _apply_figure_theme(figure, theme_mode)
        st.plotly_chart(figure, use_container_width=True, theme=None)

    st.markdown("#### :material/timeline: ผลแบบรอบต่อรอบ")
    if not runs_frame.empty:
        successful_runs = runs_frame[runs_frame["Status"] == "success"]
        if not successful_runs.empty:
            figure = px.line(
                successful_runs,
                x="Run",
                y="Penalty",
                color="Algorithm",
                markers=True,
                hover_data=["Seed", "Runtime (ms)", "Attempts"],
                title="Penalty ในแต่ละ Run / Seed",
                color_discrete_map=ALGORITHM_COLORS,
                template=theme_tokens(theme_mode)["plotly"],
            )
            figure.update_xaxes(dtick=1)
            _apply_figure_theme(figure, theme_mode)
            st.plotly_chart(figure, use_container_width=True, theme=None)
        _render_table(runs_frame)

    st.markdown("#### :material/calendar_month: ตารางสอบที่ดีที่สุดของแต่ละวิธี")
    schedule_tabs = st.tabs([ALGORITHM_LABELS.get(key, key) for key in summaries])
    for tab, (algorithm, summary) in zip(schedule_tabs, summaries.items()):
        with tab:
            schedule = summary.get("best_run_schedule", [])
            best_run = _best_run(raw_runs, algorithm, schedule)
            if not schedule:
                st.warning("วิธีนี้ยังไม่มีรอบที่สร้างตารางสำเร็จ")
                continue
            if best_run:
                metric_columns = st.columns(4)
                metrics = best_run.get("metrics", {})
                metric_columns[0].metric("Penalty", metrics.get("penalty_score"))
                metric_columns[1].metric("Runtime", f"{metrics.get('runtime_ms', 0):.2f} ms")
                metric_columns[2].metric("Attempts", metrics.get("attempts"))
                metric_columns[3].metric("Seed", best_run.get("parameters_used", {}).get("seed", "—"))
            render_schedule_grid(
                instance_detail,
                schedule,
                best_run.get("validation_details") if best_run else None,
                theme_mode,
            )

    histories = {
        algorithm: summary.get("best_run_history", [])
        for algorithm, summary in summaries.items()
        if summary.get("best_run_history")
    }
    if histories:
        st.markdown("#### :material/trending_down: Convergence ของรอบที่ดีที่สุด")
        history_tabs = st.tabs([ALGORITHM_LABELS.get(key, key) for key in histories])
        for tab, (algorithm, history) in zip(history_tabs, histories.items()):
            with tab:
                render_convergence_chart(
                    history,
                    f"{ALGORITHM_LABELS.get(algorithm, algorithm)} best-run convergence",
                    theme_mode,
                )

    st.markdown("#### :material/lightbulb: Experiment Insights")
    for insight in _experiment_insights(summaries):
        st.markdown(f"- {insight}")
    st.caption(
        "ข้อสรุปนี้อธิบายเฉพาะ dataset, seeds และ parameters ที่เลือกในครั้งนี้ "
        "ไม่ควรใช้สรุปว่าอัลกอริทึมใดดีที่สุดในทุกกรณี"
    )
