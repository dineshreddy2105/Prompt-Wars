from fastapi.testclient import TestClient
import pytest

def test_health_check(client):
    """Verify the health check endpoint returns 200 OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_departments(client):
    """Verify the departments list is returned correctly."""
    response = client.get("/api/departments")
    assert response.status_code == 200
    assert "departments" in response.json()
    assert len(response.json()["departments"]) > 0

def test_root_redirect(client):
    """Verify root redirects to /app."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/app"

def test_submit_complaint_missing_description(client):
    """Verify 422 if description is missing."""
    response = client.post("/api/submit-complaint", data={})
    assert response.status_code == 422

def test_submit_complaint_too_short(client):
    """Verify 400 if description is too short."""
    response = client.post("/api/submit-complaint", data={"description": "abc"})
    assert response.status_code == 400
