from contextlib import asynccontextmanager
from backend.app.core.logging import configure_logging, get_logger
from fastapi import FastAPI

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.readiness import router as readiness_router
from backend.app.config import settings
from backend.app.core.exceptions import unhandled_exception_handler
from backend.app.core.middleware import RequestIDMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    logger = get_logger(__name__)

    logger.info(
        "application_starting",
        environment=settings.app_env,
    )

    app.state.app_name = settings.app_name

    yield

    logger.info(
        "application_shutdown",
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


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": "0.1.0",
    }