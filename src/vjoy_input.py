"""
vJoy input driver for Star Citizen session replay.
Manages two virtual joysticks for a HoSaS setup.
"""

try:
    import pyvjoy
    import time
    VJOY_AVAILABLE = True
except ImportError:
    VJOY_AVAILABLE = False
    print("[vJoyManager] Warning: pyvjoy not installed. Install with: pip install pyvjoy")


class VJoyInput:
    """
    Manages two vJoy devices for a HoSaS (Hand on Stick and Stick) setup.
    - Stick 1 (Right): Handles flight/aim control (Pitch, Yaw, Roll, Mouse).
    - Stick 2 (Left): Handles strafe control (Forward/Back, Left/Right).
    """

    def __init__(self, device_id1: int = 1, device_id2: int = 2):
        if not VJOY_AVAILABLE:
            raise ImportError("pyvjoy not installed. Run: pip install pyvjoy")

        self.stick1 = self._init_stick(device_id1)
        self.stick2 = self._init_stick(device_id2)

        if not self.stick1:
            raise RuntimeError(f"vJoy device {device_id1} is essential and could not be initialized.")

        self.axis_min = 0x0
        self.axis_max = 0x8000
        self.axis_center = 0x4000

        self.axes1 = { 'x': self.axis_center, 'y': self.axis_center, 'z': self.axis_center, 'rx': self.axis_center, 'ry': self.axis_center, 'rz': self.axis_center }
        self.axes2 = { 'x': self.axis_center, 'y': self.axis_center, 'z': self.axis_center, 'rx': self.axis_center, 'ry': self.axis_center, 'rz': self.axis_center }

        self.buttons1 = {}
        self.buttons2 = {}

        # Key to axis mapping: key -> (axis_name, value, stick_id)
        self.key_to_axis = {
            # Stick 2: Strafe Movement (AZERTY)
            'z': ('y', self.axis_max, 2),     # Strafe Forward
            's': ('y', self.axis_min, 2),     # Strafe Backward
            'q': ('x', self.axis_min, 2),     # Strafe Left
            'd': ('x', self.axis_max, 2),     # Strafe Right

            # Stick 1: Flight Control (Roll)
            'a': ('rz', self.axis_min, 1),    # Roll Left
            'e': ('rz', self.axis_max, 1),    # Roll Right

            # Throttle (can be on either stick, let's use Stick 1 for now)
            'shift': ('z', self.axis_max, 1), # Boost
            'ctrl': ('z', self.axis_min, 1),  # Slow
        }

        # Key to button mapping: key -> (button_id, stick_id)
        self.key_to_button = {
            'space': (1, 1),
            'r': (2, 1),
            't': (3, 1),
            'f': (4, 1),
            'g': (5, 1),
            'n': (6, 1),
            'v': (7, 1),
            'x': (9, 1),
            'c': (10, 1),
            'enter': (11, 1),
            'esc': (12, 1),
            'alt_l': (14, 1),
            'tab': (15, 1),
            'ctrl_l': (16, 1),
        }
        
        self.mouse_sensitivity = 10.0
        self._reset_axes()

    def _init_stick(self, device_id):
        try:
            stick = pyvjoy.VJoyDevice(device_id)
            print(f"[vJoyManager] Connected to vJoy device {device_id}")
            return stick
        except Exception as e:
            print(f"[vJoyManager] Warning: Failed to connect to vJoy device {device_id}: {e}")
            return None

    def _reset_axes(self):
        for stick in [self.stick1, self.stick2]:
            if stick:
                stick.data.wAxisX = self.axis_center
                stick.data.wAxisY = self.axis_center
                stick.data.wAxisZ = self.axis_center
                stick.data.wAxisXRot = self.axis_center
                stick.data.wAxisYRot = self.axis_center
                stick.data.wAxisZRot = self.axis_center
                stick.update()

    def _get_cleaned_key(self, key_str: str) -> str:
        if key_str.startswith('\'') and key_str.endswith('\'') and len(key_str) >= 3:
            key_str = key_str[1:-1]
        if key_str.startswith('Key.'):
            key_str = key_str.split('.')[1].lower()
        return key_str.lower()

    def key_down(self, key_str: str):
        key = self._get_cleaned_key(key_str)

        if key in self.key_to_button:
            button_id, stick_id = self.key_to_button[key]
            stick = self.stick1 if stick_id == 1 else self.stick2
            buttons = self.buttons1 if stick_id == 1 else self.buttons2
            if stick:
                stick.set_button(button_id, 1)
                buttons[key] = button_id
                print(f"[vJoyManager] Stick {stick_id} Button {button_id} pressed (key: {key})")
            return

        if key in self.key_to_axis:
            axis_name, axis_value, stick_id = self.key_to_axis[key]
            self._update_axis(stick_id, axis_name, axis_value)
            print(f"[vJoyManager] Stick {stick_id} Axis {axis_name} = {axis_value} (key: {key})")

    def key_up(self, key_str: str):
        key = self._get_cleaned_key(key_str)

        if key in self.buttons1 or key in self.buttons2:
            stick_id = 1 if key in self.buttons1 else 2
            stick = self.stick1 if stick_id == 1 else self.stick2
            buttons = self.buttons1 if stick_id == 1 else self.buttons2
            button_id = buttons.pop(key)
            if stick:
                stick.set_button(button_id, 0)
                print(f"[vJoyManager] Stick {stick_id} Button {button_id} released (key: {key})")
            return

        if key in self.key_to_axis:
            axis_name, _, stick_id = self.key_to_axis[key]
            self._update_axis(stick_id, axis_name, self.axis_center)
            print(f"[vJoyManager] Stick {stick_id} Axis {axis_name} centered (key: {key})")

    def mouse_move_relative(self, dx: int, dy: int):
        # Mouse movement always goes to Stick 1 (right stick for aiming)
        rx_delta = int(dx * (self.axis_max / 2) / self.mouse_sensitivity)
        ry_delta = -int(dy * (self.axis_max / 2) / self.mouse_sensitivity)

        if self.stick1:
            self.stick1.data.wAxisXRot = self.axis_center + rx_delta
            self.stick1.data.wAxisYRot = self.axis_center + ry_delta
            self.stick1.update()
            time.sleep(0.01)
            self.stick1.data.wAxisXRot = self.axis_center
            self.stick1.data.wAxisYRot = self.axis_center
            self.stick1.update()

    def mouse_down(self, button: str = 'left'):
        # Mouse buttons go to Stick 1
        button_map = {'left': 1, 'right': 2, 'middle': 3}
        if button in button_map and self.stick1:
            button_id = button_map[button]
            self.stick1.set_button(button_id, 1)
            self.buttons1[f'mouse_{button}'] = button_id

    def mouse_up(self, button: str = 'left'):
        key = f'mouse_{button}'
        if key in self.buttons1 and self.stick1:
            button_id = self.buttons1.pop(key)
            self.stick1.set_button(button_id, 0)

    def _update_axis(self, stick_id, axis_name, value):
        stick = self.stick1 if stick_id == 1 else self.stick2
        axes = self.axes1 if stick_id == 1 else self.axes2
        if not stick: return
        
        axes[axis_name] = value
        
        if axis_name == 'x': stick.data.wAxisX = value
        elif axis_name == 'y': stick.data.wAxisY = value
        elif axis_name == 'z': stick.data.wAxisZ = value
        elif axis_name == 'rx': stick.data.wAxisXRot = value
        elif axis_name == 'ry': stick.data.wAxisYRot = value
        elif axis_name == 'rz': stick.data.wAxisZRot = value
        
        stick.update()

    def release_all(self):
        for stick, buttons in [(self.stick1, self.buttons1), (self.stick2, self.buttons2)]:
            if stick:
                for button_id in list(buttons.values()):
                    stick.set_button(button_id, 0)
        self.buttons1.clear()
        self.buttons2.clear()
        self._reset_axes()