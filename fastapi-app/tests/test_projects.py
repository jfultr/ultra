from fastapi.testclient import TestClient
from conftest import signup_and_login


def test_project_crud_flow(client: TestClient):
    token = signup_and_login(client, "user@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    res = client.post("/api/projects/", json={"title": "A", "description": "B"}, headers=headers)
    assert res.status_code == 201, res.text
    project = res.json()
    project_id = project["id"]

    # List
    res = client.get("/api/projects/", headers=headers)
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) == 1

    # Get
    res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == project_id

    # Update
    res = client.put(f"/api/projects/{project_id}", json={"title": "X"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "X"

    # Delete
    res = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert res.status_code == 204

    # Not found after delete
    res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert res.status_code == 404


def test_non_owner_cannot_delete_project(client: TestClient):
    # owner creates project
    owner_token = signup_and_login(client, "owner_del@example.com", "password123")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    res = client.post("/api/projects/", json={"title": "Del", "description": "X"}, headers=owner_headers)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # editor user
    editor_token = signup_and_login(client, "editor_del@example.com", "password123")
    editor_headers = {"Authorization": f"Bearer {editor_token}"}

    # owner adds editor
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "editor_del@example.com", "role": "editor"},
        headers=owner_headers,
    )
    assert res.status_code == 200

    # editor attempts to delete -> 404 (cannot see delete outcome per router)
    res = client.delete(f"/api/projects/{project_id}", headers=editor_headers)
    assert res.status_code in (403, 404)


def test_empty_update_payload_noop_and_non_member_update_404(client: TestClient):
    # creator makes project
    token = signup_and_login(client, "upd@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/projects/", json={"title": "U", "description": "D"}, headers=headers)
    assert res.status_code == 201
    project_id = res.json()["id"]

    # Empty update payload should succeed and not error
    res = client.put(f"/api/projects/{project_id}", json={}, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "U"
    assert body["description"] == "D"

    # Non-member update should 404 (cannot see project)
    outsider_token = signup_and_login(client, "updoutsider@example.com", "password123")
    outsider_headers = {"Authorization": f"Bearer {outsider_token}"}
    res = client.put(f"/api/projects/{project_id}", json={"title": "new"}, headers=outsider_headers)
    assert res.status_code == 404


def test_editor_can_update_project(client: TestClient):
    # user1 creates project
    token1 = signup_and_login(client, "user1@example.com", "password123")
    headers1 = {"Authorization": f"Bearer {token1}"}

    res = client.post("/api/projects/", json={"title": "P", "description": "D"}, headers=headers1)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # user2 signs up
    token2 = signup_and_login(client, "user2@example.com", "password123")
    headers2 = {"Authorization": f"Bearer {token2}"}

    # owner adds user2 as editor
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "user2@example.com", "role": "editor"},
        headers=headers1,
    )
    assert res.status_code == 200, res.text

    # editor can update the project
    res = client.put(f"/api/projects/{project_id}", json={"title": "P2"}, headers=headers2)
    assert res.status_code == 200
    assert res.json()["title"] == "P2"


def test_viewer_cannot_update_project(client: TestClient):
    # user1 creates project
    token1 = signup_and_login(client, "user1@example.com", "password123")
    headers1 = {"Authorization": f"Bearer {token1}"}

    res = client.post("/api/projects/", json={"title": "P", "description": "D"}, headers=headers1)
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # user2 signs up
    token2 = signup_and_login(client, "user2@example.com", "password123")
    headers2 = {"Authorization": f"Bearer {token2}"}

    # owner adds user2 as viewer
    res = client.post(
        f"/api/projects/{project_id}/users",
        json={"principal": "user2@example.com", "role": "viewer"},
        headers=headers1,
    )
    assert res.status_code == 200, res.text

    # viewer cannot update the project (should 404 due to membership check)
    res = client.put(f"/api/projects/{project_id}", json={"title": "P3"}, headers=headers2)
    assert res.status_code == 404
