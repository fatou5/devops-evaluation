from fastapi.testclient import TestClient

from app.main import app, redis_client


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint_uses_redis():
    before = int(redis_client.get("requests") or 0)

    response = client.get("/")

    after = int(redis_client.get("requests") or 0)

    assert response.status_code == 200
    assert response.json()["message"] == "DevOps Evaluation API"
    assert after == before + 1


def test_metrics_endpoint():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_slow_endpoint():
    response = client.get("/test-slow")

    assert response.status_code == 200
    assert response.json()["message"] == "intentional slow response"

