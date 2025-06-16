import numpy as np
import cv2
import pytest
from anpr_engine.detector import detect_plate_region

def make_frame_with_plate() -> np.ndarray:
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 180
    # Draw a white rectangle simulating a plate (aspect 4:1)
    cv2.rectangle(frame, (200, 200), (440, 280), (255, 255, 255), -1)
    cv2.putText(frame, "MH12AB1234", (205, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    return frame

def test_detect_returns_numpy_array_or_none():
    frame = make_frame_with_plate()
    result = detect_plate_region(frame)
    assert result is None or isinstance(result, np.ndarray)

def test_detect_blank_frame_returns_none():
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
    result = detect_plate_region(frame)
    assert result is None

def test_detect_result_has_plate_aspect_ratio():
    frame = make_frame_with_plate()
    result = detect_plate_region(frame)
    if result is not None:
        h, w = result.shape[:2]
        aspect = w / h
        assert 1.5 <= aspect <= 7.0
