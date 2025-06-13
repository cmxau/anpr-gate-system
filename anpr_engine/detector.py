import cv2
import numpy as np

def detect_plate_region(frame: np.ndarray) -> np.ndarray | None:
    """
    Returns cropped plate region from frame using contour detection.
    Returns None if no plate-shaped region found.
    Tuned for rectangular Indian plates (aspect ratio 2.0–6.0).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edges = cv2.Canny(blur, 30, 200)
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if h == 0:
                continue
            aspect = w / h
            if 2.0 <= aspect <= 6.0:
                return frame[y:y + h, x:x + w]
    return None
