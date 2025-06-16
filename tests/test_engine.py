import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base
from backend import crud
from backend.schemas import VehicleCreate

@pytest.fixture
def db():
    engine = sa_create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_engine_opens_gate_for_registered_vehicle(db, tmp_path):
    v = crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                               roll_number="21BCE001", vehicle_type="bike"))
    gate_calls = []

    with patch("anpr_engine.engine.SessionLocal", return_value=db), \
         patch("anpr_engine.engine.trigger_gate", side_effect=lambda: gate_calls.append(1)), \
         patch("anpr_engine.engine.settings") as mock_settings, \
         patch("anpr_engine.engine.detect_plate_region", return_value=np.ones((30, 120, 3), dtype=np.uint8)), \
         patch("anpr_engine.engine.read_plate", return_value=("MH12AB1234", 0.95)), \
         patch("anpr_engine.engine.frame_sampler", return_value=iter([np.zeros((480, 640, 3), dtype=np.uint8)])):
        mock_settings.confidence_threshold = 0.85
        mock_settings.duplicate_suppression_seconds = 30
        mock_settings.snapshot_dir = str(tmp_path)
        mock_settings.gate_direction = "IN"
        from anpr_engine.engine import run_engine
        run_engine()

    assert len(gate_calls) == 1
    logs = crud.list_logs(db)
    assert len(logs) == 1
    assert logs[0].plate == "MH12AB1234"

def test_engine_alerts_for_unknown_vehicle(db, tmp_path):
    alert_calls = []

    with patch("anpr_engine.engine.SessionLocal", return_value=db), \
         patch("anpr_engine.engine.trigger_gate") as mock_gate, \
         patch("anpr_engine.engine.send_guard_alert", side_effect=lambda p, s, t: alert_calls.append(p)), \
         patch("anpr_engine.engine.settings") as mock_settings, \
         patch("anpr_engine.engine.detect_plate_region", return_value=np.ones((30, 120, 3), dtype=np.uint8)), \
         patch("anpr_engine.engine.read_plate", return_value=("KA05XY9988", 0.91)), \
         patch("anpr_engine.engine.frame_sampler", return_value=iter([np.zeros((480, 640, 3), dtype=np.uint8)])):
        mock_settings.confidence_threshold = 0.85
        mock_settings.duplicate_suppression_seconds = 30
        mock_settings.snapshot_dir = str(tmp_path)
        mock_settings.gate_direction = "IN"
        from anpr_engine.engine import run_engine
        run_engine()

    mock_gate.assert_not_called()
    assert "KA05XY9988" in alert_calls
