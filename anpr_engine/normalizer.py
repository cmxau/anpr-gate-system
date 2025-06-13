import re

def normalize_plate(raw: str) -> str:
    return re.sub(r'[^A-Z0-9]', '', raw.upper())
