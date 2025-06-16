from backend.models import Vehicle, Log, Alert
from backend import crud
from backend.schemas import VehicleCreate, VehicleUpdate
from datetime import datetime, timezone

def test_create_vehicle(db):
    v = Vehicle(plate="MH12AB1234", owner_name="Rahul", roll_number="21BCE001", vehicle_type="bike", active=True)
    db.add(v)
    db.commit()
    result = db.query(Vehicle).filter_by(plate="MH12AB1234").first()
    assert result.owner_name == "Rahul"
    assert result.active is True

def test_create_log(db):
    v = Vehicle(plate="MH12AB1234", owner_name="Rahul", roll_number="21BCE001", vehicle_type="bike", active=True)
    db.add(v); db.commit()
    log = Log(plate="MH12AB1234", owner_id=v.id, direction="IN", method="ANPR",
              confidence_score=0.92, anomaly=False, timestamp=datetime.now(timezone.utc))
    db.add(log); db.commit()
    result = db.query(Log).first()
    assert result.direction == "IN"
    assert result.confidence_score == 0.92

def test_create_alert(db):
    alert = Alert(plate="KA05XY9988", snapshot_path="/tmp/snap.jpg",
                  timestamp=datetime.now(timezone.utc), resolved=False)
    db.add(alert); db.commit()
    result = db.query(Alert).first()
    assert result.resolved is False

def test_get_vehicle_by_plate(db):
    crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                           roll_number="21BCE001", vehicle_type="bike"))
    result = crud.get_vehicle_by_plate(db, "MH12AB1234")
    assert result is not None
    assert result.owner_name == "Rahul"

def test_get_vehicle_by_plate_missing(db):
    assert crud.get_vehicle_by_plate(db, "NOTEXIST") is None

def test_list_vehicles_with_search(db):
    crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                           roll_number="21BCE001", vehicle_type="bike"))
    crud.create_vehicle(db, VehicleCreate(plate="KA05XY9988", owner_name="Priya",
                                           roll_number="21BCE002", vehicle_type="car"))
    results = crud.list_vehicles(db, search="Rahul")
    assert len(results) == 1
    assert results[0].plate == "MH12AB1234"

def test_deactivate_vehicle(db):
    v = crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                               roll_number="21BCE001", vehicle_type="bike"))
    assert crud.deactivate_vehicle(db, v.id) is True
    assert crud.get_vehicle_by_plate(db, "MH12AB1234").active is False

def test_is_double_entry_no_logs(db):
    assert crud.is_double_entry(db, "MH12AB1234") is False

def test_is_double_entry_after_in(db):
    v = crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                               roll_number="21BCE001", vehicle_type="bike"))
    crud.create_log(db, plate="MH12AB1234", owner_id=v.id, direction="IN", confidence_score=0.9)
    assert crud.is_double_entry(db, "MH12AB1234") is True

def test_is_double_entry_after_out(db):
    v = crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                               roll_number="21BCE001", vehicle_type="bike"))
    crud.create_log(db, plate="MH12AB1234", owner_id=v.id, direction="IN", confidence_score=0.9)
    crud.create_log(db, plate="MH12AB1234", owner_id=v.id, direction="OUT", confidence_score=0.9)
    assert crud.is_double_entry(db, "MH12AB1234") is False

def test_resolve_alert(db):
    alert = crud.create_alert(db, plate="KA05XY9988", snapshot_path="/tmp/snap.jpg")
    assert crud.resolve_alert(db, alert.id) is True
    result = db.query(Alert).first()
    assert result.resolved is True
