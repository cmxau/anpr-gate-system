import time
from config import settings

def trigger_gate(duration_seconds: int = None) -> None:
    """Open gate by activating relay. Closes after duration_seconds."""
    if duration_seconds is None:
        duration_seconds = settings.gate_close_delay

    if settings.relay_mode == "mock":
        print(f"[GATE] Opened for {duration_seconds}s (mock)")
        return

    if settings.relay_mode == "gpio":
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(settings.relay_pin, GPIO.OUT)
        GPIO.output(settings.relay_pin, GPIO.HIGH)
        time.sleep(duration_seconds)
        GPIO.output(settings.relay_pin, GPIO.LOW)
        return

    raise ValueError(f"Unknown relay_mode: {settings.relay_mode}")
