from fastapi.testclient import TestClient

import jwt
from app.config import get_settings


settings = get_settings()

def test_register_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["email"] == "alice@example.com"
    assert isinstance(response_body["id"], int)
    assert "created_at" in response_body

    assert "password" not in response_body
    assert "hashed_password" not in response_body


def test_register_duplicate_email(client: TestClient) -> None:
    registration = {
        "email": "alice@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/auth/register",
        json=registration,
    )
    second_response = client.post(
        "/auth/register",
        json=registration,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "A user with this email already exists."
    }


def test_register_rejects_invalid_input(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_login_returns_valid_access_token(
    client: TestClient,
) -> None:
    registration_response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "password123",
        },
    )

    user_id = registration_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    response_body = login_response.json()

    assert response_body["token_type"] == "bearer"
    assert isinstance(response_body["access_token"], str)

    payload = jwt.decode(
        response_body["access_token"],
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == str(user_id)
    assert "iat" in payload
    assert "exp" in payload


def test_login_rejects_incorrect_password(
    client: TestClient,
) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect email or password."
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_unknown_email(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect email or password."
    }