#!/usr/bin/env python3
"""
Debug script to see what keys are recorded in a session.
Helps diagnose key parsing issues.
"""

import json
import sys
from pathlib import Path
from collections import Counter

def analyze_session(session_path):
    """Analyze keys in a session."""
    inputs_file = Path(session_path) / "inputs.json"

    if not inputs_file.exists():
        print(f"Error: {inputs_file} not found")
        return

    with open(inputs_file, 'r') as f:
        data = json.load(f)

    events = data.get('events', [])

    print("=" * 60)
    print(f"Session Analysis: {session_path}")
    print("=" * 60)
    print(f"Total events: {len(events)}")
    print()

    # Count event types
    event_types = Counter(e['type'] for e in events)
    print("Event types:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    print()

    # Extract all unique keys
    keys_pressed = set()
    keys_released = set()

    for event in events:
        if event['type'] == 'key_press':
            key = event['data']['key_id']
            keys_pressed.add(key)
        elif event['type'] == 'key_release':
            key = event['data']['key_id']
            keys_released.add(key)

    all_keys = keys_pressed | keys_released

    print(f"Unique keys used: {len(all_keys)}")
    print()

    # Show first 20 keys with their representation
    print("Sample keys (first 20):")
    for i, key in enumerate(sorted(all_keys)[:20], 1):
        # Show the key, its length, and hex representation
        hex_repr = ' '.join(f'{ord(c):02x}' for c in key)
        print(f"  {i:2d}. '{key}' (len={len(key)}, hex={hex_repr})")

    if len(all_keys) > 20:
        print(f"  ... and {len(all_keys) - 20} more keys")

    print()

    # Check for problematic keys
    print("Checking for potential issues:")

    # Keys with quotes
    quoted_keys = [k for k in all_keys if k.startswith("'") and k.endswith("'")]
    if quoted_keys:
        print(f"  ⚠ Found {len(quoted_keys)} keys with quotes:")
        for key in quoted_keys[:5]:
            print(f"    - {repr(key)}")
        if len(quoted_keys) > 5:
            print(f"    ... and {len(quoted_keys) - 5} more")
    else:
        print("  ✓ No keys with extra quotes")

    # Non-printable characters
    non_printable = [k for k in all_keys if any(ord(c) < 32 and c not in '\t\n\r' for c in k)]
    if non_printable:
        print(f"  ⚠ Found {len(non_printable)} keys with non-printable characters:")
        for key in non_printable[:5]:
            hex_repr = ' '.join(f'{ord(c):02x}' for c in key)
            print(f"    - {repr(key)} (hex: {hex_repr})")
    else:
        print("  ✓ No non-printable characters")

    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python debug_keys.py <session_path>")
        print()
        print("Example:")
        print("  python debug_keys.py recordings/session_20231127_143022")
        sys.exit(1)

    analyze_session(sys.argv[1])
