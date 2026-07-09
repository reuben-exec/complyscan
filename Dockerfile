# ── Build stage: Node.js for frontend ──────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend-next/package.json frontend-next/package-lock.json ./frontend-next/
RUN cd frontend-next && npm ci
COPY frontend-next/ ./frontend-next/
RUN cd frontend-next && npm run build

# ── Runtime stage: Python ──────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# Install required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/

# Copy pre-built frontend from build stage
COPY --from=frontend-builder /app/frontend-next/out/ ./frontend-next/out/

# Expose port
EXPOSE 10000

# Start the server
CMD uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
