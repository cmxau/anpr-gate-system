import easyocr
import numpy as np

_reader = None

def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _reader

def read_plate(image: np.ndarray) -> tuple[str, float]:
    """Returns (text, confidence). Returns ('', 0.0) on no detection."""
    reader = _get_reader()
    results = reader.readtext(image)
    if not results:
        return '', 0.0
    best = max(results, key=lambda r: r[2])
    return best[1].strip(), float(best[2])
