from enum import StrEnum


class TrainingSessionStatus(StrEnum):
    CREATED = "created"
    DISPATCHED = "dispatched"
    CONNECTING = "connecting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EvaluationStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"