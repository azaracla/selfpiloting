"""
Windows native input using SendInput API.
This bypasses pyautogui limitations and works with games like Star Citizen.
"""

import ctypes
import time
from ctypes import wintypes
from typing import Dict

# Windows API constants
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# Virtual key codes for common keys
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
    'return': 0x0D,  # Alias for enter
    'tab': 0x09,
    'esc': 0x1B,
    'escape': 0x1B,  # Alias for esc
    'backspace': 0x08,
    'delete': 0x2E,
    'del': 0x2E,  # Alias for delete

    'shift': 0x10,
    'shiftleft': 0xA0,
    'shift_l': 0xA0,
    'shiftright': 0xA1,
    'shift_r': 0xA1,
    'ctrl': 0x11,
    'control': 0x11,
    'ctrlleft': 0xA2,
    'ctrl_l': 0xA2,
    'ctrlright': 0xA3,
    'ctrl_r': 0xA3,
    'alt': 0x12,
    'altleft': 0xA4,
    'alt_l': 0xA4,
    'altright': 0xA5,
    'alt_r': 0xA5,

    'up': 0x26,
    'down': 0x28,
    'left': 0x25,
    'right': 0x27,

    'pageup': 0x21,
    'page_up': 0x21,
    'pagedown': 0x22,
    'page_down': 0x22,
    'home': 0x24,
    'end': 0x23,
    'insert': 0x2D,

    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,

    # Additional symbols and numpad keys
    'num0': 0x60, 'num1': 0x61, 'num2': 0x62, 'num3': 0x63,
    'num4': 0x64, 'num5': 0x65, 'num6': 0x66, 'num7': 0x67,
    'num8': 0x68, 'num9': 0x69,
    'multiply': 0x6A, 'add': 0x6B, 'subtract': 0x6D,
    'decimal': 0x6E, 'divide': 0x6F,

    # Common symbols
    '-': 0xBD, '=': 0xBB, '[': 0xDB, ']': 0xDD,
    ';': 0xBA, "'": 0xDE, ',': 0xBC, '.': 0xBE,
    '/': 0xBF, '\\': 0xDC, '`': 0xC0,
}


# C structures
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(wintypes.ULONG))
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(wintypes.ULONG))
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ('uMsg', wintypes.DWORD),
        ('wParamL', wintypes.WORD),
        ('wParamH', wintypes.WORD)
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT)
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ('type', wintypes.DWORD),
        ('union', INPUT_UNION)
    ]


class WindowsInput:
    """Handles keyboard and mouse input using Windows SendInput API."""

    def __init__(self):
        """Initialize Windows input handler."""
        self.user32 = ctypes.windll.user32
        self.pressed_keys: Dict[str, int] = {}  # Map key name to VK code

    def _get_vk_code(self, key_str: str) -> int:
        """
        Get virtual key code for a key string.

        Args:
            key_str: Key string (e.g., 'w', 'space', 'shift')

        Returns:
            Virtual key code
        """
        # Strip quotes if present (e.g., "'z'" -> "z")
        # This happens when pynput KeyCode objects are converted to string
        if key_str.startswith("'") and key_str.endswith("'") and len(key_str) >= 3:
            key_str = key_str[1:-1]

        key_lower = key_str.lower()

        # Handle Key.xxx format from pynput
        if key_str.startswith('Key.'):
            key_lower = key_str.split('.')[1].lower()
            # Map pynput names to our VK codes
            if key_lower == 'shift_l':
                key_lower = 'shiftleft'
            elif key_lower == 'shift_r':
                key_lower = 'shiftright'
            elif key_lower == 'ctrl_l':
                key_lower = 'ctrlleft'
            elif key_lower == 'ctrl_r':
                key_lower = 'ctrlright'
            elif key_lower == 'alt_l':
                key_lower = 'altleft'
            elif key_lower == 'alt_r':
                key_lower = 'altright'
            elif key_lower == 'page_up':
                key_lower = 'pageup'
            elif key_lower == 'page_down':
                key_lower = 'pagedown'

        return VK_CODE.get(key_lower, 0)

    def key_down(self, key_str: str):
        """
        Press a key down.

        Args:
            key_str: Key string (e.g., 'w', 'space', 'shift')
        """
        vk_code = self._get_vk_code(key_str)
        if vk_code == 0:
            # Show both the string and hex representation for debugging
            hex_repr = ''.join(f'\\x{ord(c):02x}' for c in key_str)
            print(f"[WindowsInput] Warning: Unknown key '{key_str}' (hex: {hex_repr})")
            return

        self.pressed_keys[key_str] = vk_code

        # Create input structure
        extra = ctypes.c_ulong(0)
        ii_ = INPUT_UNION()
        ii_.ki = KEYBDINPUT(
            wVk=vk_code,
            wScan=0,
            dwFlags=0,  # Key down
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )

        x = INPUT(type=INPUT_KEYBOARD, union=ii_)
        self.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def key_up(self, key_str: str):
        """
        Release a key.

        Args:
            key_str: Key string (e.g., 'w', 'space', 'shift')
        """
        vk_code = self._get_vk_code(key_str)
        if vk_code == 0:
            return

        if key_str in self.pressed_keys:
            del self.pressed_keys[key_str]

        # Create input structure
        extra = ctypes.c_ulong(0)
        ii_ = INPUT_UNION()
        ii_.ki = KEYBDINPUT(
            wVk=vk_code,
            wScan=0,
            dwFlags=KEYEVENTF_KEYUP,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )

        x = INPUT(type=INPUT_KEYBOARD, union=ii_)
        self.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def press_key(self, key_str: str, duration: float = 0.05):
        """
        Press and release a key.

        Args:
            key_str: Key string
            duration: How long to hold the key (seconds)
        """
        self.key_down(key_str)
        time.sleep(duration)
        self.key_up(key_str)

    def mouse_move(self, x: int, y: int):
        """
        Move mouse to absolute position.

        Args:
            x: X coordinate (screen coordinates)
            y: Y coordinate (screen coordinates)
        """
        # Get screen dimensions
        screen_width = self.user32.GetSystemMetrics(0)
        screen_height = self.user32.GetSystemMetrics(1)

        # Convert to absolute coordinates (0-65535)
        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)

        extra = ctypes.c_ulong(0)
        ii_ = INPUT_UNION()
        ii_.mi = MOUSEINPUT(
            dx=abs_x,
            dy=abs_y,
            mouseData=0,
            dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )

        x = INPUT(type=INPUT_MOUSE, union=ii_)
        self.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def mouse_down(self, button: str = 'left'):
        """
        Press mouse button down.

        Args:
            button: Button name ('left', 'right', 'middle')
        """
        button_flags = {
            'left': MOUSEEVENTF_LEFTDOWN,
            'right': MOUSEEVENTF_RIGHTDOWN,
            'middle': MOUSEEVENTF_MIDDLEDOWN,
        }

        flag = button_flags.get(button.lower(), MOUSEEVENTF_LEFTDOWN)

        extra = ctypes.c_ulong(0)
        ii_ = INPUT_UNION()
        ii_.mi = MOUSEINPUT(
            dx=0, dy=0, mouseData=0,
            dwFlags=flag,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )

        x = INPUT(type=INPUT_MOUSE, union=ii_)
        self.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def mouse_up(self, button: str = 'left'):
        """
        Release mouse button.

        Args:
            button: Button name ('left', 'right', 'middle')
        """
        button_flags = {
            'left': MOUSEEVENTF_LEFTUP,
            'right': MOUSEEVENTF_RIGHTUP,
            'middle': MOUSEEVENTF_MIDDLEUP,
        }

        flag = button_flags.get(button.lower(), MOUSEEVENTF_LEFTUP)

        extra = ctypes.c_ulong(0)
        ii_ = INPUT_UNION()
        ii_.mi = MOUSEINPUT(
            dx=0, dy=0, mouseData=0,
            dwFlags=flag,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )

        x = INPUT(type=INPUT_MOUSE, union=ii_)
        self.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def mouse_scroll(self, amount: int):
        """
        Scroll mouse wheel.

        Args:
            amount: Scroll amount (positive = up, negative = down)
        """
        # Windows uses WHEEL_DELTA = 120 as one "notch"
        WHEEL_DELTA = 120
        scroll_amount = int(amount * WHEEL_DELTA)

        extra = ctypes.c_ulong(0)
        ii_ = INPUT_UNION()
        ii_.mi = MOUSEINPUT(
            dx=0, dy=0,
            mouseData=wintypes.DWORD(scroll_amount),
            dwFlags=MOUSEEVENTF_WHEEL,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )

        x = INPUT(type=INPUT_MOUSE, union=ii_)
        self.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_all_keys(self):
        """Release all currently pressed keys."""
        for key_str in list(self.pressed_keys.keys()):
            self.key_up(key_str)
        self.pressed_keys.clear()
