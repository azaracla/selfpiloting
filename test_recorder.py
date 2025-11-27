#!/usr/bin/env python3
"""
Test script to verify the recorder works correctly.
Records for 5 seconds as a quick test.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_recorder import DataRecorder


def main():
    print("=" * 60)
    print("Star Citizen Recorder - Quick Test")
    print("=" * 60)
    print()
    print("This will record for 5 seconds to verify everything works.")
    print("Move your mouse and press some keys during the test.")
    print()

    # Create test recorder
    recorder = DataRecorder(
        output_dir="test_recordings",
        fps=30,
        resolution=(640, 480),  # Low res for quick test
        video_codec='libx264'
    )

    print("Starting test recording in 2 seconds...")
    time.sleep(2)

    # Start recording
    recorder.start(session_name="test_session")

    # Record for 5 seconds
    for i in range(5, 0, -1):
        print(f"Recording... {i} seconds remaining")
        time.sleep(1)

    # Stop recording
    recorder.stop()

    # Print results
    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()

    # Check if files were created
    test_dir = Path("test_recordings/test_session")
    if test_dir.exists():
        print("✓ Session directory created")

        files = {
            "gameplay.mp4": "Video file",
            "inputs.json": "Raw input events",
            "inputs_frame_aligned.json": "Frame-aligned inputs",
            "metadata.json": "Session metadata"
        }

        for filename, description in files.items():
            filepath = test_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size / 1024  # KB
                print(f"✓ {description}: {filename} ({size:.1f} KB)")
            else:
                print(f"✗ Missing: {filename}")
    else:
        print("✗ Session directory not created!")

    print()
    print("You can now use the full recorder with: python record.py")


if __name__ == '__main__':
    main()
