FROM python:3.12-slim

# Install system dependencies required for OpenCV, MediaPipe, and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libgles2 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    PYTHONPATH=/app:/app/whatever

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Collect static files for production
RUN cd whatever && python manage.py collectstatic --noinput

# Cloud Run defaults to PORT 8080
EXPOSE 8080

# Run migrations and launch Daphne ASGI server (handles both HTTP and WebSockets)
CMD ["sh", "-c", "cd whatever && python manage.py migrate --noinput && daphne -b 0.0.0.0 -p ${PORT:-8080} whatever.asgi:application"]
