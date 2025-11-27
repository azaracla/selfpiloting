#!/usr/bin/env python3
"""
Quick test to verify Z key works with WindowsInput.
Run this with Star Citizen in foreground to test.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.windows_input import WindowsInput
except ImportError:
    from windows_input import WindowsInput

print("=" * 60)
print("Testing Z Key with WindowsInput")
print("=" * 60)
print()
print("Make sure Star Citizen is in the FOREGROUND!")
print()
print("This will test:")
print("  1. Press and hold Z for 2 seconds")
print("  2. Release Z")
print()
print("Your character should move forward.")
print()

for i in range(5, 0, -1):
    print(f"Starting in {i}...")
    time.sleep(1)

print()
print("Testing Z key now...")

input_handler = WindowsInput()

# Test with the exact format from the recording: 'z' (with quotes)
print("1. Testing raw 'z'")
input_handler.key_down('z')
time.sleep(2)
input_handler.key_up('z')
print("   Released")

time.sleep(1)

# Test with quoted format like in recordings
print("2. Testing quoted \"'z'\" (like in recordings)")
input_handler.key_down("'z'")
time.sleep(2)
input_handler.key_up("'z'")
print("   Released")

print()
print("=" * 60)
print("Test Complete!")
print("=" * 60)
print()
print("Did your character move forward?")
print("  - If YES for test 1: Basic Z key works")
print("  - If YES for test 2: Quoted format works (recordings will work)")
print("  - If NO for both: There may be another issue")
print()
