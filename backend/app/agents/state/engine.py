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
            allowed_objectives: list[str] | set[str] | None = None,
    ) -> None:
        self._state = initial_state or ConversationState()
        self._allowed_objectives = frozenset(
            objective.strip()
            for objective in (allowed_objectives or [])
            if objective.strip()
        )

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

    def record_tool_execution(self, *, succeeded: bool) -> ConversationState:
        """Record a tool execution outcome without changing business state."""
        event = (
            ConversationEvent.TOOL_EXECUTION_SUCCEEDED
            if succeeded
            else ConversationEvent.TOOL_EXECUTION_FAILED
        )
        return self.apply_event(event)

    def complete_objective(
            self,
            objective: str,
    ) -> ConversationState:
        """Mark a valid scenario objective as completed."""
        normalized_objective = objective.strip()

        if normalized_objective not in self._allowed_objectives:
            from backend.app.agents.state.transitions import InvalidStateTransition

            raise InvalidStateTransition(
                f"Objective is not defined by the active scenario: "
                f"{normalized_objective!r}"
            )

        self._state = complete_objective(
            self._state,
            normalized_objective,
        )

        return self.state

    def serialize(self) -> dict:
        """Return JSON-serializable state."""

        return self._state.to_dict()