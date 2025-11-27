#!/usr/bin/env python3
"""
Star Citizen AI Training Data Recorder

Simple script to record gameplay sessions for training an AI agent.
Records both video and keyboard/mouse inputs.

Usage:
    python record.py                    # Start recording with auto-generated name
    python record.py --name my_session  # Start with custom name
    python record.py --fps 60           # Record at 60 FPS
    python record.py --help             # Show help

Press Ctrl+C to stop recording.
"""

import argparse
import signal
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_recorder import DataRecorder


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n[Main] Interrupt received, stopping recording...")
    if recorder and recorder.recording:
        recorder.stop()
    sys.exit(0)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Record Star Citizen gameplay for AI training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python record.py
      Start recording with auto-generated session name

  python record.py --name "ace_pilot_training"
      Record session with custom name

  python record.py --fps 60 --resolution 1920 1080
      Record at 60 FPS in full HD

  python record.py --output my_recordings
      Save to custom output directory
        """
    )

    parser.add_argument(
        '--name', '-n',
        type=str,
        default=None,
        help='Session name (auto-generated if not specified)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='recordings',
        help='Output directory for recordings (default: recordings)'
    )

    parser.add_argument(
        '--fps', '-f',
        type=int,
        default=30,
        help='Frames per second (default: 30)'
    )

    parser.add_argument(
        '--resolution', '-r',
        type=int,
        nargs=2,
        metavar=('WIDTH', 'HEIGHT'),
        default=None,
        help='Video resolution (default: native screen resolution). Example: --resolution 1280 720'
    )

    parser.add_argument(
        '--codec',
        type=str,
        default='libx264',
        help='Video codec (default: libx264)'
    )

    parser.add_argument(
        '--monitor',
        type=int,
        default=1,
        help='Monitor number to capture (default: 1 = primary)'
    )

    return parser.parse_args()


def main():
    """Main function."""
    global recorder

    args = parse_args()

    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Convert resolution to tuple if provided
    resolution = tuple(args.resolution) if args.resolution else None

    # Create recorder
    print("=" * 60)
    print("Star Citizen AI Training Data Recorder")
    print("=" * 60)
    print()

    recorder = DataRecorder(
        output_dir=args.output,
        fps=args.fps,
        resolution=resolution,
        video_codec=args.codec
    )

    # Start recording
    print(f"Configuration:")
    print(f"  FPS: {args.fps}")
    print(f"  Resolution: {resolution if resolution else 'Native'}")
    print(f"  Output: {args.output}")
    print(f"  Monitor: {args.monitor}")
    print()
    print("Starting in 3 seconds... Switch to Star Citizen!")
    print()

    # Countdown
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    print()
    recorder.start(session_name=args.name)

    # Main loop - print status updates
    try:
        last_status_time = time.time()
        while True:
            time.sleep(1)

            # Print status every 10 seconds
            current_time = time.time()
            if current_time - last_status_time >= 10:
                status = recorder.get_status()
                if status['recording']:
                    print(f"\n[Status] Duration: {status['duration']:.1f}s | "
                          f"Frames: {status['screen_stats']['frame_count']} | "
                          f"Inputs: {status['input_stats']['total_events']}")
                last_status_time = current_time

    except KeyboardInterrupt:
        pass

    # Stop recording
    recorder.stop()

    print()
    print("=" * 60)
    print("Recording complete!")
    print("=" * 60)
    print()
    print("Your training data is ready for use with your AI model.")
    print("Files saved:")
    status = recorder.get_status()
    if 'output_dir' in status:
        print(f"  - Video: {status['output_dir']}/gameplay.mp4")
        print(f"  - Inputs: {status['output_dir']}/inputs.json")
        print(f"  - Frame-aligned inputs: {status['output_dir']}/inputs_frame_aligned.json")
        print(f"  - Metadata: {status['output_dir']}/metadata.json")


if __name__ == '__main__':
    recorder = None
    main()
