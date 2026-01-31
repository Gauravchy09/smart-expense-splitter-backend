FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render sets PORT env var, but we default to 10000)
ENV PORT=10000
EXPOSE 10000

# Start command
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
