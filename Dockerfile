# Karl AI Ecosystem - Multi-stage Docker Build
# Optimized for Render.com deployment

# Stage 1: Base Python Environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry
RUN poetry config virtualenvs.create false

# Stage 2: Dependencies
FROM base as deps

# Copy dependency files
COPY pyproject.toml poetry.lock ./
COPY requirements.txt ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi
RUN pip install -r requirements.txt

# Stage 3: Application
FROM base as app

# Copy dependencies from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Set work directory
WORKDIR /app

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash karl
RUN chown -R karl:karl /app
USER karl

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["poetry", "run", "uvicorn", "corehub.api.main:app", "--host", "0.0.0.0", "--port", "8000"]