import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_is_ok_without_dependencies(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.integration
def test_ready_with_dependencies(client):
    resp = client.get("/ready")
    assert resp.status_code == 200, resp.json()
    assert resp.json()["checks"] == {"database": True, "redis": True}


@pytest.mark.integration
def test_api_status(client):
    body = client.get("/api/v1/status").json()
    assert body["version"]
    assert body["checks"]["database"] is True
