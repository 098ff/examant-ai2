"""
Course Conflict Graph & Helper Utilities for ExamAnt.
Shared by all 3 algorithms (Greedy, Random Feasible, ACO) so that feasibility checks,
course ordering, and incremental penalty (Delta P) calculations are 100% consistent.
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple
from app.schemas.models import ExamSlotRecord, ProblemData


class ConflictGraph:
    """
    Precomputes enrollment relationships, conflict graph C(a, b), and slot structures
    from a standardized `ProblemData` object.
    """

    def __init__(self, problem: ProblemData):
        self.problem = problem
        self.courses: List[str] = list(problem.courses)
        self.students: List[str] = list(problem.students)

        # Ordered slots by (day_index, slot_index)
        self.ordered_slots: List[ExamSlotRecord] = sorted(
            problem.slots, key=lambda s: (s.day_index, s.slot_index)
        )
        self.slot_map: Dict[str, ExamSlotRecord] = {s.slot_id: s for s in self.ordered_slots}
        self.slot_ids: List[str] = [s.slot_id for s in self.ordered_slots]

        # Map (day_index, slot_index) -> slot_id and find companion slot on the same day
        self.day_slot_to_id: Dict[Tuple[int, int], str] = {
            (s.day_index, s.slot_index): s.slot_id for s in self.ordered_slots
        }
        self.companion_slot_on_same_day: Dict[str, str] = {}
        for s in self.ordered_slots:
            other_index = 2 if s.slot_index == 1 else 1
            other_slot_id = self.day_slot_to_id.get((s.day_index, other_index))
            if other_slot_id:
                self.companion_slot_on_same_day[s.slot_id] = other_slot_id

        # Build enrollment maps
        self.course_students: Dict[str, Set[str]] = {c: set() for c in self.courses}
        self.student_courses: Dict[str, Set[str]] = {st: set() for st in self.students}

        for enr in problem.enrollments:
            if enr.course_id in self.course_students:
                self.course_students[enr.course_id].add(enr.student_id)
            if enr.student_id in self.student_courses:
                self.student_courses[enr.student_id].add(enr.course_id)

        # Build conflict matrix C(a, b) and adjacency list
        self.shared_students_count: Dict[str, Dict[str, int]] = {
            c: defaultdict(int) for c in self.courses
        }
        self.neighbors: Dict[str, Set[str]] = {c: set() for c in self.courses}

        for i, c1 in enumerate(self.courses):
            s1 = self.course_students[c1]
            for j in range(i + 1, len(self.courses)):
                c2 = self.courses[j]
                s2 = self.course_students[c2]
                overlap = len(s1.intersection(s2))
                if overlap > 0:
                    self.shared_students_count[c1][c2] = overlap
                    self.shared_students_count[c2][c1] = overlap
                    self.neighbors[c1].add(c2)
                    self.neighbors[c2].add(c1)

    def get_conflict_degree(self, course_id: str) -> int:
        """Number of other courses that share at least 1 student with `course_id`."""
        return len(self.neighbors.get(course_id, set()))

    def get_ordered_courses(self) -> List[str]:
        """
        Return courses sorted by conflict degree descending; tie-break by course_id ascending.
        Used by Greedy (Spec 7.1) and ACO (Spec 7.3).
        """
        return sorted(
            self.courses,
            key=lambda cid: (-self.get_conflict_degree(cid), cid),
        )

    def is_slot_feasible(
        self,
        course_id: str,
        slot_id: str,
        partial_schedule: Dict[str, str],
    ) -> bool:
        """
        Check if assigning `course_id` to `slot_id` violates any Hard Constraint
        given `partial_schedule` (mapping of already-assigned course_id -> slot_id).
        """
        if slot_id not in self.slot_map:
            return False

        # Hard Constraint 1: No conflicting course already assigned to `slot_id`
        for neighbor_cid in self.neighbors[course_id]:
            if partial_schedule.get(neighbor_cid) == slot_id:
                return False

        # Hard Constraint 2: No student > 2 exams on the same day
        # (Under 2 slots/day and no same-slot conflict, this is naturally satisfied,
        #  but we verify explicitly as required by Spec Section 2 & 7.)
        target_day = self.slot_map[slot_id].day_index
        for student_id in self.course_students[course_id]:
            exams_on_day = 0
            for enrolled_cid in self.student_courses.get(student_id, set()):
                assigned_slot = partial_schedule.get(enrolled_cid)
                if assigned_slot and self.slot_map[assigned_slot].day_index == target_day:
                    exams_on_day += 1
                    if exams_on_day >= 2:
                        return False

        return True

    def get_feasible_slots(
        self,
        course_id: str,
        partial_schedule: Dict[str, str],
    ) -> List[str]:
        """Return all feasible `slot_id`s (in chronological order) for `course_id`."""
        return [
            slot_id
            for slot_id in self.slot_ids
            if self.is_slot_feasible(course_id, slot_id, partial_schedule)
        ]

    def calculate_delta_penalty(
        self,
        course_id: str,
        slot_id: str,
        partial_schedule: Dict[str, str],
    ) -> int:
        """
        Calculate incremental soft penalty (Delta P) if `course_id` is placed in `slot_id`
        given `partial_schedule`.
        Delta P = number of students in `course_id` who ALREADY have an exam scheduled
        in the companion slot (morning vs afternoon) on the same day.
        """
        other_slot_id = self.companion_slot_on_same_day.get(slot_id)
        if not other_slot_id:
            return 0

        delta_p = 0
        for neighbor_cid in self.neighbors[course_id]:
            if partial_schedule.get(neighbor_cid) == other_slot_id:
                # Assuming no student has 2 courses in `other_slot_id` (since partial_schedule is feasible),
                # each student shared between `course_id` and `neighbor_cid` gets +1 consecutive pair on this day.
                delta_p += self.shared_students_count[course_id][neighbor_cid]

        return delta_p

    def to_graph_dict(self) -> Dict:
        """Export graph nodes and edges for Frontend Conflict Graph visualization."""
        nodes = [
            {
                "course_id": cid,
                "degree": self.get_conflict_degree(cid),
                "student_count": len(self.course_students[cid]),
            }
            for cid in self.courses
        ]
        edges = []
        for i, c1 in enumerate(self.courses):
            for j in range(i + 1, len(self.courses)):
                c2 = self.courses[j]
                w = self.shared_students_count[c1].get(c2, 0)
                if w > 0:
                    edges.append({"source": c1, "target": c2, "shared_students": w})
        return {"nodes": nodes, "edges": edges}
