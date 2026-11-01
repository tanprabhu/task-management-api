from fastapi.testclient import TestClient


def authenticated_user(
    client: TestClient,
    email: str = "alice@example.com",
) -> tuple[dict[str, str], int]:
    registration_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "password123",
        },
    )

    user_id = registration_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    return headers, user_id


def test_create_task(client: TestClient) -> None:
    headers, user_id = authenticated_user(client)

    response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": "  Learn FastAPI  ",
            "description": "Build a protected endpoint.",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    task = response.json()

    assert isinstance(task["id"], int)
    assert task["title"] == "Learn FastAPI"
    assert task["description"] == "Build a protected endpoint."
    assert task["status"] == "todo"
    assert task["priority"] == "high"
    assert task["owner_id"] == user_id
    assert "created_at" in task
    assert "updated_at" in task


def test_create_task_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/tasks",
        json={
            "title": "Unauthorized task",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }


def test_create_task_rejects_invalid_values(
    client: TestClient,
) -> None:
    headers, _ = authenticated_user(client)

    response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": "",
            "status": "unknown",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422

def test_list_tasks_returns_only_owned_tasks(
    client: TestClient,
) -> None:
    alice_headers, _ = authenticated_user(
        client,
        email="alice@example.com",
    )
    bob_headers, _ = authenticated_user(
        client,
        email="bob@example.com",
    )

    client.post(
        "/tasks",
        headers=alice_headers,
        json={"title": "Alice task"},
    )
    client.post(
        "/tasks",
        headers=bob_headers,
        json={"title": "Bob task"},
    )

    alice_response = client.get(
        "/tasks",
        headers=alice_headers,
    )
    bob_response = client.get(
        "/tasks",
        headers=bob_headers,
    )

    assert alice_response.status_code == 200
    assert bob_response.status_code == 200

    assert [
        task["title"] for task in alice_response.json()
    ] == ["Alice task"]

    assert [
        task["title"] for task in bob_response.json()
    ] == ["Bob task"]


def test_get_owned_task(client: TestClient) -> None:
    headers, _ = authenticated_user(client)

    creation_response = client.post(
        "/tasks",
        headers=headers,
        json={"title": "Read this task"},
    )

    task_id = creation_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Read this task"


def test_user_cannot_read_another_users_task(
    client: TestClient,
) -> None:
    alice_headers, _ = authenticated_user(
        client,
        email="alice@example.com",
    )
    bob_headers, _ = authenticated_user(
        client,
        email="bob@example.com",
    )

    creation_response = client.post(
        "/tasks",
        headers=alice_headers,
        json={"title": "Alice private task"},
    )

    task_id = creation_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=bob_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }


def test_get_nonexistent_task_returns_not_found(
    client: TestClient,
) -> None:
    headers, _ = authenticated_user(client)

    response = client.get(
        "/tasks/999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_update_task_changes_only_provided_fields(
    client: TestClient,
) -> None:
    headers, _ = authenticated_user(client)

    creation_response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": "Original title",
            "description": "Keep this description",
            "priority": "high",
        },
    )
    task_id = creation_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        headers=headers,
        json={"status": "done"},
    )

    assert response.status_code == 200

    task = response.json()
    assert task["title"] == "Original title"
    assert task["description"] == "Keep this description"
    assert task["status"] == "done"
    assert task["priority"] == "high"


def test_update_task_can_clear_description(
    client: TestClient,
) -> None:
    headers, _ = authenticated_user(client)

    creation_response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": "Task with description",
            "description": "Remove this text",
        },
    )
    task_id = creation_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        headers=headers,
        json={"description": None},
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_task_rejects_empty_update(
    client: TestClient,
) -> None:
    headers, _ = authenticated_user(client)

    creation_response = client.post(
        "/tasks",
        headers=headers,
        json={"title": "Unchanged task"},
    )
    task_id = creation_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        headers=headers,
        json={},
    )

    assert response.status_code == 422


def test_user_cannot_update_another_users_task(
    client: TestClient,
) -> None:
    alice_headers, _ = authenticated_user(
        client,
        email="alice@example.com",
    )
    bob_headers, _ = authenticated_user(
        client,
        email="bob@example.com",
    )

    creation_response = client.post(
        "/tasks",
        headers=alice_headers,
        json={"title": "Alice private task"},
    )
    task_id = creation_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        headers=bob_headers,
        json={"title": "Bob changed this"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    unchanged_task = client.get(
        f"/tasks/{task_id}",
        headers=alice_headers,
    )
    assert unchanged_task.json()["title"] == "Alice private task"


def test_delete_owned_task(client: TestClient) -> None:
    headers, _ = authenticated_user(client)

    creation_response = client.post(
        "/tasks",
        headers=headers,
        json={"title": "Delete this task"},
    )
    task_id = creation_response.json()["id"]

    deletion_response = client.delete(
        f"/tasks/{task_id}",
        headers=headers,
    )

    assert deletion_response.status_code == 204
    assert deletion_response.content == b""

    retrieval_response = client.get(
        f"/tasks/{task_id}",
        headers=headers,
    )
    assert retrieval_response.status_code == 404


def test_user_cannot_delete_another_users_task(
    client: TestClient,
) -> None:
    alice_headers, _ = authenticated_user(
        client,
        email="alice@example.com",
    )
    bob_headers, _ = authenticated_user(
        client,
        email="bob@example.com",
    )

    creation_response = client.post(
        "/tasks",
        headers=alice_headers,
        json={"title": "Alice private task"},
    )
    task_id = creation_response.json()["id"]

    deletion_response = client.delete(
        f"/tasks/{task_id}",
        headers=bob_headers,
    )

    assert deletion_response.status_code == 404
    assert deletion_response.json() == {
        "detail": "Task not found."
    }

    retrieval_response = client.get(
        f"/tasks/{task_id}",
        headers=alice_headers,
    )
    assert retrieval_response.status_code == 200


def test_delete_nonexistent_task_returns_not_found(
    client: TestClient,
) -> None:
    headers, _ = authenticated_user(client)

    response = client.delete(
        "/tasks/999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_delete_task_requires_authentication(
    client: TestClient,
) -> None:
    response = client.delete("/tasks/1")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }
