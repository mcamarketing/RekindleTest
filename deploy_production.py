#!/usr/bin/env python3
"""
Rekindle.ai Production Deployment Script
========================================
One-click deployment to Railway or Render

Usage:
    python deploy_production.py --platform railway
    python deploy_production.py --platform render
    python deploy_production.py --check  # Validate configuration only
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

REQUIRED_ENV_VARS = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "SENDGRID_API_KEY",
    "SENDGRID_FROM_EMAIL",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER",
    "STRIPE_SECRET_KEY",
    "JWT_SECRET",
]

OPTIONAL_ENV_VARS = [
    "SENDGRID_FROM_NAME",
    "STRIPE_WEBHOOK_SECRET",
    "SENTRY_DSN",
    "CALENDAR_ENCRYPTION_KEY",
]


class DeploymentValidator:
    """Validates deployment readiness"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.env_file = Path("backend/crewai_agents/.env")

    def validate_all(self) -> bool:
        """Run all validation checks"""
        print(f"{BLUE}[1/5] Validating environment variables...{RESET}")
        self.check_env_file()

        print(f"{BLUE}[2/5] Validating file structure...{RESET}")
        self.check_file_structure()

        print(f"{BLUE}[3/5] Validating dependencies...{RESET}")
        self.check_dependencies()

        print(f"{BLUE}[4/5] Validating git repository...{RESET}")
        self.check_git()

        print(f"{BLUE}[5/5] Validating build configuration...{RESET}")
        self.check_build_config()

        return len(self.errors) == 0

    def check_env_file(self):
        """Check environment variables"""
        if not self.env_file.exists():
            self.errors.append(f".env file not found at {self.env_file}")
            return

        # Load .env file
        env_vars = {}
        with open(self.env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

        # Check required variables
        missing_required = []
        for var in REQUIRED_ENV_VARS:
            if var not in env_vars or not env_vars[var] or 'your_' in env_vars[var]:
                missing_required.append(var)

        if missing_required:
            self.errors.append(f"Missing required environment variables: {', '.join(missing_required)}")
            print(f"{RED}   [FAIL] Missing {len(missing_required)} required variables{RESET}")
        else:
            print(f"{GREEN}   [OK] All {len(REQUIRED_ENV_VARS)} required variables set{RESET}")

        # Check optional variables
        missing_optional = []
        for var in OPTIONAL_ENV_VARS:
            if var not in env_vars or not env_vars[var] or 'your_' in env_vars[var]:
                missing_optional.append(var)

        if missing_optional:
            self.warnings.append(f"Missing optional variables: {', '.join(missing_optional)}")
            print(f"{YELLOW}   [WARNING] {len(missing_optional)} optional variables not set{RESET}")

    def check_file_structure(self):
        """Validate required files exist"""
        required_files = [
            "package.json",
            "backend/package.json",
            "backend/crewai_agents/api_server.py",
            "backend/crewai_agents/requirements.txt",
            "src/main.tsx",
            "index.html",
        ]

        missing_files = [f for f in required_files if not Path(f).exists()]

        if missing_files:
            self.errors.append(f"Missing required files: {', '.join(missing_files)}")
            print(f"{RED}   [FAIL] Missing {len(missing_files)} required files{RESET}")
        else:
            print(f"{GREEN}   [OK] All required files present{RESET}")

    def check_dependencies(self):
        """Check if dependencies are installed"""
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            node_version = result.stdout.strip()
            print(f"{GREEN}   [OK] Node.js {node_version}{RESET}")
        except FileNotFoundError:
            self.errors.append("Node.js not installed")
            print(f"{RED}   [FAIL] Node.js not found{RESET}")

        # Check Python
        try:
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            python_version = result.stdout.strip()
            print(f"{GREEN}   [OK] Python {python_version}{RESET}")
        except FileNotFoundError:
            self.errors.append("Python not installed")
            print(f"{RED}   [FAIL] Python not found{RESET}")

        # Check npm dependencies
        if not Path("node_modules").exists():
            self.warnings.append("Frontend dependencies not installed (run: npm install)")
            print(f"{YELLOW}   [WARNING] Run 'npm install' first{RESET}")

        if not Path("backend/node_modules").exists():
            self.warnings.append("Backend dependencies not installed (run: cd backend && npm install)")
            print(f"{YELLOW}   [WARNING] Run 'cd backend && npm install' first{RESET}")

    def check_git(self):
        """Check git repository status"""
        try:
            # Check if git is initialized
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                self.warnings.append("Not a git repository (optional for deployment)")
                print(f"{YELLOW}   [WARNING] Not a git repository{RESET}")
            else:
                print(f"{GREEN}   [OK] Git repository initialized{RESET}")

                # Check for uncommitted changes
                if "nothing to commit" not in result.stdout:
                    self.warnings.append("Uncommitted changes detected")
                    print(f"{YELLOW}   [WARNING] Uncommitted changes{RESET}")
        except FileNotFoundError:
            self.warnings.append("Git not installed")
            print(f"{YELLOW}   [WARNING] Git not found{RESET}")

    def check_build_config(self):
        """Check build configuration files"""
        if Path("railway.json").exists():
            print(f"{GREEN}   [OK] Railway config found{RESET}")
        else:
            self.warnings.append("railway.json not found")
            print(f"{YELLOW}   [WARNING] railway.json missing{RESET}")

        if Path("render.yaml").exists():
            print(f"{GREEN}   [OK] Render config found{RESET}")
        else:
            self.warnings.append("render.yaml not found")
            print(f"{YELLOW}   [WARNING] render.yaml missing{RESET}")

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("DEPLOYMENT VALIDATION SUMMARY")
        print("="*60)

        if self.errors:
            print(f"\n{RED}[ERRORS] {len(self.errors)} critical issues:{RESET}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n{YELLOW}[WARNINGS] {len(self.warnings)} non-critical issues:{RESET}")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print(f"\n{GREEN}[SUCCESS] All checks passed! Ready to deploy.{RESET}")
        elif not self.errors:
            print(f"\n{GREEN}[READY] No critical errors. You can deploy, but warnings should be addressed.{RESET}")
        else:
            print(f"\n{RED}[BLOCKED] Fix errors before deploying.{RESET}")

        print("\n" + "="*60 + "\n")


class RailwayDeployer:
    """Deploy to Railway"""

    def deploy(self):
        """Execute Railway deployment"""
        print(f"\n{BLUE}Deploying to Railway...{RESET}\n")

        # Check if Railway CLI is installed
        try:
            subprocess.run(['railway', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"{RED}[ERROR] Railway CLI not installed{RESET}")
            print(f"\nInstall it with: npm install -g @railway/cli")
            print(f"Then login with: railway login")
            return False

        # Link to Railway project (or create new)
        print(f"{BLUE}[1/4] Linking to Railway project...{RESET}")
        subprocess.run(['railway', 'link'])

        # Set environment variables
        print(f"\n{BLUE}[2/4] Setting environment variables...{RESET}")
        env_file = Path("backend/crewai_agents/.env")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key in REQUIRED_ENV_VARS or key in OPTIONAL_ENV_VARS:
                        print(f"  Setting {key}...")
                        subprocess.run(['railway', 'variables', 'set', f'{key}={value}'],
                                     capture_output=True)

        # Deploy
        print(f"\n{BLUE}[3/4] Deploying application...{RESET}")
        result = subprocess.run(['railway', 'up', '--detach'])

        if result.returncode == 0:
            print(f"\n{GREEN}[4/4] Deployment successful!{RESET}")
            print(f"\nView your deployment: railway open")
            print(f"View logs: railway logs")
            return True
        else:
            print(f"\n{RED}[4/4] Deployment failed{RESET}")
            return False


class RenderDeployer:
    """Deploy to Render"""

    def deploy(self):
        """Execute Render deployment"""
        print(f"\n{BLUE}Deploying to Render...{RESET}\n")

        print(f"{YELLOW}Render deployment requires manual setup:{RESET}\n")
        print(f"1. Go to https://dashboard.render.com/")
        print(f"2. Click 'New +' → 'Blueprint'")
        print(f"3. Connect your GitHub repository")
        print(f"4. Render will detect render.yaml and create all services")
        print(f"5. Set environment variables in the Render dashboard:")

        # Print environment variables to set
        env_file = Path("backend/crewai_agents/.env")
        if env_file.exists():
            print(f"\n{BLUE}Environment variables to set:{RESET}")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key in REQUIRED_ENV_VARS:
                            print(f"  {key}={value[:10]}..." if len(value) > 10 else f"  {key}={value}")

        print(f"\n6. Deploy all services")
        print(f"\n{GREEN}Follow these steps in your browser to complete deployment.{RESET}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Deploy Rekindle.ai to production")
    parser.add_argument('--platform', choices=['railway', 'render'],
                       help="Deployment platform")
    parser.add_argument('--check', action='store_true',
                       help="Only validate configuration, don't deploy")

    args = parser.parse_args()

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Rekindle.ai Production Deployment{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Validate configuration
    validator = DeploymentValidator()
    is_valid = validator.validate_all()
    validator.print_summary()

    if args.check:
        sys.exit(0 if is_valid else 1)

    if not is_valid:
        print(f"{RED}Fix validation errors before deploying.{RESET}\n")
        sys.exit(1)

    # Deploy
    if not args.platform:
        print(f"{YELLOW}Please specify a platform: --platform railway or --platform render{RESET}")
        sys.exit(1)

    if args.platform == 'railway':
        deployer = RailwayDeployer()
        success = deployer.deploy()
    else:
        deployer = RenderDeployer()
        success = deployer.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
