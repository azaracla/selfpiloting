# Anti-Cheat Limitations for Session Replay

## Problem Statement

Star Citizen uses **Easy Anti-Cheat (EAC)**, which actively blocks synthetic input methods:

- ❌ **SendInput API** - Blocked
- ❌ **Windows Messages (WM_KEYDOWN/WM_KEYUP)** - Blocked
- ❌ **pyautogui** - Blocked
- ❌ **Most software-based input simulation** - Blocked

This prevents session replay from working directly with Star Citizen.

## Why This Happens

Easy Anti-Cheat is designed to prevent:
- Botting and automation
- Aimbots and wallhacks
- Macro abuse
- Any form of automated gameplay

It detects synthetic inputs by monitoring:
- Input API calls (SendInput, SendMessage, etc.)
- Driver signatures
- Input timing patterns
- System hooks

## Confirmed Test Results

| Method | Works in Notepad | Works in Star Citizen |
|--------|-----------------|---------------------|
| SendInput API | ✅ Yes | ❌ No (blocked by EAC) |
| Windows Messages | ✅ Yes | ❌ No (blocked by EAC) |
| pyautogui | ✅ Yes | ❌ No (blocked by EAC) |

## Possible Solutions

### Option 1: Hardware-Level Input (Safest)

Use a physical USB device (Arduino/Teensy) to send real keyboard/mouse inputs.

**Pros:**
- ✅ 100% undetectable (real hardware)
- ✅ No risk of ban
- ✅ Works with any game

**Cons:**
- ❌ Requires hardware (~$15-30 USD)
- ❌ More complex setup
- ❌ Requires flashing device firmware

**Hardware options:**
- Arduino Leonardo (~$20)
- Arduino Pro Micro (~$15)
- Teensy 3.2/4.0 (~$25-30)

**Implementation:**
1. Flash device with HID keyboard/mouse firmware
2. Send commands via serial from Python
3. Device acts as real USB keyboard/mouse
4. Game sees it as legitimate hardware

**Example project:** [Arduino HID Project](https://github.com/NicoHood/HID)

### Option 2: Interception Driver (Risky)

Use a kernel-mode driver to emulate hardware-level inputs.

**Pros:**
- ✅ Software-only solution
- ✅ Emulates hardware at kernel level

**Cons:**
- ❌ **HIGH RISK OF BAN** if detected by EAC
- ❌ Complex installation (test mode, unsigned drivers)
- ❌ May require disabling secure boot
- ❌ Windows updates may break it

**NOT RECOMMENDED** for online games with anti-cheat.

**Repository:** [Interception](https://github.com/oblitum/Interception)

### Option 3: Star Citizen Offline Mode

Star Citizen's **Arena Commander** can be played offline without EAC.

**To disable EAC for offline play:**
1. Go to Star Citizen installation folder
2. Find `EasyAntiCheat` folder
3. Rename it temporarily (e.g., `EasyAntiCheat.bak`)
4. Launch game in offline mode
5. Session replay should work!

**Important:** Only works for:
- Arena Commander solo
- Single-player modes
- Cannot play online/multiplayer

### Option 4: Alternative Uses

Use the recording system for other purposes:

**Data Analysis:**
- Extract gameplay statistics
- Analyze movement patterns
- Study player behavior
- Generate heatmaps

**Machine Learning:**
- Train AI models on gameplay data
- Behavior prediction
- Pattern recognition

**Visualization:**
- Convert to video playback
- Create trajectory plots
- Generate gameplay reports

**Other Games:**
Many games don't have anti-cheat and will work fine:
- Single-player games
- Indie games
- Older games
- Emulators

## Recommendations

### For Star Citizen Players:

1. **Best solution:** Hardware-based input (Arduino)
   - Safe, reliable, undetectable
   - Initial cost but works forever

2. **Alternative:** Use offline mode only
   - Free, works immediately
   - Limited to single-player

3. **Last resort:** Use for analysis only
   - Extract data, generate statistics
   - No gameplay automation

### For Other Games:

The session replay works perfectly with games that don't have anti-cheat:
- ✅ Most single-player games
- ✅ Older MMOs without modern anti-cheat
- ✅ Indie games
- ✅ Simulation games

## Legal and Ethical Considerations

**Important:**
- Using automated inputs in **online multiplayer** may violate Terms of Service
- Could result in account bans
- Only use for:
  - Personal testing/research
  - Offline/single-player modes
  - Games where automation is permitted

**This tool is for:**
- ✅ Testing and development
- ✅ Research and analysis
- ✅ Personal offline use
- ✅ Accessibility assistance

**NOT for:**
- ❌ Competitive advantage in multiplayer
- ❌ Circumventing anti-cheat
- ❌ Violating Terms of Service
- ❌ Unfair gameplay

## Technical Details

### Why Software Methods Fail

Easy Anti-Cheat monitors:
- `SendInput()` API calls
- `SendMessage()` / `PostMessage()` calls
- Device driver signatures
- Input event timing
- Kernel-mode hooks

### How Hardware Bypasses Detection

Physical USB devices:
- Generate real USB HID events
- Indistinguishable from user input
- No software API calls involved
- EAC has no way to detect

## Conclusion

Session replay with Star Citizen requires either:
1. **Hardware solution** (recommended)
2. **Offline mode** (free, limited)
3. **Accept limitation** (analysis only)

For other games without anti-cheat, the current implementation works perfectly.

## References

- [Easy Anti-Cheat Official](https://easy.ac/)
- [Arduino HID Library](https://www.arduino.cc/reference/en/language/functions/usb/keyboard/)
- [Windows Input API Docs](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput)
