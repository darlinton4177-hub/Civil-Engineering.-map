import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Engineering & Science Hub" in data["service"]
    assert data["api_v1"] == "/api/v1"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "supabase_connected" in data
    assert data["supabase_connected"] is True


def test_departments_endpoint():
    response = client.get("/api/v1/departments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["code"] == "civil"


def test_courses_endpoint():
    response = client.get("/api/v1/courses?department=civil")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    codes = [c["code"] for c in data]
    assert "CE-101" in codes
    assert "CE-201" in codes


def test_problem_modules_list():
    response = client.get("/api/v1/problem-modules?discipline=civil")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    slugs = [m["slug"] for m in data]
    assert "simply-supported-beam" in slugs
    assert "mohrs-circle" in slugs


def test_get_single_problem_module():
    response = client.get("/api/v1/problem-modules/simply-supported-beam")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "simply-supported-beam"
    assert data["course_code"] == "CE-201"


def test_module_validation():
    response = client.post(
        "/api/v1/problem-modules/simply-supported-beam/validate",
        json={"inputs": {"span_length": 6.0, "load_magnitude": 15.0}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True


def test_runs_create_and_list():
    create_resp = client.post(
        "/api/v1/runs",
        json={
            "module_slug": "simply-supported-beam",
            "title": "Test Beam Calculation",
            "inputs": {"span": 5.0},
            "outputs": {"reaction_A": 25.0},
        },
    )
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["title"] == "Test Beam Calculation"

    list_resp = client.get("/api/v1/runs")
    assert list_resp.status_code == 200
    runs = list_resp.json()
    assert len(runs) >= 1
    assert runs[0]["title"] == "Test Beam Calculation"
