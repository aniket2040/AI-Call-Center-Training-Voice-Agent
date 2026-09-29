from backend.app.agents.state.events import ConversationEvent
from backend.app.agents.state.models import ConversationState
from backend.app.agents.state.transitions import (
    TransitionContext,
    apply_transition,
    complete_objective,
)


class ConversationStateEngine:
    """
    Domain engine responsible for maintaining conversation state.

    This class has no dependency on LiveKit, FastAPI, PostgreSQL,
    STT, LLM, or TTS.
    """

    def __init__(
        self,
        initial_state: ConversationState | None = None,
    ) -> None:
        self._state = initial_state or ConversationState()

    @property
    def state(self) -> ConversationState:
        """Return the current inspectable state."""
        return self._state.model_copy(deep=True)

    def apply_event(
        self,
        event: ConversationEvent,
        *,
        context: TransitionContext | None = None,
    ) -> ConversationState:
        """Apply a deterministic state transition."""

        self._state = apply_transition(
            self._state,
            event,
            context,
        )

        return self.state

    def complete_objective(
        self,
        objective: str,
    ) -> ConversationState:
        """Mark a scenario objective as completed."""

        self._state = complete_objective(
            self._state,
            objective,
        )

        return self.state

    def serialize(self) -> dict:
        """Return JSON-serializable state."""

        return self._state.to_dict()