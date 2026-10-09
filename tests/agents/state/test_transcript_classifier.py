
from backend.app.agents.state.events import ConversationEvent
from backend.app.agents.state.transcript_classifier import (
    TranscriptClassification,
    classify_transcript,
)


def test_empty_transcript_returns_no_events():
    assert classify_transcript("") == TranscriptClassification()


def test_whitespace_transcript_returns_no_events():
    assert classify_transcript("   \n ").events == ()


def test_non_repeated_transcript_returns_no_events():
    result = classify_transcript(
        "Please check my refund."
    )

    assert result.events == ()


def test_repeated_transcript_emits_repeated_question():
    result = classify_transcript(
        "Where is my refund?",
        "Where is my refund?",
    )

    assert result.events == (
        ConversationEvent.REPEATED_QUESTION,
    )


def test_repeated_transcript_ignores_case_and_whitespace():
    result = classify_transcript(
        "  WHERE is my refund? ",
        "where is my refund?",
    )

    assert result.events == (
        ConversationEvent.REPEATED_QUESTION,
    )


def test_different_transcripts_do_not_emit_event():
    result = classify_transcript(
        "Where is my refund?",
        "When will my order arrive?",
    )

    assert result.events == ()
