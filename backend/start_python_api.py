"""
Startup script for Python AI Backend
Ensures correct environment variables are loaded from crewai_agents/.env
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Get the directory of this script (backend/)
backend_dir = Path(__file__).parent
crewai_agents_dir = backend_dir / "crewai_agents"
env_file = crewai_agents_dir / ".env"

# Load environment variables from crewai_agents/.env
if env_file.exists():
    print(f"Loading environment from: {env_file}")
    load_dotenv(dotenv_path=env_file, override=True)
else:
    print(f"WARNING: .env file not found at {env_file}")
    sys.exit(1)

# Verify PORT is set correctly
port = os.getenv("PORT", "8081")
print(f"Starting Python AI Backend on port: {port}")

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Import and run the API server
if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    port = int(os.getenv("PORT", 8081))
    environment = os.getenv("ENVIRONMENT", "development")
    reload = environment != "production"

    print(f"Environment: {environment}")
    print(f"Reload: {reload}")
    print(f"CORS Origins: {os.getenv('ALLOWED_ORIGINS', 'Not set')}")
    print(f"Anthropic API Key: {'Set [OK]' if os.getenv('ANTHROPIC_API_KEY') else 'Not set [ERROR]'}")
    print(f"Supabase URL: {'Set [OK]' if os.getenv('SUPABASE_URL') else 'Not set [ERROR]'}")
    print("")
    print(f"Starting Rekindle AI Backend on http://0.0.0.0:{port}")
    print("")

    uvicorn.run(
        "crewai_agents.api_server:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )
