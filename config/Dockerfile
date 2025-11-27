FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for face recognition
# Note: libatlas-base-dev removed (not available in newer Debian, libopenblas-dev is sufficient)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY config/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads
RUN mkdir -p assets/photos assets/images

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.api.attendance_api:app", "--host", "0.0.0.0", "--port", "8000"]

