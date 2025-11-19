"""
Script to update all agents with action-first behavior.

This script:
1. Scans all agent files
2. Updates system prompts with action-first directives
3. Adds action-first enforcer imports
4. Ensures all agents follow execution-first protocol
"""

import os
import re
from pathlib import Path

# Agent files to update
AGENT_FILES = [
    "backend/crewai_agents/agents/researcher_agents.py",
    "backend/crewai_agents/agents/intelligence_agents.py",
    "backend/crewai_agents/agents/writer_agents.py",
    "backend/crewai_agents/agents/content_agents.py",
    "backend/crewai_agents/agents/safety_agents.py",
    "backend/crewai_agents/agents/sync_agents.py",
    "backend/crewai_agents/agents/revenue_agents.py",
    "backend/crewai_agents/agents/dead_lead_reactivation_agent.py",
    "backend/crewai_agents/agents/optimization_agents.py",
    "backend/crewai_agents/agents/infrastructure_agents.py",
    "backend/crewai_agents/agents/analytics_agents.py",
    "backend/crewai_agents/agents/master_intelligence_agent.py",
    "backend/crewai_agents/agents/launch_agents.py",
]

def update_agent_file(file_path: str):
    """Update a single agent file with action-first behavior."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Add import if not present
    if "from ..utils.action_first_enforcer import ActionFirstEnforcer" not in content:
        # Find the last import statement
        import_pattern = r"(from \.\.utils\.[^\n]+\n)"
        imports = re.findall(import_pattern, content)
        if imports:
            # Insert after last utils import
            last_import = imports[-1]
            content = content.replace(
                last_import,
                last_import + "from ..utils.action_first_enforcer import ActionFirstEnforcer\n"
            )
        else:
            # Add after other imports
            content = re.sub(
                r"(from \.\.utils\.[^\n]+\n)",
                r"\1from ..utils.action_first_enforcer import ActionFirstEnforcer\n",
                content,
                count=1
            )
    
    # 2. Update system_message to use ActionFirstEnforcer
    # Pattern: system_message="""..."""
    system_message_pattern = r'system_message="""(\[PERSONALITY\][\s\S]*?\[/PERSONALITY\][\s\S]*?)"""'
    
    def wrap_system_message(match):
        system_msg = match.group(1)
        # Check if already wrapped
        if "ActionFirstEnforcer.enforce_action_first" in system_msg:
            return match.group(0)
        # Wrap it
        return f'system_message=ActionFirstEnforcer.enforce_action_first("""{system_msg}""")'
    
    content = re.sub(system_message_pattern, wrap_system_message, content)
    
    # 3. Add action-first directive to backstory if system_message not found
    if "ActionFirstEnforcer.enforce_action_first" not in content:
        # Look for backstory and add directive
        backstory_pattern = r'(backstory="""[^"]*")'
        def add_directive_to_backstory(match):
            backstory = match.group(1)
            if "Execute immediately" not in backstory:
                backstory = backstory.rstrip('"') + '\nExecute immediately. Return results, not explanations."'
            return backstory
        content = re.sub(backstory_pattern, add_directive_to_backstory, content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
        return True
    else:
        print(f"No changes needed: {file_path}")
        return False

if __name__ == "__main__":
    print("Updating all agents with action-first behavior...")
    updated_count = 0
    for file_path in AGENT_FILES:
        if update_agent_file(file_path):
            updated_count += 1
    print(f"\nUpdated {updated_count} agent files.")

