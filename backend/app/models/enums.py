from enum import StrEnum



class TrainingSessionStatus(StrEnum):
    CREATED = "created"
    DISPATCHING = "dispatching"
    CONNECTING = "connecting"
    ACTIVE = "active"
    ENDING = "ending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class EvaluationStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"