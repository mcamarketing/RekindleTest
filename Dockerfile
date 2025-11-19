# Rekindle.ai Production Dockerfile
# Multi-stage build for Node.js frontend + Python backend

FROM python:3.11-slim as base

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY backend/crewai_agents/requirements.txt ./backend/crewai_agents/

# Install dependencies
RUN npm ci
RUN python -m venv /opt/venv
RUN . /opt/venv/bin/activate && pip install -r backend/crewai_agents/requirements.txt

# Copy application code
COPY . .

# Build frontend
RUN npm run build

# Expose port (Railway will override with $PORT)
EXPOSE 8081

# Keep WORKDIR at /app to support Python package imports
WORKDIR /app

# Use exec form with sh to properly expand PORT environment variable
# Activate venv and run uvicorn via python -m to avoid permission issues
CMD ["/bin/sh", "-c", ". /opt/venv/bin/activate && python -m uvicorn backend.crewai_agents.api_server:app --host 0.0.0.0 --port ${PORT:-8081}"]
