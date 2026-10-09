
from unittest.mock import Mock

from backend.app.agents.training_customer import register_transcript_events
from backend.app.agents.training_customer import (
    TrainingCustomer,
    TrainingScenarioMetadata,
)
from tests.agents.test_training_customer_behavior import make_customer

customer = TrainingCustomer(
        TrainingScenarioMetadata(
            scenario_id=1,
            name="Refund complaint",
            persona="An unhappy customer",
            situation="A refund has not arrived",
            rules=[],
            objectives=[],
        )
    )


def test_final_transcript_is_logged():
    from unittest.mock import patch

    session = Mock()
    registered_handlers = {}

    def register_handler(event_name):
        def decorator(handler):
            registered_handlers[event_name] = handler
            return handler
        return decorator

    session.on.side_effect = register_handler

    customer = make_customer()

    with patch(
        "backend.app.agents.training_customer.logger.info"
    ) as mock_log:
        register_transcript_events(session, customer)

        event = Mock()
        event.is_final = True
        event.transcript = "I have been waiting for my refund."

        registered_handlers["user_input_transcribed"](event)

    mock_log.assert_called_once_with(
        "user_transcript_received",
        transcript=event.transcript,
        classified_events=[],
    )



def test_interim_transcript_is_ignored(capsys):
    session = Mock()
    registered_handlers = {}

    def register_handler(event_name):
        def decorator(handler):
            registered_handlers[event_name] = handler
            return handler
        return decorator

    session.on.side_effect = register_handler

    register_transcript_events(session, customer)

    event = Mock()
    event.is_final = False
    event.transcript = "I have been..."

    registered_handlers["user_input_transcribed"](event)

    captured = capsys.readouterr()
    assert captured.out == ""



def test_final_transcript_does_not_change_behavior_state(capsys):
    from backend.app.agents.training_customer import (
        TrainingCustomer,
        TrainingScenarioMetadata,
    )

    customer = TrainingCustomer(
        TrainingScenarioMetadata(
            scenario_id=1,
            name="Refund complaint",
            persona="An unhappy customer",
            situation="A refund has not arrived",
            rules=[],
            objectives=[],
        )
    )

    session = Mock()
    registered_handlers = {}

    def register_handler(event_name):
        def decorator(handler):
            registered_handlers[event_name] = handler
            return handler
        return decorator

    session.on.side_effect = register_handler

    register_transcript_events(session, customer)

    event = Mock()
    event.is_final = True
    event.transcript = "I understand your concern and will check."

    registered_handlers["user_input_transcribed"](event)

    assert customer.state_engine.state.turn_count == 0
    assert customer.state_engine.state.empathy.value == "not_detected"


def test_repeated_final_transcript_updates_behavior_state():
    customer = make_customer()
    session = Mock()
    registered_handlers = {}

    def register_handler(event_name):
        def decorator(handler):
            registered_handlers[event_name] = handler
            return handler
        return decorator

    session.on.side_effect = register_handler

    register_transcript_events(session, customer)
    handler = registered_handlers["user_input_transcribed"]

    first_event = Mock()
    first_event.is_final = True
    first_event.transcript = "Where is my refund?"

    second_event = Mock()
    second_event.is_final = True
    second_event.transcript = "Where is my refund?"

    handler(first_event)
    handler(second_event)

    state = customer.state_engine.state

    assert state.repeated_question_count == 1
    assert state.event_history.count("repeated_question") == 1
