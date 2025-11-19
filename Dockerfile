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

# Create .env.production file using printf to avoid truncation
RUN printf "VITE_SUPABASE_URL=%s\nVITE_SUPABASE_ANON_KEY=%s\nVITE_API_URL=%s\n" \
    "$VITE_SUPABASE_URL" "$VITE_SUPABASE_ANON_KEY" "$VITE_API_URL" > .env.production && \
    echo "=== .env.production contents ===" && \
    cat .env.production && \
    echo "=== Environment variable lengths ===" && \
    printf "VITE_SUPABASE_URL length: %d\n" ${#VITE_SUPABASE_URL} && \
    printf "VITE_SUPABASE_ANON_KEY length: %d\n" ${#VITE_SUPABASE_ANON_KEY} && \
    printf "VITE_API_URL length: %d\n" ${#VITE_API_URL}

RUN npm run build

# Expose port (Railway will override with $PORT)
EXPOSE 8081

# Keep WORKDIR at /app to support Python package imports
WORKDIR /app

# Use venv's Python directly - no activation needed, no permission issues
# Railway will inject $PORT at runtime
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "backend.crewai_agents.api_server:app", "--host", "0.0.0.0", "--port", "8081"]
