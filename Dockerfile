FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium firefox

# Copy application code
COPY . .

# Create reports directory
RUN mkdir -p reports

# Set environment variables
ENV PYTHONPATH=/app
ENV HEADLESS=true

# Expose port for potential web interface
EXPOSE 8000

# Default command
CMD ["python", "cli.py", "--help"]