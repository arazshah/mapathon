import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, SessionLocal, engine, Base

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """
    ساخت دیتابیس موقت برای تست
    """
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_submit_feedback():
    response = client.post("/api/v1/feedback/", json={
        "query_text": "مترو نزدیک میدان انقلاب",
        "feedback_type": "correct",
        "comment": "پاسخ خوب بود",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["feedback_type"] == "correct"
    assert data["query_text"] == "مترو نزدیک میدان انقلاب"


def test_list_feedback():
    client.post("/api/v1/feedback/", json={
        "query_text": "تست نظر",
        "feedback_type": "suggestion",
    })
    response = client.get("/api/v1/feedback/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["feedback_type"] == "suggestion"


def test_feedback_stats():
    client.post("/api/v1/feedback/", json={
        "feedback_type": "wrong_result",
    })
    response = client.get("/api/v1/feedback/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "wrong_result" in data["by_type"]
