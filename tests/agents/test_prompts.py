from backend.app.agents.prompts import (
    build_agent_instructions,
)
from backend.app.agents.state import (
    ConversationState,
    CustomerMood,
    CustomerPatience,
)
from backend.app.scenarios.models import (
    EvaluationConfig,
    PersonaConfig,
    RulesConfig,
    ScenarioDefinition,
    SituationConfig,
)


def create_scenario() -> ScenarioDefinition:
    return ScenarioDefinition(
        id="refund_angry_customer",
        name="Angry Customer - Refund",
        difficulty="medium",
        persona=PersonaConfig(
            name="Rahul",
            mood="frustrated",
            patience="low",
        ),
        situation=SituationConfig(
            issue="refund_not_received",
            days_waiting=14,
        ),
        objectives=[
            "verify_customer",
            "show_empathy",
            "understand_problem",
            "provide_resolution",
        ],
        rules=RulesConfig(
            become_angry_if_ignored=True,
            calm_if_handled_well=True,
        ),
        evaluation=EvaluationConfig(
            criteria=[
                "empathy",
                "communication",
                "problem_understanding",
                "resolution",
                "professionalism",
            ],
        ),
    )


def test_prompt_contains_required_layers():
    scenario = create_scenario()

    state = ConversationState()

    prompt = build_agent_instructions(
        scenario,
        state,
    )

    assert "AI customer-roleplay agent" in prompt
    assert "Angry Customer - Refund" in prompt
    assert "Rahul" in prompt
    assert "frustrated" in prompt
    assert "medium" in prompt
    assert "refund_not_received" in prompt
    assert "show_empathy" in prompt
    assert "become progressively more frustrated" in prompt
    assert "TOOL INSTRUCTIONS" in prompt
    assert "CONVERSATION ENDING" in prompt


def test_prompt_contains_current_state():
    scenario = create_scenario()

    state = ConversationState(
        customer_mood=CustomerMood.FRUSTRATED,
        customer_patience=CustomerPatience.LOW,
        turn_count=5,
    )

    prompt = build_agent_instructions(
        scenario,
        state,
    )

    assert "Customer mood:\nfrustrated" in prompt
    assert "Customer patience:\nlow" in prompt
    assert "Conversation turns:\n5" in prompt


def test_completed_objectives_are_not_repeated():
    scenario = create_scenario()

    state = ConversationState(
        completed_objectives={
            "verify_customer",
            "show_empathy",
        },
    )

    prompt = build_agent_instructions(
        scenario,
        state,
    )

    objectives_section = prompt.split(
        "TRAINING OBJECTIVES",
        maxsplit=1,
    )[1]

    assert "- verify_customer" not in objectives_section
    assert "- show_empathy" not in objectives_section

    assert "- understand_problem" in objectives_section
    assert "- provide_resolution" in objectives_section


def test_prompt_does_not_expose_evaluation_criteria():
    scenario = create_scenario()

    prompt = build_agent_instructions(
        scenario,
        ConversationState(),
    )

    # The prompt may mention evaluation criteria conceptually,
    # but must not expose the actual evaluation criteria values.
    criteria_block = "\n".join(
        f"- {criterion}" for criterion in scenario.evaluation.criteria
    )

    assert criteria_block not in prompt

    # Evaluation-specific criteria must not appear individually.
    assert "professionalism" not in prompt
    assert "communication" not in prompt
    assert "problem_understanding" not in prompt

def test_prompt_contains_no_livekit_dependency():
    scenario = create_scenario()

    prompt = build_agent_instructions(
        scenario,
        ConversationState(),
    )

    assert "livekit" not in prompt.lower()


def test_prompt_instructs_agent_not_to_invent_data():
    scenario = create_scenario()

    prompt = build_agent_instructions(
        scenario,
        ConversationState(),
    )

    assert "Do not invent" in prompt
    assert "required tool" in prompt.lower()


def test_prompt_is_deterministic():
    scenario = create_scenario()
    state = ConversationState()

    first = build_agent_instructions(
        scenario,
        state,
    )

    second = build_agent_instructions(
        scenario,
        state,
    )

    assert first == second