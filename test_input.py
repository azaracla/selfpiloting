#!/usr/bin/env python3
"""
Test script to verify if pyautogui works with Star Citizen.
This will help diagnose the input replay issue.
"""

import pyautogui
import time

print("=" * 60)
print("Input Test Script")
print("=" * 60)
print()
print("This will test if pyautogui can send inputs to Star Citizen.")
print()
print("Instructions:")
print("1. Make sure Star Citizen is running and in the FOREGROUND")
print("2. Put your cursor in the game window")
print("3. Watch if the character moves or keys are pressed")
print()
print("Starting test in 5 seconds...")
print()

for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print()
print("Testing inputs now...")
print()

# Test 1: Simple key press
print("Test 1: Pressing 'W' key (move forward)")
pyautogui.press('w')
time.sleep(1)

# Test 2: Hold key
print("Test 2: Holding 'W' key for 2 seconds")
pyautogui.keyDown('w')
time.sleep(2)
pyautogui.keyUp('w')
time.sleep(1)

# Test 3: Mouse movement
print("Test 3: Moving mouse slightly")
current_x, current_y = pyautogui.position()
pyautogui.moveTo(current_x + 50, current_y + 50, duration=0.5)
pyautogui.moveTo(current_x, current_y, duration=0.5)
time.sleep(1)

# Test 4: Multiple keys
print("Test 4: Pressing 'A' then 'D' (strafe left/right)")
pyautogui.press('a')
time.sleep(0.5)
pyautogui.press('d')
time.sleep(1)

print()
print("=" * 60)
print("Test complete!")
print("=" * 60)
print()
print("Did you see any movement in the game?")
print("  - If YES: pyautogui works, the replay code has another issue")
print("  - If NO: Star Citizen blocks pyautogui, we need DirectInput")
print()
