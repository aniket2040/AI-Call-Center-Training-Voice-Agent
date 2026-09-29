from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/ready")
async def readiness() -> dict:
    checks: dict[str, str] = {}

    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        checks["database"] = "ready"

    except Exception:
        checks["database"] = "unavailable"

    finally:
        await engine.dispose()

    ready = all(status == "ready" for status in checks.values())

    return {
        "status": "ready" if ready else "not_ready",
        "checks": checks,
    }