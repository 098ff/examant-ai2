"""
Central Data & API Schemas for ExamAnt.
Follows `docs/01-project-idea-spec.md` (Sections 3, 4, 5, 8) + visualization extensions.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# 1. Dataset / Entity Schemas (Section 3 of Spec)
# ==============================================================================

class CourseRecord(BaseModel):
    course_id: str = Field(..., description="Unique course identifier, e.g., 'C01'")
    course_name: str = Field(..., description="Display name of the course")
    student_count: Optional[int] = Field(default=None, description="Number of enrolled students")


class StudentRecord(BaseModel):
    student_id: str = Field(..., description="Unique simulated student identifier, e.g., 'S001'")


class EnrollmentRecord(BaseModel):
    student_id: str = Field(..., description="Reference to Student.student_id")
    course_id: str = Field(..., description="Reference to Course.course_id")


class ExamSlotRecord(BaseModel):
    slot_id: str = Field(..., description="Unique slot identifier, e.g., 'D1_S1'")
    day_index: int = Field(..., ge=1, description="Day index starting at 1")
    slot_index: Literal[1, 2] = Field(..., description="1 = Morning, 2 = Afternoon")
    label: str = Field(..., description="Display label, e.g., 'Day 1 Morning'")


class ExamInstanceDocument(BaseModel):
    """
    Embedded MongoDB document in `exam_instances` collection (Sections 3.1 - 3.5).
    """
    instance_id: str = Field(..., description="Unique problem instance ID, e.g., 'demo_01'")
    name: str = Field(..., description="Human-readable dataset name")
    seed: int = Field(default=42, description="Random seed used when generating this dataset")
    description: str = Field(default="", description="Short description of dataset difficulty/characteristics")
    courses: List[CourseRecord]
    students: List[StudentRecord]
    enrollments: List[EnrollmentRecord]
    slots: List[ExamSlotRecord]

    def to_problem_data(self) -> "ProblemData":
        """Convert full instance document into standardized algorithm input (Section 3.6)."""
        return ProblemData(
            instance_id=self.instance_id,
            courses=[c.course_id for c in self.courses],
            students=[s.student_id for s in self.students],
            enrollments=self.enrollments,
            slots=self.slots,
        )


class ExamInstanceSummary(BaseModel):
    """Lightweight summary returned by GET /instances."""
    instance_id: str
    name: str
    seed: int
    description: str
    num_courses: int
    num_students: int
    num_enrollments: int
    num_slots: int
    num_days: int


class ProblemData(BaseModel):
    """
    Standardized algorithm input (Section 3.6 of Spec).
    Passed identically to Greedy, Random Feasible, and ACO.
    """
    instance_id: str
    courses: List[str]
    students: List[str]
    enrollments: List[EnrollmentRecord]
    slots: List[ExamSlotRecord]


# ==============================================================================
# 2. Algorithm Parameters & Request Schemas (Sections 4.1, 5, 8)
# ==============================================================================

AlgorithmType = Literal["greedy", "random_feasible", "aco"]
SolveStatusType = Literal["success", "no_solution_found", "invalid_input", "timeout"]


class AlgorithmParameters(BaseModel):
    """Unified parameter model supporting all 3 algorithms (Section 5)."""
    seed: int = Field(default=42, description="Random seed for reproducibility")
    # Random Feasible specific
    max_attempts: int = Field(default=400, ge=1, le=10000, description="Max candidate schedule attempts (Random Feasible)")
    # ACO specific
    num_ants: int = Field(default=20, ge=1, le=200, description="Number of ants per iteration")
    iterations: int = Field(default=20, ge=1, le=500, description="Number of ACO iterations")
    alpha: float = Field(default=1.0, ge=0.0, le=5.0, description="Pheromone weight (alpha)")
    beta: float = Field(default=2.0, ge=0.0, le=5.0, description="Heuristic visibility weight (beta)")
    rho: float = Field(default=0.2, ge=0.01, le=0.99, description="Pheromone evaporation rate (rho)")
    q: float = Field(default=1.0, gt=0.0, le=1000.0, description="Pheromone deposit constant (Q)")
    initial_pheromone: float = Field(default=1.0, gt=0.0, le=100.0, description="Initial pheromone value (tau_0)")


class SolveRequest(BaseModel):
    """Standard request for POST /solve (Section 4.1)."""
    instance_id: str = Field(..., description="Dataset instance ID to load from MongoDB")
    algorithm: AlgorithmType = Field(..., description="Algorithm to run: 'greedy', 'random_feasible', or 'aco'")
    parameters: AlgorithmParameters = Field(default_factory=AlgorithmParameters)
    problem_data: Optional[ProblemData] = Field(
        default=None,
        description="Optional inline problem data override (if not loading from DB)",
    )


class CompareRequest(BaseModel):
    """Standard request for POST /compare (Section 8)."""
    instance_id: str = Field(..., description="Dataset instance ID to compare on")
    algorithms: List[AlgorithmType] = Field(
        default=["greedy", "random_feasible", "aco"],
        description="List of algorithms to compare",
    )
    runs: int = Field(default=10, ge=1, le=100, description="Number of multi-seed runs for stochastic algorithms")
    seed_start: int = Field(default=100, description="Starting seed (run i uses seed_start + i)")
    parameters: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "random_feasible": {"max_attempts": 400},
            "aco": {
                "num_ants": 20,
                "iterations": 20,
                "alpha": 1.0,
                "beta": 2.0,
                "rho": 0.2,
                "q": 1.0,
                "initial_pheromone": 1.0,
            },
        }
    )


# ==============================================================================
# 3. Response & Validation Schemas (Sections 4.2, 4.3, 8)
# ==============================================================================

class ScheduleItem(BaseModel):
    course_id: str
    slot_id: str


class SolveMetrics(BaseModel):
    hard_conflict_count: int = Field(..., description="Number of (student, conflicting course pair) violations (must be 0 for valid)")
    consecutive_exam_pair_count: int = Field(..., description="Number of (student, day) cases with both morning & afternoon exams")
    penalty_score: int = Field(..., description="Soft penalty score (equals consecutive_exam_pair_count in MVP)")
    runtime_ms: float = Field(..., description="Algorithm execution time in milliseconds")
    attempts: int = Field(..., description="Number of candidate schedules constructed/attempted")
    best_iteration: Optional[int] = Field(default=None, description="Iteration where best solution was found (ACO/Random)")


class IterationHistoryPoint(BaseModel):
    """Convergence tracking point per iteration/attempt for Frontend visualization."""
    iteration: int
    best_penalty: Optional[int] = None
    iteration_best_penalty: Optional[int] = None
    feasible_ants: Optional[int] = None


class ConsecutiveCaseDetail(BaseModel):
    """Details of a student having both morning and afternoon exams on the same day."""
    student_id: str
    day_index: int
    morning_course_id: str
    afternoon_course_id: str


class HardConflictDetail(BaseModel):
    """Details of a hard constraint violation (if any)."""
    student_id: str
    slot_id: str
    course_a: str
    course_b: str


class ValidationDetails(BaseModel):
    """Detailed report produced by the independent Central Validator (Section 4.3)."""
    is_valid: bool
    unassigned_courses: List[str] = Field(default_factory=list)
    duplicate_courses: List[str] = Field(default_factory=list)
    invalid_slots: List[str] = Field(default_factory=list)
    exceeded_daily_limit_students: List[str] = Field(default_factory=list)
    hard_conflicts: List[HardConflictDetail] = Field(default_factory=list)
    consecutive_cases: List[ConsecutiveCaseDetail] = Field(default_factory=list)


class SolveResponse(BaseModel):
    """Standard response for POST /solve (Section 4.2 + visualization extensions)."""
    instance_id: str
    algorithm: AlgorithmType
    status: SolveStatusType
    schedule: List[ScheduleItem]
    metrics: SolveMetrics
    parameters_used: Dict[str, Any]
    history: List[IterationHistoryPoint] = Field(default_factory=list)
    validation_details: Optional[ValidationDetails] = None
    message: Optional[str] = None


class AlgorithmComparisonSummary(BaseModel):
    """Aggregated multi-run statistics for a single algorithm in POST /compare."""
    algorithm: AlgorithmType
    total_runs: int
    successful_runs: int
    success_rate: float
    best_penalty: Optional[int] = None
    mean_penalty: Optional[float] = None
    median_penalty: Optional[float] = None
    std_penalty: Optional[float] = None
    mean_runtime_ms: float
    mean_attempts: float
    best_run_schedule: List[ScheduleItem] = Field(default_factory=list)
    best_run_history: List[IterationHistoryPoint] = Field(default_factory=list)


class CompareResponse(BaseModel):
    """Standard response for POST /compare (Section 8)."""
    instance_id: str
    runs: int
    seed_start: int
    summaries: Dict[str, AlgorithmComparisonSummary]
    raw_runs: Dict[str, List[SolveResponse]]
