from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health(request: Request) -> dict:
    return {
        "status": "healthy",
        "request_id": request.state.request_id,
    }