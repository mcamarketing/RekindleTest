#!/usr/bin/env python3
"""
Fix AIAgents.tsx by removing corrupted duplicate code after line 805.
"""

file_path = r"c:\Users\Hello\OneDrive\Documents\REKINDLE\src\pages\AIAgents.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep only the first 805 lines
fixed_lines = lines[:805]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"Fixed {file_path}")
print(f"Removed {len(lines) - 805} lines of corrupted code")
