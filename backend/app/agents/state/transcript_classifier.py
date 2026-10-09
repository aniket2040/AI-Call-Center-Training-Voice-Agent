
from dataclasses import dataclass

from backend.app.agents.state.events import ConversationEvent


@dataclass(frozen=True, slots=True)
class TranscriptClassification:
    """Behavior signals identified in a customer transcript."""

    events: tuple[ConversationEvent, ...] = ()


def classify_transcript(
    transcript: str,
    previous_transcript: str | None = None,
) -> TranscriptClassification:
    """Detect a repeated question by comparing consecutive transcripts."""

    current = " ".join(transcript.casefold().split())

    if not current:
        return TranscriptClassification()

    previous = (
        " ".join(previous_transcript.casefold().split())
        if previous_transcript
        else ""
    )

    if current == previous:
        return TranscriptClassification(
            events=(ConversationEvent.REPEATED_QUESTION,)
        )

    return TranscriptClassification()
