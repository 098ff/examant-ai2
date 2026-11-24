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
    consecutive_counts: Dict[str, int] | None = None,
    partner_courses: Dict[str, set[str]] | None = None,
) -> str:
    """Return HTML for one morning or afternoon timetable session."""
    tokens = theme_tokens(theme_mode)
    consecutive_counts = consecutive_counts or {}
    partner_courses = partner_courses or {}
    unique_students: set[str] = set()
    course_badges = []
    for course_id in sorted(course_ids):
        unique_students.update(course_students.get(course_id, set()))
        label = escape(course_names.get(course_id, course_id))
        count = len(course_students.get(course_id, set()))
        penalty_count = consecutive_counts.get(course_id, 0)
        partners = sorted(partner_courses.get(course_id, set()))

        if penalty_count > 0:
            card_bg = tokens["penalty_bg"]
            card_border = f'1.5px solid {tokens["penalty_border"]}'
            partner_text = f" คู่กับ {', '.join(escape(p) for p in partners)}" if partners else ""
            penalty_pill = (
                f'<span style="display:inline-block;margin-left:8px;padding:2px 8px;'
                f'border-radius:999px;font-size:11.5px;font-weight:600;'
                f'background:{tokens["penalty_badge_bg"]};color:{tokens["penalty_badge_text"]}">'
                f'สอบติดกัน {penalty_count} คน{partner_text}</span>'
            )
        else:
            card_bg = tokens["surface"]
            card_border = f'1px solid {tokens["border"]}'
            penalty_pill = ""

        course_badges.append(
            f'<div style="padding:8px 10px;margin:6px 0;border-radius:8px;'
            f'background:{card_bg};border:{card_border};color:{tokens["text"]};'
            f'display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">'
            f'<div><strong>{escape(course_id)}</strong> — {label}{penalty_pill}</div>'
            f'<span style="color:{tokens["muted"]};font-size:13px;white-space:nowrap">{count} คน</span></div>'
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

    tokens = theme_tokens(theme_mode)
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
        morning_counts: Dict[str, int] = defaultdict(int)
        afternoon_counts: Dict[str, int] = defaultdict(int)
        morning_partners: Dict[str, set[str]] = defaultdict(set)
        afternoon_partners: Dict[str, set[str]] = defaultdict(set)

        for case in cases:
            m_cid = case.get("morning_course_id")
            a_cid = case.get("afternoon_course_id")
            if m_cid:
                morning_counts[m_cid] += 1
                if a_cid:
                    morning_partners[m_cid].add(a_cid)
            if a_cid:
                afternoon_counts[a_cid] += 1
                if m_cid:
                    afternoon_partners[a_cid].add(m_cid)

        status = (
            f'<span style="color:{tokens["penalty_badge_text"]};background:{tokens["penalty_badge_bg"]};'
            f'padding:4px 10px;border-radius:999px;font-size:13px;font-weight:600">'
            f'Penalty {len(cases)} กรณี</span>'
            if cases
            else (
                f'<span style="color:{tokens["ok_badge_text"]};background:{tokens["ok_badge_bg"]};'
                f'padding:4px 10px;border-radius:999px;font-size:13px;font-weight:600">ไม่มี Penalty</span>'
            )
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
                    morning_counts,
                    morning_partners,
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
                    afternoon_counts,
                    afternoon_partners,
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
