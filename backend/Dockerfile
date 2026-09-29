FROM python:3.12-slim

# Prevent Python from creating .pyc files
# and make stdout/stderr immediately visible.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create a non-root user.
RUN groupadd --system app \
    && useradd --system --gid app --create-home app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for Docker layer caching.
COPY requirements.txt pyproject.toml ./

# Install dependencies into the system Python environment.
RUN uv pip install --system -r requirements.txt

# Copy application source.
COPY backend ./backend
COPY tests ./tests
COPY alembic.ini ./
COPY alembic ./alembic



# Change ownership to non-root user.
RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=10s \
            --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]