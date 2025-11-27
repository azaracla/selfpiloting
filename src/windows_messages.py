"""
Windows input using Windows Messages (WM_KEYDOWN/WM_KEYUP, etc).
This is an alternative to SendInput that might work with anti-cheat games.
"""

import ctypes
from ctypes import wintypes
import time
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Windows message constants
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A

# Virtual key codes (same as windows_input.py)
VK_CODE = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
    'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
    'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
    's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
    'y': 0x59, 'z': 0x5A,

    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,

    'space': 0x20,
    'enter': 0x0D,
    'tab': 0x09,
    'esc': 0x1B,
    'backspace': 0x08,
    'delete': 0x2E,

    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,

    'up': 0x26,
    'down': 0x28,
    'left': 0x25,
    'right': 0x27,

    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
}


class WindowsMessages:
    """Send input using Windows Messages instead of SendInput."""

    def __init__(self, window_title=None):
        """
        Initialize Windows Messages input.

        Args:
            window_title: Partial window title to target (e.g., "Star Citizen")
        """
        self.user32 = ctypes.windll.user32
        self.window_handle = None
        self.window_title = window_title

        if window_title:
            self._find_window(window_title)

    def _find_window(self, title_partial):
        """Find window by partial title."""
        if not gw:
            print("[WindowsMessages] Warning: pygetwindow not available")
            return False

        try:
            windows = gw.getAllWindows()
            for window in windows:
                if title_partial.lower() in window.title.lower():
                    # Get window handle using ctypes
                    self.window_handle = self.user32.FindWindowW(None, window.title)
                    print(f"[WindowsMessages] Found window: '{window.title}' (handle: {self.window_handle})")
                    return True

            print(f"[WindowsMessages] Warning: Could not find window with '{title_partial}'")
            return False

        except Exception as e:
            print(f"[WindowsMessages] Error finding window: {e}")
            return False

    def set_window_handle(self, hwnd):
        """Manually set the target window handle."""
        self.window_handle = hwnd

    def _get_vk_code(self, key_str: str) -> int:
        """Get virtual key code for a key string."""
        # Strip quotes if present
        if key_str.startswith("'") and key_str.endswith("'") and len(key_str) >= 3:
            key_str = key_str[1:-1]

        # Handle escaped characters
        if key_str.startswith('\\x') and len(key_str) == 4:
            return 0

        # Handle Key.xxx format
        if key_str.startswith('Key.'):
            key_name = key_str.split('.')[1].lower()
            return VK_CODE.get(key_name, 0)

        # Regular key
        key_lower = key_str.lower()
        return VK_CODE.get(key_lower, 0)

    def key_down(self, key_str: str):
        """Send key down message."""
        if not self.window_handle:
            print("[WindowsMessages] Warning: No window handle set")
            return

        vk_code = self._get_vk_code(key_str)
        if vk_code == 0:
            print(f"[WindowsMessages] Warning: Unknown key '{key_str}'")
            return

        # lParam encoding: repeat count (1), scan code, extended flag, context code, previous state, transition state
        # For simplicity, we use 0x00000001 (repeat=1, everything else=0)
        lparam = 0x00000001

        self.user32.PostMessageW(self.window_handle, WM_KEYDOWN, vk_code, lparam)

    def key_up(self, key_str: str):
        """Send key up message."""
        if not self.window_handle:
            return

        vk_code = self._get_vk_code(key_str)
        if vk_code == 0:
            return

        # lParam for key up: bit 30 = previous state (1), bit 31 = transition state (1)
        lparam = 0xC0000001

        self.user32.PostMessageW(self.window_handle, WM_KEYUP, vk_code, lparam)

    def press_key(self, key_str: str, duration: float = 0.05):
        """Press and release a key."""
        self.key_down(key_str)
        time.sleep(duration)
        self.key_up(key_str)


# Note: Mouse movement with messages is more complex and often doesn't work well
# because games typically use raw input or DirectInput for mouse control.
# We're focusing on keyboard for now.
