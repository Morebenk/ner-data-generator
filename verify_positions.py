#!/usr/bin/env python3
"""Quick verification that positions are 100% accurate."""
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python verify_positions.py <json_file>")
    sys.exit(1)

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"\n🔍 Verifying positions in {sys.argv[1]}")
print("=" * 70)

errors = 0
total = 0

for i, item in enumerate(data, 1):  # Check all items
    text = item["text"]
    entities = item["entities"]
    
    print(f"\nItem {i}:")
    print(f"Full text ({len(text)} chars): {text}")
    print(f"\nChecking {len(entities)} entities:")
    
    for start, end, label, expected in entities:
        total += 1
        actual = text[start:end]
        match = "✓" if actual == expected else "✗"
        print(f"  [{start:3d}:{end:3d}] {label:20s} Expected: '{expected}' | Got: '{actual}' {match}")
        
        if actual != expected:
            errors += 1

print("\n" + "=" * 70)
if errors == 0:
    print(f"✅ PERFECT! All {total} positions are 100% accurate!")
else:
    print(f"❌ {errors}/{total} positions have errors")
