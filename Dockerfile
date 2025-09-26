# Multi-stage Docker build for Currency Converter Application
FROM python:3.11-slim-bookworm as builder

# Set working directory
WORKDIR /app

# Install system dependencies and security updates
RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY application/backend/requirements.txt /app/
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim-bookworm

# Install security updates and runtime dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage to appuser's home
COPY --from=builder /root/.local /home/appuser/.local

# Copy application files
COPY application/ /app/
COPY README.md /app/

# Create logs directory and set permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app /home/appuser/.local

# Switch to non-root user for security
USER appuser

# Add local Python packages to PATH for appuser
ENV PATH=/home/appuser/.local/bin:$PATH

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch back to root temporarily to create startup script
USER root

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Currency Converter Application..."\n\
echo "Backend + Frontend will run on: http://0.0.0.0:8080"\n\
cd /app/backend\n\
echo "Starting Flask application on port 8080..."\n\
python app.py' > /app/start.sh

# Make startup script executable and switch back to appuser
RUN chmod +x /app/start.sh && chown appuser:appuser /app/start.sh

# Switch back to non-root user
USER appuser

# Run the startup script
CMD ["/app/start.sh"]