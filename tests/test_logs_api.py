import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base, get_db
from backend.main import app
from backend import crud
from backend.schemas import VehicleCreate

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = Session()
    v = crud.create_vehicle(db, VehicleCreate(plate="MH12AB1234", owner_name="Rahul",
                                               roll_number="21BCE001", vehicle_type="bike"))
    crud.create_log(db, plate="MH12AB1234", owner_id=v.id, direction="IN", confidence_score=0.92)
    crud.create_log(db, plate="MH12AB1234", owner_id=v.id, direction="OUT", confidence_score=0.88)
    db.close()

    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_list_logs(client):
    res = client.get("/logs/")
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_filter_logs_by_plate(client):
    res = client.get("/logs/?plate=MH12AB1234")
    assert res.status_code == 200
    assert all(l["plate"] == "MH12AB1234" for l in res.json())

def test_export_logs_csv(client):
    res = client.get("/logs/export")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "MH12AB1234" in res.text
