from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# ==========================================
# TEST DATABASE
# ==========================================

SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ==========================================
# TEST DATABASE DEPENDENCY
# ==========================================

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ==========================================
# RESET DATABASE BEFORE EACH TEST
# ==========================================

import pytest


@pytest.fixture(autouse=True)
def reset_database():

    Base.metadata.drop_all(bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    yield


# ==========================================
# TESTS
# ==========================================

def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Appreciation API is running"
    }


def test_get_appreciations():

    response = client.get("/appreciations")

    assert response.status_code == 200

    assert response.json()["count"] == 0


def test_appreciate():

    response = client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    assert response.status_code == 201

    assert response.json()["message"] == (
        "Thank you for the appreciation!"
    )

    assert response.json()["id"] == 1


def test_duplicate_appreciation():

    first_response = client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    second_response = client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    assert first_response.status_code == 201

    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "You have already appreciated this website."
    )


def test_different_visitors_can_appreciate():

    first_response = client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    second_response = client.post(
        "/appreciate",
        params={"visitor_id": "visitor-002"}
    )

    assert first_response.status_code == 201

    assert second_response.status_code == 201


def test_count_after_appreciation():

    client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    response = client.get("/appreciations")

    assert response.status_code == 200

    assert response.json()["count"] == 1


def test_duplicate_does_not_increase_count():

    client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    response = client.get("/appreciations")

    assert response.status_code == 200

    assert response.json()["count"] == 1


def test_appreciation_status_before_appreciating():

    response = client.get(
        "/appreciation/status",
        params={"visitor_id": "visitor-001"}
    )

    assert response.status_code == 200

    assert response.json() == {
        "appreciated": False
    }


def test_appreciation_status_after_appreciating():

    client.post(
        "/appreciate",
        params={"visitor_id": "visitor-001"}
    )

    response = client.get(
        "/appreciation/status",
        params={"visitor_id": "visitor-001"}
    )

    assert response.status_code == 200

    assert response.json() == {
        "appreciated": True
    }
