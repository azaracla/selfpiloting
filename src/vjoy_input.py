"""
vJoy input driver for Star Citizen session replay.
Converts keyboard/mouse inputs to virtual joystick inputs.

This bypasses Easy Anti-Cheat because:
- vJoy is a signed Windows driver
- Star Citizen natively supports joysticks
- EAC has no reason to block joystick input

Installation:
1. Download and install vJoy: https://sourceforge.net/projects/vjoystick/
2. Install pyvjoy: pip install pyvjoy
"""

try:
    import pyvjoy
    VJOY_AVAILABLE = True
except ImportError:
    VJOY_AVAILABLE = False
    print("[vJoyInput] Warning: pyvjoy not installed. Install with: pip install pyvjoy")


class VJoyInput:
    """
    Interface to vJoy virtual joystick for input replay.

    Maps keyboard/mouse to joystick axes and buttons:
    - W/S keys -> Y axis (pitch)
    - A/D keys -> X axis (yaw)
    - Q/E keys -> RZ axis (roll)
    - Mouse X -> RX axis (look horizontal)
    - Mouse Y -> RY axis (look vertical)
    - Space, Shift, etc. -> Buttons
    """

    def __init__(self, device_id: int = 1):
        """
        Initialize vJoy device.

        Args:
            device_id: vJoy device ID (1-16, usually 1)
        """
        if not VJOY_AVAILABLE:
            raise ImportError("pyvjoy not installed. Run: pip install pyvjoy")

        self.device_id = device_id
        try:
            self.joystick = pyvjoy.VJoyDevice(device_id)
            print(f"[vJoyInput] Connected to vJoy device {device_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to vJoy device {device_id}: {e}\n"
                             "Make sure vJoy is installed and device {device_id} is enabled.")

        # Axis ranges (vJoy uses 0-32767, center is 16384)
        self.axis_min = 0x0
        self.axis_max = 0x8000  # 32768
        self.axis_center = 0x4000  # 16384

        # Current axis values
        self.axes = {
            'x': self.axis_center,   # Yaw (A/D keys)
            'y': self.axis_center,   # Pitch (W/S keys)
            'z': self.axis_center,   # Throttle
            'rx': self.axis_center,  # Mouse X (look horizontal)
            'ry': self.axis_center,  # Mouse Y (look vertical)
            'rz': self.axis_center,  # Roll (Q/E keys)
        }

        # Button state (1-based indexing for vJoy)
        self.buttons = {}

        # Key to axis mapping for Star Citizen
        self.key_to_axis = {
            # Movement
            'w': ('y', self.axis_max),     # Forward (pitch up)
            's': ('y', self.axis_min),     # Backward (pitch down)
            'a': ('x', self.axis_min),     # Strafe left (yaw left)
            'd': ('x', self.axis_max),     # Strafe right (yaw right)
            'q': ('rz', self.axis_min),    # Roll left
            'e': ('rz', self.axis_max),    # Roll right

            # Throttle
            'shift': ('z', self.axis_max),  # Boost
            'ctrl': ('z', self.axis_min),   # Slow
        }

        # Key to button mapping
        self.key_to_button = {
            'space': 1,      # Primary weapon
            'r': 2,          # Reload/Rearm
            't': 3,          # Target
            'f': 4,          # Flares
            'g': 5,          # Landing gear
            'n': 6,          # Flight mode
            'v': 7,          # Camera
            'tab': 8,        # Target cycle
            'x': 9,          # Match target speed
            'c': 10,         # Cruise control
            'enter': 11,     # Confirm
            'esc': 12,       # Menu
        }

        # Mouse sensitivity for axis conversion
        self.mouse_sensitivity = 100.0  # Pixels to axis range
        self.last_mouse_pos = None

        # Reset all axes to center
        self._reset_axes()

    def _reset_axes(self):
        """Reset all axes to center position."""
        self.joystick.data.wAxisX = self.axis_center
        self.joystick.data.wAxisY = self.axis_center
        self.joystick.data.wAxisZ = self.axis_center
        self.joystick.data.wAxisXRot = self.axis_center
        self.joystick.data.wAxisYRot = self.axis_center
        self.joystick.data.wAxisZRot = self.axis_center
        self.joystick.update()

    def key_down(self, key_str: str):
        """
        Press a key down.

        Args:
            key_str: Key string (e.g., 'w', 'space', 'shift')
        """
        # Strip quotes if present
        if key_str.startswith("'") and key_str.endswith("'") and len(key_str) >= 3:
            key_str = key_str[1:-1]

        # Handle Key.xxx format
        if key_str.startswith('Key.'):
            key_str = key_str.split('.')[1].lower()

        key_lower = key_str.lower()

        # Check if it's a button
        if key_lower in self.key_to_button:
            button_id = self.key_to_button[key_lower]
            self.joystick.set_button(button_id, 1)
            self.buttons[key_lower] = button_id
            print(f"[vJoyInput] Button {button_id} pressed (key: {key_str})")
            return

        # Check if it's an axis
        if key_lower in self.key_to_axis:
            axis_name, axis_value = self.key_to_axis[key_lower]
            self.axes[axis_name] = axis_value
            self._update_axis(axis_name)
            print(f"[vJoyInput] Axis {axis_name} = {axis_value} (key: {key_str})")

    def key_up(self, key_str: str):
        """
        Release a key.

        Args:
            key_str: Key string (e.g., 'w', 'space', 'shift')
        """
        # Strip quotes
        if key_str.startswith("'") and key_str.endswith("'") and len(key_str) >= 3:
            key_str = key_str[1:-1]

        # Handle Key.xxx format
        if key_str.startswith('Key.'):
            key_str = key_str.split('.')[1].lower()

        key_lower = key_str.lower()

        # Release button
        if key_lower in self.buttons:
            button_id = self.buttons[key_lower]
            self.joystick.set_button(button_id, 0)
            del self.buttons[key_lower]
            print(f"[vJoyInput] Button {button_id} released (key: {key_str})")
            return

        # Reset axis to center
        if key_lower in self.key_to_axis:
            axis_name, _ = self.key_to_axis[key_lower]
            self.axes[axis_name] = self.axis_center
            self._update_axis(axis_name)
            print(f"[vJoyInput] Axis {axis_name} centered (key: {key_str})")

    def mouse_move_relative(self, dx: int, dy: int):
        """
        Move mouse relative (for camera control).

        Args:
            dx: Delta X (pixels)
            dy: Delta Y (pixels)
        """
        # Convert pixel movement to axis movement
        # Scale to axis range
        rx_delta = int(dx * (self.axis_max - self.axis_min) / self.mouse_sensitivity)
        ry_delta = int(dy * (self.axis_max - self.axis_min) / self.mouse_sensitivity)

        # Update axes (with clamping)
        self.axes['rx'] = max(self.axis_min, min(self.axis_max,
                              self.axes['rx'] + rx_delta))
        self.axes['ry'] = max(self.axis_min, min(self.axis_max,
                              self.axes['ry'] + ry_delta))

        self._update_axis('rx')
        self._update_axis('ry')

    def mouse_down(self, button: str = 'left'):
        """
        Press mouse button.

        Args:
            button: Button name ('left', 'right', 'middle')
        """
        button_map = {
            'left': 1,    # Primary weapon
            'right': 2,   # Secondary weapon
            'middle': 3,  # Target lock
        }

        if button in button_map:
            button_id = button_map[button]
            self.joystick.set_button(button_id, 1)
            self.buttons[f'mouse_{button}'] = button_id

    def mouse_up(self, button: str = 'left'):
        """
        Release mouse button.

        Args:
            button: Button name ('left', 'right', 'middle')
        """
        key = f'mouse_{button}'
        if key in self.buttons:
            button_id = self.buttons[key]
            self.joystick.set_button(button_id, 0)
            del self.buttons[key]

    def _update_axis(self, axis_name: str):
        """Update a single axis on the vJoy device."""
        value = self.axes[axis_name]

        if axis_name == 'x':
            self.joystick.data.wAxisX = value
        elif axis_name == 'y':
            self.joystick.data.wAxisY = value
        elif axis_name == 'z':
            self.joystick.data.wAxisZ = value
        elif axis_name == 'rx':
            self.joystick.data.wAxisXRot = value
        elif axis_name == 'ry':
            self.joystick.data.wAxisYRot = value
        elif axis_name == 'rz':
            self.joystick.data.wAxisZRot = value

        self.joystick.update()

    def release_all(self):
        """Release all buttons and center all axes."""
        # Release all buttons
        for button_id in list(self.buttons.values()):
            self.joystick.set_button(button_id, 0)
        self.buttons.clear()

        # Center all axes
        for axis_name in self.axes:
            self.axes[axis_name] = self.axis_center
            self._update_axis(axis_name)
