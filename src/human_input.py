"""
A humanized version of Windows native input.

This module provides a class that inherits from WindowsInput and overrides
methods to simulate more human-like behavior by adding randomness and breaking
down mouse movements into smaller steps.
"""

import ctypes
import time
import random
import math
from src.windows_input import WindowsInput

class HumanizedWindowsInput(WindowsInput):
    """
    Handles keyboard and mouse input using Windows SendInput API with a touch of humanity.
    """

    def __init__(self):
        """Initialize the humanized Windows input handler."""
        super().__init__()

    def key_down(self, key_str: str):
        """
        Press a key down with a small random delay.
        """
        self._human_pause()
        super().key_down(key_str)

    def key_up(self, key_str: str):
        """
        Release a key with a small random delay.
        """
        self._human_pause()
        super().key_up(key_str)

    def mouse_down(self, button: str = 'left'):
        """
        Press a mouse button down with a small random delay.
        """
        self._human_pause()
        super().mouse_down(button)

    def mouse_up(self, button: str = 'left'):
        """
        Release a mouse button with a small random delay.
        """
        self._human_pause()
        super().mouse_up(button)

    def mouse_move_relative(self, dx: int, dy: int):
        """
        Move mouse relative to current position in a human-like way.

        This method breaks down the movement into smaller steps to simulate
        a smoother, less robotic motion path.
        """
        if dx == 0 and dy == 0:
            return

        total_distance = math.sqrt(dx**2 + dy**2)
        
        # Determine the number of steps based on the distance
        # For very short distances, a single step is fine. For longer, more steps.
        num_steps = max(1, min(20, int(total_distance / 15)))

        if num_steps == 1:
            super().mouse_move_relative(dx, dy)
            self._human_pause()
            return

        step_dx = dx / num_steps
        step_dy = dy / num_steps
        
        for i in range(num_steps):
            # Add some randomness to each step to make the path less linear
            noise_x = random.uniform(-1.5, 1.5)
            noise_y = random.uniform(-1.5, 1.5)

            # Move one step
            super().mouse_move_relative(step_dx + noise_x, step_dy + noise_y)

            # The duration of the pause can depend on the number of steps
            # to keep the total movement time somewhat consistent.
            # A longer movement should take a bit longer.
            sleep_duration = random.uniform(0.001, 0.005) * (total_distance / 100)
            sleep_duration = min(0.01, sleep_duration) # cap sleep time
            if sleep_duration > 0.001:
                time.sleep(sleep_duration)

    def _human_pause(self):
        """
        A short, random pause to simulate human reaction time.
        """
        time.sleep(random.uniform(0.01, 0.04))
