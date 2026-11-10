"""
[งานของคนที่ 3: โรส]
Exam Schedule Grid Component (`frontend/components/schedule_grid.py`).

แสดงผลตารางสอบแบ่งตามวัน (Day 1..D) และช่วงสอบ 2 ช่วงต่อวัน:
- ช่วงที่ 1: ช่วงเช้า (`slot_index = 1`)
- ช่วงที่ 2: ช่วงบ่าย (`slot_index = 2`)
พร้อมแสดงรายชื่อกรณีที่นักศึกษาต้องสอบติดกัน เช้า-บ่าย ในวันเดียวกัน (`consecutive_cases`)
"""

from collections import defaultdict
from typing import Any, Dict, List
import pandas as pd
import streamlit as st


def render_schedule_grid(
    instance_detail: Dict[str, Any],
    schedule: List[Dict[str, str]],
    validation_details: Dict[str, Any] | None = None,
) -> None:
    """Render a 2-slots-per-day timetable grid from a solve response."""
    if not schedule:
        st.warning("ไม่มีตารางสอบที่จะแสดงผล (ไม่พบคำตอบ หรือยังไม่ได้รันอัลกอริทึม)")
        return

    slots = sorted(instance_detail.get("slots", []), key=lambda s: (s["day_index"], s["slot_index"]))
    course_name_map = {
        c["course_id"]: f"{c['course_id']} ({c['course_name']})"
        for c in instance_detail.get("courses", [])
    }

    slot_to_courses: Dict[str, List[str]] = defaultdict(list)
    for item in schedule:
        cid = item["course_id"]
        sid = item["slot_id"]
        slot_to_courses[sid].append(course_name_map.get(cid, cid))

    # Build day-by-day rows (Morning vs Afternoon)
    days_map: Dict[int, Dict[str, str]] = defaultdict(lambda: {"ช่วงเช้า (Slot 1)": "-", "ช่วงบ่าย (Slot 2)": "-"})
    for s in slots:
        day_idx = s["day_index"]
        col_name = "ช่วงเช้า (Slot 1)" if s["slot_index"] == 1 else "ช่วงบ่าย (Slot 2)"
        courses_in_slot = sorted(slot_to_courses.get(s["slot_id"], []))
        days_map[day_idx][col_name] = ", ".join(courses_in_slot) if courses_in_slot else "— (ว่าง)"

    rows = []
    for day_idx in sorted(days_map.keys()):
        rows.append(
            {
                "วันสอบ": f"วันที่ {day_idx}",
                "🌅 ช่วงเช้า (slot_index = 1)": days_map[day_idx]["ช่วงเช้า (Slot 1)"],
                "🌇 ช่วงบ่าย (slot_index = 2)": days_map[day_idx]["ช่วงบ่าย (Slot 2)"],
            }
        )

    df_grid = pd.DataFrame(rows)
    st.dataframe(df_grid, use_container_width=True, hide_index=True)

    # Show consecutive exam details if provided by Central Validator
    if validation_details:
        consecutive_cases = validation_details.get("consecutive_cases", [])
        if consecutive_cases:
            with st.expander(f"🔍 ดูรายละเอียดนักศึกษาที่ต้องสอบติดกัน เช้า-บ่าย ({len(consecutive_cases)} กรณี)"):
                st.dataframe(pd.DataFrame(consecutive_cases), use_container_width=True, hide_index=True)
        else:
            st.success("🎉 ไม่มีนักศึกษาคนใดต้องสอบติดกันทั้งเช้าและบ่ายในวันเดียวกันเลย (Penalty = 0)!")
