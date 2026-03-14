# Multi-stage build for Dual-RAG-Evaluator

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels
RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Copy application code
COPY . .

# Install wheels
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/* && \
    pip install -e .

# Create data directories
RUN mkdir -p /app/data/documents \
    /app/data/embeddings \
    /app/data/cache \
    /app/results

# Set permissions
RUN chmod -R 755 /app/data /app/results

# Expose port for potential REST API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Set entry point
ENTRYPOINT ["python", "-m"]
CMD ["ui.main_window"]
