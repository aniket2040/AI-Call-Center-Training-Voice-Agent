import pytest
from pydantic import ValidationError

from backend.app.schemas import (
    CallRequest,
    EvaluationResponse,
    ScenarioCreate,
    UserCreate,
)


def test_valid_user():
    user = UserCreate(
        name="Test Trainee",
        phone_number="+919876543210",
    )

    assert user.name == "Test Trainee"
    assert user.phone_number == "+919876543210"


@pytest.mark.parametrize(
    "phone_number",
    [
        "123",
        "abc",
        "+91-9876543210",
        "",
    ],
)
def test_invalid_phone_number(phone_number):
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test Trainee",
            phone_number=phone_number,
        )


@pytest.mark.parametrize(
    "difficulty",
    [
        "easy",
        "medium",
        "hard",
    ],
)
def test_supported_difficulty(difficulty):
    scenario = ScenarioCreate(
        name="Test Scenario",
        description="Test scenario",
        difficulty=difficulty,
        objectives=["Test objective"],
    )

    assert scenario.difficulty == difficulty


def test_invalid_difficulty():
    with pytest.raises(ValidationError):
        ScenarioCreate(
            name="Test Scenario",
            description="Test scenario",
            difficulty="extreme",
            objectives=["Test objective"],
        )


@pytest.mark.parametrize(
    "scenario_id",
    [
        0,
        -1,
    ],
)
def test_invalid_scenario_id(scenario_id):
    with pytest.raises(ValidationError):
        CallRequest(
            trainee_id=1,
            scenario_id=scenario_id,
            phone_number="+919876543210",
        )


@pytest.mark.parametrize(
    "score",
    [
        -1,
        101,
    ],
)
def test_invalid_score(score):
    with pytest.raises(ValidationError):
        EvaluationResponse(
            id=1,
            session_id=1,
            status="completed",
            overall_score=score,
            criteria_scores={},
            strengths=[],
            weaknesses=[],
        )


def test_valid_score():
    evaluation = EvaluationResponse(
        id=1,
        session_id=1,
        status="completed",
        overall_score=87.5,
        criteria_scores={},
        strengths=[],
        weaknesses=[],
    )

    assert evaluation.overall_score == 87.5


def test_invalid_evaluation_status():
    with pytest.raises(ValidationError):
        EvaluationResponse(
            id=1,
            session_id=1,
            status="banana",
            overall_score=50,
            criteria_scores={},
            strengths=[],
            weaknesses=[],
        )