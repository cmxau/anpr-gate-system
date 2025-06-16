import numpy as np
import cv2
import pytest
from anpr_engine.ocr import read_plate

def make_plate_image(text: str) -> np.ndarray:
    img = np.ones((60, 200, 3), dtype=np.uint8) * 255
    cv2.putText(img, text, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    return img

def test_read_plate_returns_text_and_confidence():
    img = make_plate_image("MH12AB")
    text, confidence = read_plate(img)
    assert isinstance(text, str)
    assert 0.0 <= confidence <= 1.0

def test_read_plate_blank_image_returns_empty():
    img = np.ones((60, 200, 3), dtype=np.uint8) * 255
    text, confidence = read_plate(img)
    assert text == "" or confidence == 0.0

def test_read_plate_returns_tuple():
    img = make_plate_image("KA05")
    result = read_plate(img)
    assert len(result) == 2
