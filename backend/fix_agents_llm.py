#!/usr/bin/env python3
"""
Quick script to add Anthropic LLM configuration to all CrewAI agents
"""
import os
import re

agents_dir = r"c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents\agents"

# Pattern to find Agent instantiation
pattern = r'(self\.agent = Agent\()'

# LLM configuration to insert
llm_config = '''        # Configure to use Anthropic Claude
        from crewai import LLM
        llm = LLM(model="claude-3-5-sonnet-20241022", provider="anthropic")

        '''

for filename in os.listdir(agents_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(agents_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if LLM is already configured
        if 'LLM(model="claude-3-5-sonnet-20241022"' in content:
            print(f"[OK] {filename} already has LLM configured")
            continue

        # Check if it has an Agent instantiation
        if 'self.agent = Agent(' not in content:
            print(f"[SKIP] {filename} has no Agent instantiation")
            continue

        # Find all Agent instantiations and add llm parameter if not present
        original = content

        # Add LLM import and configuration before Agent instantiation
        content = re.sub(
            r'(        )(self\.agent = Agent\()',
            llm_config + r'\1\2',
            content,
            count=0  # Replace all occurrences
        )

        # Add llm parameter to Agent if not already present
        # This is a simple approach - finds closing ) after Agent
        lines = content.split('\n')
        new_lines = []
        in_agent = False
        indent_level = 0

        for i, line in enumerate(lines):
            new_lines.append(line)

            if 'self.agent = Agent(' in line:
                in_agent = True
                indent_level = len(line) - len(line.lstrip())
            elif in_agent and line.strip() == ')':
                # Check if llm= is already in the Agent definition
                agent_block = '\n'.join(new_lines[-20:])  # Look at last 20 lines
                if 'llm=' not in agent_block:
                    # Insert llm parameter before closing )
                    new_lines.insert(-1, ' ' * (indent_level + 12) + 'llm=llm')
                in_agent = False

        content = '\n'.join(new_lines)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed {filename}")
        else:
            print(f"[SKIP] {filename} unchanged")

print("\nDone!")
