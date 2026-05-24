# ==========================================
# Stage 1: Build Dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install minimal build tools if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python packages to the user directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Stage 2: Final Runtime Environment
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a secure non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -m -d /home/appuser -s /sbin/nologin appuser

# Copy installed dependencies from builder to user home directory
COPY --from=builder /root/.local /home/appuser/.local

# Ensure path is updated to find user-installed scripts/executables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app/app.py

# Copy application files and change ownership to the non-root user
COPY --chown=appuser:appgroup . .

# Set ownership for runtime directories
RUN chown -R appuser:appgroup /app /home/appuser

# Switch to non-privileged user
USER appuser

EXPOSE 5000

# CMD to start the production web server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.app:app"]
