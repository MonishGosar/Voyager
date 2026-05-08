FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y nodejs npm

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

# Update main.py to serve frontend static files
# We do this natively in main.py instead but for now just run uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
