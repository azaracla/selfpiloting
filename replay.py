#!/usr/bin/env python3
"""
Star Citizen Session Replay Tool

Replays recorded keyboard and mouse inputs from a session.
Useful for verifying recordings and testing.

Usage:
    python replay.py recordings/session_20231127_143022
    python replay.py recordings/session_20231127_143022 --speed 2.0
    python replay.py recordings/session_20231127_143022 --delay 5

Press Ctrl+C to stop replay.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.session_replay import SessionReplay


def list_sessions(recordings_dir: str = "recordings"):
    """List all available sessions."""
    recordings_path = Path(recordings_dir)

    if not recordings_path.exists():
        print(f"Recordings directory not found: {recordings_dir}")
        return []

    sessions = []
    for session_dir in sorted(recordings_path.iterdir()):
        if session_dir.is_dir():
            inputs_file = session_dir / "inputs.json"
            if inputs_file.exists():
                sessions.append(session_dir)

    return sessions


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Replay recorded Star Citizen session inputs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python replay.py recordings/session_20231127_143022
      Replay session at normal speed

  python replay.py recordings/session_20231127_143022 --speed 2.0
      Replay at 2x speed

  python replay.py recordings/session_20231127_143022 --delay 10
      Wait 10 seconds before starting

  python replay.py --list
      List all available sessions
        """
    )

    parser.add_argument(
        'session_path',
        type=str,
        nargs='?',
        help='Path to session directory to replay'
    )

    parser.add_argument(
        '--speed', '-s',
        type=float,
        default=1.0,
        help='Playback speed multiplier (default: 1.0 = normal speed)'
    )

    parser.add_argument(
        '--delay', '-d',
        type=int,
        default=3,
        help='Delay in seconds before starting replay (default: 3)'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available recorded sessions'
    )

    parser.add_argument(
        '--input-method', '-i',
        type=str,
        default='human',
        choices=['native', 'human', 'vjoy', 'pyautogui'],
        help='Input simulation method: "native", "human", "vjoy", or "pyautogui" (default: human)'
    )

    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()

    # List sessions if requested
    if args.list:
        print("=" * 60)
        print("Available Recorded Sessions")
        print("=" * 60)
        print()

        sessions = list_sessions()

        if not sessions:
            print("No recorded sessions found in 'recordings/' directory.")
            print("Record a session first with: python record.py")
            return

        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session.name}")

            # Load and show info
            try:
                # Default to native for listing to avoid loading human input class here
                replayer = SessionReplay(str(session), input_method='native')
                info = replayer.get_info()

                print(f"   Duration: {info['duration']:.1f}s")
                print(f"   Events: {info['total_events']}")
                print()
            except Exception as e:
                print(f"   Error loading: {e}")
                print()

        print(f"To replay a session, use:")
        print(f"  python replay.py recordings/SESSION_NAME")
        return

    # Check if session path provided
    if not args.session_path:
        print("Error: Please provide a session path to replay")
        print("Use --list to see available sessions")
        print()
        print("Usage: python replay.py <session_path>")
        sys.exit(1)

    # Validate session path
    session_path = Path(args.session_path)
    if not session_path.exists():
        print(f"Error: Session path does not exist: {args.session_path}")
        print()
        print("Use --list to see available sessions")
        sys.exit(1)

    # Load session
    print("=" * 60)
    print("Star Citizen Session Replay")
    print("=" * 60)
    print()

    try:
        replayer = SessionReplay(args.session_path, input_method=args.input_method)

        # Show session info
        info = replayer.get_info()
        print(f"Session: {session_path.name}")
        print(f"Duration: {info['duration']:.1f}s")
        print(f"Total events: {info['total_events']}")
        print(f"Input method: {args.input_method}")
        print()

        # Show event breakdown
        if 'event_counts' in info:
            print("Event breakdown:")
            for event_type, count in info['event_counts'].items():
                print(f"  {event_type}: {count}")
            print()

        # Replay
        replayer.play(speed=args.speed, start_delay=args.delay)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print()
        print("Make sure the session directory contains an 'inputs.json' file.")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 60)
    print("Replay Complete!")
    print("=" * 60)



if __name__ == '__main__':
    main()
