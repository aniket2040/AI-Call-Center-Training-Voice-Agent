import pytest

from backend.app.models import Scenario
from backend.app.scenarios import (
    ScenarioValidationError,
    validate_scenario,
)


def create_valid_scenario() -> Scenario:
    return Scenario(
        id=1,
        name="Angry Customer - Refund",
        description="Customer has not received a refund.",
        difficulty="medium",
        persona_config={
            "name": "Rahul",
            "mood": "frustrated",
            "patience": "low",
        },
        rules_config={
            "become_angry_if_ignored": True,
            "calm_if_handled_well": True,
            "situation": {
                "issue": "refund_not_received",
                "days_waiting": 14,
            },
        },
        objectives=[
            "verify_customer",
            "show_empathy",
            "understand_problem",
            "provide_resolution",
        ],
        evaluation_config={
            "criteria": [
                "empathy",
                "communication",
                "problem_understanding",
                "resolution",
                "professionalism",
            ],
        },
        is_active=True,
    )


def test_valid_scenario_is_converted():
    scenario = create_valid_scenario()

    result = validate_scenario(scenario)

    assert result.id == "1"
    assert result.name == "Angry Customer - Refund"
    assert result.difficulty == "medium"
    assert result.persona.name == "Rahul"
    assert result.persona.mood == "frustrated"
    assert result.situation.issue == "refund_not_received"
    assert result.situation.days_waiting == 14
    assert "show_empathy" in result.objectives
    assert result.rules.become_angry_if_ignored is True
    assert "empathy" in result.evaluation.criteria


def test_invalid_persona_is_rejected():
    scenario = create_valid_scenario()

    scenario.persona_config = {
        "name": "",
        "mood": "frustrated",
        "patience": "low",
    }

    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)


def test_invalid_situation_is_rejected():
    scenario = create_valid_scenario()

    scenario.rules_config["situation"] = {
        "issue": "",
        "days_waiting": -1,
    }

    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)


def test_empty_objectives_are_rejected():
    scenario = create_valid_scenario()

    scenario.objectives = []

    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)


def test_empty_evaluation_criteria_are_rejected():
    scenario = create_valid_scenario()

    scenario.evaluation_config = {
        "criteria": [],
    }

    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)