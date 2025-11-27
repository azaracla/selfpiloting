"""
Main data recorder that synchronizes screen capture and input recording.
Saves data in formats suitable for machine learning training.
"""

import os
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import imageio

from .screen_recorder import ScreenRecorder
from .input_recorder import InputRecorder


class DataRecorder:
    """Main recorder that combines screen and input recording."""

    def __init__(self, output_dir: str = "recordings",
                 fps: int = 30,
                 resolution: Optional[Tuple[int, int]] = (1280, 720),
                 video_codec: str = 'libx264'):
        """
        Initialize the data recorder.

        Args:
            output_dir: Directory to save recordings
            fps: Frames per second for video capture
            resolution: Video resolution (width, height). None = native
            video_codec: Video codec for encoding
        """
        self.output_dir = Path(output_dir)
        self.fps = fps
        self.resolution = resolution
        self.video_codec = video_codec

        self.screen_recorder = ScreenRecorder(
            monitor=1,
            target_fps=fps,
            resolution=resolution
        )
        self.input_recorder = InputRecorder()

        self.recording = False
        self._save_thread = None
        self._session_dir = None
        self._video_writer = None
        self._start_time = None

    def start(self, session_name: Optional[str] = None):
        """
        Start recording.

        Args:
            session_name: Optional name for this session. Auto-generated if None
        """
        if self.recording:
            print("[DataRecorder] Already recording!")
            return

        # Create session directory
        if session_name is None:
            session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")

        self._session_dir = self.output_dir / session_name
        self._session_dir.mkdir(parents=True, exist_ok=True)

        print(f"[DataRecorder] Starting recording session: {session_name}")
        print(f"[DataRecorder] Output directory: {self._session_dir}")

        # Start recorders
        self._start_time = time.time()
        self.screen_recorder.start()
        self.input_recorder.start()

        self.recording = True

        # Start save thread
        self._save_thread = threading.Thread(target=self._save_loop, daemon=True)
        self._save_thread.start()

        print("[DataRecorder] Recording started. Press Ctrl+C or call stop() to finish.")

    def stop(self):
        """Stop recording and save all data."""
        if not self.recording:
            return

        print("[DataRecorder] Stopping recording...")
        self.recording = False

        # Stop recorders
        self.screen_recorder.stop()
        self.input_recorder.stop()

        # Wait for save thread to finish
        if self._save_thread:
            self._save_thread.join(timeout=5.0)

        # Close video writer
        if self._video_writer:
            self._video_writer.close()
            self._video_writer = None

        # Save input events
        self._save_input_data()

        # Save metadata
        self._save_metadata()

        print(f"[DataRecorder] Recording saved to: {self._session_dir}")

    def _save_loop(self):
        """Main loop for saving frames to video."""
        video_path = self._session_dir / "gameplay.mp4"

        # Initialize video writer with first frame
        first_frame = None
        while self.recording and first_frame is None:
            frame_data = self.screen_recorder.get_frame(timeout=0.1)
            if frame_data:
                _, first_frame = frame_data

        if first_frame is None:
            print("[DataRecorder] Failed to capture initial frame!")
            return

        # Create video writer
        self._video_writer = imageio.get_writer(
            str(video_path),
            fps=self.fps,
            codec=self.video_codec,
            quality=8,
            pixelformat='yuv420p',
            macro_block_size=1
        )

        # Write first frame
        self._video_writer.append_data(first_frame)
        frame_count = 1

        # Continue writing frames
        while self.recording:
            frame_data = self.screen_recorder.get_frame(timeout=0.1)
            if frame_data:
                timestamp, frame = frame_data
                self._video_writer.append_data(frame)
                frame_count += 1

                # Print progress every 5 seconds
                if frame_count % (self.fps * 5) == 0:
                    duration = frame_count / self.fps
                    print(f"[DataRecorder] Recorded {duration:.1f}s "
                          f"({frame_count} frames)")

    def _save_input_data(self):
        """Save input events to JSON file."""
        events = self.input_recorder.get_events()

        input_path = self._session_dir / "inputs.json"

        # Convert events to serializable format
        events_data = {
            'events': events,
            'total_events': len(events),
            'duration': events[-1]['timestamp'] if events else 0
        }

        with open(input_path, 'w') as f:
            json.dump(events_data, f, indent=2)

        print(f"[DataRecorder] Saved {len(events)} input events")

        # Also save as compact numpy format for faster loading
        self._save_input_numpy(events)

    def _save_input_numpy(self, events):
        """Save input events in numpy format for ML training."""
        if not events:
            return

        # Create frame-aligned input states
        duration = events[-1]['timestamp'] if events else 0
        num_frames = int(duration * self.fps) + 1

        # Initialize arrays for frame-aligned data
        frames_data = []

        for frame_idx in range(num_frames):
            timestamp = frame_idx / self.fps
            state = self.input_recorder.get_state_at_time(timestamp)

            frames_data.append({
                'timestamp': timestamp,
                'pressed_keys': list(state['pressed_keys']),
                'mouse_x': state['mouse_position'][0],
                'mouse_y': state['mouse_position'][1],
                'mouse_buttons': list(state['mouse_buttons'])
            })

        # Save as JSON for readability
        aligned_path = self._session_dir / "inputs_frame_aligned.json"
        with open(aligned_path, 'w') as f:
            json.dump(frames_data, f, indent=2)

        print(f"[DataRecorder] Saved frame-aligned inputs ({num_frames} frames)")

    def _save_metadata(self):
        """Save session metadata."""
        screen_stats = self.screen_recorder.get_stats()
        input_stats = self.input_recorder.get_stats()

        metadata = {
            'session_start': datetime.fromtimestamp(self._start_time).isoformat(),
            'fps': self.fps,
            'resolution': self.resolution,
            'video_codec': self.video_codec,
            'screen_stats': screen_stats,
            'input_stats': input_stats,
            'duration': time.time() - self._start_time
        }

        metadata_path = self._session_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"[DataRecorder] Session duration: {metadata['duration']:.1f}s")

    def get_status(self) -> dict:
        """Get current recording status."""
        if not self.recording:
            return {'recording': False}

        return {
            'recording': True,
            'duration': time.time() - self._start_time,
            'screen_stats': self.screen_recorder.get_stats(),
            'input_stats': self.input_recorder.get_stats(),
            'output_dir': str(self._session_dir)
        }
