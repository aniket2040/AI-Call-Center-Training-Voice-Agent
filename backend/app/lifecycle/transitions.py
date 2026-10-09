
from backend.app.models.enums import TrainingSessionStatus


class InvalidLifecycleTransition(ValueError):
    """Raised when a session lifecycle transition is not allowed."""


TERMINAL_STATES = frozenset(
    {
        TrainingSessionStatus.COMPLETED,
        TrainingSessionStatus.FAILED,
        TrainingSessionStatus.CANCELLED,
        TrainingSessionStatus.TIMEOUT,
    }
)


VALID_TRANSITIONS = {
    TrainingSessionStatus.CREATED: frozenset(
        {
            TrainingSessionStatus.DISPATCHING,
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.CANCELLED,
        }
    ),
    TrainingSessionStatus.DISPATCHING: frozenset(
        {
            TrainingSessionStatus.CONNECTING,
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.CANCELLED,
            TrainingSessionStatus.TIMEOUT,
        }
    ),
    TrainingSessionStatus.CONNECTING: frozenset(
        {
            TrainingSessionStatus.ACTIVE,
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.CANCELLED,
            TrainingSessionStatus.TIMEOUT,
        }
    ),
    TrainingSessionStatus.ACTIVE: frozenset(
        {
            TrainingSessionStatus.ENDING,
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.CANCELLED,
            TrainingSessionStatus.TIMEOUT,
        }
    ),
    TrainingSessionStatus.ENDING: frozenset(
        {
            TrainingSessionStatus.COMPLETED,
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.TIMEOUT,
        }
    ),
}


def validate_transition(
    current: TrainingSessionStatus,
    target: TrainingSessionStatus,
) -> bool:
    """Validate a lifecycle transition.

    Returns False for an idempotent same-state request.
    Raises InvalidLifecycleTransition for an invalid transition.
    """

    if current == target:
        return False

    allowed = VALID_TRANSITIONS.get(current, frozenset())

    if target not in allowed:
        raise InvalidLifecycleTransition(
            f"Cannot transition session from "
            f"'{current.value}' to '{target.value}'."
        )

    return True