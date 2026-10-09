
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import re
import uuid

from pydantic import BaseModel, Field, ValidationError

from backend.app.core.logging import get_logger

logger = get_logger("agent_tools")


# ---- Typed input and output schemas ----

class CustomerLookupInput(BaseModel):
    customer_id: str = Field(
        min_length=4,
        max_length=20,
        pattern=r"^CUST-[A-Z0-9]{4,16}$",
    )


class OrderLookupInput(BaseModel):
    order_id: str = Field(
        min_length=4,
        max_length=20,
        pattern=r"^ORD-[A-Z0-9]{4,16}$",
    )


class RefundStatusInput(BaseModel):
    order_id: str = Field(
        min_length=4,
        max_length=20,
        pattern=r"^ORD-[A-Z0-9]{4,16}$",
    )


class SupportTicketInput(BaseModel):
    customer_id: str = Field(
        min_length=4,
        max_length=20,
        pattern=r"^CUST-[A-Z0-9]{4,16}$",
    )
    issue: str = Field(min_length=5, max_length=500)


class EscalationInput(BaseModel):
    reason: str = Field(min_length=5, max_length=300)


class CustomerOutput(BaseModel):
    customer_id: str
    name: str
    account_status: Literal["active", "inactive"]
    tier: Literal["standard", "premium"]


class OrderOutput(BaseModel):
    order_id: str
    customer_id: str
    status: Literal["processing", "shipped", "delivered"]
    total: float
    currency: Literal["INR"] = "INR"


class RefundOutput(BaseModel):
    order_id: str
    status: Literal["not_requested", "pending", "approved", "rejected"]
    amount: float
    currency: Literal["INR"] = "INR"
    message: str


class SupportTicketOutput(BaseModel):
    ticket_id: str
    customer_id: str
    status: Literal["open"] = "open"
    message: str


class EscalationOutput(BaseModel):
    escalation_id: str
    status: Literal["requested"] = "requested"
    reason: str
    message: str


@dataclass(slots=True)
class AgentToolState:
    """State scoped to one training-agent session."""

    escalated: bool = False
    escalation_reason: str | None = None
    escalation_id: str | None = None


# ---- Controlled mock business data ----

_CUSTOMERS = {
    "CUST-A100": {
        "customer_id": "CUST-A100",
        "name": "Aarav Sharma",
        "account_status": "active",
        "tier": "premium",
    },
    "CUST-B200": {
        "customer_id": "CUST-B200",
        "name": "Priya Verma",
        "account_status": "active",
        "tier": "standard",
    },
}

_ORDERS = {
    "ORD-A100": {
        "order_id": "ORD-A100",
        "customer_id": "CUST-A100",
        "status": "delivered",
        "total": 1499.0,
    },
    "ORD-B200": {
        "order_id": "ORD-B200",
        "customer_id": "CUST-B200",
        "status": "shipped",
        "total": 799.0,
    },
}

_REFUNDS = {
    "ORD-A100": {
        "status": "pending",
        "amount": 1499.0,
        "message": "The refund is being processed.",
    },
    "ORD-B200": {
        "status": "not_requested",
        "amount": 0.0,
        "message": "No refund request has been recorded.",
    },
}


# ---- Business tools ----

def get_customer(customer_id: str) -> CustomerOutput:
    """Look up a customer in the controlled demo dataset."""
    try:
        request = CustomerLookupInput(customer_id=customer_id.strip())
        customer = _CUSTOMERS.get(request.customer_id)

        if customer is None:
            raise LookupError("Customer was not found.")

        result = CustomerOutput.model_validate(customer)
        logger.info("customer_lookup_succeeded", customer_id=request.customer_id)
        return result

    except (ValidationError, AttributeError):
        logger.warning("customer_lookup_invalid_input")
        raise ValueError("Invalid customer identifier.") from None
    except LookupError:
        logger.info("customer_lookup_not_found")
        raise


def get_order(order_id: str) -> OrderOutput:
    """Look up an order in the controlled demo dataset."""
    try:
        request = OrderLookupInput(order_id=order_id.strip())
        order = _ORDERS.get(request.order_id)

        if order is None:
            raise LookupError("Order was not found.")

        result = OrderOutput.model_validate(order)
        logger.info("order_lookup_succeeded", order_id=request.order_id)
        return result

    except (ValidationError, AttributeError):
        logger.warning("order_lookup_invalid_input")
        raise ValueError("Invalid order identifier.") from None
    except LookupError:
        logger.info("order_lookup_not_found")
        raise


def get_refund_status(order_id: str) -> RefundOutput:
    """Return simulated refund information for a known order."""
    try:
        request = RefundStatusInput(order_id=order_id.strip())
    except (ValidationError, AttributeError):
        logger.warning("refund_lookup_invalid_input")
        raise ValueError("Invalid order identifier.") from None

    if request.order_id not in _ORDERS:
        logger.info("refund_lookup_order_not_found")
        raise LookupError("Order was not found.")

    refund = _REFUNDS[request.order_id]
    result = RefundOutput(
        order_id=request.order_id,
        **refund,
    )
    logger.info("refund_lookup_succeeded", order_id=request.order_id)
    return result


def create_support_ticket(
    customer_id: str,
    issue: str,
) -> SupportTicketOutput:
    """Create a simulated support ticket and return its ID."""
    try:
        request = SupportTicketInput(
            customer_id=customer_id.strip(),
            issue=issue.strip(),
        )
    except (ValidationError, AttributeError):
        logger.warning("support_ticket_invalid_input")
        raise ValueError("Invalid customer identifier or issue description.") from None

    if request.customer_id not in _CUSTOMERS:
        logger.info("support_ticket_customer_not_found")
        raise LookupError("Customer was not found.")

    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    result = SupportTicketOutput(
        ticket_id=ticket_id,
        customer_id=request.customer_id,
        message="Support ticket created successfully.",
    )
    logger.info(
        "support_ticket_created",
        ticket_id=ticket_id,
        customer_id=request.customer_id,
    )
    return result


def escalate_to_supervisor(
    reason: str,
    state: AgentToolState,
) -> EscalationOutput:
    """Record a simulated escalation in the current session's state."""
    try:
        request = EscalationInput(reason=reason.strip())
    except (ValidationError, AttributeError):
        logger.warning("supervisor_escalation_invalid_input")
        raise ValueError("Invalid escalation reason.") from None

    if state.escalated and state.escalation_id:
        logger.info("supervisor_escalation_already_recorded")
        return EscalationOutput(
            escalation_id=state.escalation_id,
            reason=state.escalation_reason or request.reason,
            message="This session has already been escalated.",
        )

    escalation_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    state.escalated = True
    state.escalation_reason = request.reason
    state.escalation_id = escalation_id

    logger.info(
        "supervisor_escalation_recorded",
        escalation_id=escalation_id,
    )

    return EscalationOutput(
        escalation_id=escalation_id,
        reason=request.reason,
        message="Supervisor escalation recorded for this training session.",
    )
