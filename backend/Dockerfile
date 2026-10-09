# =====================================================================
# HelvetiaVeritas - Sovereign Apertus Backend Container
# =====================================================================
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install security updates and curl for container healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create sovereign non-root app user
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

# Copy application, statutory datasets and frontend dashboard
COPY --chown=appuser:appuser backend/app /app/app
COPY --chown=appuser:appuser data /app/data
COPY --chown=appuser:appuser frontend /app/frontend

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
