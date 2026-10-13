
from backend.app.agents.state.enums import (
    CustomerMood,
    CustomerPatience,
    EscalationStatus,
)
from backend.app.agents.state.events import ConversationEvent
from backend.app.agents.training_customer import (
    TrainingCustomer,
    TrainingScenarioMetadata,
    register_tool_execution_events,
)
import json
from unittest.mock import patch
import pytest

def make_scenario(**overrides) -> TrainingScenarioMetadata:
    data = {
        "scenario_id": 1,
        "name": "Refund complaint",
        "persona": "An unhappy customer",
        "situation": "A refund has not arrived",
        "rules": [],
        "objectives": [],
    }
    data.update(overrides)
    return TrainingScenarioMetadata(**data)


def make_customer(**overrides) -> TrainingCustomer:
    return TrainingCustomer(make_scenario(**overrides))


def test_empathy_reduces_frustration_and_improves_patience():
    customer = make_customer()

    customer.apply_behavior_event(ConversationEvent.PROBLEM_IGNORED)
    state = customer.apply_behavior_event(
        ConversationEvent.EMPATHY_DETECTED
    )

    assert state["customer_mood"] == CustomerMood.NEUTRAL
    assert state["customer_patience"] == CustomerPatience.MEDIUM


def test_repeated_failures_increase_frustration():
    customer = make_customer()

    state = customer.apply_behavior_event(
        ConversationEvent.REPEATED_FAILURE
    )

    assert state["failure_count"] == 1
    assert state["customer_mood"] == CustomerMood.FRUSTRATED


def test_failure_threshold_triggers_escalation():
    customer = make_customer(escalate_if_repeated_failures=2)

    customer.apply_behavior_event(ConversationEvent.REPEATED_FAILURE)
    state = customer.apply_behavior_event(
        ConversationEvent.REPEATED_FAILURE
    )

    assert state["failure_count"] == 2
    assert state["escalation"] == EscalationStatus.REQUESTED
    assert (
        state["event_history"][-1]
        == ConversationEvent.ESCALATION_TRIGGERED.value
    )


def test_each_customer_has_independent_state():
    first = make_customer()
    second = make_customer()

    first.apply_behavior_event(ConversationEvent.REPEATED_FAILURE)

    assert first.state_engine.state.failure_count == 1
    assert second.state_engine.state.failure_count == 0



def test_automatic_escalation_records_supervisor_escalation():
    customer = make_customer(escalate_if_repeated_failures=1)

    state = customer.apply_behavior_event(
        ConversationEvent.REPEATED_FAILURE
    )

    assert state["escalation"] == EscalationStatus.REQUESTED
    assert customer.tool_state.escalated is True
    assert customer.tool_state.escalation_id is not None
    assert (
        customer.tool_state.escalation_reason
        == "Repeated failure threshold reached"
    )

def test_each_customer_has_independent_tool_event_history():
    first = make_customer()
    second = make_customer()

    first.tool_events.record_success(
        "lookup_customer",
        "Customer lookup succeeded",
    )

    assert len(first.tool_events.records) == 1
    assert second.tool_events.records == []




@pytest.mark.asyncio
async def test_request_supervisor_updates_tool_and_conversation_state():
    customer = make_customer()

    result = await customer.request_supervisor(
        reason="Customer requests human assistance"
    )
    result_data = json.loads(result)

    assert result_data["status"] == "requested"
    assert customer.tool_state.escalated is True
    assert customer.tool_state.escalation_reason == (
        "Customer requests human assistance"
    )
    assert (
        "escalation_triggered"
        in customer.state_engine.state.event_history
    )
    assert customer.tool_events.records[-1].tool_name == "request_supervisor"
    assert customer.tool_events.records[-1].status == "success"



from livekit.agents.llm.chat_context import FunctionCall
from livekit.agents.voice.events import (
    ToolCallEnded,
    ToolCallStarted,
    ToolExecutionUpdatedEvent,
)

@pytest.mark.asyncio
async def test_lookup_customer_returns_tool_result_and_records_state():
    customer = make_customer()

    result = await customer.lookup_customer(customer_id="CUST-A100")
    result_data = json.loads(result)

    assert result_data["customer_id"] == "CUST-A100"
    assert customer.tool_events.records[-1].tool_name == "lookup_customer"
    assert customer.tool_events.records[-1].status == "success"
    assert (
        "tool_execution_succeeded"
        in customer.state_engine.state.event_history
    )


def test_tool_execution_events_log_start_and_end(caplog):
    class FakeSession:
        def __init__(self):
            self.handlers = {}

        def on(self, event_name):
            def decorator(callback):
                self.handlers[event_name] = callback
                return callback
            return decorator

    session = FakeSession()
    register_tool_execution_events(session)

    call = FunctionCall(
        call_id="call-123",
        name="lookup_customer",
        arguments='{"customer_id": "CUST-A100"}',
    )

    with patch(
            "backend.app.agents.training_customer.logger.info"
    ) as mock_info:
        session.handlers["tool_execution_updated"](
            ToolExecutionUpdatedEvent(
                update=ToolCallStarted(function_call=call)
            )
        )
        session.handlers["tool_execution_updated"](
            ToolExecutionUpdatedEvent(
                update=ToolCallEnded(
                    id="call-123",
                    call_id="call-123",
                    status="done",
                    message='{"name": "Example Customer"}',
                )
            )
        )

    events = {
        call.args[0]: call.kwargs
        for call in mock_info.call_args_list
    }

    assert "agent_tool_execution_started" in events
    assert "agent_tool_execution_ended" in events
    assert events["agent_tool_execution_started"]["tool_name"] == "lookup_customer"
    assert events["agent_tool_execution_ended"]["execution_status"] == "done"

    logged_text = repr(mock_info.call_args_list)
    assert "CUST-A100" not in logged_text
    assert "Example Customer" not in logged_text



