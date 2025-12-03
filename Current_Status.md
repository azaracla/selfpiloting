# Final Status: Reliable Input Simulation for Star Citizen via vJoy

This document summarizes the final, working solution for replaying recorded game sessions in Star Citizen.

## 1. Problem Summary

The goal was to reliably simulate keyboard and mouse inputs for replaying recorded sessions. The primary challenges were:
- Bypassing Star Citizen's anti-cheat, which blocks common software input methods like `SendInput`.
- Accommodating the user's specific AZERTY keyboard layout.
- Handling the game's complex control schemes, especially for a HOTAS/HOSAS (dual joystick) setup, without having physical sticks to configure bindings easily.

## 2. The Solution: vJoy with User-Editable Configuration

After multiple attempts, a robust solution using a **single virtual joystick (vJoy)** was implemented and confirmed to be working. This method is successful because games like Star Citizen are built to trust joystick hardware, and vJoy creates a virtual version of that hardware that the game accepts.

The final implementation has these key features:

- **Single vJoy Device:** Simplifies setup by only requiring one virtual joystick, avoiding the configuration complexity of a dual-stick setup in-game.
- **User-Configurable Axis Mappings:** To solve the "pitch instead of forward" problem, the `src/vjoy_input.py` file now contains a clear, commented configuration section. This empowers you to easily change which joystick axis is used for which keyboard key, allowing you to find the correct axis for "forward" movement (`Throttle Forward/Back`) by simple trial-and-error (e.g., changing `'y'` to `'z'`).
- **AZERTY Layout:** The key-to-axis mappings are configured for an AZERTY keyboard layout (`Z` for forward, `Q` for left strafe, etc.).
- **Mouse "Flick" Translation:** Recorded mouse movements are translated into quick "flicks" of the joystick's aiming axes (`Rx`/`Ry`), ensuring that aiming from a recording is functional.

## 3. How to Use

The replay functionality is now fully operational.

### Dependencies:
1.  **vJoy Driver:** Must be installed and a virtual device (Device 1) must be enabled.
2.  **`pyvjoy` library:** Install via `pip install pyvjoy`.

### Running a Replay:
Use the `replay.py` script with `vjoy` as the input method.

```sh
python replay.py recordings/YOUR_SESSION_NAME --input-method vjoy
```

### Final In-Game Configuration:
As you discovered, the final step is to ensure Star Citizen correctly interprets the vJoy inputs. This involves:
1. Loading a joystick-based profile in the game (e.g., a T16000M profile).
2. Going into `Options > Keybindings` and assigning the correct vJoy axes to the desired actions (e.g., mapping `vJoy Z-Axis` to `Throttle Forward/Back`).

## 4. Project Cleanup
All temporary test files created during the debugging process have been deleted, leaving only `test_vjoy_movement.py` as a quick, working diagnostic script. The project is now in a clean, documented, and functional state.