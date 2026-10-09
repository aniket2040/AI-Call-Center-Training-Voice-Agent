from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.schemas.call import CallRequest, CallResponse
from backend.app.services.call_service import (
    CallService,
    CallDispatchError,
    TraineeNotFoundError,
    InvalidTraineeError,
    ScenarioNotFoundError,
    InactiveScenarioError,
)

router = APIRouter(tags=["Calls"])


@router.post(
    "/calls",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_call(
    request: CallRequest,
    db: AsyncSession = Depends(get_db),
) -> CallResponse:
    service = CallService(db)

    try:
        session = await service.create_call(
            trainee_id=request.trainee_id,
            scenario_id=request.scenario_id,
            phone_number=request.phone_number,
        )


    except (TraineeNotFoundError, ScenarioNotFoundError) as exc:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=str(exc),

        ) from exc


    except InvalidTraineeError as exc:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=str(exc),

        ) from exc


    except InactiveScenarioError as exc:

        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,

            detail=str(exc),

        ) from exc


    except CallDispatchError as exc:

        raise HTTPException(

            status_code=status.HTTP_502_BAD_GATEWAY,

            detail=str(exc),

        ) from exc

    return CallResponse(
        session_id=session.id,
        status=session.status,
    )
