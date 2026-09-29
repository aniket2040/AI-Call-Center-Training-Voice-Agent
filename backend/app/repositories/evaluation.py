from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Evaluation


class EvaluationRepository:
    """Database operations for session evaluations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        evaluation_id: int,
    ) -> Evaluation | None:
        result = await self.session.execute(
            select(Evaluation).where(
                Evaluation.id == evaluation_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_session_id(
        self,
        session_id: int,
    ) -> Evaluation | None:
        result = await self.session.execute(
            select(Evaluation).where(
                Evaluation.session_id == session_id
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        session_id: int,
        status: str = "pending",
        model: str | None = None,
    ) -> Evaluation:
        evaluation = Evaluation(
            session_id=session_id,
            status=status,
            model=model,
        )

        self.session.add(evaluation)
        await self.session.flush()

        return evaluation

    async def update_result(
        self,
        evaluation: Evaluation,
        *,
        status: str,
        overall_score: float | None = None,
        criteria_scores: dict | None = None,
        evidence: list[dict] | None = None,
        strengths: list[str] | None = None,
        weaknesses: list[str] | None = None,
        feedback: str | None = None,
        model: str | None = None,
    ) -> Evaluation:
        evaluation.status = status
        evaluation.overall_score = overall_score

        if criteria_scores is not None:
            evaluation.criteria_scores = criteria_scores

        if evidence is not None:
            evaluation.evidence = evidence

        if strengths is not None:
            evaluation.strengths = strengths

        if weaknesses is not None:
            evaluation.weaknesses = weaknesses

        if feedback is not None:
            evaluation.feedback = feedback

        if model is not None:
            evaluation.model = model

        await self.session.flush()

        return evaluation