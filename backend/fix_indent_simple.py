#!/usr/bin/env python3
"""
Simple fix: Replace 6-space indented self.agent with 8-space indented.
"""
import os

agents_dir = r"c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents\agents"

fixed_count = 0

for filename in os.listdir(agents_dir):
    if not filename.endswith('.py'):
        continue

    filepath = os.path.join(agents_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix 6-space indentation to 8-space for self.agent = Agent( lines
    content = content.replace('      self.agent = Agent(', '        self.agent = Agent(')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {filename}")
        fixed_count += 1
    else:
        print(f"[OK] {filename}")

print(f"\nFixed {fixed_count} files")
