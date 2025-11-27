"""
Input recording module for keyboard and mouse events.
Captures all keyboard and mouse inputs with precise timestamps.
"""

import time
import threading
from queue import Queue
from typing import Optional, List, Dict, Any
from pynput import keyboard, mouse


class InputRecorder:
    """Records keyboard and mouse inputs with timestamps."""

    def __init__(self):
        """Initialize input recorder."""
        self.recording = False
        self.events_queue = Queue()
        self.events_list = []  # Store all events chronologically

        self._keyboard_listener = None
        self._mouse_listener = None
        self._start_time = None

        # Track current state
        self._pressed_keys = set()
        self._mouse_position = (0, 0)
        self._mouse_buttons = set()

    def start(self):
        """Start recording inputs."""
        if self.recording:
            return

        self.recording = True
        self.events_list = []
        self._pressed_keys = set()
        self._mouse_buttons = set()
        self._start_time = time.time()

        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._keyboard_listener.start()

        # Start mouse listener
        self._mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self._mouse_listener.start()

        print("[InputRecorder] Started recording inputs")

    def stop(self):
        """Stop recording inputs."""
        if not self.recording:
            return

        self.recording = False

        # Stop listeners
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        print(f"[InputRecorder] Stopped. Recorded {len(self.events_list)} events")

    def _get_timestamp(self) -> float:
        """Get relative timestamp since recording started."""
        return time.time() - self._start_time

    def _add_event(self, event_type: str, data: Dict[str, Any]):
        """Add an event with timestamp."""
        event = {
            'timestamp': self._get_timestamp(),
            'type': event_type,
            'data': data
        }
        self.events_list.append(event)
        self.events_queue.put(event)

    def _on_key_press(self, key):
        """Callback for key press events."""
        if not self.recording:
            return

        try:
            # Try to get character
            key_char = key.char if hasattr(key, 'char') else str(key)
        except:
            key_char = str(key)

        key_id = str(key)

        if key_id not in self._pressed_keys:
            self._pressed_keys.add(key_id)
            self._add_event('key_press', {
                'key': key_char,
                'key_id': key_id
            })

    def _on_key_release(self, key):
        """Callback for key release events."""
        if not self.recording:
            return

        try:
            key_char = key.char if hasattr(key, 'char') else str(key)
        except:
            key_char = str(key)

        key_id = str(key)

        if key_id in self._pressed_keys:
            self._pressed_keys.discard(key_id)
            self._add_event('key_release', {
                'key': key_char,
                'key_id': key_id
            })

    def _on_mouse_move(self, x, y):
        """Callback for mouse movement."""
        if not self.recording:
            return

        self._mouse_position = (x, y)
        self._add_event('mouse_move', {
            'x': x,
            'y': y
        })

    def _on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse clicks."""
        if not self.recording:
            return

        button_name = str(button).split('.')[-1]  # Extract button name

        if pressed:
            self._mouse_buttons.add(button_name)
            self._add_event('mouse_press', {
                'x': x,
                'y': y,
                'button': button_name
            })
        else:
            self._mouse_buttons.discard(button_name)
            self._add_event('mouse_release', {
                'x': x,
                'y': y,
                'button': button_name
            })

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Callback for mouse scroll."""
        if not self.recording:
            return

        self._add_event('mouse_scroll', {
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy
        })

    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get all recorded events.

        Returns:
            List of event dictionaries with timestamps
        """
        return self.events_list.copy()

    def get_state_at_time(self, timestamp: float) -> Dict[str, Any]:
        """
        Get input state at a specific timestamp.

        Args:
            timestamp: Time to query state

        Returns:
            Dictionary with keyboard and mouse state
        """
        state = {
            'pressed_keys': set(),
            'mouse_position': (0, 0),
            'mouse_buttons': set()
        }

        # Replay events up to timestamp to reconstruct state
        for event in self.events_list:
            if event['timestamp'] > timestamp:
                break

            if event['type'] == 'key_press':
                state['pressed_keys'].add(event['data']['key_id'])
            elif event['type'] == 'key_release':
                state['pressed_keys'].discard(event['data']['key_id'])
            elif event['type'] == 'mouse_move':
                state['mouse_position'] = (event['data']['x'], event['data']['y'])
            elif event['type'] == 'mouse_press':
                state['mouse_buttons'].add(event['data']['button'])
            elif event['type'] == 'mouse_release':
                state['mouse_buttons'].discard(event['data']['button'])

        return state

    def get_stats(self) -> dict:
        """Get recording statistics."""
        event_counts = {}
        for event in self.events_list:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            'total_events': len(self.events_list),
            'event_counts': event_counts,
            'currently_pressed_keys': len(self._pressed_keys),
            'currently_pressed_buttons': len(self._mouse_buttons)
        }
