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

# Railway automatically exposes all environment variables during build
# We don't need ARG declarations - just reference them directly as ENV
# This creates .env.production for Vite to pick up during build
RUN printf "VITE_SUPABASE_URL=%s\nVITE_SUPABASE_ANON_KEY=%s\nVITE_API_URL=%s\n" \
    "${VITE_SUPABASE_URL}" "${VITE_SUPABASE_ANON_KEY}" "${VITE_API_URL}" > .env.production && \
    echo "=== .env.production contents ===" && \
    cat .env.production && \
    echo "=== Environment variable verification ===" && \
    echo "VITE_SUPABASE_URL: ${VITE_SUPABASE_URL:0:30}..." && \
    echo "VITE_SUPABASE_ANON_KEY: ${VITE_SUPABASE_ANON_KEY:0:50}..." && \
    echo "VITE_API_URL: ${VITE_API_URL}"

RUN npm run build

# Expose port (Railway will override with $PORT)
EXPOSE 8081

# Keep WORKDIR at /app to support Python package imports
WORKDIR /app

# Use venv's Python directly - no activation needed, no permission issues
# Railway will inject $PORT at runtime
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "backend.crewai_agents.api_server:app", "--host", "0.0.0.0", "--port", "8081"]
