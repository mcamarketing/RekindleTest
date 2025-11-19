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

# Build arguments for Vite environment variables (injected at build time)
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_API_URL

# Build frontend with environment variables
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_API_URL=$VITE_API_URL

# Create .env.production file for Vite to load
RUN echo "VITE_SUPABASE_URL=$VITE_SUPABASE_URL" > .env.production && \
    echo "VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY" >> .env.production && \
    echo "VITE_API_URL=$VITE_API_URL" >> .env.production && \
    echo "=== .env.production contents ===" && \
    cat .env.production && \
    echo "=== Environment variables ===" && \
    env | grep VITE

RUN npm run build

# Expose port (Railway will override with $PORT)
EXPOSE 8081

# Keep WORKDIR at /app to support Python package imports
WORKDIR /app

# Use venv's Python directly - no activation needed, no permission issues
# Railway will inject $PORT at runtime
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "backend.crewai_agents.api_server:app", "--host", "0.0.0.0", "--port", "8081"]
