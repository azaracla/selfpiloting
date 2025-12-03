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

# Import Windows native input for better game compatibility
try:
    from src.windows_input import WindowsInput
    from src.human_input import HumanizedWindowsInput
    WINDOWS_INPUT_AVAILABLE = True
except ImportError:
    try:
        from windows_input import WindowsInput
        from human_input import HumanizedWindowsInput
        WINDOWS_INPUT_AVAILABLE = True
    except ImportError:
        WINDOWS_INPUT_AVAILABLE = False
        WindowsInput = None
        HumanizedWindowsInput = None

try:
    from src.vjoy_input import VJoyInput, VJOY_AVAILABLE
except ImportError:
    try:
        from vjoy_input import VJoyInput, VJOY_AVAILABLE
    except ImportError:
        VJoyInput = None
        VJOY_AVAILABLE = False


class SessionReplay:
    """Replays recorded keyboard and mouse inputs."""

    def __init__(self, session_path: str, input_method: str = 'native'):
        """
        Initialize session replay.

        Args:
            session_path: Path to recorded session directory
            input_method: Input method to use ('native', 'human', 'vjoy', 'pyautogui').
        """
        self.session_path = Path(session_path)

        if not self.session_path.exists():
            raise ValueError(f"Session path does not exist: {session_path}")

        # Load input events
        self.events = self._load_events()

        # Platform detection
        self.is_windows = platform.system() == 'Windows'
        self.input_method = input_method

        # Choose input method
        self.input_handler = None
        if self.is_windows:
            if self.input_method == 'vjoy' and VJOY_AVAILABLE:
                print("[SessionReplay] Using vJoy input")
                try:
                    self.input_handler = VJoyInput()
                except (ImportError, RuntimeError) as e:
                    print(f"[SessionReplay] Error initializing vJoy: {e}")
                    self.input_handler = None # Fallback
            elif self.input_method == 'human' and WINDOWS_INPUT_AVAILABLE:
                print("[SessionReplay] Using humanized Windows native input")
                self.input_handler = HumanizedWindowsInput()
            elif self.input_method == 'native' and WINDOWS_INPUT_AVAILABLE:
                print("[SessionReplay] Using Windows native input (SendInput API)")
                self.input_handler = WindowsInput()

        if self.input_handler is None:
            print("[SessionReplay] Using pyautogui input (fallback)")
            self.input_method = 'pyautogui'
            # Controllers for pyautogui fallback
            self.keyboard_controller = keyboard.Controller()
            self.mouse_controller = mouse.Controller()
            # Configure pyautogui
            pyautogui.PAUSE = 0  # No pause between commands
            pyautogui.FAILSAFE = False  # Disable failsafe

        # State tracking
        self.replaying = False
        self._current_event_idx = 0
        self._start_time = None
        self._pressed_keys = {}  # Map key_id to key object/vk code
        self._last_mouse_pos = None  # Track last mouse position for relative movement

        self.game_window = None

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
            # Get all windows
            all_windows = gw.getAllWindows()

            # Filter for Star Citizen, excluding browsers and common false positives
            excluded_keywords = ['firefox', 'chrome', 'edge', 'browser', 'mozilla',
                                'github', 'discord', 'slack', 'teams', 'outlook']

            game_windows = []
            for window in all_windows:
                title_lower = window.title.lower()

                # Must contain "star citizen"
                if 'star citizen' not in title_lower:
                    continue

                # Exclude browsers and other apps
                if any(excluded in title_lower for excluded in excluded_keywords):
                    continue

                # Exclude very long titles (likely web pages)
                if len(window.title) > 100:
                    continue

                game_windows.append(window)

            if game_windows:
                # Prefer the first match
                self.game_window = game_windows[0]
                print(f"[SessionReplay] Found game window: '{self.game_window.title}'")

                # Show all found windows for debugging
                if len(game_windows) > 1:
                    print(f"[SessionReplay] Note: Found {len(game_windows)} matching windows:")
                    for i, w in enumerate(game_windows[:5]):  # Show max 5
                        print(f"  {i+1}. {w.title[:80]}")
                    print(f"[SessionReplay] Using the first one.")

                # Activate the window
                try:
                    self.game_window.activate()
                    time.sleep(0.5)  # Give time for window to activate
                    print(f"[SessionReplay] Game window activated successfully")
                    return True
                except Exception as e:
                    # Sometimes activate() throws an error even when it succeeds
                    # Check the error message
                    error_msg = str(e).lower()
                    if 'réussi' in error_msg or 'succeed' in error_msg or 'error code from windows: 0' in error_msg:
                        print(f"[SessionReplay] Game window activated (Windows reported success)")
                        return True

                    print(f"[SessionReplay] Warning: Could not activate window: {e}")
                    # Try to bring to front anyway
                    try:
                        self.game_window.restore()
                        self.game_window.show()
                        time.sleep(0.5)
                        print(f"[SessionReplay] Game window restored and shown")
                        return True
                    except Exception as e2:
                        print(f"[SessionReplay] Warning: Could not restore window: {e2}")
                        pass
            else:
                print("[SessionReplay] Warning: Could not find Star Citizen window")
                print("[SessionReplay] Make sure the game is running and visible")
                print("[SessionReplay] Windows with 'star citizen' in title:")
                sc_windows = [w for w in all_windows if 'star citizen' in w.title.lower()]
                if sc_windows:
                    for w in sc_windows[:5]:
                        print(f"  - {w.title[:80]}")
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
        self._last_mouse_pos = None  # Reset mouse position tracking

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
            if self.input_handler:
                # Use a unified input handler (WindowsInput or HumanizedWindowsInput)
                if event_type == 'key_press':
                    key_str = data['key_id']
                    self._pressed_keys[key_str] = True
                    self.input_handler.key_down(key_str)

                elif event_type == 'key_release':
                    key_str = data['key_id']
                    if key_str in self._pressed_keys:
                        self.input_handler.key_up(key_str)
                        del self._pressed_keys[key_str]

                elif event_type == 'mouse_move':
                    # Use relative mouse movement for games
                    x, y = data['x'], data['y']
                    if self._last_mouse_pos is not None:
                        dx = x - self._last_mouse_pos[0]
                        dy = y - self._last_mouse_pos[1]
                        self.input_handler.mouse_move_relative(dx, dy)
                    self._last_mouse_pos = (x, y)

                elif event_type == 'mouse_press':
                    button = data['button'].lower()
                    self.input_handler.mouse_down(button)

                elif event_type == 'mouse_release':
                    button = data['button'].lower()
                    self.input_handler.mouse_up(button)

                elif event_type == 'mouse_scroll':
                    if data['dy'] != 0:
                        # Convert scroll delta to clicks
                        clicks = data['dy'] / 120.0  # Standard wheel delta
                        self.input_handler.mouse_scroll(clicks)

            else:
                # Fallback to pyautogui
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
                    if data['dy'] != 0:
                        pyautogui.scroll(int(data['dy']))

        except Exception as e:
            print(f"[SessionReplay] Error executing event {event_type}: {e}")

    def _release_all_keys(self):
        """Release all currently pressed keys."""
        if self.input_handler:
            if self.input_method == 'vjoy':
                self.input_handler.release_all()
            else:
                self.input_handler.release_all_keys()
        else:
            # Pyautogui fallback
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
