#!/usr/bin/env python3
"""
Fix indentation errors in agent files caused by the LLM configuration script.
"""
import os
import re

agents_dir = r"c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents\agents"

fixed_count = 0

for filename in os.listdir(agents_dir):
    if not filename.endswith('.py'):
        continue

    filepath = os.path.join(agents_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix excessive indentation on self.agent = Agent( lines
    content = re.sub(r'(\s{8})(\s+)(self\.agent = Agent\()', r'\1\3', content)

    # Fix excessive indentation on llm=llm lines and ensure comma before it
    content = re.sub(
        r'(\s{12})allow_delegation=(True|False)\n(\s+)llm=llm',
        r'\1allow_delegation=\2,\n\1llm=llm',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[FIXED] {filename}")
        fixed_count += 1
    else:
        print(f"[OK] {filename}")

print(f"\nFixed {fixed_count} files")
