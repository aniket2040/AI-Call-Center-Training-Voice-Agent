
import pytest

from backend.app.agents.tools import (
    AgentToolState,
    create_support_ticket,
    escalate_to_supervisor,
    get_customer,
    get_order,
    get_refund_status,
)


def test_get_customer_success():
    customer = get_customer("CUST-A100")
    assert customer.customer_id == "CUST-A100"
    assert customer.tier == "premium"


def test_get_customer_invalid_identifier():
    with pytest.raises(ValueError):
        get_customer("invalid")


def test_get_customer_not_found():
    with pytest.raises(LookupError):
        get_customer("CUST-Z999")


def test_get_order_success():
    order = get_order("ORD-A100")
    assert order.order_id == "ORD-A100"
    assert order.status == "delivered"


def test_get_order_not_found():
    with pytest.raises(LookupError):
        get_order("ORD-Z999")


def test_get_refund_status_success():
    refund = get_refund_status("ORD-A100")
    assert refund.status == "pending"
    assert refund.amount == 1499.0


def test_refund_unknown_order():
    with pytest.raises(LookupError):
        get_refund_status("ORD-Z999")


def test_create_support_ticket_success():
    ticket = create_support_ticket(
        "CUST-A100",
        "Package arrived damaged",
    )
    assert ticket.ticket_id.startswith("TKT-")
    assert ticket.status == "open"


def test_create_ticket_for_unknown_customer():
    with pytest.raises(LookupError):
        create_support_ticket(
            "CUST-Z999",
            "Package arrived damaged",
        )


def test_create_ticket_rejects_invalid_issue():
    with pytest.raises(ValueError):
        create_support_ticket("CUST-A100", "bad")


def test_escalation_updates_session_state():
    state = AgentToolState()

    result = escalate_to_supervisor(
        "Customer requests a supervisor",
        state,
    )

    assert result.escalation_id.startswith("ESC-")
    assert state.escalated is True
    assert state.escalation_id == result.escalation_id


def test_escalation_is_idempotent():
    state = AgentToolState()

    first = escalate_to_supervisor("Customer requests a supervisor", state)
    second = escalate_to_supervisor("Customer requests a supervisor", state)

    assert first.escalation_id == second.escalation_id


def test_escalation_rejects_invalid_reason():
    with pytest.raises(ValueError):
        escalate_to_supervisor("bad", AgentToolState())
