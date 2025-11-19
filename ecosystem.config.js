module.exports = {
  apps: [
    {
      name: "node-scheduler-worker",
      script: "npm",
      args: "start",
      cwd: "backend/node_scheduler_worker",
      instances: 1,
      autorestart: true,
      max_memory_restart: '1G',
      watch: false,
      env: {
        NODE_ENV: "production",
        // These should be set in production via environment or secrets manager
        // SUPABASE_URL: process.env.SUPABASE_URL,
        // SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY,
        // REDIS_HOST: process.env.REDIS_HOST || "127.0.0.1",
        // REDIS_PORT: process.env.REDIS_PORT || 6379,
        // REDIS_PASSWORD: process.env.REDIS_PASSWORD,
        // REDIS_SCHEDULER_QUEUE: process.env.REDIS_SCHEDULER_QUEUE || "message_scheduler_queue",
        // LOG_AGGREGATOR_URL: process.env.LOG_AGGREGATOR_URL,
      },
      out_file: "./logs/worker-out.log",
      error_file: "./logs/worker-error.log",
      merge_logs: true,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    },
    {
      name: "fastapi-api-server",
      script: "uvicorn",
      args: "backend.crewai_agents.api_server:app --host 0.0.0.0 --port 8081",
      cwd: ".",
      instances: 1,
      autorestart: true,
      max_memory_restart: '1G',
      watch: false,
      env: {
        NODE_ENV: "production",
        // These should be set in production via environment or secrets manager
        // PYTHONPATH: ".",
        // SUPABASE_URL: process.env.SUPABASE_URL,
        // SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY,
        // TRACKER_API_TOKEN: process.env.TRACKER_API_TOKEN,
        // ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
        // ANTHROPIC_MODEL: process.env.ANTHROPIC_MODEL || "claude-3-5-sonnet-20240620",
        // REDIS_HOST: process.env.REDIS_HOST || "127.0.0.1",
        // REDIS_PORT: process.env.REDIS_PORT || 6379,
        // REDIS_PASSWORD: process.env.REDIS_PASSWORD,
        // STRIPE_MCP_URL: process.env.STRIPE_MCP_URL || "http://mcp-stripe-server",
        // LINKEDIN_MCP_URL: process.env.LINKEDIN_MCP_URL || "http://mcp-linkedin-server",
        // CALENDAR_MCP_URL: process.env.CALENDAR_MCP_URL || "http://mcp-calendar-server",
      },
      out_file: "./logs/api-out.log",
      error_file: "./logs/api-error.log",
      merge_logs: true,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    }
  ]
};


