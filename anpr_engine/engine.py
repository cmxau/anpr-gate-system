import cv2
import os
import time
from datetime import datetime, timezone
from anpr_engine.camera import frame_sampler
from anpr_engine.detector import detect_plate_region
from anpr_engine.ocr import read_plate
from anpr_engine.normalizer import normalize_plate
from anpr_engine.gate import trigger_gate
from backend.database import SessionLocal
from backend import crud
from backend.notifier import send_guard_alert
from config import settings

def run_engine() -> None:
    recently_seen: dict[str, float] = {}
    os.makedirs(settings.snapshot_dir, exist_ok=True)

    for frame in frame_sampler(settings.camera_url):
        plate_img = detect_plate_region(frame)
        if plate_img is None:
            continue

        raw_text, confidence = read_plate(plate_img)
        if confidence < settings.confidence_threshold:
            continue

        plate = normalize_plate(raw_text)
        if not plate:
            continue

        now = time.time()
        last_seen = recently_seen.get(plate, 0.0)
        if now - last_seen < settings.duplicate_suppression_seconds:
            continue
        recently_seen[plate] = now
        if len(recently_seen) > 500:
            oldest = min(recently_seen, key=recently_seen.get)
            del recently_seen[oldest]

        db = SessionLocal()
        try:
            vehicle = crud.get_vehicle_by_plate(db, plate)

            if vehicle and vehicle.active:
                anomaly = crud.is_double_entry(db, plate)
                crud.create_log(db, plate=plate, owner_id=vehicle.id,
                                direction=settings.gate_direction, confidence_score=confidence, anomaly=anomaly)
                trigger_gate()
            else:
                timestamp = datetime.now(timezone.utc).isoformat()
                snapshot_path = os.path.join(settings.snapshot_dir, f"{plate}_{int(now)}.jpg")
                cv2.imwrite(snapshot_path, frame)
                crud.create_alert(db, plate=plate, snapshot_path=snapshot_path)
                send_guard_alert(plate, snapshot_path, timestamp)
        finally:
            db.close()
