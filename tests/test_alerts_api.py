import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base, get_db
from backend.main import app
from backend import crud

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
    crud.create_alert(db, plate="KA05XY9988", snapshot_path="/tmp/snap.jpg")
    db.close()

    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)

def test_list_alerts(client):
    res = client.get("/alerts/")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["resolved"] is False

def test_list_unresolved_alerts(client):
    res = client.get("/alerts/?resolved=false")
    assert len(res.json()) == 1

def test_resolve_alert(client):
    alerts = client.get("/alerts/").json()
    alert_id = alerts[0]["id"]
    res = client.post(f"/alerts/{alert_id}/resolve")
    assert res.status_code == 200
    resolved = client.get("/alerts/?resolved=true").json()
    assert len(resolved) == 1

def test_resolve_nonexistent_alert(client):
    res = client.post("/alerts/9999/resolve")
    assert res.status_code == 404
