"""
Session replay module to replay recorded keyboard and mouse inputs.
Simulates the exact inputs from a recorded session.
"""

import json
import time
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional
from pynput import keyboard, mouse
import pyautogui
try:
    import pygetwindow as gw
except ImportError:
    gw = None


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

        # Platform detection
        self.is_windows = platform.system() == 'Windows'
        self.game_window = None

        # Configure pyautogui
        pyautogui.PAUSE = 0  # No pause between commands
        pyautogui.FAILSAFE = False  # Disable failsafe

    def _find_game_window(self) -> bool:
        """
        Find and activate the Star Citizen game window.

        Returns:
            True if window found and activated, False otherwise
        """
        if not gw:
            print("[SessionReplay] Warning: pygetwindow not available, cannot activate game window")
            return False

        try:
            # Search for Star Citizen window
            windows = gw.getWindowsWithTitle('Star Citizen')

            if not windows:
                # Try alternative window titles
                windows = gw.getWindowsWithTitle('StarCitizen')

            if not windows:
                # Try finding by partial match
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if 'star citizen' in w.title.lower()]

            if windows:
                self.game_window = windows[0]
                print(f"[SessionReplay] Found game window: '{self.game_window.title}'")

                # Activate the window
                try:
                    self.game_window.activate()
                    time.sleep(0.5)  # Give time for window to activate
                    print(f"[SessionReplay] Game window activated")
                    return True
                except Exception as e:
                    print(f"[SessionReplay] Could not activate window: {e}")
                    # Try to bring to front anyway
                    try:
                        self.game_window.restore()
                        self.game_window.show()
                        time.sleep(0.5)
                        return True
                    except:
                        pass
            else:
                print("[SessionReplay] Warning: Could not find Star Citizen window")
                print("[SessionReplay] Make sure the game is running and visible")
                return False

        except Exception as e:
            print(f"[SessionReplay] Error finding game window: {e}")
            return False

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

    def _key_to_pyautogui(self, key_str: str) -> str:
        """
        Convert pynput key string to pyautogui key name.

        Args:
            key_str: String representation of key (e.g., "Key.w", "a")

        Returns:
            pyautogui key name
        """
        # Special keys mapping
        if key_str.startswith('Key.'):
            key_name = key_str.split('.')[1]

            # Map to pyautogui key names
            key_map = {
                'space': 'space',
                'shift': 'shift',
                'shift_l': 'shiftleft',
                'shift_r': 'shiftright',
                'ctrl': 'ctrl',
                'ctrl_l': 'ctrlleft',
                'ctrl_r': 'ctrlright',
                'alt': 'alt',
                'alt_l': 'altleft',
                'alt_r': 'altright',
                'tab': 'tab',
                'enter': 'enter',
                'esc': 'esc',
                'backspace': 'backspace',
                'delete': 'delete',
                'up': 'up',
                'down': 'down',
                'left': 'left',
                'right': 'right',
                'page_up': 'pageup',
                'page_down': 'pagedown',
                'home': 'home',
                'end': 'end',
                'insert': 'insert',
                'f1': 'f1',
                'f2': 'f2',
                'f3': 'f3',
                'f4': 'f4',
                'f5': 'f5',
                'f6': 'f6',
                'f7': 'f7',
                'f8': 'f8',
                'f9': 'f9',
                'f10': 'f10',
                'f11': 'f11',
                'f12': 'f12',
            }

            return key_map.get(key_name.lower(), key_name.lower())

        # Regular character - return as is
        return key_str.lower()

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
        print()

        # Countdown
        for i in range(start_delay, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        print()

        # Try to find and activate game window
        print("[SessionReplay] Searching for Star Citizen window...")
        if self._find_game_window():
            print("[SessionReplay] Ready to replay! Game window is active.")
        else:
            print("[SessionReplay] Could not find game window automatically.")
            print("[SessionReplay] Please make sure Star Citizen is in the foreground!")
            print("[SessionReplay] Waiting 3 seconds for you to switch...")
            time.sleep(3)

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
        """Execute a single input event using pyautogui for better game compatibility."""
        event_type = event['type']
        data = event['data']

        try:
            if event_type == 'key_press':
                key_str = data['key_id']
                pyautogui_key = self._key_to_pyautogui(key_str)
                self._pressed_keys[key_str] = pyautogui_key
                pyautogui.keyDown(pyautogui_key)

            elif event_type == 'key_release':
                key_str = data['key_id']
                if key_str in self._pressed_keys:
                    pyautogui_key = self._pressed_keys[key_str]
                    pyautogui.keyUp(pyautogui_key)
                    del self._pressed_keys[key_str]

            elif event_type == 'mouse_move':
                pyautogui.moveTo(data['x'], data['y'], duration=0)

            elif event_type == 'mouse_press':
                button = data['button'].lower()
                pyautogui.mouseDown(button=button)

            elif event_type == 'mouse_release':
                button = data['button'].lower()
                pyautogui.mouseUp(button=button)

            elif event_type == 'mouse_scroll':
                # pyautogui.scroll expects a single value (positive = up, negative = down)
                # For vertical scroll, use dy; for horizontal, we'd need a different approach
                if data['dy'] != 0:
                    pyautogui.scroll(int(data['dy']))

        except Exception as e:
            print(f"[SessionReplay] Error executing event {event_type}: {e}")

    def _release_all_keys(self):
        """Release all currently pressed keys."""
        for key_id, pyautogui_key in list(self._pressed_keys.items()):
            try:
                pyautogui.keyUp(pyautogui_key)
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
