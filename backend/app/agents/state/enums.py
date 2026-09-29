from enum import StrEnum


class CustomerMood(StrEnum):
    CALM = "calm"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


class CustomerPatience(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerificationStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    FAILED = "failed"


class ProblemUnderstandingStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    UNDERSTOOD = "understood"


class EmpathyStatus(StrEnum):
    NOT_DETECTED = "not_detected"
    DETECTED = "detected"


class ResolutionStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class EscalationStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUESTED = "requested"
    ESCALATED = "escalated"