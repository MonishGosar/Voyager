FROM python:3.11-slim

# Install Node.js 20 LTS
RUN apt-get update && apt-get install -y curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build Next.js frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# Install Python deps
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Set Python path so the 'routers' imports work correctly
ENV PYTHONPATH=/app/backend

# Run uvicorn on port 8080
CMD ["sh", "-c", "cd /app/backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
