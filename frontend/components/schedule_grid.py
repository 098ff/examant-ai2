"""Render a readable two-session examination timetable."""

from collections import defaultdict
from html import escape
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from components.theme import theme_tokens


def _course_metadata(instance_detail: Dict[str, Any]) -> tuple[Dict[str, str], Dict[str, set[str]]]:
    """Build display names and enrolled-student sets for each course."""
    names = {
        course["course_id"]: course.get("course_name", course["course_id"])
        for course in instance_detail.get("courses", [])
    }
    students: Dict[str, set[str]] = defaultdict(set)
    for enrollment in instance_detail.get("enrollments", []):
        students[enrollment["course_id"]].add(enrollment["student_id"])
    return names, students


def _render_session(
    title: str,
    course_ids: List[str],
    course_names: Dict[str, str],
    course_students: Dict[str, set[str]],
    accent: str,
    theme_mode: str,
) -> str:
    """Return HTML for one morning or afternoon timetable session."""
    tokens = theme_tokens(theme_mode)
    unique_students: set[str] = set()
    course_badges = []
    for course_id in sorted(course_ids):
        unique_students.update(course_students.get(course_id, set()))
        label = escape(course_names.get(course_id, course_id))
        count = len(course_students.get(course_id, set()))
        course_badges.append(
            f'<div style="padding:8px 10px;margin:6px 0;border-radius:8px;'
            f'background:{tokens["surface"]};border:1px solid {tokens["border"]};color:{tokens["text"]}">'
            f'<strong>{escape(course_id)}</strong> — {label}'
            f'<span style="float:right;color:{tokens["muted"]}">{count} คน</span></div>'
        )

    body = (
        "".join(course_badges)
        if course_badges
        else f'<div style="color:{tokens["muted"]};padding:10px 0">ไม่มีการสอบ</div>'
    )
    return (
        f'<div style="height:100%;padding:14px;border-radius:12px;background:{tokens["surface_alt"]};'
        f'border-top:4px solid {accent};border-left:1px solid {tokens["border"]};'
        f'border-right:1px solid {tokens["border"]};border-bottom:1px solid {tokens["border"]}">'
        f'<div style="font-weight:700;color:{tokens["text"]};margin-bottom:4px">{escape(title)}</div>'
        f'<div style="font-size:13px;color:{tokens["muted"]};margin-bottom:8px">'
        f'{len(course_ids)} วิชา · ผู้เข้าสอบไม่ซ้ำ {len(unique_students)} คน</div>{body}</div>'
    )


def render_schedule_grid(
    instance_detail: Dict[str, Any],
    schedule: List[Dict[str, str]],
    validation_details: Dict[str, Any] | None = None,
    theme_mode: str = "Light",
) -> None:
    """Render timetable cards and consecutive-exam details from a solve response."""
    if not schedule:
        st.warning("ไม่มีตารางสอบที่จะแสดงผล (ไม่พบคำตอบ หรือยังไม่ได้รันอัลกอริทึม)")
        return

    slots = sorted(instance_detail.get("slots", []), key=lambda slot: (slot["day_index"], slot["slot_index"]))
    slot_lookup = {slot["slot_id"]: slot for slot in slots}
    course_names, course_students = _course_metadata(instance_detail)

    day_courses: Dict[int, Dict[int, List[str]]] = defaultdict(lambda: {1: [], 2: []})
    for item in schedule:
        slot = slot_lookup.get(item["slot_id"])
        if slot:
            day_courses[slot["day_index"]][slot["slot_index"]].append(item["course_id"])

    consecutive_cases = (validation_details or {}).get("consecutive_cases", [])
    penalty_by_day: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for case in consecutive_cases:
        penalty_by_day[case["day_index"]].append(case)

    for day_index in sorted({slot["day_index"] for slot in slots}):
        cases = penalty_by_day.get(day_index, [])
        status = (
            f'<span style="color:#b45309;background:#fef3c7;padding:4px 8px;border-radius:999px">'
            f'Penalty {len(cases)} กรณี</span>'
            if cases
            else '<span style="color:#047857;background:#d1fae5;padding:4px 8px;border-radius:999px">ไม่มี Penalty</span>'
        )
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'margin:18px 0 8px"><h4 style="margin:0">วันที่ {day_index}</h4>{status}</div>',
            unsafe_allow_html=True,
        )
        morning, afternoon = st.columns(2)
        with morning:
            st.markdown(
                _render_session(
                    "ช่วงเช้า (Slot 1)",
                    day_courses[day_index][1],
                    course_names,
                    course_students,
                    "#2563EB",
                    theme_mode,
                ),
                unsafe_allow_html=True,
            )
        with afternoon:
            st.markdown(
                _render_session(
                    "ช่วงบ่าย (Slot 2)",
                    day_courses[day_index][2],
                    course_names,
                    course_students,
                    "#F59E0B",
                    theme_mode,
                ),
                unsafe_allow_html=True,
            )

    if validation_details is None:
        st.caption("ผลนี้ไม่มีรายละเอียดจาก Central Validator จึงยังไม่สามารถแสดงรายกรณี Penalty ได้")
        return

    if consecutive_cases:
        with st.expander(
            f"ดูรายละเอียดนักศึกษาที่ต้องสอบทั้งเช้าและบ่าย ({len(consecutive_cases)} กรณี)",
            icon=":material/search:",
        ):
            details = pd.DataFrame(consecutive_cases).rename(
                columns={
                    "student_id": "Student",
                    "day_index": "Day",
                    "morning_course_id": "Morning course",
                    "afternoon_course_id": "Afternoon course",
                }
            )
            st.dataframe(details, use_container_width=True, hide_index=True)
    else:
        st.success(
            "ไม่มีนักศึกษาคนใดต้องสอบทั้งเช้าและบ่ายในวันเดียวกัน (Penalty = 0)",
            icon=":material/check_circle:",
        )
