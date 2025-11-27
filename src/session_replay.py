"""
Session replay module to replay recorded keyboard and mouse inputs.
Simulates the exact inputs from a recorded session.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from pynput import keyboard, mouse


class SessionReplay:
    """Replays recorded keyboard and mouse inputs."""

    def __init__(self, session_path: str):
        """
        Initialize session replay.

        Args:
            session_path: Path to recorded session directory
        """
        self.session_path = Path(session_path)

        if not self.session_path.exists():
            raise ValueError(f"Session path does not exist: {session_path}")

        # Load input events
        self.events = self._load_events()

        # Controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        # State tracking
        self.replaying = False
        self._current_event_idx = 0
        self._start_time = None
        self._pressed_keys = {}  # Map key_id to pynput key object

    def _load_events(self) -> List[Dict[str, Any]]:
        """Load input events from JSON file."""
        inputs_path = self.session_path / "inputs.json"

        if not inputs_path.exists():
            raise FileNotFoundError(f"Inputs file not found: {inputs_path}")

        with open(inputs_path, 'r') as f:
            data = json.load(f)

        return data.get('events', [])

    def _parse_key(self, key_str: str):
        """
        Parse key string to pynput key object.

        Args:
            key_str: String representation of key (e.g., "Key.w", "a")

        Returns:
            pynput key object
        """
        # Special keys
        if key_str.startswith('Key.'):
            key_name = key_str.split('.')[1]

            # Map common special keys
            key_map = {
                'space': keyboard.Key.space,
                'shift': keyboard.Key.shift,
                'shift_l': keyboard.Key.shift_l,
                'shift_r': keyboard.Key.shift_r,
                'ctrl': keyboard.Key.ctrl,
                'ctrl_l': keyboard.Key.ctrl_l,
                'ctrl_r': keyboard.Key.ctrl_r,
                'alt': keyboard.Key.alt,
                'alt_l': keyboard.Key.alt_l,
                'alt_r': keyboard.Key.alt_r,
                'tab': keyboard.Key.tab,
                'enter': keyboard.Key.enter,
                'esc': keyboard.Key.esc,
                'backspace': keyboard.Key.backspace,
                'delete': keyboard.Key.delete,
                'up': keyboard.Key.up,
                'down': keyboard.Key.down,
                'left': keyboard.Key.left,
                'right': keyboard.Key.right,
                'page_up': keyboard.Key.page_up,
                'page_down': keyboard.Key.page_down,
                'home': keyboard.Key.home,
                'end': keyboard.Key.end,
                'insert': keyboard.Key.insert,
                'f1': keyboard.Key.f1,
                'f2': keyboard.Key.f2,
                'f3': keyboard.Key.f3,
                'f4': keyboard.Key.f4,
                'f5': keyboard.Key.f5,
                'f6': keyboard.Key.f6,
                'f7': keyboard.Key.f7,
                'f8': keyboard.Key.f8,
                'f9': keyboard.Key.f9,
                'f10': keyboard.Key.f10,
                'f11': keyboard.Key.f11,
                'f12': keyboard.Key.f12,
            }

            return key_map.get(key_name.lower(), keyboard.KeyCode.from_char(key_name[0]))

        # Regular character
        return keyboard.KeyCode.from_char(key_str)

    def _parse_mouse_button(self, button_str: str):
        """
        Parse mouse button string to pynput button object.

        Args:
            button_str: String representation of button (e.g., "left", "right")

        Returns:
            pynput mouse button object
        """
        button_map = {
            'left': mouse.Button.left,
            'right': mouse.Button.right,
            'middle': mouse.Button.middle,
        }

        return button_map.get(button_str.lower(), mouse.Button.left)

    def play(self, speed: float = 1.0, start_delay: int = 3):
        """
        Play the recorded session.

        Args:
            speed: Playback speed multiplier (1.0 = normal, 2.0 = 2x speed, etc.)
            start_delay: Delay in seconds before starting playback
        """
        if not self.events:
            print("[SessionReplay] No events to replay!")
            return

        print(f"[SessionReplay] Loaded {len(self.events)} events")
        print(f"[SessionReplay] Playback speed: {speed}x")
        print(f"[SessionReplay] Starting in {start_delay} seconds...")
        print("[SessionReplay] Switch to Star Citizen window!")
        print()

        # Countdown
        for i in range(start_delay, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        print()
        print("[SessionReplay] Replaying session... Press Ctrl+C to stop")
        print()

        self.replaying = True
        self._current_event_idx = 0
        self._start_time = time.time()
        self._pressed_keys = {}

        try:
            while self.replaying and self._current_event_idx < len(self.events):
                event = self.events[self._current_event_idx]

                # Calculate when this event should occur
                event_time = event['timestamp'] / speed
                current_elapsed = time.time() - self._start_time

                # Wait until it's time for this event
                wait_time = event_time - current_elapsed
                if wait_time > 0:
                    time.sleep(wait_time)

                # Execute event
                self._execute_event(event)

                # Progress indicator every 5 seconds
                if self._current_event_idx % 100 == 0:
                    progress = (self._current_event_idx / len(self.events)) * 100
                    print(f"[SessionReplay] Progress: {progress:.1f}% "
                          f"({self._current_event_idx}/{len(self.events)} events)")

                self._current_event_idx += 1

        except KeyboardInterrupt:
            print("\n[SessionReplay] Interrupted by user")
        finally:
            # Release all pressed keys
            self._release_all_keys()
            self.replaying = False

        print(f"[SessionReplay] Replay complete!")

    def _execute_event(self, event: Dict[str, Any]):
        """Execute a single input event."""
        event_type = event['type']
        data = event['data']

        try:
            if event_type == 'key_press':
                key = self._parse_key(data['key_id'])
                self._pressed_keys[data['key_id']] = key
                self.keyboard_controller.press(key)

            elif event_type == 'key_release':
                key_id = data['key_id']
                if key_id in self._pressed_keys:
                    key = self._pressed_keys[key_id]
                    self.keyboard_controller.release(key)
                    del self._pressed_keys[key_id]

            elif event_type == 'mouse_move':
                self.mouse_controller.position = (data['x'], data['y'])

            elif event_type == 'mouse_press':
                button = self._parse_mouse_button(data['button'])
                self.mouse_controller.press(button)

            elif event_type == 'mouse_release':
                button = self._parse_mouse_button(data['button'])
                self.mouse_controller.release(button)

            elif event_type == 'mouse_scroll':
                self.mouse_controller.scroll(data['dx'], data['dy'])

        except Exception as e:
            print(f"[SessionReplay] Error executing event {event_type}: {e}")

    def _release_all_keys(self):
        """Release all currently pressed keys."""
        for key_id, key in list(self._pressed_keys.items()):
            try:
                self.keyboard_controller.release(key)
            except:
                pass
        self._pressed_keys.clear()

    def stop(self):
        """Stop replay."""
        self.replaying = False
        self._release_all_keys()

    def get_info(self) -> dict:
        """Get information about the session."""
        if not self.events:
            return {}

        # Calculate statistics
        duration = self.events[-1]['timestamp'] if self.events else 0

        event_counts = {}
        for event in self.events:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            'total_events': len(self.events),
            'duration': duration,
            'event_counts': event_counts,
            'session_path': str(self.session_path)
        }
