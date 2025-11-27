"""
Utility functions for loading recorded training data.
Use these functions in your AI training pipeline.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import imageio


class TrainingDataLoader:
    """Load and process recorded training data."""

    def __init__(self, session_path: str):
        """
        Initialize data loader.

        Args:
            session_path: Path to recorded session directory
        """
        self.session_path = Path(session_path)

        if not self.session_path.exists():
            raise ValueError(f"Session path does not exist: {session_path}")

        self.metadata = self._load_metadata()
        self.video_path = self.session_path / "gameplay.mp4"
        self.inputs_path = self.session_path / "inputs_frame_aligned.json"

    def _load_metadata(self) -> dict:
        """Load session metadata."""
        metadata_path = self.session_path / "metadata.json"
        if not metadata_path.exists():
            return {}

        with open(metadata_path, 'r') as f:
            return json.load(f)

    def load_inputs(self) -> List[dict]:
        """
        Load frame-aligned input data.

        Returns:
            List of input states, one per frame
        """
        if not self.inputs_path.exists():
            raise FileNotFoundError(f"Inputs file not found: {self.inputs_path}")

        with open(self.inputs_path, 'r') as f:
            return json.load(f)

    def load_video_frames(self, start_frame: int = 0,
                         end_frame: Optional[int] = None) -> np.ndarray:
        """
        Load video frames.

        Args:
            start_frame: First frame to load
            end_frame: Last frame to load (None = all)

        Returns:
            Numpy array of shape (num_frames, height, width, channels)
        """
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")

        reader = imageio.get_reader(str(self.video_path))
        frames = []

        try:
            for i, frame in enumerate(reader):
                if i < start_frame:
                    continue
                if end_frame is not None and i >= end_frame:
                    break

                frames.append(frame)

        finally:
            reader.close()

        return np.array(frames)

    def get_batch(self, start_frame: int, num_frames: int) -> Tuple[np.ndarray, List[dict]]:
        """
        Get a batch of synchronized frames and inputs.

        Args:
            start_frame: Starting frame index
            num_frames: Number of frames to load

        Returns:
            Tuple of (video_frames, input_states)
        """
        end_frame = start_frame + num_frames

        frames = self.load_video_frames(start_frame, end_frame)
        inputs = self.load_inputs()[start_frame:end_frame]

        return frames, inputs

    def get_num_frames(self) -> int:
        """Get total number of frames in the recording."""
        if 'screen_stats' in self.metadata:
            return self.metadata['screen_stats']['frame_count']

        # Fallback: count frames in video
        reader = imageio.get_reader(str(self.video_path))
        count = sum(1 for _ in reader)
        reader.close()
        return count

    def get_fps(self) -> int:
        """Get frames per second of the recording."""
        return self.metadata.get('fps', 30)

    def get_resolution(self) -> Tuple[int, int]:
        """Get video resolution (width, height)."""
        resolution = self.metadata.get('resolution')
        if resolution:
            return tuple(resolution)

        # Fallback: read from first frame
        reader = imageio.get_reader(str(self.video_path))
        first_frame = next(iter(reader))
        reader.close()

        height, width = first_frame.shape[:2]
        return (width, height)

    def get_info(self) -> dict:
        """Get comprehensive information about the recording."""
        return {
            'num_frames': self.get_num_frames(),
            'fps': self.get_fps(),
            'resolution': self.get_resolution(),
            'duration': self.metadata.get('duration', 0),
            'metadata': self.metadata
        }


def load_session(session_path: str) -> TrainingDataLoader:
    """
    Load a training session.

    Args:
        session_path: Path to session directory

    Returns:
        TrainingDataLoader instance
    """
    return TrainingDataLoader(session_path)


# Example usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python load_data.py <session_path>")
        sys.exit(1)

    session_path = sys.argv[1]

    print(f"Loading session: {session_path}")
    loader = load_session(session_path)

    info = loader.get_info()
    print(f"\nSession Info:")
    print(f"  Frames: {info['num_frames']}")
    print(f"  FPS: {info['fps']}")
    print(f"  Resolution: {info['resolution']}")
    print(f"  Duration: {info['duration']:.1f}s")

    # Load first 10 frames as example
    print(f"\nLoading first 10 frames...")
    frames, inputs = loader.get_batch(0, 10)

    print(f"  Frames shape: {frames.shape}")
    print(f"  Inputs count: {len(inputs)}")
    print(f"\nFirst input state:")
    print(f"  {inputs[0]}")
