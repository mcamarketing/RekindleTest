#!/usr/bin/env python3
"""
Environment Variables Verification Script
==========================================
Validates all required environment variables are set correctly

Usage:
    python scripts/verify_env.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Required P0 variables (app won't start without these)
P0_VARS = [
    ("SUPABASE_URL", "https://", "Supabase project URL"),
    ("SUPABASE_SERVICE_ROLE_KEY", "eyJ", "Supabase service role key (starts with eyJ)"),
    ("SUPABASE_JWT_SECRET", None, "Supabase JWT secret"),
    ("ANTHROPIC_API_KEY", "sk-ant-", "Anthropic API key for Claude"),
    ("OPENAI_API_KEY", "sk-", "OpenAI API key for CrewAI agents"),
    ("SENDGRID_API_KEY", "SG.", "SendGrid API key"),
    ("SENDGRID_FROM_EMAIL", "@", "SendGrid verified sender email"),
    ("TWILIO_ACCOUNT_SID", "AC", "Twilio Account SID"),
    ("TWILIO_AUTH_TOKEN", None, "Twilio Auth Token"),
    ("TWILIO_PHONE_NUMBER", "+", "Twilio phone number"),
    ("JWT_SECRET", None, "JWT signing secret (64+ chars recommended)"),
]

# Recommended P1 variables
P1_VARS = [
    ("STRIPE_SECRET_KEY", "sk_", "Stripe secret key for billing"),
    ("SENTRY_DSN", "https://", "Sentry DSN for error monitoring"),
    ("CALENDAR_ENCRYPTION_KEY", None, "Calendar OAuth token encryption key"),
    ("REDIS_HOST", None, "Redis host for queue (Upstash recommended)"),
]

# Optional P2 variables
P2_VARS = [
    ("GOOGLE_CALENDAR_CLIENT_ID", None, "Google Calendar OAuth client ID"),
    ("MICROSOFT_CALENDAR_CLIENT_ID", None, "Microsoft Calendar OAuth client ID"),
    ("STRIPE_WEBHOOK_SECRET", "whsec_", "Stripe webhook signing secret"),
]


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}

    if not env_path.exists():
        return env_vars

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def check_variable(name: str, prefix: str | None, description: str, env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """
    Check if a variable is set and valid

    Returns: (is_valid, message)
    """
    # Check if set
    value = env_vars.get(name, os.getenv(name))

    if not value:
        return False, f"{RED}[MISSING]{RESET} {name} - {description}"

    # Check for placeholder values
    if any(placeholder in value.lower() for placeholder in ['your_', 'example', 'changeme', 'placeholder']):
        return False, f"{RED}[PLACEHOLDER]{RESET} {name} - Contains placeholder value"

    # Check prefix if specified
    if prefix and not value.startswith(prefix):
        return False, f"{YELLOW}[WARNING]{RESET} {name} - Expected to start with '{prefix}'"

    # Check length for secrets
    if 'secret' in name.lower() or 'key' in name.lower():
        if len(value) < 20:
            return False, f"{YELLOW}[WARNING]{RESET} {name} - Seems too short for a secret ({len(value)} chars)"

    # Special validation for email
    if 'email' in name.lower():
        if '@' not in value or '.' not in value:
            return False, f"{YELLOW}[WARNING]{RESET} {name} - Invalid email format"

    # All checks passed
    return True, f"{GREEN}[OK]{RESET} {name} - {description}"


def main():
    """Main verification function"""
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}Rekindle.ai Environment Variables Verification{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")

    # Find .env file
    env_path = Path("backend/crewai_agents/.env")
    if not env_path.exists():
        print(f"{RED}[ERROR]{RESET} .env file not found at: {env_path}")
        print(f"\nCreate it with: cp backend/crewai_agents/.env.example backend/crewai_agents/.env")
        sys.exit(1)

    print(f"{GREEN}[OK]{RESET} Found .env file at: {env_path}\n")

    # Load environment
    env_vars = load_env_file(env_path)
    print(f"Loaded {len(env_vars)} variables from .env file\n")

    # Check P0 variables
    print(f"{BOLD}P0 Variables (CRITICAL - App won't start without these):{RESET}")
    print("-" * 70)

    p0_results = []
    for name, prefix, description in P0_VARS:
        is_valid, message = check_variable(name, prefix, description, env_vars)
        p0_results.append(is_valid)
        print(f"  {message}")

    p0_pass_count = sum(p0_results)
    p0_total = len(P0_VARS)
    print(f"\n{BOLD}P0 Summary:{RESET} {p0_pass_count}/{p0_total} variables configured correctly")

    # Check P1 variables
    print(f"\n{BOLD}P1 Variables (Recommended for production):{RESET}")
    print("-" * 70)

    p1_results = []
    for name, prefix, description in P1_VARS:
        is_valid, message = check_variable(name, prefix, description, env_vars)
        p1_results.append(is_valid)
        print(f"  {message}")

    p1_pass_count = sum(p1_results)
    p1_total = len(P1_VARS)
    print(f"\n{BOLD}P1 Summary:{RESET} {p1_pass_count}/{p1_total} variables configured")

    # Check P2 variables
    print(f"\n{BOLD}P2 Variables (Optional):{RESET}")
    print("-" * 70)

    p2_results = []
    for name, prefix, description in P2_VARS:
        is_valid, message = check_variable(name, prefix, description, env_vars)
        p2_results.append(is_valid)
        print(f"  {message}")

    p2_pass_count = sum(p2_results)
    p2_total = len(P2_VARS)
    print(f"\n{BOLD}P2 Summary:{RESET} {p2_pass_count}/{p2_total} variables configured")

    # Overall status
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}OVERALL STATUS{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")

    if p0_pass_count == p0_total:
        print(f"{GREEN}{BOLD}[SUCCESS] READY TO DEPLOY{RESET}")
        print(f"{GREEN}All critical (P0) variables are configured correctly!{RESET}\n")

        if p1_pass_count < p1_total:
            print(f"{YELLOW}Note: {p1_total - p1_pass_count} recommended (P1) variables missing{RESET}")
            print(f"{YELLOW}You can deploy, but consider setting these for production.{RESET}\n")

        sys.exit(0)
    else:
        missing_p0 = p0_total - p0_pass_count
        print(f"{RED}{BOLD}[NOT READY] Production deployment blocked{RESET}")
        print(f"{RED}{missing_p0} critical (P0) variables need attention!{RESET}\n")

        print(f"{BOLD}Next steps:{RESET}")
        print(f"1. Review the errors above")
        print(f"2. Set missing variables in: {env_path}")
        print(f"3. Run this script again to verify\n")

        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Verification cancelled by user{RESET}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}[ERROR]{RESET} Unexpected error: {e}\n")
        sys.exit(1)
