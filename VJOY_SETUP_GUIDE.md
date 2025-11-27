## vJoy Setup Guide for Star Citizen Session Replay

vJoy creates a virtual joystick that Star Citizen accepts, potentially bypassing Easy Anti-Cheat since joysticks are legitimate input devices for space sims.

## Why vJoy Works

- ✅ **Signed Windows driver** (legitimate software)
- ✅ **Star Citizen supports joysticks** (space sim game)
- ✅ **EAC doesn't block joystick input** (would break HOTAS users)
- ✅ **Free and open-source**
- ✅ **No additional hardware needed**

## Installation Steps

### Step 1: Install vJoy Driver

1. **Download v Joy**
   - Go to: https://sourceforge.net/projects/vjoystick/
   - Download the latest version (currently 2.1.9)

2. **Run the installer**
   - Right-click → "Run as Administrator"
   - Follow the installation wizard
   - Accept the driver installation prompt

3. **Reboot your computer** (recommended)

### Step 2: Configure vJoy Device

1. **Open "Configure vJoy"** from Start Menu

2. **Select Device 1** in the left panel

3. **Enable the following:**
   - ☑ Enable vJoy Device
   - **Axes:** 6 axes minimum
     - ☑ X Axis (Yaw - A/D keys)
     - ☑ Y Axis (Pitch - W/S keys)
     - ☑ Z Axis (Throttle - Shift/Ctrl)
     - ☑ X Rotation (Mouse X - look left/right)
     - ☑ Y Rotation (Mouse Y - look up/down)
     - ☑ Z Rotation (Roll - Q/E keys)
   - **Buttons:** 12 buttons minimum
   - **POV Hats:** 0 (not needed)

4. **Click "Apply"**

5. **Verify** the device shows as "Configured" and "Present"

### Step 3: Install Python Package

```bash
pip install pyvjoy
```

### Step 4: Test vJoy Installation

```bash
# Basic test (without Star Citizen)
python test_vjoy.py
```

This will test if vJoy is working and can send inputs.

### Step 5: Configure Star Citizen

1. **Launch Star Citizen**

2. **Go to Options → Keybindings**

3. **Select "Joystick/HOTAS"**

4. **Find "vJoy Device"** in the list
   - It should appear as "vJoy Device" or "vJoy Virtual Joystick"

5. **Test the bindings:**
   - Run `test_vjoy.py` while in-game
   - Check if movements work

6. **Optional: Rebind controls**
   - You can customize which vJoy axes/buttons control what
   - Recommended to keep defaults for testing first

## Axis Mapping

The default mapping is:

| Input | vJoy Axis | Game Function |
|-------|-----------|---------------|
| W/S keys | Y Axis | Pitch up/down |
| A/D keys | X Axis | Yaw left/right |
| Q/E keys | Z Rotation | Roll left/right |
| Mouse X | X Rotation | Look left/right |
| Mouse Y | Y Rotation | Look up/down |
| Shift/Ctrl | Z Axis | Throttle boost/slow |

| Input | vJoy Button | Game Function |
|-------|-------------|---------------|
| Space | Button 1 | Primary weapon |
| Left Click | Button 1 | Primary weapon |
| Right Click | Button 2 | Secondary weapon |
| R | Button 2 | Reload |
| T | Button 3 | Target |
| F | Button 4 | Flares |
| G | Button 5 | Landing gear |

## Usage with Session Replay

Once vJoy is configured, modify `session_replay.py` to use vJoy:

```python
# Instead of:
from src.windows_input import WindowsInput
input_handler = WindowsInput()

# Use:
from src.vjoy_input import VJoyInput
input_handler = VJoyInput(device_id=1)
```

Or use the command-line flag (if implemented):
```bash
python replay.py recordings/session_xxx --vjoy
```

## Troubleshooting

### "Failed to connect to vJoy device"

**Problem:** pyvjoy can't find the vJoy device

**Solutions:**
1. Make sure vJoy driver is installed
2. Open "Configure vJoy" and enable Device 1
3. Reboot your computer
4. Check Device Manager → "vJoy Device" should be present

### "Star Citizen doesn't respond to vJoy"

**Problem:** Game isn't detecting the virtual joystick

**Solutions:**
1. Go to SC Options → Keybindings → Joystick
2. Check if "vJoy Device" appears in the list
3. Try unplugging other controllers (potential conflicts)
4. Restart Star Citizen after configuring vJoy

### "Movements are inverted or wrong"

**Problem:** Axis mapping doesn't match game controls

**Solutions:**
1. In Star Citizen settings, check axis inversions
2. Adjust sensitivity sliders
3. Customize the mapping in `vjoy_input.py`

### "pip install pyvjoy fails"

**Problem:** pyvjoy installation error

**Solutions:**
1. Make sure you have Python 3.7+
2. Try: `pip install pyvjoy==1.0.1`
3. On some systems: `pip install git+https://github.com/tidzo/pyvjoy.git`

### "vJoy axes are jittery/unstable"

**Problem:** Axes don't stay centered

**Solutions:**
1. Set deadzone in Star Citizen joystick settings
2. Increase deadzone to 5-10%
3. Check for conflicts with other controllers

## Advanced Configuration

### Multiple vJoy Devices

If you need more axes or want separation:

```python
# Device 1 for movement
vjoy_movement = VJoyInput(device_id=1)

# Device 2 for weapons
vjoy_weapons = VJoyInput(device_id=2)
```

### Custom Axis Mapping

Edit `src/vjoy_input.py` to customize:

```python
self.key_to_axis = {
    'w': ('y', self.axis_max),  # Change these as needed
    # ... your custom mappings
}
```

### Sensitivity Adjustment

In `src/vjoy_input.py`:

```python
# Mouse sensitivity (lower = less sensitive)
self.mouse_sensitivity = 50.0  # Default: 100.0
```

## Testing Without Star Citizen

Test vJoy in Windows Game Controllers:

1. Press `Win + R`
2. Type: `joy.cpl`
3. Press Enter
4. Select "vJoy Device"
5. Click "Properties"
6. Run `test_vjoy.py` and watch axes/buttons respond

## Verifying EAC Compatibility

To verify vJoy bypasses EAC:

1. Run `test_vjoy.py` with Star Citizen running
2. If character moves → **SUCCESS!**
3. If nothing happens → Check configuration

**Note:** vJoy should work because:
- It's a legitimate signed driver
- Star Citizen needs joystick support for HOTAS users
- EAC has no reason to block joystick input

## Known Limitations

- **Mouse absolute positioning** doesn't map well to joystick
  - Use relative movement (deltas) instead
- **Many simultaneous inputs** may hit joystick axis/button limits
- **First setup** requires some trial and error with bindings

## References

- [vJoy Official Page](https://sourceforge.net/projects/vjoystick/)
- [pyvjoy on GitHub](https://github.com/tidzo/pyvjoy)
- [vJoy Documentation](http://vjoystick.sourceforge.net/site/)
- [Star Citizen Controller Setup Guide](https://robertsspaceindustries.com/spectrum/community/SC/forum/50172/thread/guide-to-setting-up-controllers-for-star-citizen)

## Next Steps

After vJoy is working:

1. ✅ Test basic movement with `test_vjoy.py`
2. ✅ Configure Star Citizen joystick bindings
3. ✅ Try replaying a short session
4. ✅ Fine-tune sensitivity and deadzone
5. ✅ Record and replay full gameplay sessions!

## Alternative: Joystick Gremlin

If you need more advanced mapping:

**Joystick Gremlin** (https://whitemagic.github.io/JoystickGremlin/)
- GUI for complex input mapping
- Can combine multiple devices
- Macro support
- Free and open-source

Install both vJoy and Joystick Gremlin for maximum control!
