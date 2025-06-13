import cv2
import numpy as np
import time
from typing import Generator

def frame_sampler(camera_url: str, interval_ms: int = 500) -> Generator[np.ndarray, None, None]:
    """Yields frames from RTSP/file stream at interval_ms cadence."""
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open stream: {camera_url}")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            yield frame
            time.sleep(interval_ms / 1000.0)
    finally:
        cap.release()
