#!/bin/bash
# Day 1 Setup Script - Automated Environment Verification
# Run this to verify all required environment variables are set

set -e

echo "=========================================="
echo "REKINDLE.AI - Day 1 Setup Verification"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
ENV_FILE="backend/crewai_agents/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating from template..."
    cp backend/crewai_agents/.env.example "$ENV_FILE"
    echo -e "${YELLOW}⚠️  Please fill in your values in $ENV_FILE${NC}"
    exit 1
fi

# Load .env file
export $(cat "$ENV_FILE" | grep -v '^#' | xargs)

# Required variables (P0)
REQUIRED_VARS=(
    "SUPABASE_URL"
    "SUPABASE_SERVICE_ROLE_KEY"
    "SUPABASE_JWT_SECRET"
    "OPENAI_API_KEY"
    "SENDGRID_API_KEY"
    "TWILIO_ACCOUNT_SID"
    "TWILIO_AUTH_TOKEN"
)

# Optional but recommended (P1)
RECOMMENDED_VARS=(
    "REDIS_HOST"
    "REDIS_PORT"
    "SENTRY_DSN"
    "STRIPE_SECRET_KEY"
)

echo "Checking required variables (P0)..."
echo ""

MISSING_REQUIRED=()
MISSING_RECOMMENDED=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ $var: MISSING${NC}"
        MISSING_REQUIRED+=("$var")
    else
        # Mask sensitive values
        value="${!var}"
        if [ ${#value} -gt 10 ]; then
            masked="${value:0:4}...${value: -4}"
        else
            masked="***"
        fi
        echo -e "${GREEN}✅ $var: SET ($masked)${NC}"
    fi
done

echo ""
echo "Checking recommended variables (P1)..."
echo ""

for var in "${RECOMMENDED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${YELLOW}⚠️  $var: MISSING (recommended)${NC}"
        MISSING_RECOMMENDED+=("$var")
    else
        echo -e "${GREEN}✅ $var: SET${NC}"
    fi
done

echo ""
echo "=========================================="

if [ ${#MISSING_REQUIRED[@]} -gt 0 ]; then
    echo -e "${RED}❌ BLOCKING: Missing required variables${NC}"
    echo "Please set these in $ENV_FILE:"
    for var in "${MISSING_REQUIRED[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

if [ ${#MISSING_RECOMMENDED[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Missing recommended variables${NC}"
    echo "These are optional but recommended for production:"
    for var in "${MISSING_RECOMMENDED[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "You can continue, but some features may not work."
fi

echo -e "${GREEN}✅ All required variables are set!${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy to production (Railway/Render)"
echo "2. Configure webhooks (SendGrid/Twilio)"
echo "3. Set up monitoring (Sentry)"
echo "4. Test end-to-end campaign flow"
echo ""
echo "See DAY1_EXECUTION_CHECKLIST.md for details"

