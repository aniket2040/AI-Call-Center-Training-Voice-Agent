from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.db.session import engine
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.readiness import router as readiness_router
from backend.app.config import settings
from backend.app.core.events import LifecycleEvent
from backend.app.core.exceptions import unhandled_exception_handler
from backend.app.core.middleware import RequestIDMiddleware
from backend.app.core.logging import (
    configure_logging,
    log_lifecycle_event,
)
from backend.app.api.v1.calls import router as calls_router

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_lifecycle_event(
        LifecycleEvent.APPLICATION_STARTUP,
        environment=settings.app_env,
    )

    app.state.app_name = settings.app_name

    yield

    await engine.dispose()

    log_lifecycle_event(
        LifecycleEvent.APPLICATION_SHUTDOWN,
    )


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)


# --------------------------------------------------
# Middleware
# --------------------------------------------------

app.add_middleware(RequestIDMiddleware)


# --------------------------------------------------
# Exception handlers
# --------------------------------------------------

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)


# --------------------------------------------------
# API routers
# --------------------------------------------------

API_V1_PREFIX = "/api/v1"

app.include_router(
    health_router,
    prefix=API_V1_PREFIX,
)

app.include_router(
    readiness_router,
    prefix=API_V1_PREFIX,
)

app.include_router(
    calls_router,
    prefix=API_V1_PREFIX,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": "0.1.0",
    }