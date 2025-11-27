#!/usr/bin/env python3
"""
Test Windows Messages approach with Star Citizen.
This is an alternative to SendInput that might bypass anti-cheat.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.windows_messages import WindowsMessages

print("=" * 60)
print("Testing Windows Messages with Star Citizen")
print("=" * 60)
print()
print("This tests sending keyboard input via Windows Messages (WM_KEYDOWN/WM_KEYUP)")
print("instead of SendInput. This might work with anti-cheat.")
print()
print("Instructions:")
print("  1. Make sure Star Citizen is RUNNING")
print("  2. Put your character in a safe place where you can see movement")
print("  3. Leave the game window in the foreground")
print()

input("Press Enter when ready...")
print()
print("Searching for Star Citizen window...")
print()

msg_input = WindowsMessages("Star Citizen")

if not msg_input.window_handle:
    print("ERROR: Could not find Star Citizen window!")
    print("Make sure the game is running.")
    sys.exit(1)

print("Starting test in 3 seconds...")
print()

for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print()
print("Testing Z key (forward movement) for 3 seconds...")
print()

# Test Z key
msg_input.key_down('z')
time.sleep(3)
msg_input.key_up('z')

print("Released Z")
print()

time.sleep(1)

print("Testing Q key (strafe left) for 2 seconds...")
msg_input.key_down('q')
time.sleep(2)
msg_input.key_up('q')

print("Released Q")
print()

print("=" * 60)
print("Test Complete!")
print("=" * 60)
print()
print("Did your character move?")
print("  - If YES: Windows Messages works! We can use this method.")
print("  - If NO: Star Citizen blocks this too. Need hardware-level solution.")
print()
