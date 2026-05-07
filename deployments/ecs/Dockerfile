# =========================================================
# Cloud Music Subscription App - ECS Backend Dockerfile
# Builds the Flask backend container for ECS deployment.
# =========================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable real-time logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application working directory
WORKDIR /app

# Install system dependencies required by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Copy dependency file first for better Docker layer caching
COPY requirements.txt .

# Install backend dependencies
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend ./backend
COPY database ./database
COPY data ./data

# ECS runtime environment
ENV AWS_REGION=us-east-1

ENV LOGIN_TABLE=login
ENV MUSIC_TABLE=music
ENV SUBSCRIPTIONS_TABLE=subscriptions

ENV MUSIC_TITLE_INDEX=title-index
ENV MUSIC_YEAR_ALBUM_INDEX=year-album-index

ENV APP_HOST=0.0.0.0
ENV APP_PORT=80
ENV FLASK_DEBUG=False
ENV CORS_ORIGINS=*

ENV S3_BUCKET_NAME=cloud-music-app-s4097885-2026-a2
ENV S3_IMAGE_PREFIX=artist-images/

# Expose HTTP port 80 for assignment compliance
EXPOSE 80

# Health check for container-level validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Run Flask app with Gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:80", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "backend.app:app"]