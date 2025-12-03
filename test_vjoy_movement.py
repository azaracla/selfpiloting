import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.vjoy_input import VJoyInput, VJOY_AVAILABLE
except ImportError:
    print("Error: Could not import vJoy modules.")
    sys.exit(1)

def main():
    print("=" * 60)
    print("Star Citizen vJoy Movement Test")
    print("=" * 60)
    print()

    print("We have determined that the direct input methods (SendInput) are likely being")
    print("blocked by the game. The vJoy method is the most reliable alternative.")
    print()
    
    if not VJOY_AVAILABLE:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: `pyvjoy` library not found. vJoy cannot work.   !!!")
        print("!!! Please install it with: pip install pyvjoy                !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print()
        sys.exit(1)

    print("*** Simplified vJoy Instructions ***")
    print("1. Install vJoy: https://sourceforge.net/projects/vjoystick/")
    print("2. In Star Citizen, go to Options -> Control Profiles.")
    print("3. Select 'vJoy Device' as your input profile.")
    print()
    print("This test will simulate pushing the joystick forward (like pressing 'W') for 3 seconds.")
    print("You should see your character or ship move forward.")
    print()
    print("The test will start in 15 seconds. Please switch to Star Citizen.")
    print()

    for i in range(15, 0, -1):
        print(f"  Starting in {i}...")
        time.sleep(1)
    
    print("\n[Test] Attempting to send FORWARD movement via vJoy...")

    try:
        # Initialize vJoy
        vjoy_handler = VJoyInput()

        # Simulate 'W' key down (moves Y-axis to max)
        vjoy_handler.key_down('w')
        print("[Test] vJoy FORWARD signal sent.")

        # Hold for 3 seconds
        print("[Test] Holding for 3 seconds...")
        time.sleep(3)

        # Simulate 'W' key up (centers Y-axis)
        vjoy_handler.key_up('w')
        print("[Test] vJoy FORWARD signal stopped.")
        
        print("\n[Test] Finished.")
        print("Please check if your character/ship moved forward for 3 seconds.")

    except (RuntimeError, Exception) as e:
        print(f"\nAn vJoy error occurred: {e}")
        print("Please ensure vJoy is installed correctly and the vJoy Device is enabled in its configuration.")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
