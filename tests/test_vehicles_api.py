import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base, get_db
from backend.main import app

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
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_create_vehicle(client):
    res = client.post("/vehicles/", json={"plate": "MH12AB1234", "owner_name": "Rahul",
                                          "roll_number": "21BCE001", "vehicle_type": "bike"})
    assert res.status_code == 201
    assert res.json()["plate"] == "MH12AB1234"

def test_create_duplicate_vehicle(client):
    client.post("/vehicles/", json={"plate": "MH12AB1234", "owner_name": "Rahul",
                                    "roll_number": "21BCE001", "vehicle_type": "bike"})
    res = client.post("/vehicles/", json={"plate": "MH12AB1234", "owner_name": "Rahul2",
                                          "roll_number": "21BCE002", "vehicle_type": "bike"})
    assert res.status_code == 400

def test_list_vehicles(client):
    client.post("/vehicles/", json={"plate": "MH12AB1234", "owner_name": "Rahul",
                                    "roll_number": "21BCE001", "vehicle_type": "bike"})
    res = client.get("/vehicles/")
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_search_vehicles(client):
    client.post("/vehicles/", json={"plate": "MH12AB1234", "owner_name": "Rahul",
                                    "roll_number": "21BCE001", "vehicle_type": "bike"})
    client.post("/vehicles/", json={"plate": "KA05XY9988", "owner_name": "Priya",
                                    "roll_number": "21BCE002", "vehicle_type": "car"})
    res = client.get("/vehicles/?search=Priya")
    assert len(res.json()) == 1
    assert res.json()[0]["plate"] == "KA05XY9988"

def test_deactivate_vehicle(client):
    res = client.post("/vehicles/", json={"plate": "MH12AB1234", "owner_name": "Rahul",
                                          "roll_number": "21BCE001", "vehicle_type": "bike"})
    vehicle_id = res.json()["id"]
    res = client.delete(f"/vehicles/{vehicle_id}")
    assert res.status_code == 200
    vehicles = client.get("/vehicles/").json()
    assert vehicles[0]["active"] is False

def test_csv_import(client):
    csv_content = "plate,owner_name,roll_number,vehicle_type\nMH12AB1234,Rahul,21BCE001,bike\nKA05XY9988,Priya,21BCE002,car\n"
    res = client.post("/vehicles/import", files={"file": ("vehicles.csv", csv_content, "text/csv")})
    assert res.status_code == 200
    assert res.json()["imported"] == 2
    assert res.json()["skipped"] == 0
