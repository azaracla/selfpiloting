#!/usr/bin/env python3
"""
Test vJoy virtual joystick with Star Citizen.
This tests if vJoy bypasses Easy Anti-Cheat.

Prerequisites:
1. Download and install vJoy: https://sourceforge.net/projects/vjoystick/
2. Install pyvjoy: pip install pyvjoy
3. Configure vJoy device 1 with at least 6 axes and 12 buttons
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.vjoy_input import VJoyInput, VJOY_AVAILABLE
except ImportError as e:
    print(f"Error importing vJoyInput: {e}")
    sys.exit(1)

if not VJOY_AVAILABLE:
    print("=" * 60)
    print("ERROR: pyvjoy not installed")
    print("=" * 60)
    print()
    print("Please install:")
    print("  1. vJoy driver: https://sourceforge.net/projects/vjoystick/")
    print("  2. pyvjoy: pip install pyvjoy")
    print()
    sys.exit(1)

print("=" * 60)
print("Testing vJoy with Star Citizen")
print("=" * 60)
print()
print("This tests if vJoy can bypass Easy Anti-Cheat.")
print()
print("Prerequisites:")
print("  ✓ vJoy driver installed")
print("  ✓ pyvjoy package installed")
print("  ✓ vJoy device 1 enabled (use vJoy Configure tool)")
print()
print("Instructions:")
print("  1. Make sure Star Citizen is RUNNING")
print("  2. Get in your ship or on foot")
print("  3. Make sure the game is in the FOREGROUND")
print()

input("Press Enter when ready...")
print()
print("Initializing vJoy device...")

try:
    vjoy = VJoyInput(device_id=1)
except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("Make sure:")
    print("  1. vJoy is installed")
    print("  2. vJoy device 1 is enabled (use 'Configure vJoy' app)")
    print("  3. Device has at least 6 axes and 12 buttons configured")
    sys.exit(1)

print()
print("vJoy device ready!")
print()
print("Starting test in 3 seconds...")
print()

for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print()
print("=" * 60)
print("Test 1: Forward movement (W key -> Y axis)")
print("=" * 60)
print("Your character/ship should move forward for 3 seconds...")
vjoy.key_down('w')
time.sleep(3)
vjoy.key_up('w')
print("Released")
time.sleep(1)

print()
print("=" * 60)
print("Test 2: Strafe left (A key -> X axis)")
print("=" * 60)
print("Your character/ship should strafe left for 2 seconds...")
vjoy.key_down('a')
time.sleep(2)
vjoy.key_up('a')
print("Released")
time.sleep(1)

print()
print("=" * 60)
print("Test 3: Primary weapon (Space -> Button 1)")
print("=" * 60)
print("Should trigger primary weapon/action...")
vjoy.key_down('space')
time.sleep(0.5)
vjoy.key_up('space')
print("Released")
time.sleep(1)

print()
print("=" * 60)
print("Test 4: Mouse movement simulation (RX/RY axes)")
print("=" * 60)
print("Camera should move...")
for i in range(5):
    vjoy.mouse_move_relative(10, 5)
    time.sleep(0.1)
time.sleep(1)

print()
print("=" * 60)
print("Test Complete!")
print("=" * 60)
print()
print("Did your character/ship respond to the inputs?")
print()
print("  ✅ If YES: vJoy works! It bypasses Easy Anti-Cheat!")
print("     You can now use session replay with Star Citizen.")
print()
print("  ❌ If NO: vJoy might not be configured correctly.")
print("     Check:")
print("       - vJoy device is enabled")
print("       - Star Citizen detects the vJoy controller")
print("       - Controller bindings in Star Citizen settings")
print()
print("Note: You may need to configure Star Citizen to recognize")
print("the vJoy controller in: Options > Keybindings > Joystick")
print()
