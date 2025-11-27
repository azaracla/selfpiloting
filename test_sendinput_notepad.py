#!/usr/bin/env python3
"""
Test SendInput in Notepad to verify it works at all.
This helps determine if the issue is with SendInput or Star Citizen blocking it.
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
print("Testing SendInput in Notepad")
print("=" * 60)
print()
print("This will test if SendInput works at all.")
print()
print("Instructions:")
print("  1. Open Notepad (search 'notepad' in Windows)")
print("  2. Put the cursor in Notepad")
print("  3. Make sure Notepad is in the FOREGROUND")
print("  4. Come back here and press Enter")
print()
input("Press Enter when Notepad is ready and in foreground...")
print()
print("Switching to Notepad in 3 seconds...")
print()

for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print()
print("Sending text to Notepad now...")
print()

input_handler = WindowsInput()

# Type a test message
test_text = "Hello from SendInput! This is a test.\n"
print(f"Typing: {test_text}")

for char in test_text:
    if char == '\n':
        input_handler.press_key('enter', 0.05)
    elif char == ' ':
        input_handler.press_key('space', 0.05)
    else:
        input_handler.key_down(char)
        time.sleep(0.05)
        input_handler.key_up(char)
    time.sleep(0.05)  # Small delay between chars

time.sleep(0.5)

# Test Z key specifically (hold for longer)
print("Now testing Z key (hold for 2 seconds)...")
input_handler.key_down('z')
time.sleep(2)
input_handler.key_up('z')

print()
print("=" * 60)
print("Test Complete!")
print("=" * 60)
print()
print("Check Notepad. You should see:")
print("  1. The text: 'Hello from SendInput! This is a test.'")
print("  2. A line of 'zzzz...' (from holding Z)")
print()
print("Results:")
print("  - If you SEE the text: SendInput works! Star Citizen is blocking it.")
print("  - If you DON'T see text: SendInput itself doesn't work (permissions/admin issue)")
print()
