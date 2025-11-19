"""
Main Entry Point for CrewAI Agents

CLI interface for running crews (all agents working together).
"""

import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()

from .orchestration_service import OrchestrationService


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m backend.crewai_agents <command> [args]")
        print("\nCommands:")
        print("  dead-lead-reactivation <user_id> - Run dead lead reactivation crew")
        print("  full-campaign <user_id> <lead_ids...> - Run full campaign crew")
        print("  handle-reply <lead_id> <reply_text> - Handle inbound reply")
        print("  auto-icp <user_id> - Run Auto-ICP crew")
        print("  daily-workflow <user_id> - Run complete daily workflow")
        return
    
    command = sys.argv[1]
    service = OrchestrationService()
    
    if command == "dead-lead-reactivation":
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not user_id:
            print("Error: user_id required")
            return
        
        result = service.run_dead_lead_reactivation(user_id)
        print(json.dumps(result, indent=2))
    
    elif command == "full-campaign":
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        lead_ids = sys.argv[3:] if len(sys.argv) > 3 else []
        
        if not user_id or not lead_ids:
            print("Error: user_id and lead_ids required")
            return
        
        result = service.run_full_campaign(user_id, lead_ids)
        print(json.dumps(result, indent=2))
    
    elif command == "handle-reply":
        lead_id = sys.argv[2] if len(sys.argv) > 2 else None
        reply_text = sys.argv[3] if len(sys.argv) > 3 else ""
        
        if not lead_id or not reply_text:
            print("Error: lead_id and reply_text required")
            return
        
        result = service.handle_inbound_reply(lead_id, reply_text)
        print(json.dumps(result, indent=2))
    
    elif command == "auto-icp":
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not user_id:
            print("Error: user_id required")
            return
        
        result = service.run_auto_icp_sourcing(user_id)
        print(json.dumps(result, indent=2))
    
    elif command == "daily-workflow":
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not user_id:
            print("Error: user_id required")
            return
        
        result = service.run_daily_workflow(user_id)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

