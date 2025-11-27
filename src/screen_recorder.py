"""
Screen capture module for recording Star Citizen gameplay.
Uses MSS for fast screen capture on Windows.
"""

import time
import threading
from queue import Queue
from typing import Optional, Tuple
import numpy as np
from mss import mss
from PIL import Image


class ScreenRecorder:
    """Records screen frames with timestamps."""

    def __init__(self, monitor: int = 1, target_fps: int = 30,
                 resolution: Optional[Tuple[int, int]] = None):
        """
        Initialize screen recorder.

        Args:
            monitor: Monitor number to capture (1 = primary)
            target_fps: Target frames per second
            resolution: Optional (width, height) to resize frames. None = native resolution
        """
        self.monitor = monitor
        self.target_fps = target_fps
        self.resolution = resolution
        self.frame_interval = 1.0 / target_fps

        self.recording = False
        self.frames_queue = Queue(maxsize=300)  # Buffer ~10s at 30fps
        self.frame_count = 0
        self.dropped_frames = 0

        self._capture_thread = None
        self._start_time = None

    def start(self):
        """Start recording frames."""
        if self.recording:
            return

        self.recording = True
        self.frame_count = 0
        self.dropped_frames = 0
        self._start_time = time.time()

        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()

        print(f"[ScreenRecorder] Started recording at {self.target_fps} FPS")

    def stop(self):
        """Stop recording frames."""
        if not self.recording:
            return

        self.recording = False
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)

        print(f"[ScreenRecorder] Stopped. Captured {self.frame_count} frames, "
              f"dropped {self.dropped_frames} frames")

    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        with mss() as sct:
            # Get monitor info
            monitor_info = sct.monitors[self.monitor]

            next_capture_time = time.time()

            while self.recording:
                current_time = time.time()

                # Check if it's time to capture next frame
                if current_time >= next_capture_time:
                    try:
                        # Capture screenshot
                        screenshot = sct.grab(monitor_info)

                        # Convert to numpy array
                        frame = np.array(screenshot)

                        # Convert BGRA to RGB
                        frame = frame[:, :, :3]  # Drop alpha channel
                        frame = frame[:, :, [2, 1, 0]]  # BGR to RGB

                        # Resize if needed
                        if self.resolution:
                            img = Image.fromarray(frame)
                            img = img.resize(self.resolution, Image.Resampling.LANCZOS)
                            frame = np.array(img)

                        # Calculate relative timestamp
                        timestamp = current_time - self._start_time

                        # Add to queue
                        if not self.frames_queue.full():
                            self.frames_queue.put((timestamp, frame))
                            self.frame_count += 1
                        else:
                            self.dropped_frames += 1

                        # Schedule next capture
                        next_capture_time += self.frame_interval

                    except Exception as e:
                        print(f"[ScreenRecorder] Error capturing frame: {e}")
                        next_capture_time = current_time + self.frame_interval
                else:
                    # Sleep briefly to avoid busy waiting
                    sleep_time = min(0.001, next_capture_time - current_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)

    def get_frame(self, timeout: float = 0.1) -> Optional[Tuple[float, np.ndarray]]:
        """
        Get next frame from queue.

        Args:
            timeout: Max time to wait for frame

        Returns:
            Tuple of (timestamp, frame) or None if queue is empty
        """
        try:
            return self.frames_queue.get(timeout=timeout)
        except:
            return None

    def get_stats(self) -> dict:
        """Get recording statistics."""
        return {
            'frame_count': self.frame_count,
            'dropped_frames': self.dropped_frames,
            'queue_size': self.frames_queue.qsize(),
            'fps': self.target_fps
        }
